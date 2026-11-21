import { apiRequest } from "./client";
import type { Reservation } from "./types";

export function createReservation(
  parking_lot_id: string,
  vehicle_id: string,
  start_time: string,
  end_time: string,
  spot_id?: string,
): Promise<Reservation> {
  return apiRequest<Reservation>("/api/v1/reservations", {
    method: "POST",
    body: { parking_lot_id, vehicle_id, start_time, end_time, spot_id },
  });
}

export function myReservations(): Promise<Reservation[]> {
  return apiRequest<Reservation[]>("/api/v1/reservations/me");
}

export function cancelReservation(reservationId: string): Promise<Reservation> {
  return apiRequest<Reservation>(`/api/v1/reservations/${reservationId}`, { method: "DELETE" });
}
