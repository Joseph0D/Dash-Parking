-- =============================================================================
-- Dash Parking - Migración 002: reservas por tiempo
-- Requiere haber aplicado la 001 (usa reserva.fecha_reserva sin zona horaria,
-- pago.id_reserva y la extensión btree_gist).
-- Ejecutar UNA sola vez:
--   psql -d dash_parking -f 002_time_based_reservations.sql
-- =============================================================================
BEGIN;

-- =============================================================================
-- RESERVAS POR TIEMPO
-- Regla: un espacio reservado de 10:00 a 11:00 solo está "Reservado" en esa
-- franja; a las 9:00 o a las 11:00 vuelve a estar "Disponible".
-- =============================================================================

-- 1. Garantía fuerte (resiste concurrencia): no se solapan reservas activas del mismo espacio.
--     tsrange es [inicio, fin): una reserva 10-11 y otra 11-12 SÍ son compatibles.
ALTER TABLE reserva ADD CONSTRAINT reserva_sin_traslape
  EXCLUDE USING gist (id_espacio WITH =, tsrange(fecha_reserva, fecha_hora_fin) WITH &&)
  WHERE (estado_reserva = 'activa');

-- 2. Completa zona/parqueadero desde el espacio y valida que el vehículo sea del usuario.
CREATE OR REPLACE FUNCTION fn_completar_reserva() RETURNS trigger AS $$
DECLARE v_zona integer; v_estac integer; v_dueno integer;
BEGIN
  SELECT id_zona, id_estacionamiento INTO v_zona, v_estac FROM espacios WHERE id_espacio = NEW.id_espacio;
  IF NOT FOUND THEN RAISE EXCEPTION 'El espacio % no existe', NEW.id_espacio; END IF;
  NEW.id_zona := v_zona;
  NEW.id_estacionamiento := v_estac;

  SELECT id_usuario INTO v_dueno FROM vehiculo WHERE id_vehiculo = NEW.id_vehiculo;
  IF v_dueno IS DISTINCT FROM NEW.id_usuario THEN
    RAISE EXCEPTION 'El vehículo % no pertenece al usuario %', NEW.id_vehiculo, NEW.id_usuario;
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_reserva_completar BEFORE INSERT ON reserva
FOR EACH ROW EXECUTE FUNCTION fn_completar_reserva();

-- 3. Mensaje claro cuando hay cruce de horarios (reemplaza al trigger del PDF, que ignoraba las horas)
CREATE OR REPLACE FUNCTION fn_validar_reserva_libre() RETURNS trigger AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM reserva r
             WHERE r.id_espacio = NEW.id_espacio AND r.estado_reserva = 'activa'
               AND r.id_reserva IS DISTINCT FROM NEW.id_reserva
               AND tsrange(r.fecha_reserva, r.fecha_hora_fin) && tsrange(NEW.fecha_reserva, NEW.fecha_hora_fin)) THEN
    RAISE EXCEPTION 'El espacio % ya está reservado entre % y %', NEW.id_espacio, NEW.fecha_reserva, NEW.fecha_hora_fin
      USING ERRCODE = 'exclusion_violation';
  END IF;

  -- un vehículo que está adentro ahora ocupa el espacio durante la franja actual
  IF NEW.fecha_reserva <= LOCALTIMESTAMP AND NEW.fecha_hora_fin > LOCALTIMESTAMP
     AND EXISTS (SELECT 1 FROM ticket t
                 WHERE t.id_espacio = NEW.id_espacio AND t.fecha_hora_salida IS NULL) THEN
    RAISE EXCEPTION 'El espacio % está ocupado en este momento', NEW.id_espacio
      USING ERRCODE = 'exclusion_violation';
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_reserva_libre BEFORE INSERT OR UPDATE ON reserva
FOR EACH ROW WHEN (NEW.estado_reserva = 'activa')
EXECUTE FUNCTION fn_validar_reserva_libre();

