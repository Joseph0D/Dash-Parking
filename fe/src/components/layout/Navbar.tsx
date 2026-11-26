/** Navbar.tsx — adaptado 1:1 de index.html (.navbar/.brand/.nav-links del mockup). */
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import "./Navbar.css";

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const isHome = location.pathname === "/";
  const isRolePanel = ["/cuenta", "/admin", "/owner"].some(
    (path) => location.pathname === path || location.pathname.startsWith(`${path}/`),
  );

  if (user && isRolePanel) return null;

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <nav className={`navbar${isHome ? " navbar--home" : ""}`}>
      <Link to="/" className="brand">
        Dash<span>Parking</span>
      </Link>
      <ul className="nav-links">
        {isHome ? (
          <>
            <li><a href="#parqueaderos">Parqueaderos</a></li>
            <li><a href="#reservas">Reservas</a></li>
            <li><a href="#servicios">Servicios</a></li>
            <li><a href="#manual">Guía</a></li>
          </>
        ) : (
          <>
            <li><Link to="/disponibilidad">Reservar</Link></li>
            {!user && <li><Link to="/registro?tipo=dueno">Soy dueño</Link></li>}
          </>
        )}
        <li>
          {/* Abre la hoja de soporte (manual de usuario y técnico) en una pestaña nueva
              para no sacar al usuario de su sesión. Archivo: fe/public/soporte/ */}
          <a
            href="/soporte/SOPORTE_DASHPARKING.pdf"
            target="_blank"
            rel="noopener noreferrer"
          >
            Soporte
          </a>
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
        {user && user.role === "owner" && (
          <li>
            <Link to="/owner" className="btn-cta">
              Mis parqueaderos
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
