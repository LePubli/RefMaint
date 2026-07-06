import os
import warnings
from typing import Optional

_DEFAULT_SECRET = "trimaint-secret-key-change-in-production-2024"
SECRET_KEY = os.getenv("SECRET_KEY", _DEFAULT_SECRET)
if SECRET_KEY == _DEFAULT_SECRET:
    warnings.warn(
        "SECRET_KEY is using the insecure default value. "
        "Set the SECRET_KEY environment variable before deploying to production.",
        stacklevel=1,
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

DATABASE_URL = os.getenv("DATABASE_URL", "")

_default_upload = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uploads")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", _default_upload)
os.makedirs(UPLOAD_DIR, exist_ok=True)
