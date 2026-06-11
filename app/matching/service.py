from sqlalchemy.ext.asyncio import AsyncSession
from app.resumes.repository import ResumeRepository
from app.jobs.repository import JobRepository
from fastapi import HTTPException



class MatchingService:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def match_jobs(self, user_id, limit: int = 20):
        resume_repo = ResumeRepository(self.session)
        job_repo = JobRepository(self.session)
        
        resume = await resume_repo.get_by_user_id(user_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        matching = await job_repo.find_simular(resume.embedding, limit)
        return matching 
        