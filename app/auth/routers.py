from fastapi import APIRouter, Depends
from app.auth.schemas import UserResponse, UserCreate, TokenResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.service import AuthService, create_access_token, create_refresh_token
from app.auth.oauth import oauth
from starlette.requests import Request
from app.auth.repository import UserRepository
from app.core.dependencies import get_current_user
from app.auth.models import User

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserCreate,
    session: AsyncSession = Depends(get_db)
):
    service = AuthService(session)
    result = await service.register(data)
    return result 

@router.post("/auth/login", response_model=TokenResponse)
async def login(
    data: UserCreate,
    session: AsyncSession = Depends(get_db)
):
    service = AuthService(session)
    result = await service.login(data)
    return result

@router.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback", response_model=TokenResponse)
async def google_callback(request: Request, session: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    email = user_info.get("email")
    repo = UserRepository(session)
    user = await repo.get_by_email(email)
    if not user:
        user = await repo.create_user(email, hashed_password=None)
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user