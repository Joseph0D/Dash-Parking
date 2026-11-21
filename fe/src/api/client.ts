/**
 * client.ts
 * Qué: wrapper único sobre fetch para hablar con la API de Dash Parking.
 * Para qué: centralizar la base URL, el header de autenticación (JWT) y el manejo de errores,
 *           para que cada llamada en api/*.ts no repita ese boilerplate.
 * Impacto: si esto falla silenciosamente, cualquier página podría mostrar datos vacíos sin
 *          explicar por qué (ej. token expirado) — por eso ApiError siempre lleva el detail
 *          que devuelve el backend (ver be/app/routers/*.py).
 */

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const API_BASE_URL =
  configuredApiBaseUrl || (import.meta.env.DEV ? "http://localhost:8000" : undefined);

if (!API_BASE_URL) {
  throw new Error("VITE_API_BASE_URL debe configurarse antes de compilar el frontend.");
}

if (!import.meta.env.DEV && !API_BASE_URL.startsWith("https://")) {
  throw new Error("VITE_API_BASE_URL debe usar HTTPS fuera del entorno local.");
}

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
  // Token explícito. Lo usan los módulos de la base nueva (api/accounts.ts), cuya sesión es
  // independiente de la anterior; si se envía, reemplaza al token guardado en `dash_parking_token`.
  token?: string | null;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true, token } = options;

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const bearer = token !== undefined ? token : auth ? getToken() : null;
  if (bearer) headers.Authorization = `Bearer ${bearer}`;

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
