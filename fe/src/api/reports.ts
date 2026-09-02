import { apiRequest } from "./client";
import type { DashboardData, VehicleType } from "./types";

export interface DashboardFilters {
  vehicle_type?: VehicleType;
  start_date?: string;
  end_date?: string;
}

export function getDashboard(filters: DashboardFilters = {}): Promise<DashboardData> {
  const params = new URLSearchParams();
  if (filters.vehicle_type) params.set("vehicle_type", filters.vehicle_type);
  if (filters.start_date) params.set("start_date", filters.start_date);
  if (filters.end_date) params.set("end_date", filters.end_date);
  const query = params.toString();
  return apiRequest<DashboardData>(`/api/v1/reports/dashboard${query ? `?${query}` : ""}`);
}
