import { useEffect, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from "react-leaflet";
import * as ownerApi from "../../api/owner";
import { getErrorMessage } from "../../api/errors";
import type {
  OwnerInventoryInput,
  OwnerParkingLot,
  OwnerParkingLotDashboard,
  ParkingScheduleInput,
  VehicleCategory,
} from "../../api/types";
import { formatCurrency } from "../../utils/formatCurrency";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import "./OwnerDashboard.css";

const WEEKDAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
const VEHICLE_LABELS: Record<string, string> = {
  car: "Carro",
  motorcycle: "Moto",
  bicycle: "Bicicleta",
  electric_motorcycle: "Moto eléctrica",
  scooter: "Patineta eléctrica",
  truck: "Camión",
};
const BOGOTA: [number, number] = [4.6533, -74.0821];

interface LocationValue {
  address: string;
  latitude: number;
  longitude: number;
}

interface InventoryDraft extends OwnerInventoryInput {
  name: string;
  isConfigured: boolean;
}

function defaultSchedule(): ParkingScheduleInput[] {
  return WEEKDAYS.map((_, day_of_week) => ({
    day_of_week,
    opens_at: null,
    closes_at: null,
    is_closed: true,
    is_24_hours: false,
  }));
}

function defaultInventory(categories: VehicleCategory[]): InventoryDraft[] {
  return categories.map((category) => ({
    vehicle_category_id: category.id,
    name: category.name,
    space_count: 0,
    price_per_minute: "",
    price_per_day: null,
    price_per_month: null,
    isConfigured: false,
  }));
}

function inventoryFromLot(
  categories: VehicleCategory[],
  lot: OwnerParkingLot,
): InventoryDraft[] {
  return categories.map((category) => {
    const saved = lot.inventory.find((item) => item.vehicle_category_id === category.id);
    return {
      vehicle_category_id: category.id,
      name: category.name,
      space_count: saved?.space_count ?? 0,
      price_per_minute: saved?.price_per_minute ?? "",
      price_per_day: saved?.price_per_day ?? null,
      price_per_month: saved?.price_per_month ?? null,
      isConfigured: saved !== undefined,
    };
  });
}

function toInventoryInput(items: InventoryDraft[]): OwnerInventoryInput[] {
  return items
    .filter((item) => item.space_count > 0)
    .map((item) => ({
      vehicle_category_id: item.vehicle_category_id,
      space_count: item.space_count,
      price_per_minute: item.price_per_minute,
      price_per_day: item.price_per_day,
      price_per_month: item.price_per_month,
    }));
}

function markerIcon(): L.DivIcon {
  return L.divIcon({
    className: "owner-map-marker",
    html: "<span></span>",
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
}

function MapCenter({ position }: { position: [number, number] }) {
  const map = useMap();
  const [latitude, longitude] = position;
  useEffect(() => {
    map.setView([latitude, longitude]);
  }, [map, latitude, longitude]);
  return null;
}

function MapClick({ onPick }: { onPick: (position: [number, number]) => void }) {
  useMapEvents({
    click(event) {
      onPick([event.latlng.lat, event.latlng.lng]);
    },
  });
  return null;
}

function LocationPicker({
  value,
  onChange,
  onPositionSelected,
}: {
  value: LocationValue;
  onChange: (value: LocationValue) => void;
  onPositionSelected?: () => void;
}) {
  const [search, setSearch] = useState(value.address);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const position: [number, number] = [value.latitude, value.longitude];

  async function searchAddress(event: FormEvent) {
    event.preventDefault();
    setSearching(true);
    setSearchError(null);
    try {
      const query = new URLSearchParams({
        format: "jsonv2",
        limit: "1",
        countrycodes: "co",
        q: search,
      });
      const response = await fetch(`https://nominatim.openstreetmap.org/search?${query}`);
      if (!response.ok) throw new Error("No se pudo buscar la dirección. Intenta de nuevo.");
      const results = (await response.json()) as { display_name: string; lat: string; lon: string }[];
      const result = results[0];
      if (!result) throw new Error("No se encontró la dirección. Marca el punto en el mapa.");
      const latitude = Number(result.lat);
      const longitude = Number(result.lon);
      if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
        throw new Error("El servicio devolvió coordenadas inválidas.");
      }
      onChange({
        address: result.display_name,
        latitude,
        longitude,
      });
      onPositionSelected?.();
      setSearch(result.display_name);
    } catch (error) {
      setSearchError(getErrorMessage(error));
    } finally {
      setSearching(false);
    }
  }

  function setPosition(next: [number, number]) {
    onChange({ ...value, latitude: next[0], longitude: next[1] });
    onPositionSelected?.();
  }

  return (
    <div className="owner-location">
      <label htmlFor="lot-address">Dirección</label>
      <div className="owner-address-search">
        <input
          id="lot-address"
          required
          minLength={3}
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
            onChange({ ...value, address: event.target.value });
          }}
        />
        <Button type="button" variant="secondary" loading={searching} onClick={searchAddress}>
          Buscar dirección
        </Button>
      </div>
      {searchError && <p className="owner-error" role="alert">{searchError}</p>}
      <p className="owner-hint">También puedes hacer clic en el mapa o arrastrar el marcador.</p>
      <p className="owner-hint">
        Búsqueda geográfica mediante{" "}
        <a href="https://nominatim.org/" target="_blank" rel="noreferrer">Nominatim</a>.
      </p>
      <div className="owner-map-frame">
        <MapContainer center={position} zoom={14} scrollWheelZoom className="owner-map">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapCenter position={position} />
          <MapClick onPick={setPosition} />
          <Marker
            position={position}
            draggable
            icon={markerIcon()}
            eventHandlers={{
              dragend(event) {
                const marker = event.target as L.Marker;
                const point = marker.getLatLng();
                setPosition([point.lat, point.lng]);
              },
            }}
          />
        </MapContainer>
      </div>
      <small>
        Coordenadas: {value.latitude.toFixed(5)}, {value.longitude.toFixed(5)} · Mapa © OpenStreetMap
      </small>
    </div>
  );
}

