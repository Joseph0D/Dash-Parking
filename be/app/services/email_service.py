"""Envío de correos transaccionales mediante un servidor SMTP configurable."""
from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode

from app.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(email: str, token: str) -> None:
    if not settings.smtp_configured:
        logger.error("Password-reset email was not sent because SMTP is not configured")
        return

    reset_url = (
        f"{settings.frontend_base_url.rstrip('/')}/restablecer-contrasena?"
        f"{urlencode({'token': token})}"
    )
    message = EmailMessage()
    message["Subject"] = "Restablece tu contraseña de Dash Parking"
    message["From"] = settings.smtp_from_email
    message["To"] = email
    message.set_content(
        "Recibimos una solicitud para cambiar la contraseña de tu cuenta de Dash Parking.\n\n"
        f"Usa este enlace dentro de los próximos 30 minutos:\n{reset_url}\n\n"
        "El enlace solo se puede usar una vez. Si no solicitaste el cambio, ignora este correo."
    )

    try:
        context = ssl.create_default_context()
        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(
                settings.smtp_host,
                settings.smtp_port,
                timeout=10,
                context=context,
            ) as server:
                _authenticate_and_send(server, message)
            return

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            if settings.smtp_use_tls:
                server.starttls(context=context)
            _authenticate_and_send(server, message)
    except (OSError, smtplib.SMTPException) as exc:
        logger.error(
            "Password-reset email delivery failed (%s)",
            type(exc).__name__,
        )


def _authenticate_and_send(server: smtplib.SMTP, message: EmailMessage) -> None:
    if settings.smtp_username and settings.smtp_password:
        server.login(
            settings.smtp_username,
            settings.smtp_password.get_secret_value(),
        )
    server.send_message(message)
