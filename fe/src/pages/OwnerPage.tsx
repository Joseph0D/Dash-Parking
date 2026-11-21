/**
 * OwnerPage.tsx
 * Qué: panel del dueño (o administrador) del parqueadero: reservas vigentes, registro de
 *      ingreso y vehículos que están adentro con su registro de salida.
 * Para qué: cerrar el ciclo del espacio del informe: Reservado → Ocupado (ingreso) →
 *           Disponible (salida).
 * Impacto: el backend valida que el parqueadero sea del dueño (403 si no). Aquí solo se oculta
 *          el panel a quien no tiene el rol.
 */
import { useCallback, useEffect, useState } from "react";
import { getErrorMessage } from "../api/errors";
import * as reservasApi from "../api/reservas";
import type { ActiveTicket, ReservationDetail } from "../api/types";
import { AccountForm } from "../components/booking/AccountForm";
import { paymentLabel } from "../components/booking/paymentMethods";
import { RESERVATION_STATUS_LABEL } from "../components/booking/reservationStatus";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { useAccount } from "../context/AccountContext";
import { useToast } from "../context/ToastContext";
import { formatCurrency } from "../utils/formatCurrency";
import { formatDateTime } from "../utils/timeWindow";
import "./SpotsPage.css";
import "../components/booking/booking.css";

export function OwnerPage() {
  const { account, token, loading, logout } = useAccount();
  const toast = useToast();
  const [reservations, setReservations] = useState<ReservationDetail[]>([]);
  const [tickets, setTickets] = useState<ActiveTicket[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const isManager = account?.role === "dueno" || account?.role === "administrador";

  const load = useCallback(async () => {
    if (!token || !isManager) return;
    try {
      const [res, tix] = await Promise.all([
        reservasApi.listManagedReservations(token),
        reservasApi.listActiveTickets(token),
      ]);
      setReservations(res);
      setTickets(tix);
      setError(null);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }, [token, isManager]);

  useEffect(() => {
    void load();
  }, [load]);

  async function run(key: string, action: () => Promise<unknown>, okMessage: string) {
    setBusyId(key);
    try {
      await action();
      toast.success(okMessage);
      await load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className="espacios-section">
      <div className="section-header">
        <h2>Panel del dueño</h2>
        <p>Registra el ingreso y la salida de los vehículos con reserva</p>
      </div>

      {loading ? (
        <p className="availability-loading">Verificando sesión...</p>
      ) : !account ? (
        <Card className="owner-login">
          <h3>Ingresa con tu cuenta de dueño</h3>
          <AccountForm allowRegister={false} />
        </Card>
      ) : !isManager ? (
        <Card className="owner-login">
          <p>Tu cuenta ({account.email}) no tiene permisos de dueño o administrador.</p>
          <Button variant="ghost" onClick={logout}>Cambiar de cuenta</Button>
        </Card>
      ) : (
        <>
          <div className="session-bar">
            <span>
              {account.first_name} {account.last_name} ({account.role})
            </span>
            <button type="button" className="booking-link" onClick={() => void load()}>
              Actualizar
            </button>
            <button type="button" className="booking-link" onClick={logout}>
              Salir
            </button>
          </div>
          {error && <div className="form-error">{error}</div>}

          <div className="owner-section">
            <h3>Reservas vigentes</h3>
            {reservations.length === 0 ? (
              <p className="booking-empty">No hay reservas vigentes.</p>
            ) : (
              <div className="owner-table-wrap">
                <table className="owner-table">
                  <thead>
                    <tr>
                      <th>Espacio</th><th>Placa</th><th>Cliente</th><th>Desde</th><th>Hasta</th>
                      <th>Pago</th><th>Estado</th><th />
                    </tr>
                  </thead>
                  <tbody>
                    {reservations.map((item) => (
                      <tr key={item.id_reserva}>
                        <td>{item.numero_espacio}</td>
                        <td>{item.placa}</td>
                        <td>{item.cliente}</td>
                        <td>{formatDateTime(item.fecha_inicio)}</td>
                        <td>{formatDateTime(item.fecha_fin)}</td>
                        <td>
                          {paymentLabel(item.metodo_pago)} · {formatCurrency(Number(item.monto_total ?? 0))}
                        </td>
                        <td>
                          <span className={`status-badge status-badge--${item.estado_reserva.replace(" ", "-")}`}>
                            {RESERVATION_STATUS_LABEL[item.estado_reserva]}
                          </span>
                        </td>
                        <td>
                          {item.estado_reserva === "activa" && (
                            <Button
                              loading={busyId === `in-${item.id_reserva}`}
                              onClick={() =>
                                run(
                                  `in-${item.id_reserva}`,
                                  () => reservasApi.registerEntry(token!, item.id_reserva),
                                  `Ingreso registrado: ${item.numero_espacio} ocupado`,
                                )
                              }
                            >
                              Registrar ingreso
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="owner-section">
            <h3>Vehículos dentro del parqueadero</h3>
            {tickets.length === 0 ? (
              <p className="booking-empty">No hay vehículos adentro.</p>
            ) : (
              <div className="owner-table-wrap">
                <table className="owner-table">
                  <thead>
                    <tr>
                      <th>Espacio</th><th>Placa</th><th>Tipo</th><th>Ingresó</th><th>Ticket</th><th />
                    </tr>
                  </thead>
                  <tbody>
                    {tickets.map((ticket) => (
                      <tr key={ticket.id_ticket}>
                        <td>{ticket.numero_espacio} · {ticket.zona}</td>
                        <td>{ticket.placa}</td>
                        <td>{ticket.tipo_vehiculo}</td>
                        <td>{formatDateTime(ticket.fecha_ingreso)}</td>
                        <td>{ticket.estado_ticket}</td>
                        <td>
                          <Button
                            variant="secondary"
                            loading={busyId === `out-${ticket.id_ticket}`}
                            onClick={() =>
                              run(
                                `out-${ticket.id_ticket}`,
                                () => reservasApi.registerExit(token!, ticket.id_ticket),
                                `Salida registrada: ${ticket.numero_espacio} disponible`,
                              )
                            }
                          >
                            Registrar salida
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </section>
  );
}