function ScheduleEditor({
  schedules,
  onChange,
}: {
  schedules: ParkingScheduleInput[];
  onChange: (schedules: ParkingScheduleInput[]) => void;
}) {
  function update(day: number, patch: Partial<ParkingScheduleInput>) {
    onChange(schedules.map((entry) => entry.day_of_week === day ? { ...entry, ...patch } : entry));
  }

  return (
    <div className="owner-schedule-list">
      {schedules.map((entry) => (
        <div className="owner-schedule-row" key={entry.day_of_week}>
          <strong>{WEEKDAYS[entry.day_of_week]}</strong>
          <label className="owner-check">
            <input
              type="checkbox"
              checked={entry.is_closed}
              onChange={(event) => update(entry.day_of_week, {
                is_closed: event.target.checked,
                is_24_hours: false,
                opens_at: event.target.checked ? null : "08:00:00",
                closes_at: event.target.checked ? null : "20:00:00",
              })}
            />
            Cerrado
          </label>
          <label className="owner-check">
            <input
              type="checkbox"
              checked={entry.is_24_hours}
              disabled={entry.is_closed}
              onChange={(event) => update(entry.day_of_week, {
                is_24_hours: event.target.checked,
                opens_at: event.target.checked ? null : "08:00:00",
                closes_at: event.target.checked ? null : "20:00:00",
              })}
            />
            24 horas
          </label>
          {!entry.is_closed && !entry.is_24_hours && (
            <div className="owner-time-range">
              <input
                type="time"
                required
                value={entry.opens_at?.slice(0, 5) ?? ""}
                onChange={(event) => update(entry.day_of_week, {
                  opens_at: event.target.value ? `${event.target.value}:00` : null,
                })}
                aria-label={`Apertura ${WEEKDAYS[entry.day_of_week]}`}
              />
              <span>a</span>
              <input
                type="time"
                required
                value={entry.closes_at?.slice(0, 5) ?? ""}
                onChange={(event) => update(entry.day_of_week, {
                  closes_at: event.target.value ? `${event.target.value}:00` : null,
                })}
                aria-label={`Cierre ${WEEKDAYS[entry.day_of_week]}`}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function InventoryEditor({
  items,
  onChange,
}: {
  items: InventoryDraft[];
  onChange: (items: InventoryDraft[]) => void;
}) {
  function update(categoryId: string, patch: Partial<InventoryDraft>) {
    onChange(items.map((item) => item.vehicle_category_id === categoryId
      ? { ...item, ...patch }
      : item));
  }

  return (
    <div className="owner-inventory-list">
      {items.map((item) => (
        <fieldset className="owner-inventory-item" key={item.vehicle_category_id}>
          <legend>{item.name}</legend>
          <label>
            Espacios
            <input
              type="number"
              min={item.isConfigured ? "1" : "0"}
              max="5000"
              value={item.space_count}
              onChange={(event) => update(item.vehicle_category_id, {
                space_count: Number(event.target.value),
              })}
            />
          </label>
          {item.space_count > 0 && (
            <>
              <label>
                Tarifa por minuto (COP)
                <input
                  type="number"
                  required
                  min="0.01"
                  step="0.01"
                  value={item.price_per_minute}
                  onChange={(event) => update(item.vehicle_category_id, {
                    price_per_minute: event.target.value,
                  })}
                />
              </label>
              <label>
                Tarifa diaria (opcional)
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={item.price_per_day ?? ""}
                  onChange={(event) => update(item.vehicle_category_id, {
                    price_per_day: event.target.value || null,
                  })}
                />
              </label>
              <label>
                Tarifa mensual (opcional)
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={item.price_per_month ?? ""}
                  onChange={(event) => update(item.vehicle_category_id, {
                    price_per_month: event.target.value || null,
                  })}
                />
              </label>
            </>
          )}
        </fieldset>
      ))}
    </div>
  );
}

function NewParkingLotForm({
  categories,
  onCreated,
  onCancel,
}: {
  categories: VehicleCategory[];
  onCreated: (lot: OwnerParkingLot) => void;
  onCancel: () => void;
}) {
  const [name, setName] = useState("");
  const [identification, setIdentification] = useState("");
  const [phone, setPhone] = useState("");
  const [locationConfirmed, setLocationConfirmed] = useState(false);
  const [location, setLocation] = useState<LocationValue>({
    address: "",
    latitude: BOGOTA[0],
    longitude: BOGOTA[1],
  });
  const [schedules, setSchedules] = useState(defaultSchedule);
  const [inventory, setInventory] = useState(() => defaultInventory(categories));
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    const selectedInventory = toInventoryInput(inventory);
    if (selectedInventory.length === 0) {
      setError("Asigna al menos un espacio a un tipo de vehículo.");
      return;
    }
    if (!locationConfirmed) {
      setError("Busca la dirección o marca y confirma el punto del parqueadero en el mapa.");
      return;
    }
    if (schedules.some((entry) =>
      !entry.is_closed && !entry.is_24_hours && entry.opens_at === entry.closes_at
    )) {
      setError("La apertura y el cierre de cada día deben ser diferentes.");
      return;
    }
    setSaving(true);
    try {
      const lot = await ownerApi.createParkingLot({
        name,
        identification,
        address: location.address,
        phone: phone || null,
        latitude: location.latitude,
        longitude: location.longitude,
        schedules,
        inventory: selectedInventory,
      });
      onCreated(lot);
    } catch (cause) {
      setError(getErrorMessage(cause));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card className="owner-form-card">
      <form className="owner-form" onSubmit={submit}>
        <div className="owner-form-heading">
          <div>
            <p className="owner-eyebrow">Nuevo parqueadero</p>
            <h2>Configura tu ubicación</h2>
          </div>
          <Button type="button" variant="ghost" onClick={onCancel}>Volver</Button>
        </div>
        <ol className="owner-hint">
          <li>Completa el nombre y la identificación del parqueadero.</li>
          <li>Busca la dirección o marca su ubicación en el mapa.</li>
          <li>Abre los días de atención y define el horario.</li>
          <li>Asigna espacios y tarifas por tipo de vehículo.</li>
        </ol>
        {error && <p className="owner-error" role="alert">{error}</p>}
        {categories.length === 0 && (
          <p className="owner-error" role="alert">
            No hay categorías de vehículos configuradas. No se pueden crear espacios hasta que
            administración inicialice el catálogo.
          </p>
        )}
        <div className="owner-fields-grid">
          <label>
            Nombre
            <input required minLength={2} maxLength={100} value={name} onChange={(event) => setName(event.target.value)} />
          </label>
          <label>
            NIT o identificación
            <input required maxLength={40} value={identification} onChange={(event) => setIdentification(event.target.value)} />
          </label>
          <label>
            Teléfono (opcional)
            <input maxLength={30} value={phone} onChange={(event) => setPhone(event.target.value)} />
          </label>
        </div>
        <LocationPicker
          value={location}
          onChange={setLocation}
          onPositionSelected={() => setLocationConfirmed(true)}
        />
        <section>
          <h3>Horario semanal</h3>
          <p className="owner-hint">
            Cada día inicia como cerrado. Desmarca los días de atención y elige su horario o activa
            la opción de 24 horas.
          </p>
          <ScheduleEditor schedules={schedules} onChange={setSchedules} />
        </section>
        <section>
          <h3>Espacios y tarifas por tipo</h3>
          <p className="owner-hint">
            Define cuántos espacios tendrá cada categoría y su tarifa. Esto crea los espacios del
            parqueadero; no necesitas registrar aquí los carros de tus clientes.
          </p>
          <InventoryEditor items={inventory} onChange={setInventory} />
        </section>
        <Button type="submit" loading={saving} disabled={categories.length === 0}>
          Crear parqueadero
        </Button>
      </form>
    </Card>
  );
}

function ExistingParkingLotForm({
  lot,
  categories,
  onUpdated,
}: {
  lot: OwnerParkingLot;
  categories: VehicleCategory[];
  onUpdated: (lot: OwnerParkingLot) => void;
}) {
  const [name, setName] = useState(lot.name);
  const [identification, setIdentification] = useState(lot.identification);
  const [phone, setPhone] = useState(lot.phone ?? "");
  const [active, setActive] = useState(lot.is_active);
  const [location, setLocation] = useState<LocationValue>({
    address: lot.address,
    latitude: lot.latitude ?? BOGOTA[0],
    longitude: lot.longitude ?? BOGOTA[1],
  });
  const [schedules, setSchedules] = useState(() => {
    const existing = new Map(lot.schedules.map((schedule) => [schedule.day_of_week, schedule]));
    return defaultSchedule().map((entry) => existing.get(entry.day_of_week) ?? entry);
  });
  const [inventory, setInventory] = useState(() => inventoryFromLot(categories, lot));
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<string | null>(null);

  async function saveProfile(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSaving("profile");
    try {
      onUpdated(await ownerApi.updateParkingLot(lot.id, {
        name,
        identification,
        phone: phone || null,
        address: location.address,
        latitude: location.latitude,
        longitude: location.longitude,
        is_active: active,
      }));
    } catch (cause) {
      setError(getErrorMessage(cause));
    } finally {
      setSaving(null);
    }
  }

  async function saveSchedule(event: FormEvent) {
    event.preventDefault();
    setError(null);
    if (schedules.some((entry) =>
      !entry.is_closed && !entry.is_24_hours && entry.opens_at === entry.closes_at
    )) {
      setError("La apertura y el cierre de cada día deben ser diferentes.");
      return;
    }
    setSaving("schedule");
    try {
      onUpdated(await ownerApi.updateSchedule(lot.id, schedules));
    } catch (cause) {
      setError(getErrorMessage(cause));
    } finally {
      setSaving(null);
    }
  }

  async function saveInventory(event: FormEvent) {
    event.preventDefault();
    setError(null);
    const selectedInventory = toInventoryInput(inventory);
    if (selectedInventory.length === 0) {
      setError("El parqueadero debe mantener al menos un tipo de espacio.");
      return;
    }
    setSaving("inventory");
    try {
      onUpdated(await ownerApi.updateInventory(lot.id, selectedInventory));
    } catch (cause) {
      setError(getErrorMessage(cause));
    } finally {
      setSaving(null);
    }
  }

  return (
    <div className="owner-configuration">
      {error && <p className="owner-error" role="alert">{error}</p>}
      <Card className="owner-form-card">
        <form className="owner-form" onSubmit={saveProfile}>
          <h2>Datos y ubicación</h2>
          <div className="owner-fields-grid">
            <label>
              Nombre
              <input required minLength={2} maxLength={100} value={name} onChange={(event) => setName(event.target.value)} />
            </label>
            <label>
              NIT o identificación
              <input required maxLength={40} value={identification} onChange={(event) => setIdentification(event.target.value)} />
            </label>
            <label>
              Teléfono
              <input maxLength={30} value={phone} onChange={(event) => setPhone(event.target.value)} />
            </label>
            <label className="owner-check owner-active-toggle">
              <input type="checkbox" checked={active} onChange={(event) => setActive(event.target.checked)} />
              Parqueadero activo y visible para clientes
            </label>
          </div>
          <LocationPicker value={location} onChange={setLocation} />
          <Button type="submit" loading={saving === "profile"}>Guardar datos</Button>
        </form>
      </Card>
      <Card className="owner-form-card">
        <form className="owner-form" onSubmit={saveSchedule}>
          <h2>Horario de atención</h2>
          <p className="owner-hint">
            {lot.schedule_configured
              ? "Los cambios no pueden dejar una reserva confirmada fuera del nuevo horario."
              : "Configura los siete días para habilitar las reservas de tus clientes."}
          </p>
          <ScheduleEditor schedules={schedules} onChange={setSchedules} />
          <Button type="submit" loading={saving === "schedule"}>Guardar horario</Button>
        </form>
      </Card>
      <Card className="owner-form-card">
        <form className="owner-form" onSubmit={saveInventory}>
          <h2>Espacios y tarifas</h2>
          <p className="owner-hint">
            No se pueden retirar espacios con reservas vigentes o vehículos dentro.
          </p>
          <InventoryEditor items={inventory} onChange={setInventory} />
          <Button type="submit" loading={saving === "inventory"}>Guardar espacios y tarifas</Button>
        </form>
      </Card>
    </div>
  );
}

export function OwnerDashboard() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [lots, setLots] = useState<OwnerParkingLot[]>([]);
  const [categories, setCategories] = useState<VehicleCategory[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<OwnerParkingLotDashboard | null>(null);
  const showCreate = searchParams.get("crear") === "1";
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([ownerApi.listParkingLots(), ownerApi.listVehicleCategories()])
      .then(([ownerLots, vehicleCategories]) => {
        if (!active) return;
        setLots(ownerLots);
        setCategories(vehicleCategories);
        setSelectedId(ownerLots[0]?.id ?? null);
      })
      .catch((cause) => {
        if (active) setError(getErrorMessage(cause));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, []);

  const selectedLot = lots.find((lot) => lot.id === selectedId) ?? null;

  useEffect(() => {
    if (!selectedId) {
      setDashboard(null);
      return;
    }
    let active = true;
    ownerApi.getDashboard(selectedId)
      .then((result) => {
        if (active) setDashboard(result);
      })
      .catch((cause) => {
        if (active) setError(getErrorMessage(cause));
      });
    return () => { active = false; };
  }, [selectedId, lots]);

  function updateLot(updated: OwnerParkingLot) {
    setLots((current) => current.map((lot) => lot.id === updated.id ? updated : lot));
  }

  function addLot(created: OwnerParkingLot) {
    setLots((current) => [...current, created].sort((a, b) => a.name.localeCompare(b.name)));
    setSelectedId(created.id);
    setSearchParams({}, { replace: true });
    setError(null);
  }

  function setCreateMode(enabled: boolean) {
    setSearchParams(enabled ? { crear: "1" } : {}, { replace: true });
    if (enabled) setError(null);
  }

  if (loading) return <div className="owner-page-loading">Cargando tus parqueaderos…</div>;

  return (
    <main className="owner-dashboard">
      <header className="owner-page-heading">
        <div>
          <p className="owner-eyebrow">Administración de propietario</p>
          <h1>Mis parqueaderos</h1>
          <p>Configura ubicaciones, horarios, espacios y tarifas de forma independiente.</p>
        </div>
        <Button onClick={() => setCreateMode(true)}>
          Crear parqueadero
        </Button>
      </header>
      {error && <p className="owner-error" role="alert">{error}</p>}
      {showCreate ? (
        <NewParkingLotForm
          categories={categories}
          onCreated={addLot}
          onCancel={() => setCreateMode(false)}
        />
      ) : (
        <div className="owner-dashboard-grid">
          <aside className="owner-lot-list" aria-label="Tus parqueaderos">
            {lots.length === 0 ? (
              <Card>
                <p>Aún no has creado parqueaderos.</p>
                <Button onClick={() => setCreateMode(true)}>Crear el primero</Button>
              </Card>
            ) : lots.map((lot) => (
              <button
                className={`owner-lot-choice${lot.id === selectedId ? " is-selected" : ""}`}
                key={lot.id}
                onClick={() => { setSelectedId(lot.id); setError(null); }}
              >
                <strong>{lot.name}</strong>
                <span>{lot.address}</span>
                <small>{lot.total_capacity} espacios · {lot.is_active ? "Activo" : "Inactivo"}</small>
              </button>
            ))}
          </aside>
          {selectedLot ? (
            <section className="owner-selected-lot">
              <div className="owner-selected-heading">
                <div>
                  <h2>{selectedLot.name}</h2>
                  <p>{selectedLot.schedule_configured ? "Horario configurado" : "Falta configurar el horario"}</p>
                </div>
                {!selectedLot.schedule_configured && <span className="owner-status-warning">Reservas deshabilitadas</span>}
              </div>
              <div className="owner-stat-grid">
                <Card><strong>{dashboard?.reservation_count ?? "—"}</strong><span>Reservas de hoy</span></Card>
                <Card><strong>{selectedLot.total_capacity}</strong><span>Espacios totales</span></Card>
                <Card><strong>{formatCurrency(Number(dashboard?.income_today ?? 0))}</strong><span>Ingresos de hoy</span></Card>
              </div>
              <Card className="owner-breakdown">
                <h3>Ocupación actual por tipo de vehículo</h3>
                {dashboard?.occupancy_by_vehicle_type.length ? (
                  <ul>
                    {dashboard.occupancy_by_vehicle_type.map((item) => (
                      <li key={item.vehicle_type}>
                        <span>{VEHICLE_LABELS[item.vehicle_type] ?? item.vehicle_type}</span>
                        <strong>{item.count}</strong>
                      </li>
                    ))}
                  </ul>
                ) : <p>No hay vehículos actualmente en el parqueadero.</p>}
              </Card>
              <Card className="owner-breakdown">
                <h3>Reservas de hoy</h3>
                {dashboard?.daily_reservations.length ? (
                  <div className="owner-reservation-list">
                    {dashboard.daily_reservations.map((reservation) => (
                      <div className="owner-reservation-row" key={reservation.id}>
                        <strong>{reservation.plate ?? "Vehículo sin placa"}</strong>
                        <span>{VEHICLE_LABELS[reservation.vehicle_type] ?? reservation.vehicle_type}</span>
                        <span>Espacio {reservation.spot_code}</span>
                        <time>
                          {new Date(reservation.start_time).toLocaleTimeString("es-CO", {
                            hour: "2-digit",
                            minute: "2-digit",
                            timeZone: "America/Bogota",
                          })}
                          {" – "}
                          {new Date(reservation.end_time).toLocaleTimeString("es-CO", {
                            hour: "2-digit",
                            minute: "2-digit",
                            timeZone: "America/Bogota",
                          })}
                        </time>
                      </div>
                    ))}
                  </div>
                ) : <p>No hay reservas para hoy.</p>}
              </Card>
              <ExistingParkingLotForm
                key={selectedLot.id}
                lot={selectedLot}
                categories={categories}
                onUpdated={updateLot}
              />
            </section>
          ) : !showCreate && lots.length === 0 ? null : (
            <Card><p>Selecciona un parqueadero para ver su panel.</p></Card>
          )}
        </div>
      )}
    </main>
  );
}
