import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import aiofiles
from app.core.config import UPLOAD_DIR
from app.core.security import get_current_user

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/")
async def upload_file(file: UploadFile = File(...), _=Depends(get_current_user)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return {"filename": filename, "url": f"/api/uploads/{filename}"}


@router.get("/{filename}")
async def get_file(filename: str, _=Depends(get_current_user)):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    safe_path = os.path.realpath(filepath)
    safe_dir = os.path.realpath(UPLOAD_DIR)
    if not safe_path.startswith(safe_dir):
        raise HTTPException(status_code=403, detail="Access denied")
    return FileResponse(filepath)
