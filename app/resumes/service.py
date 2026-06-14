from app.core.embedding_service import EmbeddingService
from fastapi import HTTPException
from app.core.pdf_service import PdfService
from app.core.storage_service import StorageService
from sqlalchemy.ext.asyncio import AsyncSession
from app.resumes.repository import ResumeRepository
import logging

logger = logging.getLogger(__name__)

class ResumeService:
    
    def __init__(self, session, storage=None, pdf=None, embedding=None):
        self.session = session
        self.storage_service = storage or StorageService()
        self.pdf_service = pdf or PdfService()
        self.embedding_service = embedding or EmbeddingService()
        
    async def upload_resume(self, user_id: int, file):
        text = self.pdf_service.extract_text(file.file)
        embedding = self.embedding_service.get_embedding(text)
        file.file.seek(0)
        self.storage_service.upload_file(file.file, file.filename)
        repo = ResumeRepository(self.session)
        resume = await repo.get_by_user_id(user_id)
        if resume:
            resume = await repo.update(user_id, file.filename, text, embedding)
            return resume
        resume = await repo.create(user_id, file.filename, text, embedding)
        logger.info("resume uploaded user_id=%s filename=%s", user_id, file.filename)
        return resume
        
        
    async def get_my_resume(self, user_id: int):
        repo = ResumeRepository(self.session)
        result = await repo.get_by_user_id(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Resume not found")
        return result 