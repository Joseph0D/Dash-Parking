import { apiRequest } from "./client";
import type { Payment, QRPass, QRValidation } from "./types";

export function payVirtual(session_id: string): Promise<Payment> {
  return apiRequest<Payment>("/api/v1/payments/virtual", { method: "POST", body: { session_id } });
}

export function payCash(session_id: string): Promise<Payment> {
  return apiRequest<Payment>("/api/v1/payments/cash", { method: "POST", body: { session_id } });
}

export function getQrPass(sessionId: string): Promise<QRPass> {
  return apiRequest<QRPass>(`/api/v1/payments/qr/${sessionId}`);
}

export function validateQr(token: string): Promise<QRValidation> {
  return apiRequest<QRValidation>("/api/v1/payments/qr/validate", { method: "POST", body: { token } });
}

export function chargeAfterQr(sessionId: string): Promise<Payment> {
  return apiRequest<Payment>(`/api/v1/payments/qr/${sessionId}/charge`, { method: "POST" });
}
