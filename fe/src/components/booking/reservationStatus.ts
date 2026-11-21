import type { ReservationDetail } from "../../api/types";

/** Texto que ve el usuario para cada estado de una reserva. */
export const RESERVATION_STATUS_LABEL: Record<ReservationDetail["estado_reserva"], string> = {
  activa: "Reservada",
  "en curso": "En curso",
  vencida: "No utilizada",
  finalizada: "Finalizada",
  cancelada: "Cancelada",
};
