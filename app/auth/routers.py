from fastapi import APIRouter, Depends, HTTPException
from app.auth.schemas import UserResponse, UserCreate, TokenResponse, RefreshRequest
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.service import AuthService, create_access_token, create_refresh_token
from app.auth.oauth import oauth
from starlette.requests import Request
from authlib.integrations.base_client.errors import OAuthError
from app.core.dependencies import get_current_user
from app.auth.models import User
from fastapi.responses import RedirectResponse
from app.core.limiter import limiter, email_limiter, EMAIL_LOGIN_LIMIT
import logging 

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/minute")
async def register(
    request: Request, 
    data: UserCreate,
    session: AsyncSession = Depends(get_db)
):
    service = AuthService(session)
    result = await service.register(data)
    return result 

@router.post("/auth/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,  
    data: UserCreate,
    session: AsyncSession = Depends(get_db)
):
    user_agent = request.headers.get("user-agent")
    ip = request.client.host
    email_key = "login:email:" + data.email.lower()
    if not email_limiter.hit(EMAIL_LOGIN_LIMIT, email_key):
        logger.warning("rate limit hit by_email domain=%s", data.email.split("@")[1])
        raise HTTPException(status_code=429, detail="Too many login attempts for this email. Try again in a minute.")
    service = AuthService(session)
    result = await service.login(data, user_agent, ip)
    return result

@router.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def google_callback(request: Request, session: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        logger.warning("oauth callback failed reason=state_mismatch")
        return RedirectResponse("http://localhost:5173/login?oauth_error=1")
    email = token.get("userinfo").get("email")
    user_agent = request.headers.get("user-agent")
    ip = request.client.host
    service = AuthService(session)
    tokens = await service.oauth_login(email, user_agent, ip)
    return RedirectResponse(
        f"http://localhost:5173/auth/callback?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}",
        status_code=302,
    )

@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/auth/refresh", response_model=TokenResponse)
@limiter.limit("5/minute")
async def refresh(request: Request, data: RefreshRequest, session: AsyncSession = Depends(get_db)):
    user_agent = request.headers.get("user-agent")
    ip = request.client.host
    service = AuthService(session)
    return await service.refresh(data.refresh_token, user_agent, ip)

@router.post("/auth/logout", status_code=204)
async def logout(data: RefreshRequest, session: AsyncSession = Depends(get_db)):
    service = AuthService(session)
    await service.logout(data.refresh_token)
    return None

@router.post("/auth/logout-all", status_code=204)
async def logout_all(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)
    await service.logout_all(current_user.id)
    return None