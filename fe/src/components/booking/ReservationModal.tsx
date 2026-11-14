/**
 * ReservationModal.tsx
 * Qué: ventana para reservar un espacio elegido: sesión, vehículo, medio de pago, resumen,
 *      pago simulado y comprobante.
 * Para qué: MVP del informe — reservar y pagar en un solo paso. Al confirmar, el espacio pasa a
 *           "Reservado" solo en la franja elegida.
 * Impacto: si otro cliente tomó el espacio mientras tanto, el backend responde 409: se muestra
 *          el mensaje y se actualiza la cuadrícula para que elija otro.
 */
import { useCallback, useEffect, useState, type FormEvent } from "react";
import * as accountsApi from "../../api/accounts";
import { ApiError } from "../../api/client";
import { getErrorMessage } from "../../api/errors";
import * as reservasApi from "../../api/reservas";
import type {
  AccountVehicle,
  ParkingLot,
  ParkingVehicleType,
  OnlinePaymentMethod,
  ReservationDetail,
  Space,
} from "../../api/types";
import { useAccount } from "../../context/AccountContext";
import { formatCurrency } from "../../utils/formatCurrency";
import { formatDateTime, formatDuration, toApiDateTime } from "../../utils/timeWindow";
import { Button } from "../ui/Button";
import { AccountForm } from "./AccountForm";
import { PAYMENT_METHODS, paymentLabel } from "./paymentMethods";
import "./booking.css";

interface Props {
  lot: ParkingLot;
  space: Space;
  vehicleType: ParkingVehicleType;
  start: string;
  end: string;
  estimatedPrice: string | null;
  onClose: () => void;
  onBooked: () => void;
  onConflict: () => void;
}

