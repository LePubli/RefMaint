import os
import io
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import aiofiles
from PIL import Image
from app.core.config import UPLOAD_DIR
from app.core.security import get_current_user

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Magic bytes pour valider le type réel du fichier.
_MAGIC_SIGNATURES = {
    b"\xFF\xD8\xFF": "image/jpeg",
    b"\x89PNG\r\n\x1A\n": "image/png",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
    b"RIFF": "image/webp",   # WEBP : RIFF....WEBP
    b"%PDF": "application/pdf",
}


def _check_magic_bytes(content: bytes, ext: str) -> bool:
    """Vérifie que les premiers octets correspondent au type déclaré par l'extension."""
    expected_types = {
        ".jpg": {"image/jpeg"},
        ".jpeg": {"image/jpeg"},
        ".png": {"image/png"},
        ".gif": {"image/gif"},
        ".webp": {"image/webp"},
        ".pdf": {"application/pdf"},
    }
    expected = expected_types.get(ext)
    if not expected:
        return False
    for magic, mime in _MAGIC_SIGNATURES.items():
        if mime in expected and content.startswith(magic):
            return True
    return False


def _sanitize_image(content: bytes, ext: str) -> bytes:
    """Re-traite l'image via Pillow pour éliminer les payloads malveillants
    éventuellement cachés dans les métadonnées EXIF ou les chunks annexes."""
    try:
        img = Image.open(io.BytesIO(content))
        img.load()  # force le décodage complet
        buf = io.BytesIO()
        save_format = "JPEG" if ext in (".jpg", ".jpeg") else ext.lstrip(".").upper()
        if save_format == "JPG":
            save_format = "JPEG"
        img.save(buf, format=save_format)
        return buf.getvalue()
    except Exception:
        raise HTTPException(status_code=400, detail="Image corrompue ou invalide")


@router.post("/")
async def upload_file(file: UploadFile = File(...), _=Depends(get_current_user)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Type de fichier non autorisé. Autorisés : {ALLOWED_EXTENSIONS}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 10 Mo)")

    # Validation par magic bytes.
    if not _check_magic_bytes(content, ext):
        raise HTTPException(status_code=400, detail="Le contenu du fichier ne correspond pas à son extension.")

    # Sanitization des images via Pillow.
    if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        content = _sanitize_image(content, ext)

    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return {"filename": filename, "url": f"/api/uploads/{filename}"}


@router.get("/{filename}")
async def get_file(filename: str, _=Depends(get_current_user)):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    safe_path = os.path.realpath(filepath)
    safe_dir = os.path.realpath(UPLOAD_DIR)
    if not safe_path.startswith(safe_dir):
        raise HTTPException(status_code=403, detail="Accès refusé")
    return FileResponse(filepath)
