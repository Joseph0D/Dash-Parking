import { apiRequest } from "./client";
import type { Vehicle, VehicleType } from "./types";

export function listMyVehicles(): Promise<Vehicle[]> {
  return apiRequest<Vehicle[]>("/api/v1/vehicles/me");
}

export function registerVehicle(plate: string, vehicle_type: VehicleType, model?: string): Promise<Vehicle> {
  return apiRequest<Vehicle>("/api/v1/vehicles", { method: "POST", body: { plate, vehicle_type, model } });
}

export function deleteVehicle(vehicleId: string): Promise<void> {
  return apiRequest<void>(`/api/v1/vehicles/${vehicleId}`, { method: "DELETE" });
}
