/**
 * timeWindow.ts
 * Qué: utilidades para la franja horaria que elige el cliente (inputs datetime-local).
 * Para qué: trabajar siempre con "hora Colombia" como texto "YYYY-MM-DDTHH:mm", que es lo que
 *           entrega <input type="datetime-local"> y lo que espera la base de datos, sin depender
 *           de la zona horaria del navegador.
 * Impacto: si se mezclan zonas aquí, un cliente fuera de Colombia vería disponibilidad de otra
 *          hora distinta a la que cree estar consultando.
 */

/** Mismo margen que el backend (be/app/services/availability_service.py). */
export const PAST_TOLERANCE_MINUTES = 5;

/** Hora actual en Colombia como "YYYY-MM-DDTHH:mm". `now` es inyectable para poder probarla. */
export function nowInColombia(now: Date = new Date()): string {
  const text = new Intl.DateTimeFormat("sv-SE", {
    timeZone: "America/Bogota",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).format(now);
  return text.replace(" ", "T");
}

/** Suma minutos a un "YYYY-MM-DDTHH:mm" tratándolo como hora de pared (sin zona ni horario de verano). */
export function addMinutes(local: string, minutes: number): string {
  const date = new Date(`${local}:00Z`);
  date.setUTCMinutes(date.getUTCMinutes() + minutes);
  return date.toISOString().slice(0, 16);
}

/** Próxima hora en punto (ej. 14:20 → 15:00). Punto de partida cómodo para elegir una franja. */
export function nextFullHour(now: Date = new Date()): string {
  const current = nowInColombia(now);
  return addMinutes(`${current.slice(0, 13)}:00`, 60);
}

/** Convierte "YYYY-MM-DDTHH:mm" al formato con segundos que espera la API. */
export function toApiDateTime(local: string): string {
  return `${local}:00`;
}

/** Devuelve el mensaje de error de la franja, o null si es válida. */
export function validateWindow(start: string, end: string, now: Date = new Date()): string | null {
  if (!start || !end) return "Elige la hora de inicio y la de fin";
  if (end <= start) return "La hora de fin debe ser posterior a la de inicio";
  if (start < addMinutes(nowInColombia(now), -PAST_TOLERANCE_MINUTES)) {
    return "La hora de inicio no puede estar en el pasado";
  }
  return null;
}

/** Duración legible entre dos "YYYY-MM-DDTHH:mm[:ss]": "45 min", "1 h", "1 h 30 min", "1 d 2 h". */
export function formatDuration(start: string, end: string): string {
  const minutes = Math.round(
    (new Date(`${end.slice(0, 16)}:00Z`).getTime() - new Date(`${start.slice(0, 16)}:00Z`).getTime()) /
      60000,
  );
  if (minutes <= 0) return "—";
  const days = Math.floor(minutes / 1440);
  const hours = Math.floor((minutes % 1440) / 60);
  const rest = minutes % 60;
  const parts: string[] = [];
  if (days) parts.push(`${days} d`);
  if (hours) parts.push(`${hours} h`);
  if (rest) parts.push(`${rest} min`);
  return parts.join(" ");
}

/** Fecha y hora para mostrar al usuario (la hora es de pared, no se convierte de zona). */
export function formatDateTime(local: string): string {
  return new Intl.DateTimeFormat("es-CO", {
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(local));
}
