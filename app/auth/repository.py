from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import User, RefreshToken
from sqlalchemy import select, update
from typing import Optional
from datetime import datetime, timezone
from app.resumes.models import Resume


class UserRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_user(self, email: str, hashed_password: Optional[str]):
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def get_by_email(self, email: str):
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    
    async def get_by_id(self, user_id: int):
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    
    async def get_all_with_resumes(self):
        result = await self.session.execute(select(User).join(Resume, User.id == Resume.user_id))
        return result.scalars().all()
    
class RefreshTokenRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_refresh(self, user_id, token_hash, expires_at, user_agent=None, ip=None) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip=ip
        )
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token
    
    async def get_by_hash(self, token_hash: str):
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        return result.scalar_one_or_none()
    
    async def revoke(self, token: RefreshToken, replaced_by_id = None):
        token.revoked_at = datetime.now(timezone.utc)
        if replaced_by_id is not None:
            token.replaced_by_id = replaced_by_id
        await self.session.flush()
        return token
    
    async def revoke_all_for_user(self, user_id: int):
        await self.session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(timezone.utc))
        )
        
        
    
    
    
    
        