/**
 * AccountForm.tsx
 * Qué: formulario de inicio de sesión / registro de la cuenta de la base nueva.
 * Para qué: que quien quiera reservar (o entrar al panel del dueño) tenga sesión sin salir de
 *           la pantalla en la que está.
 * Impacto: el registro siempre crea una cuenta de cliente; dueños y administradores los
 *          asigna el equipo (ver db/README.md).
 */
import { useState, type FormEvent } from "react";
import { getErrorMessage } from "../../api/errors";
import { useAccount } from "../../context/AccountContext";
import { Button } from "../ui/Button";
import "./booking.css";

export function AccountForm({ allowRegister = true }: { allowRegister?: boolean }) {
  const { login, register } = useAccount();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [fields, setFields] = useState({
    first_name: "",
    last_name: "",
    document_id: "",
    phone: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function update(name: keyof typeof fields, value: string) {
    setFields((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === "login") await login(fields.email, fields.password);
      else await register(fields);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="booking-form" onSubmit={handleSubmit}>
      {error && <div className="form-error">{error}</div>}

      {mode === "register" && (
        <>
          <div className="booking-form__row">
            <label className="form-field">
              <span>Nombres</span>
              <input required minLength={2} value={fields.first_name}
                onChange={(e) => update("first_name", e.target.value)} />
            </label>
            <label className="form-field">
              <span>Apellidos</span>
              <input required minLength={2} value={fields.last_name}
                onChange={(e) => update("last_name", e.target.value)} />
            </label>
          </div>
          <div className="booking-form__row">
            <label className="form-field">
              <span>Documento</span>
              <input required minLength={5} maxLength={20} value={fields.document_id}
                onChange={(e) => update("document_id", e.target.value)} />
            </label>
            <label className="form-field">
              <span>Teléfono</span>
              <input required minLength={7} maxLength={15} value={fields.phone}
                onChange={(e) => update("phone", e.target.value)} />
            </label>
          </div>
        </>
      )}

      <label className="form-field">
        <span>Correo electrónico</span>
        <input type="email" required autoComplete="email" value={fields.email}
          onChange={(e) => update("email", e.target.value)} />
      </label>
      <label className="form-field">
        <span>Contraseña</span>
        <input type="password" required minLength={mode === "register" ? 8 : 1}
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          value={fields.password} onChange={(e) => update("password", e.target.value)} />
      </label>

      <Button type="submit" loading={loading}>
        {mode === "login" ? "Ingresar" : "Crear cuenta"}
      </Button>

      {allowRegister && (
        <button type="button" className="booking-link"
          onClick={() => { setError(null); setMode(mode === "login" ? "register" : "login"); }}>
          {mode === "login" ? "¿No tienes cuenta? Regístrate" : "Ya tengo cuenta"}
        </button>
      )}
    </form>
  );
}
