/**
 * types.ts — Tipos compartidos entre el frontend y los schemas Pydantic del backend.
 * Mantener sincronizado manualmente con be/app/schemas/*.py y be/app/models/enums.py.
 */

export type VehicleType = "car" | "motorcycle" | "bicycle" | "electric_motorcycle" | "scooter" | "truck";
export type UserRole = "client" | "operator" | "owner" | "admin";
export type SpotStatus = "available" | "occupied" | "reserved";
export type SessionStatus = "active" | "completed";
export type ReservationStatus = "confirmed" | "cancelled" | "completed";
export type PaymentMethod = "cash" | "virtual" | "qr";
export type PaymentStatus = "pending" | "paid" | "rejected";

export interface User {
  id: string;
  name: string;
  surname: string | null;
  document_type: string | null;
  document_number: string | null;
  phone: string | null;
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
  plate: string | null;
  vehicle_type: VehicleType;
  vehicle_category_id: string | null;
  brand: string | null;
  model: string | null;
  color: string | null;
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
  parking_lot_id: string | null;
  parking_lot_name: string | null;
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

export interface VehicleQRPass {
  token: string;
  qr_image_base64: string;
  vehicle_id: string;
  plate: string | null;
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
  id: string;
  name: string;
  identification: string;
  address: string;
  phone: string | null;
  total_capacity: number;
  latitude: number | null;
  longitude: number | null;
  schedule_configured: boolean;
}

export interface ParkingSchedule {
  day_of_week: number;
  opens_at: string | null;
  closes_at: string | null;
  is_closed: boolean;
  is_24_hours: boolean;
}

export interface VehicleCategory {
  id: string;
  code: VehicleType;
  name: string;
  description: string | null;
}

export interface OwnerInventoryItem {
  vehicle_category_id: string;
  code: VehicleType;
  name: string;
  space_count: number;
  price_per_minute: string | null;
  price_per_day: string | null;
  price_per_month: string | null;
}

export interface OwnerParkingLot extends ParkingLot {
  is_active: boolean;
  schedules: ParkingSchedule[];
  inventory: OwnerInventoryItem[];
}

export interface OwnerParkingLotDashboard {
  report_date: string;
  reservation_count: number;
  daily_reservations: {
    id: string;
    plate: string | null;
    vehicle_type: VehicleType;
    start_time: string;
    end_time: string;
    status: ReservationStatus;
    spot_code: string;
  }[];
  reservations_by_vehicle_type: { vehicle_type: VehicleType; count: number }[];
  occupancy_by_vehicle_type: { vehicle_type: VehicleType; count: number }[];
  income_today: string;
}

export type ParkingScheduleInput = ParkingSchedule;

export interface OwnerInventoryInput {
  vehicle_category_id: string;
  space_count: number;
  price_per_minute: string;
  price_per_day: string | null;
  price_per_month: string | null;
}

export interface ParkingVehicleType {
  id: string;
  code: VehicleType;
  name: string;
  description: string | null;
  price_per_hour: string | null;
}

export interface ZoneAvailability {
  zone_id: string;
  zone_name: string;
  vehicle_type_id: string;
  capacity: number;
  available: number;
  reserved: number;
  occupied: number;
}

export interface AvailabilityResponse {
  parking_lot_id: string;
  start: string;
  end: string;
  zones: ZoneAvailability[];
}

export interface Space {
  id: string;
  code: string;
  zone_id: string;
  zone_name: string;
  space_type_id: string | null;
  status: SpaceStatus;
}

export interface SpacesResponse {
  parking_lot_id: string;
  vehicle_type_id: string;
  start: string;
  end: string;
  estimated_price: string | null;
  available_count: number;
  spaces: Space[];
}
