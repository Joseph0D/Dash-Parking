/** OccupancyOverview.tsx — resumen de ocupación + vehículos actualmente dentro (RF-003, CA-003.1/2). */
import { useEffect, useState } from "react";
import * as parkingApi from "../../api/parking";
import * as sessionsApi from "../../api/sessions";
import type { OccupancySummary, SessionDetail } from "../../api/types";
import { VEHICLE_TYPE_ICON } from "../../hooks/useVehicleLabels";
import { formatCurrency } from "../../utils/formatCurrency";
import { Card } from "../../components/ui/Card";

export function OccupancyOverview() {
  const [occupancy, setOccupancy] = useState<OccupancySummary | null>(null);
  const [activeSessions, setActiveSessions] = useState<SessionDetail[]>([]);

  useEffect(() => {
    Promise.all([parkingApi.getOccupancy(), sessionsApi.listActiveSessions()]).then(([o, s]) => {
      setOccupancy(o);
      setActiveSessions(s);
    });
  }, []);

  if (!occupancy) return <div className="page-loading">Cargando...</div>;

  return (
    <div>
      <div className="stat-grid">
        <Card className="stat-card">
          <div className="stat-value">{occupancy.total_spots}</div>
          <div className="stat-label">Total espacios</div>
        </Card>
        <Card className="stat-card">
          <div className="stat-value" style={{ color: "var(--color-success)" }}>{occupancy.available_spots}</div>
          <div className="stat-label">Libres</div>
        </Card>
        <Card className="stat-card">
          <div className="stat-value" style={{ color: "var(--color-danger)" }}>{occupancy.occupied_spots}</div>
          <div className="stat-label">Ocupados</div>
        </Card>
        <Card className="stat-card">
          <div className="stat-value" style={{ color: "var(--color-warning)" }}>{occupancy.reserved_spots}</div>
          <div className="stat-label">Reservados</div>
        </Card>
      </div>

      <Card>
        <h3 style={{ marginBottom: "0.8rem" }}>Vehículos dentro del parqueadero</h3>
        {activeSessions.length === 0 ? (
          <p className="empty-state">No hay vehículos dentro en este momento.</p>
        ) : (
          <div className="entity-list">
            {activeSessions.map((s) => (
              <div className="entity-row" key={s.id}>
                <div>
                  <div className="entity-main">
                    {VEHICLE_TYPE_ICON[s.vehicle_type]} {s.plate} — {s.spot_code}
                  </div>
                  <div className="entity-sub">Desde {new Date(s.entry_time).toLocaleTimeString("es-CO")}</div>
                </div>
                <div className="entity-sub">{formatCurrency(Number(s.estimated_amount))} estimado</div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
