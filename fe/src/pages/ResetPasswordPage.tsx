import { useState, type FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import * as authApi from "../api/auth";
import { getErrorMessage } from "../api/errors";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import "./AuthPages.css";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(
    token ? null : "El enlace no contiene un token de recuperación.",
  );
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    if (!token) {
      setError("El enlace no es válido o ya venció.");
      return;
    }
    if (password !== confirmation) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    setLoading(true);
    try {
      const response = await authApi.confirmPasswordReset(token, password);
      setMessage(response.message);
    } catch (cause) {
      setError(getErrorMessage(cause));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <Card className="auth-card">
        <h1>Crear contraseña nueva</h1>
        <p className="subtitle">
          El enlace vence a los 30 minutos y se usa una sola vez. La contraseña debe tener entre
          8 y 72 bytes en UTF-8.
        </p>
        {error && <div className="form-error" role="alert">{error}</div>}
        {message && <div className="form-success" role="status">{message}</div>}
        {!message && (
          <form onSubmit={submit}>
            <div className="form-field">
              <label htmlFor="new-password">Nueva contraseña</label>
              <input
                id="new-password"
                type="password"
                autoComplete="new-password"
                minLength={8}
                maxLength={100}
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>
            <div className="form-field">
              <label htmlFor="confirm-password">Confirmar contraseña</label>
              <input
                id="confirm-password"
                type="password"
                autoComplete="new-password"
                minLength={8}
                maxLength={100}
                required
                value={confirmation}
                onChange={(event) => setConfirmation(event.target.value)}
              />
            </div>
            <Button type="submit" loading={loading}>Guardar contraseña</Button>
          </form>
        )}
        {message && <p className="auth-switch"><Link to="/login">Ir a ingresar</Link></p>}
      </Card>
    </main>
  );
}
