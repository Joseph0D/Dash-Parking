import { ApiError } from "./client";

/** Extrae un mensaje legible de cualquier error capturado, priorizando el detail del backend. */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "Ocurrió un error inesperado. Intenta de nuevo.";
}
