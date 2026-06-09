from sqlalchemy.ext.asyncio import AsyncSession
from app.jobs.schemas import JobCreate
from app.jobs.repository import JobRepository
from app.core.embedding_service import EmbeddingService


class JobService:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_job(self, data: JobCreate):
        repo = JobRepository(self.session)
        text = f"{data.title}. {data.description}"
        embedding = EmbeddingService().get_embedding(text)
        result = await repo.create(
            data.title, 
            data.description,
            data.salary_from, 
            data.salary_to, 
            data.company,
            data.url,
            data.location,
            data.published_at,
            embedding
        )
        return result 
    
    async def get_jobs(self, limit: int = 20, offset: int = 0):
        repo = JobRepository(self.session)
        result = await repo.get_all(limit, offset)
        return result 
    
    async def get_job_by_id(self, job_id):
        repo = JobRepository(self.session)
        result = await repo.get_by_id(job_id)
        return result 
        