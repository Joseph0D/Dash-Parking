/**
 * MyReservations.tsx
 * Qué: lista de las reservas del cliente con su resumen, estado y botón para cancelar.
 * Para qué: que el cliente vea qué reservó, cuánto pagó y pueda cancelar antes de que empiece
 *           (con devolución simulada).
 * Impacto: la regla de "solo se cancela antes de empezar" la aplica el backend; aquí solo se
 *          oculta el botón cuando no corresponde.
 */
import { useCallback, useEffect, useState } from "react";
import { getErrorMessage } from "../../api/errors";
import * as reservasApi from "../../api/reservas";
import type { ReservationDetail } from "../../api/types";
import { useAccount } from "../../context/AccountContext";
import { useToast } from "../../context/ToastContext";
import { formatCurrency } from "../../utils/formatCurrency";
import { formatDateTime, nowInColombia } from "../../utils/timeWindow";
import { Card } from "../ui/Card";
import { paymentLabel } from "./paymentMethods";
import { RESERVATION_STATUS_LABEL } from "./reservationStatus";
import "./booking.css";

export function MyReservations({ refreshKey, onChanged }: { refreshKey: number; onChanged: () => void }) {
  const { token } = useAccount();
  const toast = useToast();
  const [items, setItems] = useState<ReservationDetail[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    try {
      setItems(await reservasApi.listMyReservations(token));
      setError(null);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }, [token]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  async function handleCancel(item: ReservationDetail) {
    if (!token) return;
    if (!window.confirm("¿Cancelar esta reserva? Se reembolsará el pago (simulado).")) return;
    try {
      const result = await reservasApi.cancelReservation(token, item.id_reserva);
      toast.success(`Reserva cancelada. Reembolso: ${formatCurrency(Number(result.monto_reembolsado))}`);
      onChanged();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  const now = nowInColombia();

  return (
    <section className="my-reservations">
      <h3>Mis reservas</h3>
      {error && <div className="form-error">{error}</div>}
      {!error && items.length === 0 && <p className="booking-empty">Aún no tienes reservas.</p>}
      <div className="reservation-list">
        {items.map((item) => (
          <Card key={item.id_reserva} className="reservation-card">
            <div className="reservation-card__head">
              <strong>
                {item.numero_espacio} · {item.zona}
              </strong>
              <span className={`status-badge status-badge--${item.estado_reserva.replace(" ", "-")}`}>
                {RESERVATION_STATUS_LABEL[item.estado_reserva]}
              </span>
            </div>
            <div className="reservation-card__body">
              <span>{item.nombre_parqueadero}</span>
              <span>
                {formatDateTime(item.fecha_inicio)} → {formatDateTime(item.fecha_fin)}
              </span>
              <span>
                {item.placa} · {paymentLabel(item.metodo_pago)} ·{" "}
                {formatCurrency(Number(item.monto_total ?? 0))}
                {item.estado_pago === "Reembolsado" && " (reembolsado)"}
              </span>
              {item.id_comprobante && <span>Comprobante {item.id_comprobante}</span>}
            </div>
            {item.estado_reserva === "activa" && item.fecha_inicio.slice(0, 16) > now && (
              <button type="button" className="booking-link booking-link--danger"
                onClick={() => handleCancel(item)}>
                Cancelar reserva
              </button>
            )}
          </Card>
        ))}
      </div>
    </section>
  );
}
