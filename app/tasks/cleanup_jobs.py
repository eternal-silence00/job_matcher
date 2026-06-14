import asyncio
import logging
from app.core.celery_app import celery_app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.jobs.repository import JobRepository

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_old_jobs():
    try:
        asyncio.run(_cleanup_old_jobs())
    except Exception:
        logger.exception("task=cleanup_old_jobs failed")
        raise


async def _cleanup_old_jobs():
    logger.info("task=cleanup_old_jobs started")
    engine = create_async_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        repo = JobRepository(session)
        await repo.delete_old(30)
        await session.commit()
    await engine.dispose()
    logger.info("task=cleanup_old_jobs finished")
