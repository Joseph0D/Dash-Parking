import { apiRequest } from "./client";
import type { AuthResponse, User } from "./types";

export function register(name: string, email: string, password: string): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/api/v1/auth/register", {
    method: "POST",
    body: { name, email, password },
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

export function me(): Promise<User> {
  return apiRequest<User>("/api/v1/auth/me");
}
