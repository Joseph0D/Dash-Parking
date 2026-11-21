/**
 * AvailabilityPage.tsx
 * Qué: el cliente elige parqueadero, tipo de vehículo y franja horaria, y ve qué espacios están
 *      libres SOLO en esa franja, y reservar eligiendo uno de sus vehículos.
 */
import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import * as availabilityApi from "../api/availability";
import { getErrorMessage } from "../api/errors";
import * as reservationsApi from "../api/reservations";
import * as vehiclesApi from "../api/vehicles";
import type {
  AvailabilityResponse,
  ParkingLot,
  ParkingVehicleType,
  SpaceStatus,
  SpacesResponse,
  Vehicle,
} from "../api/types";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { addMinutes, nextFullHour, toApiDateTime, validateWindow } from "../utils/timeWindow";
import { formatCurrency } from "../utils/formatCurrency";
import "./SpotsPage.css";
import "./AvailabilityPage.css";

const STATUS_LABEL: Record<SpaceStatus, string> = {
  available: "Libre",
  reserved: "Reservado",
  occupied: "Ocupado",
  maintenance: "Mantenimiento",
};

const DURATION_PRESETS = [
  { label: "1 hora", minutes: 60 },
  { label: "2 horas", minutes: 120 },
  { label: "4 horas", minutes: 240 },
  { label: "24 horas", minutes: 1440 },
  { label: "48 horas", minutes: 2880 },
];