function Line({ label, value }: { label: string; value: string }) {
  return (
    <div className="summary-line">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export function ReservationModal({
  lot, space, vehicleType, start, end, estimatedPrice, onClose, onBooked, onConflict,
}: Props) {
  const { account, token, loading: sessionLoading, logout } = useAccount();
  const [vehicles, setVehicles] = useState<AccountVehicle[]>([]);
  const [vehicleId, setVehicleId] = useState<number | null>(null);
  const [addingVehicle, setAddingVehicle] = useState(false);
  const [newVehicle, setNewVehicle] = useState({ plate: "", brand: "", model: "", color: "" });
  const [method, setMethod] = useState<OnlinePaymentMethod>("Nequi");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [receipt, setReceipt] = useState<ReservationDetail | null>(null);

  const total = estimatedPrice !== null ? formatCurrency(Number(estimatedPrice)) : "—";

  // Solo se ofrecen los vehículos del tipo de este espacio (un carro no entra a la zona de motos).
  const loadVehicles = useCallback(async () => {
    if (!token) return;
    const all = await accountsApi.listMyVehicles(token);
    const compatible = all.filter((v) => v.vehicle_type_id === vehicleType.id);
    setVehicles(compatible);
    setVehicleId((current) => current ?? compatible[0]?.id ?? null);
    setAddingVehicle(compatible.length === 0);
  }, [token, vehicleType.id]);

  useEffect(() => {
    loadVehicles().catch((err) => setError(getErrorMessage(err)));
  }, [loadVehicles]);

  // Escape cierra la ventana (salvo mientras se procesa el pago).
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key !== "Escape" || submitting) return;
      if (receipt) onBooked();
      else onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [submitting, receipt, onClose, onBooked]);

  async function handleAddVehicle(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setError(null);
    setSubmitting(true);
    try {
      const created = await accountsApi.createMyVehicle(token, {
        plate: newVehicle.plate,
        vehicle_type_id: vehicleType.id,
        brand: newVehicle.brand || undefined,
        model: newVehicle.model || undefined,
        color: newVehicle.color || undefined,
      });
      setNewVehicle({ plate: "", brand: "", model: "", color: "" });
      setVehicleId(created.id);
      await loadVehicles();
      setVehicleId(created.id);
      setAddingVehicle(false);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function handlePay() {
    if (!token || vehicleId === null) return;
    setError(null);
    setSubmitting(true);
    try {
      const response = await reservasApi.createReservation(token, {
        id_estacionamiento: lot.id,
        id_vehiculo: vehicleId,
        id_espacio: space.id,
        fecha_inicio: toApiDateTime(start),
        fecha_fin: toApiDateTime(end),
        metodo_pago: method,
      });
      setReceipt(response.data.resumen);
    } catch (err) {
      setError(getErrorMessage(err));
      if (err instanceof ApiError && err.status === 409) onConflict();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={() => !submitting && (receipt ? onBooked() : onClose())}>
      <div className="modal" role="dialog" aria-modal="true" aria-label="Reservar espacio"
        onClick={(event) => event.stopPropagation()}>
        {receipt ? (
          <>
            <h3 className="modal__title modal__title--ok">Reserva confirmada</h3>
            <p className="modal__subtitle">Pago simulado aprobado. Guarda tu comprobante.</p>
            <div className="receipt">
              <Line label="Comprobante" value={receipt.id_comprobante ?? "—"} />
              <Line label="Parqueadero" value={receipt.nombre_parqueadero} />
              <Line label="Espacio" value={`${receipt.numero_espacio} · ${receipt.zona}`} />
              <Line label="Vehículo" value={`${receipt.placa} (${receipt.tipo_vehiculo})`} />
              <Line label="Desde" value={formatDateTime(receipt.fecha_inicio)} />
              <Line label="Hasta" value={formatDateTime(receipt.fecha_fin)} />
              <Line label="Medio de pago" value={paymentLabel(receipt.metodo_pago)} />
              <Line label="Referencia" value={receipt.referencia_transaccion ?? "—"} />
              <Line label="Total pagado" value={formatCurrency(Number(receipt.monto_total ?? 0))} />
            </div>
            <div className="modal__actions">
              <Button onClick={onBooked}>Listo</Button>
            </div>
          </>
        ) : (
          <>
            <h3 className="modal__title">Reservar espacio {space.code}</h3>
            <div className="receipt">
              <Line label="Parqueadero" value={lot.name} />
              <Line label="Zona" value={space.zone_name} />
              <Line label="Desde" value={formatDateTime(start)} />
              <Line label="Hasta" value={formatDateTime(end)} />
              <Line label="Duración" value={formatDuration(start, end)} />
              <Line label="Total a pagar" value={total} />
            </div>

            {error && <div className="form-error">{error}</div>}

            {sessionLoading ? (
              <p className="modal__subtitle">Verificando sesión...</p>
            ) : !account ? (
              <>
                <p className="modal__subtitle">Inicia sesión o crea una cuenta para reservar.</p>
                <AccountForm />
              </>
            ) : (
              <>
                <p className="modal__session">
                  {account.first_name} {account.last_name} ·{" "}
                  <button type="button" className="booking-link" onClick={logout}>Cambiar de cuenta</button>
                </p>

                {addingVehicle ? (
                  <form className="booking-form" onSubmit={handleAddVehicle}>
                    <p className="modal__subtitle">
                      Registra tu vehículo ({vehicleType.name}) para continuar.
                    </p>
                    <div className="booking-form__row">
                      <label className="form-field">
                        <span>Placa</span>
                        <input required minLength={3} maxLength={10} value={newVehicle.plate}
                          onChange={(e) => setNewVehicle({ ...newVehicle, plate: e.target.value })} />
                      </label>
                      <label className="form-field">
                        <span>Marca</span>
                        <input value={newVehicle.brand}
                          onChange={(e) => setNewVehicle({ ...newVehicle, brand: e.target.value })} />
                      </label>
                    </div>
                    <div className="booking-form__row">
                      <label className="form-field">
                        <span>Modelo</span>
                        <input value={newVehicle.model}
                          onChange={(e) => setNewVehicle({ ...newVehicle, model: e.target.value })} />
                      </label>
                      <label className="form-field">
                        <span>Color</span>
                        <input value={newVehicle.color}
                          onChange={(e) => setNewVehicle({ ...newVehicle, color: e.target.value })} />
                      </label>
                    </div>
                    <div className="modal__actions">
                      <Button type="submit" loading={submitting}>Guardar vehículo</Button>
                      {vehicles.length > 0 && (
                        <Button type="button" variant="ghost" onClick={() => setAddingVehicle(false)}>
                          Volver
                        </Button>
                      )}
                    </div>
                  </form>
                ) : (
                  <>
                    <label className="form-field">
                      <span>Vehículo</span>
                      <select value={vehicleId ?? ""} onChange={(e) => setVehicleId(Number(e.target.value))}>
                        {vehicles.map((v) => (
                          <option key={v.id} value={v.id}>
                            {v.plate} · {v.vehicle_type_name}
                            {v.brand ? ` · ${v.brand}` : ""}
                          </option>
                        ))}
                      </select>
                    </label>
                    <button type="button" className="booking-link" onClick={() => setAddingVehicle(true)}>
                      + Agregar otro vehículo
                    </button>

                    <fieldset className="pay-methods">
                      <legend>Medio de pago</legend>
                      {PAYMENT_METHODS.map((option) => (
                        <label key={option.value}
                          className={`pay-option ${method === option.value ? "pay-option--on" : ""}`}>
                          <input type="radio" name="payment-method" value={option.value}
                            checked={method === option.value} onChange={() => setMethod(option.value)} />
                          {option.label}
                        </label>
                      ))}
                    </fieldset>

                    <div className="modal__actions">
                      <Button onClick={handlePay} loading={submitting} disabled={vehicleId === null}>
                        Pagar {total}
                      </Button>
                      <Button variant="ghost" onClick={onClose} disabled={submitting}>Cancelar</Button>
                    </div>
                    <p className="modal__note">Pago simulado: no se cobra dinero real ni se piden datos bancarios.</p>
                  </>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
