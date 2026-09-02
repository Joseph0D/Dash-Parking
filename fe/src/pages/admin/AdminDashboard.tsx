/** AdminDashboard.tsx — panel "/admin" (adaptado de apartados/admin.html), con tabs. */
import { useCallback, useState } from "react";
import { EntryExitPanel } from "./EntryExitPanel";
import { QrValidationPanel } from "./QrValidationPanel";
import { RatesPanel } from "./RatesPanel";
import { FilterableDashboardPanel } from "./FilterableDashboardPanel";
import { OccupancyOverview } from "./OccupancyOverview";
import "./AdminDashboard.css";

type Tab = "occupancy" | "entry-exit" | "qr" | "rates" | "dashboard";

export function AdminDashboard() {
  const [tab, setTab] = useState<Tab>("occupancy");
  const [refreshKey, setRefreshKey] = useState(0);

  const handleChange = useCallback(() => setRefreshKey((k) => k + 1), []);

  return (
    <div className="admin-dashboard">
      <h1>Panel de administración</h1>

      <div className="tabs">
        <button className={`tab-btn ${tab === "occupancy" ? "active" : ""}`} onClick={() => setTab("occupancy")}>
          Ocupación
        </button>
        <button className={`tab-btn ${tab === "entry-exit" ? "active" : ""}`} onClick={() => setTab("entry-exit")}>
          Entrada / Salida
        </button>
        <button className={`tab-btn ${tab === "qr" ? "active" : ""}`} onClick={() => setTab("qr")}>
          Validar QR
        </button>
        <button className={`tab-btn ${tab === "rates" ? "active" : ""}`} onClick={() => setTab("rates")}>
          Tarifas
        </button>
        <button className={`tab-btn ${tab === "dashboard" ? "active" : ""}`} onClick={() => setTab("dashboard")}>
          Dashboard
        </button>
      </div>

      {tab === "occupancy" && <OccupancyOverview key={refreshKey} />}
      {tab === "entry-exit" && <EntryExitPanel onChange={handleChange} />}
      {tab === "qr" && <QrValidationPanel onChange={handleChange} />}
      {tab === "rates" && <RatesPanel />}
      {tab === "dashboard" && <FilterableDashboardPanel />}
    </div>
  );
}
