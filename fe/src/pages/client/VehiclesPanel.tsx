/** VehiclesPanel.tsx — RF-001 (base) / gestión de vehículos propios del cliente. */
import { useEffect, useState, type FormEvent } from "react";
import * as vehiclesApi from "../../api/vehicles";
import type { Vehicle, VehicleType } from "../../api/types";
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
      await vehiclesApi.registerVehicle(plate, vehicleType);
      setPlate("");
      toast.success(`Vehículo ${plate.toUpperCase()} registrado`);
      await load();
      onChange?.();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(vehicleId: string, plateLabel: string) {
    try {
      await vehiclesApi.deleteVehicle(vehicleId);
      toast.success(`Vehículo ${plateLabel} eliminado`);
      await load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  return (
    <div>
      <Card style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ marginBottom: "0.8rem" }}>Registrar vehículo</h3>
        <form className="inline-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="plate">Placa</label>
            <input id="plate" required value={plate} onChange={(e) => setPlate(e.target.value)} placeholder="ABC123" />
          </div>
          <div className="form-field">
            <label htmlFor="vehicle_type">Tipo</label>
            <select id="vehicle_type" value={vehicleType} onChange={(e) => setVehicleType(e.target.value as VehicleType)}>
              <option value="car">Carro</option>
              <option value="motorcycle">Moto</option>
              <option value="bicycle">Bicicleta</option>
            </select>
          </div>
          <Button type="submit" loading={loading}>
            Agregar
          </Button>
        </form>
      </Card>

      {vehicles.length === 0 ? (
        <div className="empty-state">Todavía no tienes vehículos registrados.</div>
      ) : (
        <div className="entity-list">
          {vehicles.map((vehicle) => (
            <div className="entity-row" key={vehicle.id}>
              <div>
                <div className="entity-main">
                  {VEHICLE_TYPE_ICON[vehicle.vehicle_type]} {vehicle.plate}
                </div>
                <div className="entity-sub">{VEHICLE_TYPE_LABEL[vehicle.vehicle_type]}</div>
              </div>
              <div className="entity-actions">
                <Button variant="danger" onClick={() => handleDelete(vehicle.id, vehicle.plate)}>
                  Eliminar
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
