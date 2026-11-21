import { apiRequest } from "./client";
import type {
  OwnerInventoryInput,
  OwnerParkingLot,
  OwnerParkingLotDashboard,
  ParkingScheduleInput,
  VehicleCategory,
} from "./types";

interface ParkingLotInput {
  name: string;
  identification: string;
  address: string;
  phone: string | null;
  latitude: number;
  longitude: number;
}

interface CreateParkingLotInput extends ParkingLotInput {
  schedules: ParkingScheduleInput[];
  inventory: OwnerInventoryInput[];
}

export function listVehicleCategories(): Promise<VehicleCategory[]> {
  return apiRequest<VehicleCategory[]>("/api/v1/owner/vehicle-categories");
}

export function listParkingLots(): Promise<OwnerParkingLot[]> {
  return apiRequest<OwnerParkingLot[]>("/api/v1/owner/parking-lots");
}

export function createParkingLot(payload: CreateParkingLotInput): Promise<OwnerParkingLot> {
  return apiRequest<OwnerParkingLot>("/api/v1/owner/parking-lots", {
    method: "POST",
    body: payload,
  });
}

export function updateParkingLot(
  lotId: string,
  payload: ParkingLotInput & { is_active: boolean },
): Promise<OwnerParkingLot> {
  return apiRequest<OwnerParkingLot>(`/api/v1/owner/parking-lots/${lotId}`, {
    method: "PUT",
    body: payload,
  });
}

export function updateSchedule(
  lotId: string,
  schedules: ParkingScheduleInput[],
): Promise<OwnerParkingLot> {
  return apiRequest<OwnerParkingLot>(`/api/v1/owner/parking-lots/${lotId}/schedule`, {
    method: "PUT",
    body: { schedules },
  });
}

export function updateInventory(
  lotId: string,
  inventory: OwnerInventoryInput[],
): Promise<OwnerParkingLot> {
  return apiRequest<OwnerParkingLot>(`/api/v1/owner/parking-lots/${lotId}/inventory`, {
    method: "PUT",
    body: { inventory },
  });
}

export function getDashboard(
  lotId: string,
  reportDate?: string,
): Promise<OwnerParkingLotDashboard> {
  const query = reportDate ? `?report_date=${encodeURIComponent(reportDate)}` : "";
  return apiRequest<OwnerParkingLotDashboard>(
    `/api/v1/owner/parking-lots/${lotId}/dashboard${query}`,
  );
}
