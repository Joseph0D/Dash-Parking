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

// ---------------------------------------------------------------------------------------------
// Disponibilidad por franja (be/app/schemas/availability.py). Los precios (Decimal) llegan como
// texto desde la API: convertir con Number() solo al mostrarlos.
// ---------------------------------------------------------------------------------------------
export type SpaceStatus = "available" | "reserved" | "occupied" | "maintenance";

export interface ParkingLot {
  id: number;
  name: string;
  identification: string;
  address: string;
  phone: string;
  total_capacity: number;
}

export interface ParkingVehicleType {
  id: number;
  name: string;
  description: string | null;
  price_per_hour: string | null;
}

export interface ZoneAvailability {
  zone_id: number;
  zone_name: string;
  vehicle_type_id: number;
  capacity: number;
  available: number;
  reserved: number;
  occupied: number;
}

export interface AvailabilityResponse {
  parking_lot_id: number;
  start: string;
  end: string;
  zones: ZoneAvailability[];
}

export interface Space {
  id: number;
  code: string;
  zone_id: number;
  zone_name: string;
  space_type_id: number;
  status: SpaceStatus;
}

export interface SpacesResponse {
  parking_lot_id: number;
  vehicle_type_id: number;
  start: string;
  end: string;
  estimated_price: string | null;
  available_count: number;
  spaces: Space[];
}
