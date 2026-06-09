from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import User
from sqlalchemy import select
from typing import Optional

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
    