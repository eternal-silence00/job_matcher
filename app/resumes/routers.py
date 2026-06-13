from fastapi import APIRouter, Depends, UploadFile
from app.resumes.service import ResumeService
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.resumes.schemas import ResumeResponse
from app.auth.models import User
from app.resumes.dependencies import validate_pdf

router = APIRouter()

@router.post("/resumes", response_model=ResumeResponse)
async def post_resume(
    file: UploadFile = Depends(validate_pdf),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = ResumeService(session)
    resume = await service.upload_resume(user.id, file)
    file_url = service.storage_service.get_file_url(resume.filename)
    return {"id": resume.id, "filename": resume.filename, "file_url": file_url, "created_at": resume.created_at}

@router.get("/resumes/me", response_model=ResumeResponse)
async def get_resume(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = ResumeService(session)
    resume = await service.get_my_resume(user.id)
    file_url = service.storage_service.get_file_url(resume.filename)
    return {"id": resume.id, "filename": resume.filename, "file_url": file_url, "created_at": resume.created_at}
    
