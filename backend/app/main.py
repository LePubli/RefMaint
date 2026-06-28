import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import Base, engine
from app.api import auth, machines, pannes, interventions, pieces, search, stats, uploads
from app.core.config import UPLOAD_DIR

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TriMaint API", description="GMAO pour Triselec", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "TriMaint API"}


@app.on_event("startup")
async def startup_event():
    from sqlalchemy.orm import Session
    from app.db.database import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@trimaint.local",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created: admin / admin123")
    finally:
        db.close()
