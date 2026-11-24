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
    <div className="admin-dashboard dash-shell">
      <aside className="dash-side">
        <div>
          <p className="dash-side__role">Administración</p>
          <p className="dash-side__name">Panel de control</p>
        </div>
        <nav className="tabs" aria-label="Menú de administración">
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
        </nav>
      </aside>

      <section className="dash-main">
        <h1>Panel de administración</h1>

        {tab === "occupancy" && <OccupancyOverview key={refreshKey} />}
        {tab === "entry-exit" && <EntryExitPanel onChange={handleChange} />}
        {tab === "qr" && <QrValidationPanel onChange={handleChange} />}
        {tab === "rates" && <RatesPanel />}
        {tab === "dashboard" && <FilterableDashboardPanel />}
      </section>
    </div>
  );
}
