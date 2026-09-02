import { apiRequest } from "./client";
import type { Reservation, VehicleType } from "./types";

export function createReservation(
  vehicle_id: string,
  vehicle_type: VehicleType,
  start_time: string,
  duration_hours: number
): Promise<Reservation> {
  return apiRequest<Reservation>("/api/v1/reservations", {
    method: "POST",
    body: { vehicle_id, vehicle_type, start_time, duration_hours },
  });
}

export function myReservations(): Promise<Reservation[]> {
  return apiRequest<Reservation[]>("/api/v1/reservations/me");
}

export function cancelReservation(reservationId: string): Promise<Reservation> {
  return apiRequest<Reservation>(`/api/v1/reservations/${reservationId}`, { method: "DELETE" });
}
