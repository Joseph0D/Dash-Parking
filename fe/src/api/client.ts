/**
 * client.ts
 * Qué: wrapper único sobre fetch para hablar con la API de Dash Parking.
 * Para qué: centralizar la base URL, el header de autenticación (JWT) y el manejo de errores,
 *           para que cada llamada en api/*.ts no repita ese boilerplate.
 * Impacto: si esto falla silenciosamente, cualquier página podría mostrar datos vacíos sin
 *          explicar por qué (ej. token expirado) — por eso ApiError siempre lleva el detail
 *          que devuelve el backend (ver be/app/routers/*.py).
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function getToken(): string | null {
  return localStorage.getItem("dash_parking_token");
}

export function setToken(token: string | null): void {
  if (token) {
    localStorage.setItem("dash_parking_token", token);
  } else {
    localStorage.removeItem("dash_parking_token");
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  auth?: boolean; // por defecto true: casi todo endpoint requiere sesión
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true } = options;

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = data?.detail ?? "Ocurrió un error inesperado. Intenta de nuevo.";
    throw new ApiError(response.status, message);
  }

  return data as T;
}
