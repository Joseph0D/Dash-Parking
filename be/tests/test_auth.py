"""Pruebas del flujo de autenticación: registro y login (RF-012, RF-016)."""


def test_register_creates_client_and_returns_token(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Ana Pérez", "email": "ana@example.com", "password": "supersecret1"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["role"] == "client"
    assert body["access_token"]


def test_register_duplicate_email_returns_409(client):
    payload = {"name": "Ana", "email": "dup@example.com", "password": "supersecret1"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_login_with_wrong_password_returns_401(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Ana", "email": "login@example.com", "password": "supersecret1"},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "login@example.com", "password": "wrong-pass"}
    )
    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
