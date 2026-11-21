import type { OnlinePaymentMethod } from "../../api/types";

/** Medios de pago simulados que ofrece la reserva en línea (el efectivo es solo presencial). */
export const PAYMENT_METHODS: { value: OnlinePaymentMethod; label: string }[] = [
  { value: "Nequi", label: "Nequi" },
  { value: "Daviplata", label: "Daviplata" },
  { value: "Tarjeta Credito", label: "Tarjeta de crédito" },
  { value: "Tarjeta Debito", label: "Tarjeta débito" },
  { value: "PSE", label: "PSE" },
];

export function paymentLabel(value: string | null): string {
  return PAYMENT_METHODS.find((method) => method.value === value)?.label ?? value ?? "—";
}
