/** ClientDashboard.tsx — panel "/cuenta" (adaptado de apartados/usuario.html), con tabs. */
import { useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { VehiclesPanel } from "./VehiclesPanel";
import { ReservationsPanel } from "./ReservationsPanel";
import { SessionPanel } from "./SessionPanel";
import "./ClientDashboard.css";

type Tab = "session" | "vehicles" | "reservations";

export function ClientDashboard() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedTab = searchParams.get("tab");
  const tab: Tab = requestedTab === "vehicles" || requestedTab === "reservations"
    ? requestedTab
    : "session";

  function selectTab(nextTab: Tab) {
    setSearchParams({ tab: nextTab }, { replace: true });
  }

  return (
    <div className="client-dashboard">
      <h1>Mi cuenta</h1>
      <p className="welcome">Hola, {user?.name} — gestiona tus vehículos, reservas y pagos</p>

      <div className="tabs">
        <button className={`tab-btn ${tab === "session" ? "active" : ""}`} onClick={() => selectTab("session")}>
          Sesión activa
        </button>
        <button className={`tab-btn ${tab === "vehicles" ? "active" : ""}`} onClick={() => selectTab("vehicles")}>
          Mis vehículos
        </button>
        <button className={`tab-btn ${tab === "reservations" ? "active" : ""}`} onClick={() => selectTab("reservations")}>
          Reservas
        </button>
      </div>

      {tab === "session" && <SessionPanel />}
      {tab === "vehicles" && <VehiclesPanel />}
      {tab === "reservations" && <ReservationsPanel />}
    </div>
  );
}
