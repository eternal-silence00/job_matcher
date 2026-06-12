from sqlalchemy.ext.asyncio import AsyncSession
from app.jobs.models import Job
from sqlalchemy import select, text, delete
from datetime import datetime, timezone, timedelta


class JobRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create(self, title, description, salary_from, salary_to, company, url, location, published_at, embedding):
        job = Job(
            title=title,
            description=description,
            salary_from=salary_from,
            salary_to=salary_to,
            company=company,
            url=url,
            location=location,
            published_at=published_at,
            embedding=embedding
        )
        self.session.add(job)
        await self.session.flush()
        await self.session.refresh(job)
        return job
    
    async def get_all(self, limit: int = 20, offset: int = 0):
        result = await self.session.execute(select(Job).limit(limit).offset(offset))
        return result.scalars().all()
    
    async def get_by_id(self, job_id: int):
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()
    
    async def find_simular(self, embedding: list, limit: int):
        embedding=str([float(x) for x in embedding])
        result = await self.session.execute(select(Job).
                                            order_by(text("embedding <-> CAST(:embedding AS vector)").bindparams(embedding=embedding))
                                            .limit(limit)
                                            )
        return result.scalars().all()
    
    async def get_by_url(self, url: str):
        result = await self.session.execute(select(Job).where(Job.url == url))
        return result.scalar_one_or_none()
    
    async def delete_old(self, days: int):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        await self.session.execute(delete(Job).where(Job.created_at < cutoff))