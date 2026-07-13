import os
from typing import List

# --- Security: fail-fast if a required secret is missing or still default ---
_INSECURE_SECRET_DEFAULTS = {
    "trimaint-secret-key-change-in-production-2024",
    "change-this-to-a-random-64-char-secret-key-for-production",
    "change-this-secret-key-in-production-min-32-chars",
}


def _load_secret_key() -> str:
    value = os.getenv("SECRET_KEY", "").strip()
    if not value:
        raise RuntimeError(
            "SECRET_KEY is required. Generate one with `openssl rand -hex 32` "
            "and set the SECRET_KEY environment variable."
        )
    if value in _INSECURE_SECRET_DEFAULTS:
        raise RuntimeError(
            "SECRET_KEY is set to a known insecure default. "
            "Generate a new one with `openssl rand -hex 32`."
        )
    if len(value) < 32:
        raise RuntimeError("SECRET_KEY must be at least 32 characters long.")
    return value


SECRET_KEY = _load_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 heures (au lieu de 24h)

DATABASE_URL = os.getenv("DATABASE_URL", "")

# --- File uploads ---
_default_upload = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "uploads",
)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", _default_upload)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- CORS: origins must be explicit when allow_credentials is True ---
# Comma-separated list, e.g. "https://trimaint.example.com,https://admin.example.com"
_cors_raw = os.getenv("CORS_ORIGINS", "").strip()
if _cors_raw:
    CORS_ORIGINS: List[str] = [o.strip() for o in _cors_raw.split(",") if o.strip()]
else:
    # Local development only. Empty/unset in production = API refuses cross-origin
    # credentialed requests, which is safer than the previous "*".
    CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]

# --- API docs (Swagger / ReDoc). Disable in production. ---
ENABLE_API_DOCS = os.getenv("ENABLE_API_DOCS", "false").lower() in ("1", "true", "yes")

# --- Admin bootstrap ---
# If INITIAL_ADMIN_PASSWORD is unset, a strong random password is generated and
# printed ONCE at first startup. Avoids the hardcoded "admin123" default.
INITIAL_ADMIN_USERNAME = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
INITIAL_ADMIN_PASSWORD = os.getenv("INITIAL_ADMIN_PASSWORD", "").strip()
