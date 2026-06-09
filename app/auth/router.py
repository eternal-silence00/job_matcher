from fastapi import APIRouter, Depends
from app.auth.schemas import UserResponse, UserCreate, TokenResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.service import AuthService

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