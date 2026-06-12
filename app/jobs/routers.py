from fastapi import APIRouter, Depends, HTTPException
from app.jobs.service import JobService
from app.jobs.schemas import JobCreate, JobResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.models import User
from app.core.dependencies import get_admin_user

router = APIRouter()


@router.post("/jobs", response_model=JobResponse, status_code=201)
async def create_job(
    data: JobCreate,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    service = JobService(session)
    job = await service.create_job(data)
    return job

@router.get("/jobs", response_model=list[JobResponse])
async def get_all(
    session: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
):
    service = JobService(session)
    result = await service.get_jobs(limit, offset)
    return result 

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_by_id(
    job_id: int,
    session: AsyncSession = Depends(get_db)
):
    service = JobService(session)
    result = await service.get_job_by_id(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="job not found")
    return result 