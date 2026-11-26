import { Link, Outlet, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import "./RolePanelLayout.css";

interface PanelLink {
  label: string;
  to: string;
  tab?: string;
  create?: boolean;
}

interface RolePanelLayoutProps {
  title: string;
  links: PanelLink[];
  defaultTab?: string;
}

export function RolePanelLayout({ title, links, defaultTab }: RolePanelLayoutProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  function isActive(link: PanelLink): boolean {
    if (link.tab) return (searchParams.get("tab") ?? defaultTab) === link.tab;
    if (link.create) return searchParams.get("crear") === "1";
    return !searchParams.has("crear") && !searchParams.has("tab");
  }

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="role-panel">
      <aside className="role-panel__sidebar">
        <Link to="/" className="role-panel__brand">Dash<span>Parking</span></Link>
        <div className="role-panel__identity">
          <p className="role-panel__title">{title}</p>
          <p className="role-panel__name">{[user?.name, user?.surname].filter(Boolean).join(" ") || user?.email}</p>
        </div>
        <nav aria-label={`Menú de ${title}`}>
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={isActive(link) ? "is-active" : ""}
              aria-current={isActive(link) ? "page" : undefined}
            >
              {link.label}
            </Link>
          ))}
          {user?.role === "owner" && (
            <Link to="/disponibilidad">Ver disponibilidad</Link>
          )}
        </nav>
        <div className="role-panel__footer">
          <small>{user?.email}</small>
          <button type="button" onClick={handleLogout}>Cerrar sesión</button>
        </div>
      </aside>
      <main className="role-panel__content" key={location.pathname}>
        <Outlet />
      </main>
    </div>
  );
}
