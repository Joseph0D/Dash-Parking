/** LandingPage.tsx — adaptado de index.html (hero + valor + tarifas vigentes de RF-007). */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as parkingApi from "../api/parking";
import type { Rate } from "../api/types";
import { VEHICLE_TYPE_ICON, VEHICLE_TYPE_LABEL } from "../hooks/useVehicleLabels";
import { formatCurrency } from "../utils/formatCurrency";
import { Card } from "../components/ui/Card";
import "./LandingPage.css";

export function LandingPage() {
  const [rates, setRates] = useState<Rate[]>([]);

  useEffect(() => {
    parkingApi.listRates().then(setRates).catch(() => setRates([]));
  }, []);

  return (
    <>
      <section className="hero-container">
        <div className="hero-content">
          <h1>
            Parquea sin filas en <span>Dash Parking</span>
          </h1>
          <p>
            Reserva tu espacio, controla tu tiempo y paga desde el celular — sin efectivo,
            sin esperar en la talanquera.
          </p>
          <div className="hero-actions">
            <Link to="/registro" className="btn btn--primary">
              Crear cuenta
            </Link>
            <Link to="/espacios" className="btn btn--ghost" style={{ color: "#fff", borderColor: "#475569" }}>
              Ver disponibilidad
            </Link>
          </div>
        </div>
      </section>

      <section className="features-section">
        <Card className="feature-card">
          <h3>📅 Reserva con anticipación</h3>
          <p>Elige el vehículo y cuánto tiempo lo vas a ocupar — el espacio queda asegurado antes de que llegues.</p>
        </Card>
        <Card className="feature-card">
          <h3>💳 Pago virtual o QR</h3>
          <p>Sal del parqueadero sin efectivo: paga desde la app o muestra tu código QR en la talanquera.</p>
        </Card>
        <Card className="feature-card">
          <h3>🕓 Cobro justo por tiempo</h3>
          <p>El sistema calcula automáticamente tu tiempo de permanencia y el valor exacto a pagar.</p>
        </Card>
      </section>

      {rates.length > 0 && (
        <section className="rates-section">
          <h2>Tarifas vigentes</h2>
          <div className="rates-grid">
            {rates.map((rate) => (
              <Card key={rate.id} className="rate-card">
                <div style={{ fontSize: "1.8rem" }}>{VEHICLE_TYPE_ICON[rate.vehicle_type]}</div>
                <div className="rate-value">{formatCurrency(Number(rate.price_per_hour))}</div>
                <div className="rate-label">{VEHICLE_TYPE_LABEL[rate.vehicle_type]} / hora</div>
              </Card>
            ))}
          </div>
        </section>
      )}
    </>
  );
}
