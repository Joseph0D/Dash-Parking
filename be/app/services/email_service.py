"""Envío de correos transaccionales por SMTP o por la API HTTPS de Brevo."""

from __future__ import annotations

import json
import logging
import smtplib
import ssl
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.config import settings

logger = logging.getLogger(__name__)

BREVO_EMAIL_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_password_reset_email(email: str, token: str) -> None:
    if not settings.email_configured:
        logger.error(
            "Password-reset email was not sent because %s is not configured",
            settings.email_provider,
        )
        return

    reset_url = (
        f"{settings.frontend_base_url.rstrip('/')}/restablecer-contrasena?"
        f"{urlencode({'token': token})}"
    )
    text_content = (
        "Recibimos una solicitud para cambiar la contraseña de tu cuenta de Dash Parking.\n\n"
        f"Usa este enlace dentro de los próximos 30 minutos:\n{reset_url}\n\n"
        "El enlace solo se puede usar una vez. Si no solicitaste el cambio, ignora este correo."
    )

    try:
        if settings.email_provider == "brevo":
            _send_with_brevo(email, text_content)
        else:
            _send_with_smtp(email, text_content)
    except (HTTPError, URLError, TimeoutError, OSError, smtplib.SMTPException) as exc:
        error = f"HTTP {exc.code}" if isinstance(exc, HTTPError) else type(exc).__name__
        logger.error(
            "Password-reset email delivery via %s failed (%s)",
            settings.email_provider,
            error,
        )


def _send_with_smtp(email: str, text_content: str) -> None:
    if not settings.smtp_host or not settings.smtp_from_email:
        raise RuntimeError("SMTP host and sender email are required")

    message = EmailMessage()
    message["Subject"] = "Restablece tu contraseña de Dash Parking"
    message["From"] = settings.smtp_from_email
    message["To"] = email
    message.set_content(text_content)

    context = ssl.create_default_context()
    if settings.smtp_use_ssl:
        with smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            timeout=settings.email_timeout_seconds,
            context=context,
        ) as server:
            _authenticate_and_send(server, message)
        return

    with smtplib.SMTP(
        settings.smtp_host,
        settings.smtp_port,
        timeout=settings.email_timeout_seconds,
    ) as server:
        if settings.smtp_use_tls:
            server.starttls(context=context)
        _authenticate_and_send(server, message)


def _send_with_brevo(email: str, text_content: str) -> None:
    if settings.brevo_api_key is None or not settings.email_from_email:
        raise RuntimeError("Brevo API key and sender email are required")

    payload = {
        "sender": {
            "name": settings.email_from_name,
            "email": settings.email_from_email,
        },
        "to": [{"email": email}],
        "subject": "Restablece tu contraseña de Dash Parking",
        "textContent": text_content,
    }
    request = Request(
        BREVO_EMAIL_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": settings.brevo_api_key.get_secret_value(),
            "content-type": "application/json",
        },
        method="POST",
    )

    with urlopen(request, timeout=settings.email_timeout_seconds) as response:
        if not 200 <= response.status < 300:
            raise HTTPError(
                request.full_url,
                response.status,
                "Brevo rejected the email",
                response.headers,
                None,
            )


def _authenticate_and_send(server: smtplib.SMTP, message: EmailMessage) -> None:
    if settings.smtp_username and settings.smtp_password:
        server.login(
            settings.smtp_username,
            settings.smtp_password.get_secret_value(),
        )
    server.send_message(message)
