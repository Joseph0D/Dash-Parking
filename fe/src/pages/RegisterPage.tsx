/** Registro de clientes y dueños; los roles de operador y administrador no se asignan aquí. */
import { useState, type FormEvent } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getErrorMessage } from "../api/errors";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import "./AuthPages.css";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [name, setName] = useState("");
  const [surname, setSurname] = useState("");
  const [documentType, setDocumentType] = useState("CC");
  const [documentNumber, setDocumentNumber] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [accountType, setAccountType] = useState<"client" | "owner">(
    () => searchParams.get("tipo") === "dueno" ? "owner" : "client",
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const user = await register(
        name, surname, documentType, documentNumber, phone, email, password, accountType,
      );
      navigate(user.role === "owner" ? "/owner" : "/cuenta");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <Card className="auth-card">
        <h1>Crear cuenta</h1>
        <p className="subtitle">
          {accountType === "owner"
            ? "Crea tu cuenta para publicar y administrar parqueaderos"
            : "Regístrate para reservar espacio y pagar desde la app"}
        </p>

        {error && <div className="form-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="account_type">Tipo de cuenta</label>
            <select
              id="account_type"
              value={accountType}
              onChange={(event) =>
                setAccountType(event.target.value === "owner" ? "owner" : "client")
              }
            >
              <option value="client">Cliente</option>
              <option value="owner">Dueño de parqueadero</option>
            </select>
          </div>
          <div className="form-field">
            <label htmlFor="name">Nombres</label>
            <input id="name" required minLength={2} value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="surname">Apellidos</label>
            <input id="surname" required minLength={2} value={surname} onChange={(e) => setSurname(e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="document_type">Tipo de documento</label>
            <select id="document_type" value={documentType} onChange={(e) => setDocumentType(e.target.value)}>
              <option value="CC">Cédula de ciudadanía</option>
              <option value="CE">Cédula de extranjería</option>
              <option value="TI">Tarjeta de identidad</option>
              <option value="PA">Pasaporte</option>
            </select>
          </div>
          <div className="form-field">
            <label htmlFor="document_number">Número de documento</label>
            <input id="document_number" required value={documentNumber} onChange={(e) => setDocumentNumber(e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="phone">Teléfono</label>
            <input id="phone" required inputMode="numeric" pattern="[0-9]+" value={phone} onChange={(e) => setPhone(e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="email">Correo electrónico</label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>
          <div className="form-field">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />
          </div>
          <Button type="submit" loading={loading}>
            Crear cuenta
          </Button>
        </form>

        <p className="auth-switch">
          ¿Ya tienes cuenta? <Link to="/login">Ingresar</Link>
        </p>
      </Card>
    </div>
  );
}
