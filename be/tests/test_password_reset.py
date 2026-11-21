from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pydantic import SecretStr
from sqlalchemy import select

from app.config import settings
from app.core.security import verify_password
from app.models.password_reset import PasswordResetAttempt, PasswordResetToken
from app.models.user import User
from app.services import email_service
from app.services import password_reset_service


def _enable_test_smtp(monkeypatch):
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.test")
    monkeypatch.setattr(settings, "smtp_port", 587)
    monkeypatch.setattr(settings, "smtp_username", "test-user")
    monkeypatch.setattr(settings, "smtp_password", SecretStr("not-a-real-password"))
    monkeypatch.setattr(settings, "smtp_from_email", "no-reply@example.test")
    monkeypatch.setattr(settings, "smtp_use_tls", True)
    monkeypatch.setattr(settings, "smtp_use_ssl", False)


def test_reset_request_is_generic_rate_limited_and_stores_only_token_hash(
    client, db_session, monkeypatch
):
    _enable_test_smtp(monkeypatch)
    sent_emails = []
    monkeypatch.setattr(
        password_reset_service,
        "send_password_reset_email",
        lambda email, token: sent_emails.append((email, token)),
    )
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Ana",
            "email": "ana-reset@example.com",
            "password": "old-password-1",
        },
    )

    responses = [
        client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "ana-reset@example.com"},
        )
        for _ in range(4)
    ]
    unknown_response = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "not-registered@example.com"},
    )

    assert all(response.status_code == 202 for response in responses)
    assert len({response.json()["message"] for response in responses}) == 1
    assert unknown_response.status_code == 202
    assert unknown_response.json() == responses[0].json()
    assert len(sent_emails) == 3

    tokens = db_session.execute(select(PasswordResetToken)).scalars().all()
    active_tokens = [token for token in tokens if token.used_at is None]
    assert len(tokens) == 3
    assert len(active_tokens) == 1
    assert active_tokens[0].expires_at - active_tokens[0].created_at == timedelta(minutes=30)
    assert all(len(token.token_hash) == 64 for token in tokens)
    assert all(token.token_hash != raw for token in tokens for _, raw in sent_emails)
    attempts = db_session.execute(select(PasswordResetAttempt)).scalars().all()
    assert len(attempts) == 4
    assert all(len(attempt.email_hash) == 64 and len(attempt.ip_hash) == 64 for attempt in attempts)


def test_password_reset_token_is_one_time_and_changes_login_password(
    client, db_session, monkeypatch
):
    _enable_test_smtp(monkeypatch)
    sent_emails = []
    monkeypatch.setattr(
        password_reset_service,
        "send_password_reset_email",
        lambda email, token: sent_emails.append((email, token)),
    )
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Luis",
            "email": "luis-reset@example.com",
            "password": "old-password-1",
        },
    )
    client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "luis-reset@example.com"},
    )
    raw_token = sent_emails[0][1]

    response = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": raw_token, "new_password": "new-password-1"},
    )
    replay = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": raw_token, "new_password": "another-password-1"},
    )
    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "luis-reset@example.com", "password": "old-password-1"},
    )
    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": "luis-reset@example.com", "password": "new-password-1"},
    )
    user = db_session.execute(
        select(User).where(User.email == "luis-reset@example.com")
    ).scalar_one()

    assert response.status_code == 200
    assert replay.status_code == 400
    assert old_login.status_code == 401
    assert new_login.status_code == 200
    assert verify_password("new-password-1", user.password_hash)


def test_expired_password_reset_token_is_rejected(client, db_session, monkeypatch):
    _enable_test_smtp(monkeypatch)
    sent_emails = []
    monkeypatch.setattr(
        password_reset_service,
        "send_password_reset_email",
        lambda email, token: sent_emails.append((email, token)),
    )
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Eva",
            "email": "eva-reset@example.com",
            "password": "old-password-1",
        },
    )
    client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "eva-reset@example.com"},
    )
    token = db_session.execute(select(PasswordResetToken)).scalar_one()
    token.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": sent_emails[0][1], "new_password": "new-password-1"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "El enlace no es válido o ya venció"


def test_reset_request_is_unavailable_for_all_emails_without_smtp(
    client, monkeypatch
):
    monkeypatch.setattr(settings, "smtp_host", None)
    monkeypatch.setattr(settings, "smtp_username", None)
    monkeypatch.setattr(settings, "smtp_password", None)
    monkeypatch.setattr(settings, "smtp_from_email", None)
    monkeypatch.setattr(settings, "smtp_use_ssl", False)

    known = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "known@example.com"},
    )
    unknown = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "unknown@example.com"},
    )

    assert known.status_code == unknown.status_code == 503
    assert known.json() == unknown.json()


def test_reset_request_limits_requests_per_ip(client, db_session, monkeypatch):
    _enable_test_smtp(monkeypatch)
    monkeypatch.setattr(
        password_reset_service,
        "send_password_reset_email",
        lambda _email, _token: None,
    )
    responses = [
        client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": f"unknown-{index}@example.com"},
        )
        for index in range(11)
    ]

    assert all(response.status_code == 202 for response in responses)
    assert len({response.json()["message"] for response in responses}) == 1
    attempts = db_session.execute(select(PasswordResetAttempt)).scalars().all()
    assert len(attempts) == 10


def test_smtp_sender_uses_tls_and_builds_frontend_reset_link(monkeypatch):
    _enable_test_smtp(monkeypatch)
    monkeypatch.setattr(settings, "frontend_base_url", "https://parking.example.test")
    sent = []

    class FakeSMTP:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def starttls(self, *, context):
            self.tls_context = context

        def login(self, username, password):
            self.credentials = (username, password)

        def send_message(self, message):
            sent.append(message)

    fake_server = FakeSMTP()
    monkeypatch.setattr(email_service.smtplib, "SMTP", lambda *_args, **_kwargs: fake_server)

    email_service.send_password_reset_email("user@example.test", "abc/def-token")

    assert fake_server.tls_context is not None
    assert fake_server.credentials == ("test-user", "not-a-real-password")
    assert sent[0]["To"] == "user@example.test"
    assert "https://parking.example.test/restablecer-contrasena?token=abc%2Fdef-token" in sent[0].get_content()
