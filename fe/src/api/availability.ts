/**
 * availability.ts
 * Qué: llamadas a la API de disponibilidad por franja (be/app/routers/availability.py).
 * Para qué: elegir parqueadero, tipo de vehículo y horario, y ver qué espacios están libres
 *           SOLO en esa franja.
 * Impacto: las fechas viajan como hora Colombia sin zona ("2026-11-09T10:00:00"); el backend
 *          las interpreta así. Si se envía otra zona, el backend la convierte.
 */
import { apiRequest } from "./client";
import type {
  AvailabilityResponse,
  ParkingLot,
  ParkingVehicleType,
  SpacesResponse,
} from "./types";

const BASE = "/api/v1/parking-lots";

function windowQuery(start: string, end: string): string {
  return new URLSearchParams({ start, end }).toString();
}

export function listParkingLots(): Promise<ParkingLot[]> {
  return apiRequest<ParkingLot[]>(BASE, { auth: false });
}

export function listVehicleTypes(parkingLotId: number): Promise<ParkingVehicleType[]> {
  return apiRequest<ParkingVehicleType[]>(`${BASE}/${parkingLotId}/vehicle-types`, { auth: false });
}

export function getAvailability(
  parkingLotId: number,
  start: string,
  end: string,
): Promise<AvailabilityResponse> {
  return apiRequest<AvailabilityResponse>(
    `${BASE}/${parkingLotId}/availability?${windowQuery(start, end)}`,
    { auth: false },
  );
}

export function getSpaces(
  parkingLotId: number,
  vehicleTypeId: number,
  start: string,
  end: string,
): Promise<SpacesResponse> {
  const query = `vehicle_type_id=${vehicleTypeId}&${windowQuery(start, end)}`;
  return apiRequest<SpacesResponse>(`${BASE}/${parkingLotId}/spaces?${query}`, { auth: false });
}
