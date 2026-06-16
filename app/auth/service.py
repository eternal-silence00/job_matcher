import logging
from passlib.context import CryptContext
import hashlib
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.auth.schemas import UserCreate
from app.auth.repository import UserRepository, RefreshTokenRepository

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=['bcrypt'])

def hash_password(password: str):
    return pwd_context.hash(password)

def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
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
        user_agent: str,
        ip: str
    ):
        repo = UserRepository(self.session)
        refresh_repo = RefreshTokenRepository(self.session)
        user = await repo.get_by_email(data.email)
        if not user:
            logger.warning("login failed reason=user_not_found email_domain=%s",
                       data.email.split("@")[1])
            raise HTTPException(status_code=401, detail="Invalid credentials")
        verified = verify_password(data.password, user.hashed_password)
        if not verified:
            logger.warning("login failed reason=wrong_password user_id=%s", user.id)
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        token_hash = hash_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        await refresh_repo.create_refresh(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip=ip
        )
        logger.info("user logged in id=%s", user.id)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

        



