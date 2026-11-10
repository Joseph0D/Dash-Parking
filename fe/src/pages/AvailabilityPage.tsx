/**
 * AvailabilityPage.tsx
 * Qué: el cliente elige parqueadero, tipo de vehículo y franja horaria, y ve qué espacios están
 *      libres SOLO en esa franja (un espacio reservado de 10:00 a 11:00 sigue libre a las 9:00).
 * Para qué: saber si hay cupo antes de llegar. Consulta pública y de solo lectura; reservar
 *           exige sesión y llega en un paso posterior.
 * Impacto: la disponibilidad la calcula PostgreSQL (db/migrations/002_*.sql); esta pantalla solo
 *          la muestra. Si pide datos con una franja inválida, la API responde 422.
 */
import { useEffect, useState } from "react";
import * as availabilityApi from "../api/availability";
import { getErrorMessage } from "../api/errors";
import type {
  AvailabilityResponse,
  ParkingLot,
  ParkingVehicleType,
  SpaceStatus,
  SpacesResponse,
} from "../api/types";
import { Card } from "../components/ui/Card";
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
];

export function AvailabilityPage() {
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [lotId, setLotId] = useState<number | null>(null);
  const [vehicleTypes, setVehicleTypes] = useState<ParkingVehicleType[]>([]);
  const [vehicleTypeId, setVehicleTypeId] = useState<number | null>(null);
  const [start, setStart] = useState(() => nextFullHour());
  const [end, setEnd] = useState(() => addMinutes(nextFullHour(), 60));
  const [zones, setZones] = useState<AvailabilityResponse | null>(null);
  const [spaces, setSpaces] = useState<SpacesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const windowError = validateWindow(start, end);
  const selectedLot = lots.find((lot) => lot.id === lotId) ?? null;

  // 1) Parqueaderos disponibles. Hoy hay uno solo y queda preseleccionado.
  useEffect(() => {
    availabilityApi
      .listParkingLots()
      .then((list) => {
        setLots(list);
        setLotId(list[0]?.id ?? null);
      })
      .catch((err) => setError(getErrorMessage(err)));
  }, []);

  // 2) Tipos de vehículo (con precio por hora) del parqueadero elegido.
  useEffect(() => {
    if (lotId === null) return;
    availabilityApi
      .listVehicleTypes(lotId)
      .then((types) => {
        setVehicleTypes(types);
        setVehicleTypeId(types[0]?.id ?? null);
      })
      .catch((err) => setError(getErrorMessage(err)));
  }, [lotId]);

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
      setLoading(true);
      setError(null);
      try {
        const [zoneData, spaceData] = await Promise.all([
          availabilityApi.getAvailability(lotId, toApiDateTime(start), toApiDateTime(end)),
          availabilityApi.getSpaces(lotId, vehicleTypeId, toApiDateTime(start), toApiDateTime(end)),
        ]);
        if (cancelled) return;
        setZones(zoneData);
        setSpaces(spaceData);
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
  }, [lotId, vehicleTypeId, start, end, windowError]);

  const selectedType = vehicleTypes.find((type) => type.id === vehicleTypeId) ?? null;
  const visibleError = windowError ?? error;

  return (
    <section className="espacios-section">
      <div className="section-header">
        <h2>Disponibilidad por horario</h2>
        <p>Elige el parqueadero y la franja: un espacio solo está ocupado en el horario reservado</p>
      </div>

      <Card className="availability-controls">
        <div className="availability-field">
          <span className="availability-label">Parqueadero</span>
          {lots.length > 1 ? (
            <select value={lotId ?? ""} onChange={(e) => setLotId(Number(e.target.value))}>
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
        </>
      )}
    </section>
  );
}
