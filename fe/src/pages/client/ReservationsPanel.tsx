/** ReservationsPanel.tsx — historial y cancelación de reservas del usuario. */
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as reservationsApi from "../../api/reservations";
import { getErrorMessage } from "../../api/errors";
import type { Reservation } from "../../api/types";
import { useToast } from "../../context/ToastContext";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";

const STATUS_TONE = { confirmed: "success", cancelled: "neutral", completed: "accent" } as const;
const STATUS_LABEL = { confirmed: "Confirmada", cancelled: "Cancelada", completed: "Completada" } as const;

export function ReservationsPanel({
  refreshKey = 0,
  onChanged,
  showSearchLink = true,
}: {
  refreshKey?: number;
  onChanged?: () => void;
  showSearchLink?: boolean;
} = {}) {
  const toast = useToast();
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setReservations(await reservationsApi.myReservations());
  }, []);

  useEffect(() => {
    load()
      .catch((err) => toast.error(getErrorMessage(err)))
      .finally(() => setLoading(false));
    // The toast context value changes on provider renders; reload only for data changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [load, refreshKey]);

  async function handleCancel(reservationId: string) {
    try {
      await reservationsApi.cancelReservation(reservationId);
      toast.success("Reserva cancelada");
      setReservations((current) =>
        current.map((reservation) =>
          reservation.id === reservationId
            ? { ...reservation, status: "cancelled" }
            : reservation,
        ),
      );
      onChanged?.();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  return (
    <div>
      {showSearchLink && (
        <div className="reservation-actions">
          <Link className="btn btn--primary" to="/disponibilidad">
            Buscar parqueadero y reservar
          </Link>
        </div>
      )}

      {loading ? (
        <div className="empty-state">Cargando reservas...</div>
      ) : reservations.length === 0 ? (
        <div className="empty-state">No tienes reservas todavía.</div>
      ) : (
        <div className="entity-list">
          {reservations.map((reservation) => (
            <div className="entity-row" key={reservation.id}>
              <div>
                <div className="entity-main">
                  {reservation.parking_lot_name ?? "Parqueadero"} · {reservation.vehicle_type}
                </div>
                <div className="entity-sub">
                  {new Date(reservation.start_time).toLocaleString("es-CO")} —{" "}
                  {new Date(reservation.end_time).toLocaleString("es-CO")}
                </div>
              </div>
              <div className="entity-actions" style={{ alignItems: "center" }}>
                <Badge tone={STATUS_TONE[reservation.status]}>
                  {STATUS_LABEL[reservation.status]}
                </Badge>
                {reservation.status === "confirmed" && (
                  <Button variant="ghost" onClick={() => handleCancel(reservation.id)}>
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
