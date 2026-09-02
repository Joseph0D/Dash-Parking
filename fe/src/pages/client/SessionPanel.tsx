/**
 * SessionPanel.tsx
 * Qué: muestra la sesión activa del cliente (si tiene un vehículo dentro) con el tiempo
 *      transcurrido y el monto estimado en vivo, y ofrece pagar virtual o generar el QR
 *      (RF-005 cálculo, RF-014 pago virtual, RF-015 pase QR).
 */
import { useCallback, useEffect, useState } from "react";
import * as sessionsApi from "../../api/sessions";
import * as paymentsApi from "../../api/payments";
import type { QRPass, SessionDetail } from "../../api/types";
import { VEHICLE_TYPE_ICON } from "../../hooks/useVehicleLabels";
import { useToast } from "../../context/ToastContext";
import { getErrorMessage } from "../../api/errors";
import { formatCurrency } from "../../utils/formatCurrency";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";

function formatElapsed(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export function SessionPanel() {
  const toast = useToast();
  const [session, setSession] = useState<SessionDetail | null | undefined>(undefined);
  const [elapsed, setElapsed] = useState(0);
  const [paying, setPaying] = useState(false);
  const [qr, setQr] = useState<QRPass | null>(null);

  const load = useCallback(async () => {
    const active = await sessionsApi.myActiveSession();
    setSession(active);
    setElapsed(active?.elapsed_seconds ?? 0);
    if (!active) setQr(null);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!session) return;
    const timer = setInterval(() => setElapsed((prev) => prev + 1), 1000);
    return () => clearInterval(timer);
  }, [session]);

  async function handlePayVirtual() {
    if (!session) return;
    setPaying(true);
    try {
      await paymentsApi.payVirtual(session.id);
      toast.success("Pago virtual aprobado — espacio liberado");
      await load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setPaying(false);
    }
  }

  async function handleGenerateQr() {
    if (!session) return;
    try {
      const pass = await paymentsApi.getQrPass(session.id);
      setQr(pass);
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  if (session === undefined) return <div className="page-loading">Cargando...</div>;

  if (session === null) {
    return <div className="empty-state">No tienes una sesión activa. Ingresa al parqueadero para ver tu tiempo y valor a pagar aquí.</div>;
  }

  // RN-010: se cobra por hora completa (mínimo 1). Derivamos la tarifa/hora del monto estimado
  // inicial para poder mostrar el valor en vivo sin exponer un endpoint aparte solo para eso.
  const initialHoursBilled = Math.max(1, Math.ceil(session.elapsed_seconds / 3600));
  const pricePerHour = Number(session.estimated_amount) / initialHoursBilled;
  const hoursBilledNow = Math.max(1, Math.ceil(elapsed / 3600));
  const liveAmount = Math.round(hoursBilledNow * pricePerHour);

  return (
    <Card>
      <h3>
        {VEHICLE_TYPE_ICON[session.vehicle_type]} {session.plate} — Espacio {session.spot_code}
      </h3>
      <p style={{ color: "var(--color-text-muted)", marginTop: "0.3rem" }}>
        Ingreso: {new Date(session.entry_time).toLocaleString("es-CO")}
      </p>

      <div style={{ textAlign: "center", margin: "1.5rem 0" }}>
        <div style={{ fontSize: "0.85rem", color: "var(--color-text-muted)", textTransform: "uppercase" }}>
          Tiempo transcurrido
        </div>
        <div style={{ fontSize: "2rem", fontWeight: 700, color: "var(--color-text-strong)" }}>
          {formatElapsed(elapsed)}
        </div>
        <div className="session-amount">{formatCurrency(liveAmount)}</div>
        <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>Valor estimado a pagar</div>
      </div>

      <div style={{ display: "flex", gap: "0.8rem", flexWrap: "wrap", justifyContent: "center" }}>
        <Button onClick={handlePayVirtual} loading={paying}>
          💳 Pagar virtual
        </Button>
        <Button variant="secondary" onClick={handleGenerateQr}>
          🔲 Generar QR para pagar en talanquera
        </Button>
      </div>

      {qr && (
        <div className="qr-box">
          <img src={`data:image/png;base64,${qr.qr_image_base64}`} alt="Código QR de tu sesión de parqueo" />
          <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem", marginTop: "0.5rem" }}>
            Muestra este código al operario en la salida (CA-015.1).
          </p>
        </div>
      )}
    </Card>
  );
}
