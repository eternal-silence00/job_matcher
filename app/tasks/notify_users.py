import asyncio
from app.core.celery_app import celery_app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.auth.repository import UserRepository
from app.matching.service import MatchingService
from app.core.email_service import send_jobs


@celery_app.task
def notify_users():
    asyncio.run(_notify_users())

async def _notify_users():
    engine = create_async_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session: 
        repo = UserRepository(session)
        service = MatchingService(session)
        users = await repo.get_all_with_resumes()
        for user in users:
            jobs = await service.match_jobs(user.id)
            await send_jobs(user.email, jobs)
        await session.commit()
    await engine.dispose()