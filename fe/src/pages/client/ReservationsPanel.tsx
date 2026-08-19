/** ReservationsPanel.tsx — RF-013: reservar un espacio eligiendo vehículo + tiempo (CA-013.*). */
import { useEffect, useState, type FormEvent } from "react";
import * as vehiclesApi from "../../api/vehicles";
import * as reservationsApi from "../../api/reservations";
import type { Reservation, Vehicle } from "../../api/types";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../api/errors";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";

const STATUS_TONE = { confirmed: "success", cancelled: "neutral", completed: "accent" } as const;
const STATUS_LABEL = { confirmed: "Confirmada", cancelled: "Cancelada", completed: "Completada" } as const;

export function ReservationsPanel() {
  const toast = useToast();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [vehicleId, setVehicleId] = useState("");
  const [startTime, setStartTime] = useState("");
  const [durationHours, setDurationHours] = useState(1);
  const [loading, setLoading] = useState(false);

  async function load() {
    const [vehicleList, reservationList] = await Promise.all([
      vehiclesApi.listMyVehicles(),
      reservationsApi.myReservations(),
    ]);
    setVehicles(vehicleList);
    setReservations(reservationList);
    if (vehicleList.length > 0 && !vehicleId) setVehicleId(vehicleList[0].id);
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const vehicle = vehicles.find((v) => v.id === vehicleId);
    if (!vehicle) return;

    setLoading(true);
    try {
      await reservationsApi.createReservation(
        vehicle.id,
        vehicle.vehicle_type,
        new Date(startTime).toISOString(),
        durationHours
      );
      toast.success("Reserva confirmada");
      await load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel(reservationId: string) {
    try {
      await reservationsApi.cancelReservation(reservationId);
      toast.success("Reserva cancelada");
      await load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  if (vehicles.length === 0) {
    return <div className="empty-state">Registra al menos un vehículo para poder reservar un espacio.</div>;
  }

  return (
    <div>
      <Card style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ marginBottom: "0.8rem" }}>Nueva reserva</h3>
        <form className="inline-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="vehicle">Vehículo</label>
            <select id="vehicle" value={vehicleId} onChange={(e) => setVehicleId(e.target.value)}>
              {vehicles.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.plate}
                </option>
              ))}
            </select>
          </div>
          <div className="form-field">
            <label htmlFor="start_time">Llegada</label>
            <input
              id="start_time"
              type="datetime-local"
              required
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
            />
          </div>
          <div className="form-field">
            <label htmlFor="duration">Duración (horas)</label>
            <input
              id="duration"
              type="number"
              min={1}
              max={24}
              step={1}
              required
              value={durationHours}
              onChange={(e) => setDurationHours(Number(e.target.value))}
            />
          </div>
          <Button type="submit" loading={loading}>
            Reservar
          </Button>
        </form>
      </Card>

      {reservations.length === 0 ? (
        <div className="empty-state">No tienes reservas todavía.</div>
      ) : (
        <div className="entity-list">
          {reservations.map((r) => (
            <div className="entity-row" key={r.id}>
              <div>
                <div className="entity-main">
                  {new Date(r.start_time).toLocaleString("es-CO")} — {r.vehicle_type}
                </div>
                <div className="entity-sub">
                  Hasta {new Date(r.end_time).toLocaleString("es-CO")}
                </div>
              </div>
              <div className="entity-actions" style={{ alignItems: "center" }}>
                <Badge tone={STATUS_TONE[r.status]}>{STATUS_LABEL[r.status]}</Badge>
                {r.status === "confirmed" && (
                  <Button variant="ghost" onClick={() => handleCancel(r.id)}>
                    Cancelar
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
