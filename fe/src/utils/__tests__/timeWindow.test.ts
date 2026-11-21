import { describe, expect, it } from "vitest";
import {
  addMinutes,
  formatDateTime,
  formatDuration,
  nextFullHour,
  nowInColombia,
  toApiDateTime,
  validateWindow,
} from "../timeWindow";

// 2026-11-09 15:20 UTC == 2026-11-09 10:20 en Colombia (UTC-5)
const NOW = new Date("2026-11-09T15:20:00Z");

describe("nowInColombia", () => {
  it("converts UTC to Colombia time", () => {
    expect(nowInColombia(NOW)).toBe("2026-11-09T10:20");
  });

  it("crosses to the previous day when UTC is early morning", () => {
    expect(nowInColombia(new Date("2026-11-09T02:30:00Z"))).toBe("2026-11-08T21:30");
  });
});

describe("addMinutes", () => {
  it("adds across midnight and month boundaries", () => {
    expect(addMinutes("2026-11-30T23:30", 60)).toBe("2026-12-01T00:30");
  });

  it("subtracts minutes", () => {
    expect(addMinutes("2026-11-09T10:00", -5)).toBe("2026-11-09T09:55");
  });
});

describe("nextFullHour", () => {
  it("rounds up to the next hour in Colombia", () => {
    expect(nextFullHour(NOW)).toBe("2026-11-09T11:00");
  });
});

describe("toApiDateTime", () => {
  it("adds seconds", () => {
    expect(toApiDateTime("2026-11-09T10:00")).toBe("2026-11-09T10:00:00");
  });
});

describe("validateWindow", () => {
  it("accepts a future one-hour window", () => {
    expect(validateWindow("2026-11-09T11:00", "2026-11-09T12:00", NOW)).toBeNull();
  });

  it("requires both dates", () => {
    expect(validateWindow("", "2026-11-09T12:00", NOW)).toMatch(/Elige/);
  });

  it("rejects end before or equal to start", () => {
    expect(validateWindow("2026-11-09T12:00", "2026-11-09T12:00", NOW)).toMatch(/posterior/);
  });

  it("rejects a start in the past but tolerates a few minutes", () => {
    expect(validateWindow("2026-11-09T09:00", "2026-11-09T10:00", NOW)).toMatch(/pasado/);
    expect(validateWindow("2026-11-09T10:17", "2026-11-09T11:00", NOW)).toBeNull();
  });
});

describe("formatDuration", () => {
  it("formats minutes, hours and days", () => {
    expect(formatDuration("2026-11-09T10:00", "2026-11-09T10:45")).toBe("45 min");
    expect(formatDuration("2026-11-09T10:00:00", "2026-11-09T11:00:00")).toBe("1 h");
    expect(formatDuration("2026-11-09T10:00", "2026-11-09T11:30")).toBe("1 h 30 min");
    expect(formatDuration("2026-11-09T10:00", "2026-11-10T12:00")).toBe("1 d 2 h");
  });

  it("returns a dash for an invalid range", () => {
    expect(formatDuration("2026-11-09T11:00", "2026-11-09T10:00")).toBe("—");
  });
});

describe("formatDateTime", () => {
  it("shows the wall-clock hour without converting time zones", () => {
    expect(formatDateTime("2026-11-09T10:00:00")).toMatch(/10:00/);
  });
});
