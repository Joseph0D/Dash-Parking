/**
 * FilterableDashboardPanel.tsx
 * Qué: dashboard con ganancia total, número de sesiones y desglose, filtrable por tipo de
 *      vehículo y por rango de fechas (RF-017, CA-017.1 a CA-017.4).
 * Para qué: que el administrador analice el desempeño sin exportar un reporte cada vez.
 */
import { useEffect, useState } from "react";
import * as reportsApi from "../../api/reports";
import type { DashboardData, VehicleType } from "../../api/types";
import { VEHICLE_TYPE_LABEL } from "../../hooks/useVehicleLabels";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../api/errors";
import { formatCurrency } from "../../utils/formatCurrency";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";

export function FilterableDashboardPanel() {
  const toast = useToast();
  const [data, setData] = useState<DashboardData | null>(null);
  const [vehicleType, setVehicleType] = useState<VehicleType | "">("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const result = await reportsApi.getDashboard({
        vehicle_type: vehicleType || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      });
      setData(result);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleClearFilters() {
    setVehicleType("");
    setStartDate("");
    setEndDate("");
  }

  return (
    <div>
      <Card style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ marginBottom: "0.8rem" }}>Filtros</h3>
        <div className="filters-bar">
          <div className="form-field">
            <label htmlFor="filter-type">Tipo de vehículo</label>
            <select id="filter-type" value={vehicleType} onChange={(e) => setVehicleType(e.target.value as VehicleType | "")}>
              <option value="">Todos</option>
              <option value="car">Carro</option>
              <option value="motorcycle">Moto</option>
              <option value="bicycle">Bicicleta</option>
            </select>
          </div>
          <div className="form-field">
            <label htmlFor="filter-start">Desde</label>
            <input id="filter-start" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="filter-end">Hasta</label>
            <input id="filter-end" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
          <Button onClick={load} loading={loading}>
            Aplicar filtros
          </Button>
          <Button variant="ghost" onClick={handleClearFilters}>
            Limpiar
          </Button>
        </div>
      </Card>

      {data && (
        <>
          <div className="stat-grid">
            <Card className="stat-card">
              <div className="stat-value">{formatCurrency(Number(data.total_revenue))}</div>
              <div className="stat-label">Ganancia total</div>
            </Card>
            <Card className="stat-card">
              <div className="stat-value">{data.total_sessions}</div>
              <div className="stat-label">Sesiones pagadas</div>
            </Card>
            <Card className="stat-card">
              <div className="stat-value">{formatCurrency(Number(data.average_session_amount))}</div>
              <div className="stat-label">Promedio por sesión</div>
            </Card>
          </div>

          <Card style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ marginBottom: "0.8rem" }}>Por tipo de vehículo</h3>
            {data.by_vehicle_type.length === 0 ? (
              <p className="empty-state">Sin datos para los filtros seleccionados.</p>
            ) : (
              <table className="breakdown-table">
                <thead>
                  <tr>
                    <th>Tipo</th>
                    <th>Sesiones</th>
                    <th>Ganancia</th>
                  </tr>
                </thead>
                <tbody>
                  {data.by_vehicle_type.map((row) => (
                    <tr key={row.vehicle_type}>
                      <td>{VEHICLE_TYPE_LABEL[row.vehicle_type]}</td>
                      <td>{row.session_count}</td>
                      <td>{formatCurrency(Number(row.total_amount))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Card>

          <Card>
            <h3 style={{ marginBottom: "0.8rem" }}>Por día</h3>
            {data.by_day.length === 0 ? (
              <p className="empty-state">Sin datos para los filtros seleccionados.</p>
            ) : (
              <table className="breakdown-table">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Sesiones</th>
                    <th>Ganancia</th>
                  </tr>
                </thead>
                <tbody>
                  {data.by_day.map((row) => (
                    <tr key={row.day}>
                      <td>{new Date(row.day).toLocaleDateString("es-CO")}</td>
                      <td>{row.session_count}</td>
                      <td>{formatCurrency(Number(row.total_amount))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
