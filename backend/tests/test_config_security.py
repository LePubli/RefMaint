"""Tests de la configuration sécurité : SECRET_KEY, mot de passe admin, CORS, rate-limiting."""
import pytest


def test_secret_key_mandatory():
    """SECRET_KEY manquant → RuntimeError."""
    import importlib
    import sys
    # Retirer le module s'il est déjà importé
    for mod in list(sys.modules.keys()):
        if mod.startswith("app.core.config"):
            del sys.modules[mod]
    # S'assurer que la variable d'env n'est pas positionnée
    import os
    old = os.environ.pop("SECRET_KEY", None)
    try:
        with pytest.raises(RuntimeError, match="SECRET_KEY is required"):
            from app.core.config import SECRET_KEY  # noqa: F401
    finally:
        if old:
            os.environ["SECRET_KEY"] = old


def test_secret_key_too_short():
    """SECRET_KEY trop court → RuntimeError."""
    import os, sys, importlib
    old = os.environ.pop("SECRET_KEY", None)
    os.environ["SECRET_KEY"] = "short"
    for mod in list(sys.modules.keys()):
        if mod.startswith("app.core.config"):
            del sys.modules[mod]
    try:
        with pytest.raises(RuntimeError, match="at least 32 characters"):
            from app.core.config import SECRET_KEY  # noqa: F401
    finally:
        os.environ.pop("SECRET_KEY", None)
        if old:
            os.environ["SECRET_KEY"] = old


def test_rate_limit_on_login(client, admin_headers):
    """Plus de 10 requêtes /login par minute → 429."""
    for _ in range(10):
        res = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "wrong"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert res.status_code in (401, 429)  # les 10 premières peuvent être 401
    # La 11e doit être 429 (rate limited)
    res = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 429


def test_api_docs_disabled_by_default(client):
    """Swagger et ReDoc doivent être désactivés par défaut."""
    res = client.get("/docs")
    assert res.status_code == 404
    res = client.get("/redoc")
    assert res.status_code == 404
    res = client.get("/openapi.json")
    assert res.status_code == 404


def test_stats_requires_auth(client):
    res = client.get("/api/stats/")
    assert res.status_code == 401


def test_search_requires_auth(client):
    res = client.get("/api/search/?q=test")
    assert res.status_code == 401


def test_global_error_handler(client, admin_headers):
    """Les erreurs non gérées doivent renvoyer un JSON 500 (pas un stacktrace HTML)."""
    # On ne peut pas facilement forcer une erreur 500 sans un endpoint dédié,
    # mais on vérifie que le handler est bien enregistré.
    from app.main import app
    from starlette.exceptions import HTTPException as StarletteHTTPException
    # Vérifier que l'exception handler est enregistré
    assert Exception in app.exception_handlers
