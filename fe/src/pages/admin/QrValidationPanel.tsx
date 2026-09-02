/** QrValidationPanel.tsx — RF-015: el operario valida el token QR mostrado por el cliente. */
import { useState, type FormEvent } from "react";
import * as paymentsApi from "../../api/payments";
import type { QRValidation } from "../../api/types";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../api/errors";
import { formatCurrency } from "../../utils/formatCurrency";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";

export function QrValidationPanel({ onChange }: { onChange: () => void }) {
  const toast = useToast();
  const [token, setToken] = useState("");
  const [validated, setValidated] = useState<QRValidation | null>(null);
  const [loading, setLoading] = useState(false);
  const [charging, setCharging] = useState(false);

  async function handleValidate(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const result = await paymentsApi.validateQr(token);
      setValidated(result);
    } catch (err) {
      toast.error(getErrorMessage(err));
      setValidated(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleCharge() {
    if (!validated) return;
    setCharging(true);
    try {
      await paymentsApi.chargeAfterQr(validated.session_id);
      toast.success(`Cobro procesado para ${validated.plate} — espacio liberado`);
      setValidated(null);
      setToken("");
      onChange();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setCharging(false);
    }
  }

  return (
    <Card>
      <h3 style={{ marginBottom: "0.8rem" }}>Validar código QR</h3>
      <form className="inline-form" onSubmit={handleValidate}>
        <div className="form-field" style={{ flex: 1 }}>
          <label htmlFor="qr-token">Token del QR escaneado</label>
          <input id="qr-token" required value={token} onChange={(e) => setToken(e.target.value)} placeholder="Pega o escanea el token" />
        </div>
        <Button type="submit" loading={loading}>
          Validar
        </Button>
      </form>

      {validated && (
        <div style={{ marginTop: "1rem", textAlign: "center" }}>
          <p>
            {validated.plate} ({validated.vehicle_type})
          </p>
          <div className="session-amount">{formatCurrency(Number(validated.amount))}</div>
          <Button onClick={handleCharge} loading={charging}>
            Confirmar cobro y salida
          </Button>
        </div>
      )}
    </Card>
  );
}
