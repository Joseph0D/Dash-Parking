import { describe, expect, it } from "vitest";
import { ApiError } from "./client";
import { getErrorMessage } from "./errors";

describe("getErrorMessage", () => {
  it("preserves messages returned by the API", () => {
    expect(getErrorMessage(new ApiError(400, "Solicitud inválida"))).toBe("Solicitud inválida");
  });

  it("explains network failures without exposing browser-specific fetch text", () => {
    expect(getErrorMessage(new TypeError("Failed to fetch"))).toBe(
      "No se pudo conectar con el servidor. Verifica tu conexión e inténtalo de nuevo.",
    );
  });

  it("preserves other error messages", () => {
    expect(getErrorMessage(new Error("Error de validación"))).toBe("Error de validación");
  });
});
