import logging
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.auth.schemas import UserCreate
from app.auth.repository import UserRepository

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=['bcrypt'])

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class AuthService:
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def register(
        self, 
        data: UserCreate,
        ):
        repo = UserRepository(self.session)
        email_exists = await repo.get_by_email(data.email)
        if email_exists:
            logger.warning("registration attempt for existing email user_id=%s", email_exists.id)
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = hash_password(data.password)
        user = await repo.create_user(data.email, hashed_password)
        logger.info("user registered id=%s", user.id)
        return user
    
    async def login(
        self, 
        data: UserCreate,
    ):
        repo = UserRepository(self.session)
        user = await repo.get_by_email(data.email)
        if not user:
            logger.warning("login failed reason=user_not_found email_domain=%s",
                       data.email.split("@")[1])
            raise HTTPException(status_code=404, detail="user not found")
        verified = verify_password(data.password, user.hashed_password)
        if not verified:
            logger.warning("login failed reason=wrong_password user_id=%s", user.id)
            raise HTTPException(status_code=400, detail="Wrong password")
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        logger.info("user logged in id=%s", user.id)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

        



