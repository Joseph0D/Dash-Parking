/** Navbar.tsx — adaptado 1:1 de index.html (.navbar/.brand/.nav-links del mockup). */
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import "./Navbar.css";

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <nav className="navbar">
      <Link to="/" className="brand">
        Dash<span>Parking</span>
      </Link>
      <ul className="nav-links">
        <li>
          <Link to="/espacios">Espacios</Link>
        </li>
        {!user && (
          <>
            <li>
              <Link to="/login">Ingresar</Link>
            </li>
            <li>
              <Link to="/registro" className="btn-cta">
                Crear cuenta
              </Link>
            </li>
          </>
        )}
        {user && user.role === "client" && (
          <li>
            <Link to="/cuenta" className="btn-cta">
              Mi cuenta
            </Link>
          </li>
        )}
        {user && (user.role === "admin" || user.role === "operator") && (
          <li>
            <Link to="/admin" className="btn-cta">
              Panel admin
            </Link>
          </li>
        )}
        {user && (
          <li>
            <button className="nav-logout" onClick={handleLogout}>
              Salir
            </button>
          </li>
        )}
      </ul>
    </nav>
  );
}
