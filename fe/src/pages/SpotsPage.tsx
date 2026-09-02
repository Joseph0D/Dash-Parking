/** SpotsPage.tsx — adaptado de espacios.html. Consulta pública de ocupación (RF-003, CA-003.*). */
import { useEffect, useState } from "react";
import * as parkingApi from "../api/parking";
import type { OccupancySummary, VehicleType } from "../api/types";
import { VEHICLE_TYPE_LABEL } from "../hooks/useVehicleLabels";
import "./SpotsPage.css";

const FILTERS: { value: VehicleType | "all"; label: string }[] = [
  { value: "all", label: "Todos" },
  { value: "car", label: "Carro" },
  { value: "motorcycle", label: "Moto" },
  { value: "bicycle", label: "Bicicleta" },
];

export function SpotsPage() {
  const [data, setData] = useState<OccupancySummary | null>(null);
  const [filter, setFilter] = useState<VehicleType | "all">("all");

  async function load() {
    const summary = await parkingApi.getOccupancy();
    setData(summary);
  }

  useEffect(() => {
    load();
    // CA-003.3: refresco automático para reflejar el estado sin recarga manual del usuario.
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div className="page-loading">Cargando ocupación...</div>;

  const spots = filter === "all" ? data.spots : data.spots.filter((s) => s.vehicle_type === filter);

  return (
    <section className="espacios-section">
      <div className="section-header">
        <h2>Ocupación en tiempo real</h2>
        <p>Consulta la disponibilidad de espacios antes de llegar</p>
      </div>

      <div className="filter-bar">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            className={`filter-btn ${filter === f.value ? "active" : ""}`}
            onClick={() => setFilter(f.value)}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="leyenda">
        <span><i className="dot dot--available" /> Libre</span>
        <span><i className="dot dot--occupied" /> Ocupado</span>
        <span><i className="dot dot--reserved" /> Reservado</span>
      </div>

      <div className="summary-bar">
        <div className="summary-stat">
          <div className="value">{data.total_spots}</div>
          <div className="label">Total</div>
        </div>
        <div className="summary-stat">
          <div className="value" style={{ color: "var(--color-success)" }}>{data.available_spots}</div>
          <div className="label">Libres</div>
        </div>
        <div className="summary-stat">
          <div className="value" style={{ color: "var(--color-danger)" }}>{data.occupied_spots}</div>
          <div className="label">Ocupados</div>
        </div>
        <div className="summary-stat">
          <div className="value" style={{ color: "var(--color-warning)" }}>{data.reserved_spots}</div>
          <div className="label">Reservados</div>
        </div>
      </div>

      {data.available_spots === 0 && (
        <p style={{ textAlign: "center", color: "var(--color-danger)", fontWeight: 600, marginBottom: "1rem" }}>
          Parqueadero lleno — no hay espacios disponibles en este momento
        </p>
      )}

      <div className="spots-grid">
        {spots.map((spot) => (
          <div key={spot.id} className={`spot-cell spot-cell--${spot.status}`} title={VEHICLE_TYPE_LABEL[spot.vehicle_type]}>
            {spot.code}
            <span className="spot-zone">{spot.zone}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
