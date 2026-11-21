import pytest
from pydantic import SecretStr

from app.config import Settings


def _production_settings(**overrides) -> Settings:
    values = {
        "app_env": "production",
        "database_url": "postgresql://parking:secret@db.example.test/parking?sslmode=require",
        "jwt_secret": "a" * 48,
        "cors_origins": "https://parking.example.test",
        "frontend_base_url": "https://parking.example.test",
        "email_provider": "brevo",
        "brevo_api_key": SecretStr("test-api-key"),
        "email_from_email": "no-reply@example.test",
    }
    values.update(overrides)
    return Settings(**values)


def test_postgres_connection_url_is_normalized_for_psycopg():
    settings = _production_settings()

    assert settings.database_url == (
        "postgresql+psycopg://parking:secret@db.example.test/parking?sslmode=require"
    )
    settings.validate_production_config()


def test_production_requires_tls_for_database_connection():
    settings = _production_settings(
        database_url="postgresql://parking:secret@db.example.test/parking"
    )

    with pytest.raises(ValueError, match="sslmode"):
        settings.validate_production_config()


@pytest.mark.parametrize(
    "cors_origins",
    [
        "http://parking.example.test",
        "https://*",
        "https://parking.example.test/",
        "https://parking.example.test, http://localhost:5173",
    ],
)
def test_production_rejects_non_https_or_wildcard_cors_origins(cors_origins):
    settings = _production_settings(cors_origins=cors_origins)

    with pytest.raises(ValueError, match="CORS_ORIGINS"):
        settings.validate_production_config()


def test_production_requires_configured_email_provider():
    settings = _production_settings(brevo_api_key=None)

    with pytest.raises(ValueError, match="proveedor de correo"):
        settings.validate_production_config()


def test_production_startup_does_not_create_tables(monkeypatch):
    from app import main

    monkeypatch.setattr(main.settings, "app_env", "production")
    monkeypatch.setattr(
        type(main.settings), "validate_production_config", lambda _self: None
    )
    monkeypatch.setattr(
        main.Base.metadata,
        "create_all",
        lambda **_kwargs: pytest.fail("Production startup must not create tables"),
    )

    main.on_startup()


def test_example_seed_is_disabled_in_production(monkeypatch):
    from app.scripts import seed

    monkeypatch.setattr(seed.settings, "app_env", "production")

    with pytest.raises(RuntimeError, match="deshabilitado en producción"):
        seed.run()
