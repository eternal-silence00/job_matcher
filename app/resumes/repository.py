from sqlalchemy import select
from app.resumes.models import Resume
from sqlalchemy.ext.asyncio import AsyncSession

class ResumeRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create(self, user_id, filename, content, embedding):
        resume = Resume(
            user_id = user_id,
            filename = filename,
            content = content,
            embedding = embedding
        )
        self.session.add(resume)
        await self.session.flush()
        await self.session.refresh(resume)
        return resume
    
    async def get_by_user_id(self, user_id: int):
        result = await self.session.execute(select(Resume).where(Resume.user_id == user_id))
        return result.scalar_one_or_none()
    
    async def update(self, user_id: int, filename: str, content: str, embedding: list):
        result = await self.session.execute(select(Resume).where(Resume.user_id == user_id))
        resume = result.scalar_one_or_none()
        if not resume:
            return None
        resume.filename = filename
        resume.content = content
        resume.embedding = embedding
        await self.session.flush()
        await self.session.refresh(resume)
        return resume
    