export function AvailabilityPage() {
  const [searchParams] = useSearchParams();
  const requestedLotId = searchParams.get("parkingLotId");
  const { user, loading: authLoading } = useAuth();
  const toast = useToast();
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [lotId, setLotId] = useState<string | null>(null);
  const [vehicleTypes, setVehicleTypes] = useState<ParkingVehicleType[]>([]);
  const [vehicleTypeId, setVehicleTypeId] = useState<string | null>(null);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [vehicleId, setVehicleId] = useState("");
  const [start, setStart] = useState(() => nextFullHour());
  const [end, setEnd] = useState(() => addMinutes(nextFullHour(), 60));
  const [zones, setZones] = useState<AvailabilityResponse | null>(null);
  const [spaces, setSpaces] = useState<SpacesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [booking, setBooking] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const hasLoadedAvailability = useRef(false);

  const windowError = validateWindow(start, end);
  const selectedLot = lots.find((lot) => lot.id === lotId) ?? null;

  useEffect(() => {
    const timer = window.setInterval(() => setRefreshKey((key) => key + 1), 5_000);
    return () => window.clearInterval(timer);
  }, []);

  // 1) Parqueaderos activos; el de la URL queda preseleccionado si sigue disponible.
  useEffect(() => {
    let cancelled = false;
    availabilityApi
      .listParkingLots()
      .then((list) => {
        if (cancelled) return;
        setLots(list);
        setLotId(
          requestedLotId && list.some((lot) => lot.id === requestedLotId)
            ? requestedLotId
            : list[0]?.id ?? null,
        );
      })
      .catch((err) => {
        if (!cancelled) setError(getErrorMessage(err));
      });
    return () => {
      cancelled = true;
    };
  }, [requestedLotId]);

  // 2) Tipos de vehículo (con precio por hora) del parqueadero elegido.
  useEffect(() => {
    setVehicleTypes([]);
    setVehicleTypeId(null);
    if (lotId === null) return;
    let cancelled = false;
    availabilityApi
      .listVehicleTypes(lotId)
      .then((types) => {
        if (cancelled) return;
        setVehicleTypes(types);
        setVehicleTypeId(types[0]?.id ?? null);
      })
      .catch((err) => {
        if (!cancelled) setError(getErrorMessage(err));
      });
    return () => {
      cancelled = true;
    };
  }, [lotId]);

  useEffect(() => {
    if (!user) {
      setVehicles([]);
      setVehicleId("");
      return;
    }
    let cancelled = false;
    vehiclesApi
      .listMyVehicles()
      .then((list) => {
        if (!cancelled) setVehicles(list);
      })
      .catch((err) => {
        if (!cancelled) setError(getErrorMessage(err));
      });
    return () => {
      cancelled = true;
    };
  }, [user]);

  // 3) Disponibilidad de la franja. `cancelled` descarta respuestas viejas si el cliente sigue
  //    cambiando la hora, y el retardo evita una petición por cada tecla.
  useEffect(() => {
    if (lotId === null || vehicleTypeId === null || windowError) {
      setZones(null);
      setSpaces(null);
      return;
    }
    let cancelled = false;
    const timer = setTimeout(async () => {
      if (!hasLoadedAvailability.current) setLoading(true);
      setError(null);
      try {
        const [zoneData, spaceData] = await Promise.all([
          availabilityApi.getAvailability(lotId, toApiDateTime(start), toApiDateTime(end)),
          availabilityApi.getSpaces(lotId, vehicleTypeId, toApiDateTime(start), toApiDateTime(end)),
        ]);
        if (cancelled) return;
        setZones(zoneData);
        setSpaces(spaceData);
        hasLoadedAvailability.current = true;
      } catch (err) {
        if (cancelled) return;
        setZones(null);
        setSpaces(null);
        setError(getErrorMessage(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 300);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [lotId, vehicleTypeId, start, end, windowError, refreshKey]);

  const selectedType = vehicleTypes.find((type) => type.id === vehicleTypeId) ?? null;
  const compatibleVehicles = vehicles.filter(
    (vehicle) => vehicle.vehicle_type === selectedType?.code,
  );
  const selectedVehicle = compatibleVehicles.find((vehicle) => vehicle.id === vehicleId) ?? null;
  const visibleError = windowError ?? error;

  useEffect(() => {
    if (!compatibleVehicles.some((vehicle) => vehicle.id === vehicleId)) {
      setVehicleId(compatibleVehicles[0]?.id ?? "");
    }
  }, [vehicleId, compatibleVehicles]);

  async function handleReservation() {
    if (!selectedLot || !selectedType || !selectedVehicle || !spaces?.available_count) return;
    setBooking(true);
    try {
      await reservationsApi.createReservation(
        selectedLot.id,
        selectedVehicle.id,
        toApiDateTime(start),
        toApiDateTime(end),
      );
      toast.success("Reserva confirmada");
      setRefreshKey((key) => key + 1);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setBooking(false);
    }
  }

  return (
    <section className="espacios-section">
      <div className="section-header">
        <h2>Disponibilidad por horario</h2>
        <p>Elige el parqueadero y la franja; los cupos se actualizan automáticamente cada 5 segundos.</p>
      </div>

      <Card className="availability-controls">
        <div className="availability-field">
          <span className="availability-label">Parqueadero</span>
          {lots.length > 1 ? (
            <select
              value={lotId ?? ""}
              onChange={(e) => {
                setLotId(e.target.value || null);
                setVehicleTypeId(null);
              }}
            >
              {lots.map((lot) => (
                <option key={lot.id} value={lot.id}>
                  {lot.name}
                </option>
              ))}
            </select>
          ) : (
            selectedLot && (
              <div className="lot-card">
                <strong>{selectedLot.name}</strong>
                <span>{selectedLot.address}</span>
              </div>
            )
          )}
        </div>

        <div className="availability-field">
          <span className="availability-label">Tipo de vehículo</span>
          <div className="filter-bar filter-bar--left">
            {vehicleTypes.map((type) => (
              <button
                key={type.id}
                type="button"
                className={`filter-btn ${type.id === vehicleTypeId ? "active" : ""}`}
                onClick={() => setVehicleTypeId(type.id)}
              >
                {type.name}
                {type.price_per_hour !== null && (
                  <small> · {formatCurrency(Number(type.price_per_hour))}/h</small>
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="availability-field availability-field--row">
          <label className="form-field">
            <span>Desde</span>
            <input
              type="datetime-local"
              step={900}
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
          </label>
          <label className="form-field">
            <span>Hasta</span>
            <input
              type="datetime-local"
              step={900}
              value={end}
              onChange={(e) => setEnd(e.target.value)}
            />
          </label>
        </div>

        <div className="availability-field">
          <span className="availability-label">Duración rápida (desde la hora de inicio)</span>
          <div className="filter-bar filter-bar--left">
            {DURATION_PRESETS.map((preset) => (
              <button
                key={preset.minutes}
                type="button"
                className="filter-btn"
                disabled={!start}
                onClick={() => setEnd(addMinutes(start, preset.minutes))}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {selectedLot && !selectedLot.schedule_configured && (
        <p className="availability-error" role="status">
          Este parqueadero todavía no tiene horario semanal configurado. Puedes consultar sus
          espacios, pero aún no admite reservas.
        </p>
      )}

      {visibleError && (
        <p className="availability-error" role="alert">
          {visibleError}
        </p>
      )}
      {loading && <p className="availability-loading">Consultando disponibilidad...</p>}

      {spaces && zones && !visibleError && (
        <>
          <div className="summary-bar">
            <div className="summary-stat">
              <div className="value" style={{ color: "var(--color-success)" }}>
                {spaces.available_count}
              </div>
              <div className="label">Libres en esta franja</div>
            </div>
            <div className="summary-stat">
              <div className="value">{spaces.spaces.length}</div>
              <div className="label">Espacios de {selectedType?.name ?? "este tipo"}</div>
            </div>
            <div className="summary-stat">
              <div className="value">
                {spaces.estimated_price !== null
                  ? formatCurrency(Number(spaces.estimated_price))
                  : "—"}
              </div>
              <div className="label">Precio estimado</div>
            </div>
          </div>

          {spaces.available_count === 0 && (
            <p className="availability-error">No hay espacios libres en esa franja. Prueba otro horario.</p>
          )}

          <div className="zone-list">
            {zones.zones.map((zone) => (
              <div
                key={zone.zone_id}
                className={`zone-card ${zone.vehicle_type_id === vehicleTypeId ? "zone-card--active" : ""}`}
              >
                <strong>{zone.zone_name}</strong>
                <span>
                  {zone.available} libres de {zone.capacity}
                </span>
              </div>
            ))}
          </div>

          <div className="leyenda">
            {(Object.keys(STATUS_LABEL) as SpaceStatus[]).map((status) => (
              <span key={status}>
                <i className={`dot dot--${status}`} /> {STATUS_LABEL[status]}
              </span>
            ))}
          </div>

          <div className="spots-grid">
            {spaces.spaces.map((space) => (
              <div
                key={space.id}
                className={`spot-cell spot-cell--${space.status}`}
                title={`${space.code} · ${STATUS_LABEL[space.status]}`}
              >
                {space.code}
                <span className="spot-zone">{STATUS_LABEL[space.status]}</span>
              </div>
            ))}
          </div>

          <Card className="availability-booking">
            <h3>Reservar este horario</h3>
            {authLoading ? (
              <p>Comprobando la sesión...</p>
            ) : !user ? (
              <p>
                <Link to="/login">Inicia sesión</Link> para reservar.
              </p>
            ) : compatibleVehicles.length === 0 ? (
              <p>
                No tienes un vehículo de este tipo registrado. Agrégalo en{" "}
                <Link to="/cuenta">Mi cuenta</Link>.
              </p>
            ) : (
              <div className="availability-booking-row">
                <label className="form-field">
                  <span>Vehículo</span>
                  <select value={vehicleId} onChange={(event) => setVehicleId(event.target.value)}>
                    {compatibleVehicles.map((vehicle) => (
                      <option key={vehicle.id} value={vehicle.id}>
                        {vehicle.plate ?? vehicle.model ?? vehicle.vehicle_type}
                      </option>
                    ))}
                  </select>
                </label>
                <Button
                  type="button"
                  loading={booking}
                  disabled={
                    authLoading ||
                    selectedLot?.schedule_configured !== true ||
                    spaces.available_count === 0 ||
                    !selectedVehicle
                  }
                  onClick={handleReservation}
                >
                  Reservar espacio
                </Button>
              </div>
            )}
          </Card>
        </>
      )}
    </section>
  );
}
