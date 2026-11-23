import { apiRequest } from "./client";
import type { AuthResponse, User } from "./types";

export function register(
  name: string,
  surname: string,
  document_type: string,
  document_number: string,
  phone: string,
  email: string,
  password: string,
  account_type: "client" | "owner" = "client",
): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/api/v1/auth/register", {
    method: "POST",
    body: { name, surname, document_type, document_number, phone, email, password, account_type },
    auth: false,
  });
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/api/v1/auth/login", {
    method: "POST",
    body: { email, password },
    auth: false,
  });
}

export function requestPasswordReset(email: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>("/api/v1/auth/password-reset/request", {
    method: "POST",
    body: { email },
    auth: false,
  });
}

export function confirmPasswordReset(
  token: string,
  new_password: string,
): Promise<{ message: string }> {
  return apiRequest<{ message: string }>("/api/v1/auth/password-reset/confirm", {
    method: "POST",
    body: { token, new_password },
    auth: false,
  });
}

export function me(): Promise<User> {
  return apiRequest<User>("/api/v1/auth/me");
}
