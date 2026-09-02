/** ClientDashboard.tsx — panel "/cuenta" (adaptado de apartados/usuario.html), con tabs. */
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { VehiclesPanel } from "./VehiclesPanel";
import { ReservationsPanel } from "./ReservationsPanel";
import { SessionPanel } from "./SessionPanel";
import "./ClientDashboard.css";

type Tab = "session" | "vehicles" | "reservations";

export function ClientDashboard() {
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("session");

  return (
    <div className="client-dashboard">
      <h1>Mi cuenta</h1>
      <p className="welcome">Hola, {user?.name} — gestiona tus vehículos, reservas y pagos</p>

      <div className="tabs">
        <button className={`tab-btn ${tab === "session" ? "active" : ""}`} onClick={() => setTab("session")}>
          Sesión activa
        </button>
        <button className={`tab-btn ${tab === "vehicles" ? "active" : ""}`} onClick={() => setTab("vehicles")}>
          Mis vehículos
        </button>
        <button className={`tab-btn ${tab === "reservations" ? "active" : ""}`} onClick={() => setTab("reservations")}>
          Reservas
        </button>
      </div>

      {tab === "session" && <SessionPanel />}
      {tab === "vehicles" && <VehiclesPanel />}
      {tab === "reservations" && <ReservationsPanel />}
    </div>
  );
}
