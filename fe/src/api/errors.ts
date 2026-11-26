import { ApiError } from "./client";

/** Extrae un mensaje legible de cualquier error capturado, priorizando el detail del backend. */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (
    error instanceof TypeError
    && /failed to fetch|networkerror|load failed/i.test(error.message)
  ) {
    return "No se pudo conectar con el servidor. Verifica tu conexión e inténtalo de nuevo.";
  }
  if (error instanceof Error) return error.message;
  return "Ocurrió un error inesperado. Intenta de nuevo.";
}
