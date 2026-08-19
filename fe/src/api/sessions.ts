import { apiRequest } from "./client";
import type { SessionDetail, VehicleType } from "./types";

export function registerEntry(plate: string, vehicle_type: VehicleType): Promise<SessionDetail> {
  return apiRequest<SessionDetail>("/api/v1/sessions/entry", { method: "POST", body: { plate, vehicle_type } });
}

export function listActiveSessions(): Promise<SessionDetail[]> {
  return apiRequest<SessionDetail[]>("/api/v1/sessions/active");
}

export function myActiveSession(): Promise<SessionDetail | null> {
  return apiRequest<SessionDetail | null>("/api/v1/sessions/me/active");
}

export function getSessionByPlate(plate: string): Promise<SessionDetail> {
  return apiRequest<SessionDetail>(`/api/v1/sessions/by-plate/${encodeURIComponent(plate)}`);
}
