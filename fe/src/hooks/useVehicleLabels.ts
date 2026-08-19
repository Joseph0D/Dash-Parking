/** useVehicleLabels.ts — nombres y emojis en español para los tipos de vehículo (VehicleType). */
import type { VehicleType } from "../api/types";

export const VEHICLE_TYPE_LABEL: Record<VehicleType, string> = {
  car: "Carro",
  motorcycle: "Moto",
  bicycle: "Bicicleta",
};

export const VEHICLE_TYPE_ICON: Record<VehicleType, string> = {
  car: "🚗",
  motorcycle: "🏍️",
  bicycle: "🚲",
};
