import os
from typing import Optional

SECRET_KEY = os.getenv("SECRET_KEY", "trimaint-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

DATABASE_URL = os.getenv("DATABASE_URL", "")

_default_upload = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uploads")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", _default_upload)
os.makedirs(UPLOAD_DIR, exist_ok=True)
