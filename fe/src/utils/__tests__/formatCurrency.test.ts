import { describe, expect, it } from "vitest";
import { formatCurrency } from "../formatCurrency";

describe("formatCurrency", () => {
  it("formats a positive number as COP currency", () => {
    expect(formatCurrency(5000)).toContain("5.000");
  });

  it("formats zero without throwing", () => {
    expect(() => formatCurrency(0)).not.toThrow();
  });
});
