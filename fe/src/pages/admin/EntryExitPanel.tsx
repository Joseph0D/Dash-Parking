/** EntryExitPanel.tsx — RF-001 (entrada) y RF-004/RF-006 (salida + cobro) desde el mostrador. */
import { useState, type FormEvent } from "react";
import * as sessionsApi from "../../api/sessions";
import * as paymentsApi from "../../api/payments";
import type { SessionDetail, VehicleType } from "../../api/types";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../api/errors";
import { formatCurrency } from "../../utils/formatCurrency";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";

export function EntryExitPanel({ onChange }: { onChange: () => void }) {
  const toast = useToast();
  const [entryPlate, setEntryPlate] = useState("");
  const [entryType, setEntryType] = useState<VehicleType>("car");
  const [entryLoading, setEntryLoading] = useState(false);

  const [exitPlate, setExitPlate] = useState("");
  const [exitSession, setExitSession] = useState<SessionDetail | null>(null);
  const [exitLoading, setExitLoading] = useState(false);
  const [charging, setCharging] = useState(false);

  async function handleEntry(event: FormEvent) {
    event.preventDefault();
    setEntryLoading(true);
    try {
      const session = await sessionsApi.registerEntry(entryPlate, entryType);
      toast.success(`Vehículo ${session.plate} ingresado en el espacio ${session.spot_code}`);
      setEntryPlate("");
      onChange();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setEntryLoading(false);
    }
  }

  async function handleSearchExit(event: FormEvent) {
    event.preventDefault();
    setExitLoading(true);
    setExitSession(null);
    try {
      const session = await sessionsApi.getSessionByPlate(exitPlate);
      setExitSession(session);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setExitLoading(false);
    }
  }

  async function handleChargeCash() {
    if (!exitSession) return;
    setCharging(true);
    try {
      await paymentsApi.payCash(exitSession.id);
      toast.success(`Cobro procesado — espacio ${exitSession.spot_code} liberado`);
      setExitSession(null);
      setExitPlate("");
      onChange();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setCharging(false);
    }
  }

  return (
    <div style={{ display: "grid", gap: "1.5rem", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))" }}>
      <Card>
        <h3 style={{ marginBottom: "0.8rem" }}>Registrar entrada</h3>
        <form className="inline-form" onSubmit={handleEntry} style={{ flexDirection: "column", alignItems: "stretch" }}>
          <div className="form-field">
            <label htmlFor="entry-plate">Placa</label>
            <input id="entry-plate" required value={entryPlate} onChange={(e) => setEntryPlate(e.target.value)} placeholder="ABC123" />
          </div>
          <div className="form-field">
            <label htmlFor="entry-type">Tipo de vehículo</label>
            <select id="entry-type" value={entryType} onChange={(e) => setEntryType(e.target.value as VehicleType)}>
              <option value="car">Carro</option>
              <option value="motorcycle">Moto</option>
              <option value="bicycle">Bicicleta</option>
            </select>
          </div>
          <Button type="submit" loading={entryLoading}>
            Registrar ingreso
          </Button>
        </form>
      </Card>

      <Card>
        <h3 style={{ marginBottom: "0.8rem" }}>Registrar salida y cobrar</h3>
        <form className="inline-form" onSubmit={handleSearchExit} style={{ flexDirection: "column", alignItems: "stretch" }}>
          <div className="form-field">
            <label htmlFor="exit-plate">Placa</label>
            <input id="exit-plate" required value={exitPlate} onChange={(e) => setExitPlate(e.target.value)} placeholder="ABC123" />
          </div>
          <Button type="submit" variant="secondary" loading={exitLoading}>
            Buscar
          </Button>
        </form>

        {exitSession && (
          <div style={{ marginTop: "1rem", textAlign: "center" }}>
            <p>
              Espacio {exitSession.spot_code} — desde {new Date(exitSession.entry_time).toLocaleTimeString("es-CO")}
            </p>
            <div className="session-amount">{formatCurrency(Number(exitSession.estimated_amount))}</div>
            <Button variant="primary" onClick={handleChargeCash} loading={charging}>
              Confirmar cobro y salida
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}
