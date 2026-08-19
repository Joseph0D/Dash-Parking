import { apiRequest } from "./client";
import type { OccupancySummary, Rate, VehicleType } from "./types";

export function getOccupancy(): Promise<OccupancySummary> {
  return apiRequest<OccupancySummary>("/api/v1/parking/occupancy", { auth: false });
}

export function listRates(): Promise<Rate[]> {
  return apiRequest<Rate[]>("/api/v1/rates", { auth: false });
}

export function upsertRate(vehicle_type: VehicleType, price_per_hour: number): Promise<Rate> {
  return apiRequest<Rate>("/api/v1/rates", { method: "PUT", body: { vehicle_type, price_per_hour } });
}
