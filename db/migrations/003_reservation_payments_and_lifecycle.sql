-- =============================================================================
-- Dash Parking - Migración 003: pago de reservas y ciclo de vida del espacio
-- Requiere la 001 y la 002. Ciclo: Disponible -> Reservado -> Ocupado -> Disponible.
--   1. Estado de pago 'Reembolsado' (devolución simulada al cancelar)
--   2. La reserva se cierra al SALIR el vehículo (antes se cerraba al entrar)
--   3. Vista de detalle de reservas (resumen para el cliente y el dueño)
--   4. fn_cancelar_reserva / fn_registrar_ingreso / fn_registrar_salida
-- Ejecutar UNA sola vez:  psql -d dash_parking_v2 -f 003_reservation_payments_and_lifecycle.sql
-- =============================================================================
BEGIN;

-- 1. Devolución simulada
ALTER TABLE pago DROP CONSTRAINT pago_estado_pago_check;
ALTER TABLE pago ADD  CONSTRAINT pago_estado_pago_check
  CHECK (estado_pago IN ('Pendiente', 'Aprobado', 'Rechazado', 'Reembolsado'));

-- 2. La reserva pasa a 'finalizada' cuando el vehículo SALE, no cuando entra.
--    Si se cerrara al entrar, el resto de su franja quedaría libre aunque el carro siga
--    adentro y otro cliente podría reservar ese mismo espacio.
DROP TRIGGER trg_finalizar_reserva ON ticket;
CREATE OR REPLACE FUNCTION fn_finalizar_reserva_al_salir() RETURNS trigger AS $$
BEGIN
  UPDATE reserva SET estado_reserva = 'finalizada'
  WHERE id_reserva = NEW.id_reserva AND estado_reserva = 'activa';
  RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_finalizar_reserva_al_salir
AFTER UPDATE OF fecha_hora_salida ON ticket
FOR EACH ROW WHEN (OLD.fecha_hora_salida IS NULL AND NEW.fecha_hora_salida IS NOT NULL
                   AND NEW.id_reserva IS NOT NULL)
EXECUTE FUNCTION fn_finalizar_reserva_al_salir();

-- 3. Detalle de cada reserva con su espacio, vehículo, ticket, pago y comprobante.
--    estado_visible resume en qué punto del ciclo está (lo que ve el usuario).
CREATE VIEW vw_reservas_detalle AS
SELECT r.id_reserva, r.id_usuario, u.nombres, u.apellidos,
       r.id_estacionamiento, est.nombre_parqueadero,
       r.id_espacio, e.numero_de_espacio, z.nombre_zona,
       r.id_vehiculo, v.placa, v.id_tipo_vehiculo, tv.nombre_tipo AS tipo_vehiculo,
       r.fecha_reserva AS fecha_inicio, r.fecha_hora_fin AS fecha_fin, r.estado_reserva,
       CASE
         WHEN r.estado_reserva = 'activa' AND t.id_ticket IS NOT NULL
              AND t.fecha_hora_salida IS NULL                         THEN 'en curso'
         WHEN r.estado_reserva = 'activa' AND r.fecha_hora_fin < LOCALTIMESTAMP THEN 'vencida'
         ELSE r.estado_reserva
       END AS estado_visible,
       t.id_ticket, t.fecha_hora_entrada, t.fecha_hora_salida,
       p.id_pago, p.metodo_pago, p.monto_total, p.estado_pago, p.referencia_transaccion,
       p.fecha_pago, c.numero_comprobante AS id_comprobante
FROM reserva r
JOIN usuario u          ON u.id_usuario = r.id_usuario
JOIN estacionamiento est ON est.id_estacionamiento = r.id_estacionamiento
JOIN espacios e         ON e.id_espacio = r.id_espacio
JOIN zona z             ON z.id_zona = r.id_zona
JOIN vehiculo v         ON v.id_vehiculo = r.id_vehiculo
JOIN tipo_vehiculo tv   ON tv.id_tipo_vehiculo = v.id_tipo_vehiculo
LEFT JOIN LATERAL (SELECT * FROM ticket WHERE id_reserva = r.id_reserva
                   ORDER BY id_ticket DESC LIMIT 1) t ON TRUE
LEFT JOIN LATERAL (SELECT * FROM pago WHERE id_reserva = r.id_reserva
                   ORDER BY id_pago DESC LIMIT 1) p ON TRUE
LEFT JOIN comprobante c ON c.id_pago = p.id_pago;