-- 4. Entrada física (ticket): respeta las reservas de otros y valida la reserva propia.
CREATE OR REPLACE FUNCTION fn_validar_espacio_libre() RETURNS trigger AS $$
DECLARE r reserva;
BEGIN
  IF EXISTS (SELECT 1 FROM ticket WHERE id_espacio = NEW.id_espacio AND fecha_hora_salida IS NULL) THEN
    RAISE EXCEPTION 'El espacio % ya está ocupado', NEW.id_espacio;
  END IF;

  IF NEW.id_reserva IS NOT NULL THEN
    SELECT * INTO r FROM reserva WHERE id_reserva = NEW.id_reserva;
    IF r.id_espacio <> NEW.id_espacio OR r.id_vehiculo <> NEW.id_vehiculo THEN
      RAISE EXCEPTION 'La reserva % no corresponde a este vehículo/espacio', NEW.id_reserva;
    END IF;
  ELSIF EXISTS (SELECT 1 FROM reserva r2
                WHERE r2.id_espacio = NEW.id_espacio AND r2.estado_reserva = 'activa'
                  AND r2.fecha_reserva <= NEW.fecha_hora_entrada
                  AND r2.fecha_hora_fin >  NEW.fecha_hora_entrada) THEN
    RAISE EXCEPTION 'El espacio % está reservado por otro usuario en este horario', NEW.id_espacio;
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

-- 5. Estado de cada espacio PARA UNA FRANJA: Disponible / Reservado / Ocupado / Mantenimiento
--     (es lo que pinta la cuadrícula del frontend al elegir fecha y hora).
CREATE OR REPLACE FUNCTION fn_estado_espacios(
  p_id_estacionamiento integer,
  p_id_tipo_vehiculo   integer,
  p_inicio             timestamp,
  p_fin                timestamp
) RETURNS TABLE (
  id_espacio integer, id_zona integer, nombre_zona varchar,
  numero_de_espacio varchar, id_tipo_espacio integer, estado text
) LANGUAGE sql STABLE AS $$
  SELECT e.id_espacio, z.id_zona, z.nombre_zona, e.numero_de_espacio, e.id_tipo_espacio,
    CASE
      WHEN e.estado <> 'activo' THEN 'Mantenimiento'
      WHEN p_inicio <= LOCALTIMESTAMP
           AND EXISTS (SELECT 1 FROM ticket t
                       WHERE t.id_espacio = e.id_espacio AND t.fecha_hora_salida IS NULL) THEN 'Ocupado'
      WHEN EXISTS (SELECT 1 FROM reserva r
                   WHERE r.id_espacio = e.id_espacio AND r.estado_reserva = 'activa'
                     AND tsrange(r.fecha_reserva, r.fecha_hora_fin) && tsrange(p_inicio, p_fin)) THEN 'Reservado'
      ELSE 'Disponible'
    END
  FROM espacios e
  JOIN zona z ON z.id_zona = e.id_zona
  WHERE e.id_estacionamiento = p_id_estacionamiento
    AND z.id_tipo_vehiculo   = p_id_tipo_vehiculo
  ORDER BY e.id_espacio;
$$;

-- 6. Resumen por zona para una franja (cuántos quedan libres de 3 a 4 pm)
CREATE OR REPLACE FUNCTION fn_disponibilidad_franja(
  p_id_estacionamiento integer, p_inicio timestamp, p_fin timestamp
) RETURNS TABLE (id_zona integer, nombre_zona varchar, id_tipo_vehiculo integer,
                 capacidad integer, libres bigint, reservados bigint, ocupados bigint)
LANGUAGE sql STABLE AS $$
  SELECT z.id_zona, z.nombre_zona, z.id_tipo_vehiculo, z.capacidad,
         COUNT(*) FILTER (WHERE s.estado = 'Disponible'),
         COUNT(*) FILTER (WHERE s.estado = 'Reservado'),
         COUNT(*) FILTER (WHERE s.estado = 'Ocupado')
  FROM zona z
  CROSS JOIN LATERAL fn_estado_espacios(p_id_estacionamiento, z.id_tipo_vehiculo, p_inicio, p_fin) s
  WHERE z.id_estacionamiento = p_id_estacionamiento AND s.id_zona = z.id_zona
  GROUP BY z.id_zona, z.nombre_zona, z.id_tipo_vehiculo, z.capacidad
  ORDER BY z.id_zona;
$$;

