import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import * as authApi from "../api/auth";
import { getErrorMessage } from "../api/errors";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import "./AuthPages.css";

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      const response = await authApi.requestPasswordReset(email);
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
        <h1>Recuperar contraseña</h1>
        <p className="subtitle">
          Ingresa el correo de tu cuenta. Si está registrado, recibirás un enlace temporal.
        </p>
        {error && <div className="form-error" role="alert">{error}</div>}
        {message && <div className="form-success" role="status">{message}</div>}
        <form onSubmit={submit}>
          <div className="form-field">
            <label htmlFor="reset-email">Correo electrónico</label>
            <input
              id="reset-email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>
          <Button type="submit" loading={loading}>Enviar enlace</Button>
        </form>
        <p className="auth-switch"><Link to="/login">Volver a ingresar</Link></p>
      </Card>
    </main>
  );
}
