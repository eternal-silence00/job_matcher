import httpx
import asyncio
import logging
from app.core.celery_app import celery_app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.jobs.repository import JobRepository
from app.core.embedding_service import EmbeddingService
from datetime import datetime

logger = logging.getLogger(__name__)


@celery_app.task
def parse_jobs():
    try:
        asyncio.run(_parse_jobs())
    except Exception:
        logger.exception("task=parse_jobs failed")
        raise


TAGS = ["python", "javascript", "golang", "java", "backend"]


async def _parse_jobs():
    logger.info("task=parse_jobs started")
    engine = create_async_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with httpx.AsyncClient() as client:
        all_jobs = []
        for tag in TAGS:
            try:
                response = await client.get(f"https://remoteok.com/api?tags={tag}")
                jobs = response.json()
                jobs = [j for j in jobs if j.get("position")]
                logger.info("fetched tag=%s count=%d", tag, len(jobs))
                all_jobs.extend(jobs)
            except Exception:
                logger.exception("fetch failed tag=%s", tag)

    async with SessionLocal() as session:
        repo = JobRepository(session)
        embedding_service = EmbeddingService()
        created_count = 0
        skipped_count = 0

        for job in all_jobs:
            title = job.get("position")
            company = job.get("company")
            url = job.get("url")
            existing = await repo.get_by_url(url)
            if existing:
                skipped_count += 1
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
            created_count += 1
        await session.commit()

    await engine.dispose()
    logger.info("task=parse_jobs finished total=%d created=%d skipped=%d",
                len(all_jobs), created_count, skipped_count)
