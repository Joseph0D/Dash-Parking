/**
 * types.ts — Tipos compartidos entre el frontend y los schemas Pydantic del backend.
 * Mantener sincronizado manualmente con be/app/schemas/*.py y be/app/models/enums.py.
 */

export type VehicleType = "car" | "motorcycle" | "bicycle";
export type UserRole = "client" | "operator" | "admin";
export type SpotStatus = "available" | "occupied" | "reserved";
export type SessionStatus = "active" | "completed";
export type ReservationStatus = "confirmed" | "cancelled" | "completed";
export type PaymentMethod = "cash" | "virtual" | "qr";
export type PaymentStatus = "pending" | "paid" | "rejected";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Vehicle {
  id: string;
  plate: string;
  vehicle_type: VehicleType;
  model: string | null;
  owner_id: string;
  created_at: string;
}

export interface ParkingSpot {
  id: string;
  code: string;
  zone: string;
  vehicle_type: VehicleType;
  status: SpotStatus;
}

export interface OccupancySummary {
  total_spots: number;
  occupied_spots: number;
  available_spots: number;
  reserved_spots: number;
  spots: ParkingSpot[];
}

export interface Rate {
  id: string;
  vehicle_type: VehicleType;
  price_per_hour: string;
}

export interface SessionDetail {
  id: string;
  vehicle_id: string;
  spot_id: string;
  entry_time: string;
  exit_time: string | null;
  status: SessionStatus;
  amount: string | null;
  plate: string;
  vehicle_type: VehicleType;
  spot_code: string;
  elapsed_seconds: number;
  estimated_amount: string;
}

export interface Reservation {
  id: string;
  vehicle_id: string;
  spot_id: string;
  vehicle_type: VehicleType;
  start_time: string;
  end_time: string;
  status: ReservationStatus;
}

export interface Payment {
  id: string;
  session_id: string;
  amount: string;
  method: PaymentMethod;
  status: PaymentStatus;
  reference: string;
}

export interface QRPass {
  token: string;
  qr_image_base64: string;
  session_id: string;
}

export interface QRValidation {
  session_id: string;
  plate: string;
  vehicle_type: string;
  elapsed_seconds: number;
  amount: string;
}

export interface DashboardData {
  total_revenue: string;
  total_sessions: number;
  average_session_amount: string;
  by_vehicle_type: { vehicle_type: VehicleType; total_amount: string; session_count: number }[];
  by_day: { day: string; total_amount: string; session_count: number }[];
}
