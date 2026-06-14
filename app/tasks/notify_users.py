import asyncio
import logging
from app.core.celery_app import celery_app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.auth.repository import UserRepository
from app.matching.service import MatchingService
from app.core.email_service import send_jobs

logger = logging.getLogger(__name__)


@celery_app.task
def notify_users():
    try:
        asyncio.run(_notify_users())
    except Exception:
        logger.exception("task=notify_users failed")
        raise


async def _notify_users():
    logger.info("task=notify_users started")
    engine = create_async_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    sent_count = 0
    failed_count = 0
    async with SessionLocal() as session:
        repo = UserRepository(session)
        service = MatchingService(session)
        users = await repo.get_all_with_resumes()
        logger.info("task=notify_users users_to_notify=%d", len(users))
        for user in users:
            try:
                jobs = await service.match_jobs(user.id)
                await send_jobs(user.email, jobs)
                sent_count += 1
            except Exception:
                logger.exception("notify_user failed user_id=%s", user.id)
                failed_count += 1
        await session.commit()
    await engine.dispose()
    logger.info("task=notify_users finished sent=%d failed=%d", sent_count, failed_count)
