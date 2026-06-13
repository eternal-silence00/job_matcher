from fastapi import UploadFile, File, HTTPException
from app.core.config import settings



async def validate_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Invalid content type")
    if file.filename is None:
        raise HTTPException(status_code=400, detail="No filename")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Wrong extension")
    if file.size is not None and file.size > settings.MAX_RESUME_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File size is too big")
    first_bytes = await file.read(5)
    if first_bytes != b"%PDF-":
        raise HTTPException(status_code=415, detail="File is not a valid PDF")
    await file.seek(0)
    return file