-- 4a. Cancelar (solo el dueño de la reserva, antes de que empiece y sin haber ingresado).
--     Devuelve el monto reembolsado (simulado).
CREATE OR REPLACE FUNCTION fn_cancelar_reserva(p_id_reserva integer, p_id_usuario integer)
RETURNS numeric AS $$
DECLARE r reserva; v_reembolso numeric;
BEGIN
  SELECT * INTO r FROM reserva WHERE id_reserva = p_id_reserva AND id_usuario = p_id_usuario FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'La reserva % no existe o no te pertenece', p_id_reserva USING ERRCODE = 'no_data_found';
  END IF;
  IF r.estado_reserva <> 'activa' THEN
    RAISE EXCEPTION 'La reserva ya está %', r.estado_reserva;
  END IF;
  IF EXISTS (SELECT 1 FROM ticket WHERE id_reserva = r.id_reserva) THEN
    RAISE EXCEPTION 'El vehículo ya ingresó: la reserva no se puede cancelar';
  END IF;
  IF r.fecha_reserva <= LOCALTIMESTAMP THEN
    RAISE EXCEPTION 'La reserva ya comenzó: no se puede cancelar';
  END IF;

  UPDATE reserva SET estado_reserva = 'cancelada' WHERE id_reserva = r.id_reserva;
  UPDATE pago SET estado_pago = 'Reembolsado'
  WHERE id_reserva = r.id_reserva AND estado_pago = 'Aprobado'
  RETURNING monto_total INTO v_reembolso;
  RETURN COALESCE(v_reembolso, 0);
END; $$ LANGUAGE plpgsql;

-- 4b. Ingreso del vehículo con reserva (lo registra el dueño/operario): el espacio pasa a Ocupado.
--     Se puede ingresar desde 15 minutos antes de la hora reservada y hasta que termina la franja.
CREATE OR REPLACE FUNCTION fn_registrar_ingreso(p_id_reserva integer)
RETURNS ticket AS $$
DECLARE r reserva; t ticket;
BEGIN
  SELECT * INTO r FROM reserva WHERE id_reserva = p_id_reserva FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'La reserva % no existe', p_id_reserva USING ERRCODE = 'no_data_found';
  END IF;
  IF r.estado_reserva <> 'activa' THEN
    RAISE EXCEPTION 'La reserva está %: no se puede registrar el ingreso', r.estado_reserva;
  END IF;
  IF EXISTS (SELECT 1 FROM ticket WHERE id_reserva = r.id_reserva) THEN
    RAISE EXCEPTION 'Esta reserva ya fue utilizada';
  END IF;
  IF LOCALTIMESTAMP < r.fecha_reserva - interval '15 minutes' THEN
    RAISE EXCEPTION 'Aún no es la hora de la reserva (se puede ingresar desde 15 minutos antes)';
  END IF;
  IF LOCALTIMESTAMP >= r.fecha_hora_fin THEN
    RAISE EXCEPTION 'La franja de la reserva ya terminó';
  END IF;

  INSERT INTO ticket (id_vehiculo, id_espacio, id_reserva, fecha_hora_entrada, estado_ticket)
  VALUES (r.id_vehiculo, r.id_espacio, r.id_reserva, LOCALTIMESTAMP,
          CASE WHEN EXISTS (SELECT 1 FROM pago WHERE id_reserva = r.id_reserva
                            AND estado_pago = 'Aprobado') THEN 'Pagado' ELSE 'Activo' END)
  RETURNING * INTO t;
  RETURN t;
END; $$ LANGUAGE plpgsql;

-- 4c. Salida: el espacio vuelve a Disponible y la reserva queda 'finalizada'.
--     Solo sale un ticket con pago aprobado (propio o de su reserva).
--     Pendiente (decisión de negocio): cobro adicional si se pasa de la hora reservada.
CREATE OR REPLACE FUNCTION fn_registrar_salida(p_id_ticket integer)
RETURNS ticket AS $$
DECLARE t ticket;
BEGIN
  SELECT * INTO t FROM ticket WHERE id_ticket = p_id_ticket FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'El ticket % no existe', p_id_ticket USING ERRCODE = 'no_data_found';
  END IF;
  IF t.fecha_hora_salida IS NOT NULL THEN
    RAISE EXCEPTION 'El ticket % ya registró su salida', p_id_ticket;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pago
                 WHERE estado_pago = 'Aprobado'
                   AND (id_ticket = t.id_ticket OR (t.id_reserva IS NOT NULL AND id_reserva = t.id_reserva))) THEN
    RAISE EXCEPTION 'El ticket % no tiene un pago aprobado', p_id_ticket;
  END IF;
  UPDATE ticket SET fecha_hora_salida = LOCALTIMESTAMP, estado_ticket = 'Finalizado'
  WHERE id_ticket = t.id_ticket RETURNING * INTO t;
  RETURN t;
END; $$ LANGUAGE plpgsql;

COMMIT;
