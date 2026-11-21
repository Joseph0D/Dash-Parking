/**
 * reservas.ts
 * Qué: reservar con pago simulado, ver/cancelar reservas y operaciones del dueño
 *      (be/app/routers/reservas.py).
 * Para qué: ciclo del espacio del informe: Disponible → Reservado → Ocupado → Disponible.
 * Impacto: todas exigen el token de la cuenta (api/accounts.ts); el backend valida el rol.
 */
import { apiRequest } from "./client";
import type {
  ActiveTicket,
  CancellationResult,
  CreateReservationPayload,
  ExitResult,
  ReservationCreated,
  ReservationDetail,
} from "./types";

export function createReservation(
  token: string,
  payload: CreateReservationPayload,
): Promise<ReservationCreated> {
  return apiRequest<ReservationCreated>("/api/v1/reservas/crear", {
    method: "POST",
    body: payload,
    token,
  });
}

export function listMyReservations(token: string): Promise<ReservationDetail[]> {
  return apiRequest<ReservationDetail[]>("/api/v1/reservas/mias", { token });
}

export function cancelReservation(token: string, reservationId: number): Promise<CancellationResult> {
  return apiRequest<CancellationResult>(`/api/v1/reservas/${reservationId}/cancelar`, {
    method: "POST",
    token,
  });
}

export function listManagedReservations(token: string): Promise<ReservationDetail[]> {
  return apiRequest<ReservationDetail[]>("/api/v1/reservas/parqueadero", { token });
}

export function registerEntry(token: string, reservationId: number): Promise<ReservationDetail> {
  return apiRequest<ReservationDetail>(`/api/v1/reservas/${reservationId}/ingreso`, {
    method: "POST",
    token,
  });
}

export function listActiveTickets(token: string): Promise<ActiveTicket[]> {
  return apiRequest<ActiveTicket[]>("/api/v1/tickets/activos", { token });
}

export function registerExit(token: string, ticketId: number): Promise<ExitResult> {
  return apiRequest<ExitResult>(`/api/v1/tickets/${ticketId}/salida`, { method: "POST", token });
}
