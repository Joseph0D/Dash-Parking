/** VehiclesPanel.tsx — RF-001 (base) / gestión de vehículos propios del cliente. */
import { useEffect, useState, type FormEvent } from "react";
import * as vehiclesApi from "../../api/vehicles";
import type { Vehicle, VehicleQRPass, VehicleType } from "../../api/types";
import { VEHICLE_TYPE_ICON, VEHICLE_TYPE_LABEL } from "../../hooks/useVehicleLabels";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../api/errors";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";

export function VehiclesPanel({ onChange }: { onChange?: () => void }) {
  const toast = useToast();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [plate, setPlate] = useState("");
  const [vehicleType, setVehicleType] = useState<VehicleType>("car");
  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [color, setColor] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [vehicleQr, setVehicleQr] = useState<VehicleQRPass | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    const list = await vehiclesApi.listMyVehicles();
    setVehicles(list);
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      if (editingId) {
        await vehiclesApi.updateVehicle(editingId, plate, vehicleType, brand, model, color);
        toast.success("Vehículo actualizado");
      } else {
        await vehiclesApi.registerVehicle(plate, vehicleType, brand, model, color);
        toast.success(`Vehículo ${plate ? plate.toUpperCase() : "registrado"} registrado`);
      }
      setPlate("");
      setBrand("");
      setModel("");
      setColor("");
      setEditingId(null);
      await load();
      onChange?.();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(vehicleId: string, plateLabel: string | null) {
    try {
      await vehiclesApi.deleteVehicle(vehicleId);
      toast.success(`Vehículo ${plateLabel ?? "sin placa"} eliminado`);
      await load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  function startEdit(vehicle: Vehicle) {
    setEditingId(vehicle.id);
    setPlate(vehicle.plate ?? "");
    setVehicleType(vehicle.vehicle_type);
    setBrand(vehicle.brand ?? "");
    setModel(vehicle.model ?? "");
    setColor(vehicle.color ?? "");
  }

  function cancelEdit() {
    setEditingId(null);
    setPlate("");
    setBrand("");
    setModel("");
    setColor("");
  }

  async function handleGenerateVehicleQr(vehicleId: string) {
    try {
      const pass = await vehiclesApi.getVehicleQr(vehicleId);
      setVehicleQr(pass);
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  return (
    <div>
      <Card style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ marginBottom: "0.8rem" }}>{editingId ? "Editar vehículo" : "Registrar vehículo"}</h3>
        <form className="inline-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="plate">Placa</label>
            <input
              id="plate"
              required={vehicleType !== "bicycle" && vehicleType !== "scooter"}
              value={plate}
              onChange={(e) => setPlate(e.target.value)}
              placeholder="ABC123"
            />
          </div>
          <div className="form-field">
            <label htmlFor="vehicle_type">Tipo</label>
            <select id="vehicle_type" value={vehicleType} onChange={(e) => setVehicleType(e.target.value as VehicleType)}>
              <option value="car">Carro</option>
              <option value="motorcycle">Moto</option>
              <option value="bicycle">Bicicleta</option>
              <option value="electric_motorcycle">Moto eléctrica</option>
              <option value="scooter">Patineta</option>
              <option value="truck">Camión</option>
            </select>
          </div>
          <div className="form-field">
            <label htmlFor="brand">Marca</label>
            <input id="brand" required value={brand} onChange={(e) => setBrand(e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="model">Modelo</label>
            <input id="model" required value={model} onChange={(e) => setModel(e.target.value)} />
          </div>
          <div className="form-field">
            <label htmlFor="color">Color</label>
            <input id="color" required value={color} onChange={(e) => setColor(e.target.value)} />
          </div>
          <Button type="submit" loading={loading}>
            {editingId ? "Guardar" : "Agregar"}
          </Button>
          {editingId && (
            <Button type="button" variant="ghost" onClick={cancelEdit}>
              Cancelar
            </Button>
          )}
        </form>
      </Card>

      {vehicles.length === 0 ? (
        <div className="empty-state">Todavía no tienes vehículos registrados.</div>
      ) : (
        <>
        {vehicleQr && (
          <Card style={{ marginBottom: "1.5rem", textAlign: "center" }}>
            <h3>QR permanente — {vehicleQr.plate || "Vehículo sin placa"}</h3>
            <img
              src={`data:image/png;base64,${vehicleQr.qr_image_base64}`}
              alt="Código QR permanente del vehículo"
              style={{ maxWidth: "240px", margin: "1rem auto" }}
            />
            <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem" }}>
              Este código identifica únicamente tu vehículo. El operario puede usarlo para el ingreso.
            </p>
            <Button variant="ghost" onClick={() => setVehicleQr(null)}>Cerrar</Button>
          </Card>
        )}
        <div className="entity-list">
          {vehicles.map((vehicle) => (
            <div className="entity-row" key={vehicle.id}>
              <div>
                <div className="entity-main">
                  {VEHICLE_TYPE_ICON[vehicle.vehicle_type]} {vehicle.plate || "Sin placa"}
                </div>
                <div className="entity-sub">
                  {VEHICLE_TYPE_LABEL[vehicle.vehicle_type]} · {vehicle.brand} {vehicle.model} · {vehicle.color}
                </div>
              </div>
              <div className="entity-actions">
                <Button variant="ghost" onClick={() => startEdit(vehicle)}>
                  Editar
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => handleGenerateVehicleQr(vehicle.id)}
                >
                  QR permanente
                </Button>
                <Button variant="danger" onClick={() => handleDelete(vehicle.id, vehicle.plate)}>
                  Eliminar
                </Button>
              </div>
            </div>
          ))}
        </div>
        </>
      )}
    </div>
  );
}
