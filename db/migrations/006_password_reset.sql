-- Tokenes y límites de solicitudes para recuperación segura de contraseña.
BEGIN;

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ NULL,
    CONSTRAINT uq_password_reset_tokens_hash UNIQUE (token_hash)
);

CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_user_used
    ON password_reset_tokens (user_id, used_at);

CREATE TABLE IF NOT EXISTS password_reset_attempts (
    id UUID PRIMARY KEY,
    email_hash VARCHAR(64) NOT NULL,
    ip_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_password_reset_attempts_email_created
    ON password_reset_attempts (email_hash, created_at);
CREATE INDEX IF NOT EXISTS ix_password_reset_attempts_ip_created
    ON password_reset_attempts (ip_hash, created_at);
CREATE INDEX IF NOT EXISTS ix_password_reset_attempts_created
    ON password_reset_attempts (created_at);

COMMIT;
