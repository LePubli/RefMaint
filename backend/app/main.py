import secrets
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from app.api import (
    auth, machines, pannes, interventions, pieces,
    search, stats, uploads, admin, notifications, maintenance_preventive,
)
from app.core.config import CORS_ORIGINS, ENABLE_API_DOCS, INITIAL_ADMIN_USERNAME, INITIAL_ADMIN_PASSWORD

logger = logging.getLogger("trimaint")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

# Rate limiter global (slowapi) — branché sur les routes sensibles via @limiter.limit
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Démarrage : créer l'admin initial avec un mot de passe fort (jamais hardcodé)."""
    from app.db.database import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == INITIAL_ADMIN_USERNAME).first()
        if not admin_user:
            password = INITIAL_ADMIN_PASSWORD or secrets.token_urlsafe(18)
            admin_user = User(
                username=INITIAL_ADMIN_USERNAME,
                email=f"{INITIAL_ADMIN_USERNAME}@trimaint.local",
                hashed_password=get_password_hash(password),
                role="admin",
            )
            db.add(admin_user)
            db.commit()
            if INITIAL_ADMIN_PASSWORD:
                logger.warning(
                    "Admin initial '%s' créé avec le mot de passe fourni via INITIAL_ADMIN_PASSWORD. "
                    "Changez-le après la première connexion.",
                    INITIAL_ADMIN_USERNAME,
                )
            else:
                # Affiché une seule fois au premier démarrage.
                logger.warning(
                    "Admin initial '%s' créé. Mot de passe temporaire (à changer immédiatement) : %s",
                    INITIAL_ADMIN_USERNAME, password,
                )
    finally:
        db.close()
    yield


app = FastAPI(
    title="TriMaint API",
    description="GMAO pour Triselec",
    version="1.0.0",
    # Documentation Swagger/ReDoc désactivée par défaut (ENABLE_API_DOCS=true pour l'activer).
    docs_url="/api/docs" if ENABLE_API_DOCS else None,
    redoc_url="/api/redoc" if ENABLE_API_DOCS else None,
    openapi_url="/api/openapi.json" if ENABLE_API_DOCS else None,
    lifespan=lifespan,
)

# slowapi state (obligatoire pour le handler 429)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS : origins explicites uniquement. Compatible avec allow_credentials=True
# (contrairement à allow_origins=["*"] qui est invalide dans ce cas).
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(machines.router)
app.include_router(pannes.router)
app.include_router(interventions.router)
app.include_router(pieces.router)
app.include_router(search.router)
app.include_router(stats.router)
app.include_router(uploads.router)
app.include_router(admin.router)
app.include_router(notifications.router)
app.include_router(maintenance_preventive.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Erreur non gérée sur %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"},
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "TriMaint API"}