-- 7. Crear la reserva eligiendo parqueadero y franja. Si no se indica espacio, asigna uno libre.
CREATE OR REPLACE FUNCTION fn_crear_reserva(
  p_id_usuario         integer,
  p_id_vehiculo        integer,
  p_id_estacionamiento integer,
  p_inicio             timestamp,
  p_fin                timestamp,
  p_id_espacio         integer DEFAULT NULL
) RETURNS reserva AS $$
DECLARE v_tipo integer; v_cand integer; v_res reserva;
BEGIN
  IF p_inicio IS NULL OR p_fin IS NULL OR p_fin <= p_inicio THEN
    RAISE EXCEPTION 'La hora de fin debe ser posterior a la de inicio';
  END IF;
  IF p_inicio < LOCALTIMESTAMP - interval '5 minutes' THEN
    RAISE EXCEPTION 'No se puede reservar en el pasado';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM estacionamiento WHERE id_estacionamiento = p_id_estacionamiento) THEN
    RAISE EXCEPTION 'El parqueadero % no existe', p_id_estacionamiento;
  END IF;

  SELECT id_tipo_vehiculo INTO v_tipo FROM vehiculo
  WHERE id_vehiculo = p_id_vehiculo AND id_usuario = p_id_usuario;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'El vehículo % no pertenece al usuario %', p_id_vehiculo, p_id_usuario;
  END IF;

  -- Si se eligió un espacio puntual, debe ser de ese parqueadero y de la zona del tipo de vehículo
  IF p_id_espacio IS NOT NULL AND NOT EXISTS (
       SELECT 1 FROM espacios e JOIN zona z ON z.id_zona = e.id_zona
       WHERE e.id_espacio = p_id_espacio AND e.id_estacionamiento = p_id_estacionamiento
         AND z.id_tipo_vehiculo = v_tipo) THEN
    RAISE EXCEPTION 'El espacio % no pertenece a este parqueadero o no es para este tipo de vehículo', p_id_espacio;
  END IF;

  FOR v_cand IN
    SELECT s.id_espacio FROM fn_estado_espacios(p_id_estacionamiento, v_tipo, p_inicio, p_fin) s
    WHERE s.estado = 'Disponible' AND (p_id_espacio IS NULL OR s.id_espacio = p_id_espacio)
    ORDER BY s.id_espacio
  LOOP
    BEGIN
      INSERT INTO reserva (id_usuario, id_vehiculo, id_estacionamiento, id_espacio, id_zona,
                           fecha_reserva, fecha_hora_fin, estado_reserva)
      VALUES (p_id_usuario, p_id_vehiculo, p_id_estacionamiento, v_cand,
              (SELECT id_zona FROM espacios WHERE id_espacio = v_cand), p_inicio, p_fin, 'activa')
      RETURNING * INTO v_res;
      RETURN v_res;
    EXCEPTION WHEN exclusion_violation THEN
      CONTINUE;   -- otro usuario lo tomó en ese instante: probar el siguiente
    END;
  END LOOP;

  IF p_id_espacio IS NOT NULL THEN
    RAISE EXCEPTION 'El espacio % no está disponible entre % y %', p_id_espacio, p_inicio, p_fin
      USING ERRCODE = 'no_data_found';
  END IF;
  RAISE EXCEPTION 'No hay espacios disponibles para ese vehículo entre % y %', p_inicio, p_fin
    USING ERRCODE = 'no_data_found';
END; $$ LANGUAGE plpgsql;

-- 8. Precio estimado de una reserva (para mostrarlo ANTES de pagar). NULL si no hay tarifa vigente.
CREATE OR REPLACE FUNCTION fn_precio_estimado(
  p_id_estacionamiento integer, p_id_tipo_vehiculo integer, p_inicio timestamp, p_fin timestamp
) RETURNS numeric AS $$
BEGIN
  RETURN fn_monto_por_minutos(
    fn_tarifa_vigente(p_id_tipo_vehiculo, p_inicio::date, p_id_estacionamiento),
    (EXTRACT(EPOCH FROM (p_fin - p_inicio)) / 60)::integer);
EXCEPTION WHEN raise_exception THEN
  RETURN NULL;
END; $$ LANGUAGE plpgsql STABLE;

COMMIT;
