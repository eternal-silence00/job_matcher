from fastapi import UploadFile, File, HTTPException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def validate_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        logger.info("pdf rejected reason=bad_content_type content_type=%s", file.content_type)
        raise HTTPException(status_code=415, detail="Invalid content type")
    if file.filename is None:
        logger.info("pdf rejected reason=no_filename")
        raise HTTPException(status_code=400, detail="No filename")
    if not file.filename.lower().endswith(".pdf"):
        logger.info("pdf rejected reason=bad_extension filename=%s", file.filename)
        raise HTTPException(status_code=415, detail="Wrong extension")
    if file.size is not None and file.size > settings.MAX_RESUME_SIZE_BYTES:
        logger.info("pdf rejected reason=too_large size=%s", file.size)
        raise HTTPException(status_code=413, detail="File size is too big")
    first_bytes = await file.read(5)
    if first_bytes != b"%PDF-":
        logger.info("pdf rejected reason=bad_magic_bytes filename=%s", file.filename)
        raise HTTPException(status_code=415, detail="File is not a valid PDF")
    await file.seek(0)
    return file