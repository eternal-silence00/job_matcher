from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.matching.service import MatchingService
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import User
from app.jobs.schemas import JobResponse

router = APIRouter()

@router.get("/matching/jobs", response_model=list[JobResponse])
async def get_matching_jobs(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = 20
):
    service = MatchingService(session)
    result = await service.match_jobs(user.id, limit)
    return result