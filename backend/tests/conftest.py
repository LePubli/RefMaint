"""Configuration pytest : base de données SQLite en mémoire + client de test.

Permet d'exécuter les tests sans PostgreSQL. Les vérifications spécifiques
PostgreSQL (JSON, CHECK) ne sont pas couvertes ici — elles le sont via les
migrations Alembic en intégration.
"""
import os
import sys
from pathlib import Path

# S'assurer que SECRET_KEY et DATABASE_URL sont définis AVANT tout import app.
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only-min-32-chars!!")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("CORS_ORIGINS", "http://localhost")
os.environ.setdefault("ENABLE_API_DOCS", "false")
os.environ.setdefault("INITIAL_ADMIN_PASSWORD", "TestAdminPass123")

# Rendre le dossier `backend/` importable.
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.models import (  # noqa: F401  (enregistrer tous les modèles)
    user, machine, panne, intervention, piece,
    activity_log, notification, maintenance_preventive,
)
# Le client doit être importé APRÈS l'injection des variables d'env.
from app.main import app


@pytest.fixture(scope="function")
def db_session():
    """Session SQLAlchemy sur une base SQLite en mémoire, recréée pour chaque test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield session
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    """Client HTTP de test (le lifespan admin bootstrap s'exécute via la DB de test)."""
    with TestClient(app) as c:
        yield c


# --- Helpers d'authentification pour les tests ---

def _login(client, username: str, password: str) -> str:
    """Récupère un token JWT via /api/auth/login."""
    res = client.post(
        "/api/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token(client):
    """Token JWT du compte admin créé par le lifespan au démarrage."""
    return _login(client, "admin", "TestAdminPass123")


@pytest.fixture
def admin_headers(admin_token):
    return _auth_header(admin_token)


def _create_user(client, admin_headers, username: str, role: str, password: str = "Technicien123"):
    """Crée un utilisateur via l'API admin et renvoie son token."""
    res = client.post(
        "/api/auth/users",
        json={
            "username": username,
            "email": f"{username}@trimaint.test",
            "role": role,
            "password": password,
        },
        headers=admin_headers,
    )
    assert res.status_code == 200, res.text
    return _login(client, username, password)


@pytest.fixture
def manager_token(client, admin_headers):
    return _create_user(client, admin_headers, "manager1", "manager")


@pytest.fixture
def technicien_token(client, admin_headers):
    return _create_user(client, admin_headers, "tech1", "technicien")


@pytest.fixture
def manager_headers(manager_token):
    return _auth_header(manager_token)


@pytest.fixture
def technicien_headers(technicien_token):
    return _auth_header(technicien_token)


@pytest.fixture
def machine_id(client, admin_headers):
    """Crée une machine de test et renvoie son id."""
    res = client.post(
        "/api/machines/",
        json={"nom": "Convoyeur A", "site": "Usine 1", "ligne": "L1", "zone": "Z1"},
        headers=admin_headers,
    )
    assert res.status_code == 200, res.text
    return res.json()["id"]
