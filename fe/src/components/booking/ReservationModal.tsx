import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as vehiclesApi from "../../api/vehicles";
import * as reservationsApi from "../../api/reservations";
import { ApiError } from "../../api/client";
import { getErrorMessage } from "../../api/errors";
import type {
  ParkingLot,
  ParkingVehicleType,
  Reservation,
  Space,
  Vehicle,
} from "../../api/types";
import { useAuth } from "../../context/AuthContext";
import { formatCurrency } from "../../utils/formatCurrency";
import { formatDateTime, formatDuration, toApiDateTime } from "../../utils/timeWindow";
import { Button } from "../ui/Button";
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

function SummaryLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="summary-line">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export function ReservationModal({
  lot,
  space,
  vehicleType,
  start,
  end,
  estimatedPrice,
  onClose,
  onBooked,
  onConflict,
}: Props) {
  const { user, loading: authLoading } = useAuth();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [vehicleId, setVehicleId] = useState("");
  const [vehiclesLoading, setVehiclesLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reservation, setReservation] = useState<Reservation | null>(null);

  const compatibleVehicles = vehicles.filter(
    (vehicle) => vehicle.vehicle_type === vehicleType.code,
  );
  const selectedVehicle =
    compatibleVehicles.find((vehicle) => vehicle.id === vehicleId) ?? null;

  useEffect(() => {
    if (!user) {
      setVehicles([]);
      setVehicleId("");
      return;
    }

    let cancelled = false;
    setVehiclesLoading(true);
    vehiclesApi
      .listMyVehicles()
      .then((items) => {
        if (cancelled) return;
        const compatible = items.filter(
          (vehicle) => vehicle.vehicle_type === vehicleType.code,
        );
        setVehicles(compatible);
        setVehicleId((current) =>
          compatible.some((vehicle) => vehicle.id === current)
            ? current
            : compatible[0]?.id ?? "",
        );
      })
      .catch((err) => {
        if (!cancelled) setError(getErrorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setVehiclesLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [user, vehicleType.code]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !submitting) {
        if (reservation) onBooked();
        else onClose();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onBooked, onClose, reservation, submitting]);

  async function handleReserve() {
    if (!selectedVehicle) return;
    setError(null);
    setSubmitting(true);
    try {
      const created = await reservationsApi.createReservation(
        lot.id,
        selectedVehicle.id,
        toApiDateTime(start),
        toApiDateTime(end),
        space.id,
      );
      setReservation(created);
    } catch (err) {
      setError(getErrorMessage(err));
      if (err instanceof ApiError && err.status === 409) {
        onConflict();
      }
    } finally {
      setSubmitting(false);
    }
  }

  function closeModal() {
    if (submitting) return;
    if (reservation) onBooked();
    else onClose();
  }

  const estimatedTotal =
    estimatedPrice !== null ? formatCurrency(Number(estimatedPrice)) : "No disponible";

  return (
    <div className="modal-overlay" onClick={closeModal}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label="Reservar espacio"
        onClick={(event) => event.stopPropagation()}
      >
        {reservation ? (
          <>
            <h3 className="modal__title modal__title--ok">Reserva confirmada</h3>
            <p className="modal__subtitle">Tu espacio quedó reservado para el horario elegido.</p>
            <div className="receipt">
              <SummaryLine label="Reserva" value={reservation.id} />
              <SummaryLine label="Parqueadero" value={lot.name} />
              <SummaryLine label="Espacio" value={`${space.code} · ${space.zone_name}`} />
              <SummaryLine
                label="Vehículo"
                value={selectedVehicle?.plate ?? selectedVehicle?.model ?? vehicleType.name}
              />
              <SummaryLine label="Desde" value={formatDateTime(reservation.start_time)} />
              <SummaryLine label="Hasta" value={formatDateTime(reservation.end_time)} />
              <SummaryLine label="Estado" value="Confirmada" />
            </div>
            <div className="modal__actions">
              <Button onClick={onBooked}>Listo</Button>
            </div>
          </>
        ) : (
          <>
            <h3 className="modal__title">Reservar espacio {space.code}</h3>
            <div className="receipt">
              <SummaryLine label="Parqueadero" value={lot.name} />
              <SummaryLine label="Zona" value={space.zone_name} />
              <SummaryLine label="Desde" value={formatDateTime(start)} />
              <SummaryLine label="Hasta" value={formatDateTime(end)} />
              <SummaryLine label="Duración" value={formatDuration(start, end)} />
              <SummaryLine label="Precio estimado" value={estimatedTotal} />
            </div>

            {error && <div className="form-error" role="alert">{error}</div>}

            {authLoading ? (
              <p className="modal__subtitle">Comprobando la sesión...</p>
            ) : !user ? (
              <p className="modal__subtitle">
                <Link to="/login">Inicia sesión</Link> para reservar este espacio.
              </p>
            ) : vehiclesLoading ? (
              <p className="modal__subtitle">Cargando tus vehículos...</p>
            ) : compatibleVehicles.length === 0 ? (
              <p className="modal__subtitle">
                No tienes un vehículo de tipo {vehicleType.name}. Agrégalo en{" "}
                <Link to="/cuenta">Mi cuenta</Link>.
              </p>
            ) : (
              <label className="form-field">
                <span>Vehículo</span>
                <select
                  value={vehicleId}
                  onChange={(event) => setVehicleId(event.target.value)}
                >
                  {compatibleVehicles.map((vehicle) => (
                    <option key={vehicle.id} value={vehicle.id}>
                      {vehicle.plate ?? vehicle.model ?? vehicle.vehicle_type}
                    </option>
                  ))}
                </select>
              </label>
            )}

            <div className="modal__actions">
              <Button
                onClick={handleReserve}
                loading={submitting}
                disabled={
                  authLoading ||
                  vehiclesLoading ||
                  !selectedVehicle ||
                  lot.schedule_configured !== true
                }
              >
                Confirmar reserva
              </Button>
              <Button variant="ghost" onClick={onClose} disabled={submitting}>
                Cancelar
              </Button>
            </div>
            <p className="modal__note">
              El precio mostrado es una estimación; no se realiza un cobro en línea.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
