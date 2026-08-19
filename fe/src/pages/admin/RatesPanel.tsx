/** RatesPanel.tsx — RF-007: administración de tarifas por tipo de vehículo. */
import { useEffect, useState } from "react";
import * as parkingApi from "../../api/parking";
import type { Rate, VehicleType } from "../../api/types";
import { VEHICLE_TYPE_LABEL } from "../../hooks/useVehicleLabels";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../api/errors";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";

const TYPES: VehicleType[] = ["car", "motorcycle", "bicycle"];

export function RatesPanel() {
  const toast = useToast();
  const [rates, setRates] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState<VehicleType | null>(null);

  async function load() {
    const list: Rate[] = await parkingApi.listRates();
    const map: Record<string, string> = {};
    list.forEach((r) => (map[r.vehicle_type] = r.price_per_hour));
    setRates(map);
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSave(vehicleType: VehicleType) {
    const value = Number(rates[vehicleType]);
    if (!value || value <= 0) {
      toast.error("La tarifa debe ser un valor mayor a cero");
      return;
    }
    setSaving(vehicleType);
    try {
      await parkingApi.upsertRate(vehicleType, value);
      toast.success(`Tarifa de ${VEHICLE_TYPE_LABEL[vehicleType]} actualizada`);
      await load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setSaving(null);
    }
  }

  return (
    <Card>
      <h3 style={{ marginBottom: "1rem" }}>Tarifas por hora</h3>
      <div style={{ display: "grid", gap: "0.9rem" }}>
        {TYPES.map((type) => (
          <div key={type} className="inline-form" style={{ marginBottom: 0 }}>
            <div className="form-field" style={{ flex: 1 }}>
              <label>{VEHICLE_TYPE_LABEL[type]}</label>
              <input
                type="number"
                min={1}
                step="0.01"
                value={rates[type] ?? ""}
                onChange={(e) => setRates((prev) => ({ ...prev, [type]: e.target.value }))}
              />
            </div>
            <Button variant="secondary" onClick={() => handleSave(type)} loading={saving === type}>
              Guardar
            </Button>
          </div>
        ))}
      </div>
    </Card>
  );
}
