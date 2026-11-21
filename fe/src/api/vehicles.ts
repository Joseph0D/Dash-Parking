import { apiRequest } from "./client";
import type { Vehicle, VehicleQRPass, VehicleType } from "./types";

export function listMyVehicles(): Promise<Vehicle[]> {
  return apiRequest<Vehicle[]>("/api/v1/vehicles/me");
}

export function registerVehicle(
  plate: string,
  vehicle_type: VehicleType,
  brand: string,
  model: string,
  color: string
): Promise<Vehicle> {
  const body = vehicle_type === "bicycle" || vehicle_type === "scooter"
    ? { plate: null, vehicle_type, brand, model, color }
    : { plate, vehicle_type, brand, model, color };
  return apiRequest<Vehicle>("/api/v1/vehicles", { method: "POST", body });
}

export function deleteVehicle(vehicleId: string): Promise<void> {
  return apiRequest<void>(`/api/v1/vehicles/${vehicleId}`, { method: "DELETE" });
}

export function updateVehicle(
  vehicleId: string,
  plate: string,
  vehicle_type: VehicleType,
  brand: string,
  model: string,
  color: string
): Promise<Vehicle> {
  const body = vehicle_type === "bicycle" || vehicle_type === "scooter"
    ? { plate: null, vehicle_type, brand, model, color }
    : { plate, vehicle_type, brand, model, color };
  return apiRequest<Vehicle>(`/api/v1/vehicles/${vehicleId}`, { method: "PUT", body });
}

export function getVehicleQr(vehicleId: string): Promise<VehicleQRPass> {
  return apiRequest<VehicleQRPass>(`/api/v1/vehicles/${vehicleId}/qr`);
}
