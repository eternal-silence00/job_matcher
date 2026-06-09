import httpx
import asyncio
from app.core.celery_app import celery_app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.jobs.repository import JobRepository
from app.core.embedding_service import EmbeddingService
from datetime import datetime




@celery_app.task
def parse_jobs():
    asyncio.run(_parse_jobs())

async def _parse_jobs():
    engine = create_async_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with httpx.AsyncClient() as client:
        response = await client.get("https://remoteok.com/api?tags=python")
        jobs = response.json()
        jobs = [j for j in jobs if j.get("position")]
    
    async with SessionLocal() as session:
        repo = JobRepository(session)
        embedding_service = EmbeddingService()
        
        for job in jobs:
            title = job.get("position")
            company = job.get("company")
            url = job.get("url")
            existing = await repo.get_by_url(url)
            if existing:
                continue
            location = job.get("location")
            description = job.get("description", "")
            salary_from = job.get("salary_min")
            salary_to = job.get("salary_max")
            published = datetime.fromisoformat(job.get("date"))
            tags = ", ".join(job.get("tags", []))
            full_description = f"{description} Skills: {tags}"
            text = f"{title}. {full_description}"
            embedding = embedding_service.get_embedding(text)
            await repo.create(title, full_description, salary_from, salary_to, company, url, location, published, embedding)
        await session.commit()
    
    await engine.dispose()