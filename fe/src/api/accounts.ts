/**
 * accounts.ts
 * Qué: cuentas y vehículos de la base nueva (be/app/routers/accounts.py).
 * Para qué: iniciar sesión / registrarse para reservar y administrar los vehículos propios.
 * Impacto: usa un token propio (no el de /api/v1/auth): se pasa explícitamente en cada llamada.
 */
import { apiRequest } from "./client";
import type {
  Account,
  AccountToken,
  AccountVehicle,
  NewVehiclePayload,
  RegisterAccountPayload,
} from "./types";

const BASE = "/api/v1/accounts";

export function loginAccount(email: string, password: string): Promise<AccountToken> {
  return apiRequest<AccountToken>(`${BASE}/login`, {
    method: "POST",
    body: { email, password },
    token: null,
  });
}

export function registerAccount(payload: RegisterAccountPayload): Promise<AccountToken> {
  return apiRequest<AccountToken>(`${BASE}/register`, {
    method: "POST",
    body: payload,
    token: null,
  });
}

export function getMyAccount(token: string): Promise<Account> {
  return apiRequest<Account>(`${BASE}/me`, { token });
}

export function listMyVehicles(token: string): Promise<AccountVehicle[]> {
  return apiRequest<AccountVehicle[]>(`${BASE}/me/vehicles`, { token });
}

export function createMyVehicle(token: string, payload: NewVehiclePayload): Promise<AccountVehicle> {
  return apiRequest<AccountVehicle>(`${BASE}/me/vehicles`, { method: "POST", body: payload, token });
}
