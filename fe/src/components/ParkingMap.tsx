import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import * as availabilityApi from "../api/availability";
import { getErrorMessage } from "../api/errors";
import type { AvailabilityResponse, ParkingLot } from "../api/types";
import { addMinutes, nowInColombia, toApiDateTime } from "../utils/timeWindow";
import { Card } from "./ui/Card";
import "./ParkingMap.css";

type LotAvailability = {
  available: number;
  capacity: number;
  occupied: number;
  reserved: number;
};

function markerIcon(available: number | null): L.DivIcon {
  const count = available === null ? "…" : String(available);
  return L.divIcon({
    className: "parking-map-marker",
    html: `<span><b>${count}</b></span>`,
    iconSize: [42, 42],
    iconAnchor: [21, 21],
  });
}

function summarize(data: AvailabilityResponse): LotAvailability {
  return data.zones.reduce(
    (summary, zone) => ({
      available: summary.available + zone.available,
      capacity: summary.capacity + zone.capacity,
      occupied: summary.occupied + zone.occupied,
      reserved: summary.reserved + zone.reserved,
    }),
    { available: 0, capacity: 0, occupied: 0, reserved: 0 },
  );
}

export function ParkingMap() {
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [availability, setAvailability] = useState<Record<string, LotAvailability | null>>({});
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshTime, setRefreshTime] = useState(() => new Date());
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  const start = useMemo(() => addMinutes(nowInColombia(refreshTime), -1), [refreshTime]);
  const end = useMemo(() => addMinutes(start, 60), [start]);
  const selectedLot = lots.find((lot) => lot.id === selectedId) ?? null;

  useEffect(() => {
    let cancelled = false;
    availabilityApi
      .listParkingLots()
      .then((result) => {
        if (cancelled) return;
        setLots(result);
        setSelectedId(result[0]?.id ?? null);
      })
      .catch((cause) => {
        if (!cancelled) setError(getErrorMessage(cause));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => setRefreshTime(new Date()), 5_000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (lots.length === 0) return;
    let cancelled = false;
    const startTime = toApiDateTime(start);
    const endTime = toApiDateTime(end);
    Promise.all(
      lots.map(async (lot) => {
        try {
          const result = await availabilityApi.getAvailability(lot.id, startTime, endTime);
          return [lot.id, summarize(result)] as const;
        } catch (cause) {
          return [lot.id, null, getErrorMessage(cause)] as const;
        }
      }),
    ).then((results) => {
      if (cancelled) return;
      setAvailability(Object.fromEntries(results.map(([id, summary]) => [id, summary])));
      const failures = results.flatMap((result) => result[2] ? [result[2]] : []);
      setError(failures.length > 0 ? `No se pudo consultar la disponibilidad de ${failures.length} parqueadero(s).` : null);
      setUpdatedAt(new Date());
    });
    return () => {
      cancelled = true;
    };
  }, [lots, start, end]);

  const selectedAvailability = selectedId === null ? null : availability[selectedId];

  return (
    <section className="parking-map-section">
      <div className="parking-map-heading">
        <div>
          <span className="parking-map-eyebrow">Disponibilidad en Bogotá</span>
          <h2>Encuentra tu parqueadero</h2>
          <p>Selecciona un punto para consultar los cupos de la próxima hora.</p>
        </div>
        <div className="parking-map-live">
          <span className="parking-map-live-dot" />
          Actualización automática cada 5 segundos
          {updatedAt && <small>Actualizado {updatedAt.toLocaleTimeString("es-CO")}</small>}
        </div>
      </div>

      {error && <p className="availability-error" role="alert">{error}</p>}
      {lots.length > 0 && (
        <div className="parking-map-layout">
          <div className="parking-map-frame">
            <MapContainer
              center={[4.6533, -74.0821]}
              zoom={12}
              scrollWheelZoom
              className="parking-map"
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {lots.map((lot) => {
                if (lot.latitude === null || lot.longitude === null) return null;
                const count = availability[lot.id]?.available ?? null;
                return (
                  <Marker
                    key={lot.id}
                    position={[lot.latitude, lot.longitude]}
                    icon={markerIcon(count)}
                    eventHandlers={{ click: () => setSelectedId(lot.id) }}
                  >
                    <Popup>
                      <strong>{lot.name}</strong>
                      <br />
                      {count === null
                        ? availability[lot.id] === null
                          ? "Disponibilidad temporalmente no disponible."
                          : "Consultando disponibilidad..."
                        : `${count} de ${availability[lot.id]?.capacity ?? 0} cupos libres`}
                      <br />
                      <span>{lot.address}</span>
                    </Popup>
                  </Marker>
                );
              })}
            </MapContainer>
          </div>

          <Card className="parking-map-details">
            {selectedLot ? (
              <>
                <span className="parking-map-eyebrow">Parqueadero seleccionado</span>
                <h3>{selectedLot.name}</h3>
                <p>{selectedLot.address}</p>
                <div className="parking-map-capacity">
                  <strong>{selectedAvailability?.available ?? "—"}</strong>
                  <span>cupos libres de {selectedAvailability?.capacity ?? selectedLot.total_capacity}</span>
                </div>
                {selectedAvailability && (
                  <div className="parking-map-breakdown">
                    <span>Ocupados: {selectedAvailability.occupied}</span>
                    <span>Reservados: {selectedAvailability.reserved}</span>
                  </div>
                )}
                <Link
                  className="btn btn--primary"
                  to={`/disponibilidad?parkingLotId=${selectedLot.id}`}
                >
                  Ver espacios y horarios
                </Link>
              </>
            ) : (
              <p>{lots.length === 0 ? "Cargando parqueaderos..." : "Selecciona un punto del mapa."}</p>
            )}
          </Card>
        </div>
      )}
      <p className="parking-map-demo-note">
        Los parqueaderos marcados como “Demo” son ubicaciones de ejemplo; sus cupos se consultan en la base de disponibilidad del proyecto.
      </p>
    </section>
  );
}
