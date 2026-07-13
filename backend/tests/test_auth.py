"""Tests d'authentification et de gestion des utilisateurs."""
from fastapi.testclient import TestClient


def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_login_admin_success(client):
    res = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "TestAdminPass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_wrong_password(client):
    res = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 401


def test_me_endpoint(client, admin_headers):
    res = client.get("/api/auth/me", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"


def test_me_without_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_admin_can_list_users(client, admin_headers):
    res = client.get("/api/auth/users", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert any(u["username"] == "admin" for u in res.json())


def test_technicien_cannot_list_users(client, technicien_headers):
    """La gestion des utilisateurs est réservée aux admins (RBAC)."""
    res = client.get("/api/auth/users", headers=technicien_headers)
    assert res.status_code == 403


def test_create_user_weak_password_rejected(client, admin_headers):
    """Politique mot de passe : min 8 caractères + lettre + chiffre."""
    res = client.post(
        "/api/auth/users",
        json={
            "username": "weak",
            "email": "weak@trimaint.test",
            "role": "technicien",
            "password": "123",  # trop court
        },
        headers=admin_headers,
    )
    assert res.status_code == 400


def test_create_user_password_no_digit_rejected(client, admin_headers):
    res = client.post(
        "/api/auth/users",
        json={
            "username": "noDigits",
            "email": "nod@trimaint.test",
            "role": "technicien",
            "password": "abcdefgh",  # pas de chiffre
        },
        headers=admin_headers,
    )
    assert res.status_code == 400


def test_create_user_invalid_email_rejected(client, admin_headers):
    """EmailStr doit valider le format de l'email."""
    res = client.post(
        "/api/auth/users",
        json={
            "username": "badmail",
            "email": "not-an-email",
            "role": "technicien",
            "password": "GoodPass123",
        },
        headers=admin_headers,
    )
    assert res.status_code == 422  # Erreur de validation Pydantic


def test_create_user_valid(client, admin_headers):
    res = client.post(
        "/api/auth/users",
        json={
            "username": "valid",
            "email": "valid@trimaint.test",
            "role": "manager",
            "password": "GoodPass123",
        },
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["role"] == "manager"


def test_create_user_invalid_role_rejected(client, admin_headers):
    res = client.post(
        "/api/auth/users",
        json={
            "username": "badrole",
            "email": "badrole@trimaint.test",
            "role": "superadmin",  # rôle inexistant
            "password": "GoodPass123",
        },
        headers=admin_headers,
    )
    assert res.status_code == 400
