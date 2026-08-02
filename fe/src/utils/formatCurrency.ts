/**
 * Formatea un valor numérico como moneda en pesos colombianos (COP), sin decimales,
 * para mostrar el valor a pagar calculado por el backend (RF09).
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(value);
}
