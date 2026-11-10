-- Dash Parking - estado final de la base (dump original + migraciones 001 y 002).
-- Para una base NUEVA: createdb dash_parking_v2 && psql -d dash_parking_v2 -f dash_parking_complete.sql

--
-- PostgreSQL database dump
--


-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: btree_gist; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public;


--
-- Name: EXTENSION btree_gist; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION btree_gist IS 'support for indexing common datatypes in GiST';


--
-- Name: fn_actualizar_estado_ticket(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_actualizar_estado_ticket() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.estado_pago = 'Aprobado' THEN
        UPDATE ticket
        SET estado_ticket = CASE
            WHEN fecha_hora_salida IS NULL THEN 'Pagado'
            ELSE 'Finalizado'
        END
        WHERE id_ticket = NEW.id_ticket;
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: fn_calcular_monto_pago(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_calcular_monto_pago() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  v_tipo_vehiculo integer;
  v_estac         integer;
  v_inicio        timestamp;
  v_fin           timestamp;
  v_tarifa        tarifa;
BEGIN
  IF NEW.id_ticket IS NULL AND NEW.id_reserva IS NULL THEN
    RAISE EXCEPTION 'El pago debe asociarse a un ticket o a una reserva';
  END IF;

  IF NEW.id_ticket IS NOT NULL THEN
    SELECT t.fecha_hora_entrada, COALESCE(t.fecha_hora_salida, CURRENT_TIMESTAMP),
           v.id_tipo_vehiculo, e.id_estacionamiento
      INTO v_inicio, v_fin, v_tipo_vehiculo, v_estac
    FROM ticket t
    JOIN vehiculo v ON v.id_vehiculo = t.id_vehiculo
    JOIN espacios e ON e.id_espacio  = t.id_espacio
    WHERE t.id_ticket = NEW.id_ticket;
    v_tarifa := fn_tarifa_vigente(v_tipo_vehiculo, CURRENT_DATE, v_estac);
  ELSE
    SELECT r.fecha_reserva, r.fecha_hora_fin, v.id_tipo_vehiculo, r.id_estacionamiento
      INTO v_inicio, v_fin, v_tipo_vehiculo, v_estac
    FROM reserva r JOIN vehiculo v ON v.id_vehiculo = r.id_vehiculo
    WHERE r.id_reserva = NEW.id_reserva;
    v_tarifa := fn_tarifa_vigente(v_tipo_vehiculo, v_inicio::date, v_estac);
  END IF;

  NEW.id_tarifa   := v_tarifa.id_tarifa;
  NEW.monto_total := fn_monto_por_minutos(v_tarifa, (EXTRACT(EPOCH FROM (v_fin - v_inicio)) / 60)::integer);
  RETURN NEW;
END; $$;


--
-- Name: fn_completar_reserva(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_completar_reserva() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
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
END; $$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: reserva; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reserva (
    id_reserva integer NOT NULL,
    id_usuario integer NOT NULL,
    id_vehiculo integer NOT NULL,
    id_estacionamiento integer NOT NULL,
    id_espacio integer NOT NULL,
    id_zona integer NOT NULL,
    fecha_reserva timestamp without time zone NOT NULL,
    fecha_hora_fin timestamp without time zone NOT NULL,
    estado_reserva character varying(50) DEFAULT 'activa'::character varying NOT NULL,
    CONSTRAINT reserva_estado_reserva_check CHECK (((estado_reserva)::text = ANY (ARRAY[('activa'::character varying)::text, ('cancelada'::character varying)::text, ('finalizada'::character varying)::text]))),
    CONSTRAINT reserva_rango_valido CHECK ((fecha_hora_fin > fecha_reserva))
);


--
-- Name: COLUMN reserva.fecha_reserva; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.reserva.fecha_reserva IS 'Inicio de la franja reservada (hora Colombia)';


--
-- Name: COLUMN reserva.fecha_hora_fin; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.reserva.fecha_hora_fin IS 'Fin de la franja reservada (hora Colombia)';


--
-- Name: fn_crear_reserva(integer, integer, integer, timestamp without time zone, timestamp without time zone, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_crear_reserva(p_id_usuario integer, p_id_vehiculo integer, p_id_estacionamiento integer, p_inicio timestamp without time zone, p_fin timestamp without time zone, p_id_espacio integer DEFAULT NULL::integer) RETURNS public.reserva
    LANGUAGE plpgsql
    AS $$
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
END; $$;


--
-- Name: fn_disponibilidad_franja(integer, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_disponibilidad_franja(p_id_estacionamiento integer, p_inicio timestamp without time zone, p_fin timestamp without time zone) RETURNS TABLE(id_zona integer, nombre_zona character varying, id_tipo_vehiculo integer, capacidad integer, libres bigint, reservados bigint, ocupados bigint)
    LANGUAGE sql STABLE
    AS $$
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


--
-- Name: fn_emitir_comprobante(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_emitir_comprobante() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE v_id integer;
BEGIN
  IF NEW.estado_pago = 'Aprobado'
     AND NOT EXISTS (SELECT 1 FROM comprobante WHERE id_pago = NEW.id_pago) THEN
    v_id := nextval('comprobante_id_comprobante_seq');
    INSERT INTO comprobante (id_comprobante, id_pago, numero_comprobante, fecha_emision, monto_total)
    VALUES (v_id, NEW.id_pago, 'COMP-' || lpad(v_id::text, 6, '0'), NEW.fecha_pago, NEW.monto_total);
  END IF;
  RETURN NEW;
END; $$;


--
-- Name: fn_estado_espacios(integer, integer, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_estado_espacios(p_id_estacionamiento integer, p_id_tipo_vehiculo integer, p_inicio timestamp without time zone, p_fin timestamp without time zone) RETURNS TABLE(id_espacio integer, id_zona integer, nombre_zona character varying, numero_de_espacio character varying, id_tipo_espacio integer, estado text)
    LANGUAGE sql STABLE
    AS $$
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


--
-- Name: fn_finalizar_reserva(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_finalizar_reserva() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.id_reserva IS NOT NULL THEN
        UPDATE reserva SET estado_reserva = 'finalizada' WHERE id_reserva = NEW.id_reserva;
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: tarifa; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tarifa (
    id_tarifa integer NOT NULL,
    id_tipo_vehiculo integer NOT NULL,
    id_estacionamiento integer NOT NULL,
    valor_minuto numeric(10,2) NOT NULL,
    valor_dia numeric(10,2),
    valor_mensualidad numeric(10,2),
    fecha_vigencia_inicio date NOT NULL,
    fecha_vigencia_fin date
);


--
-- Name: fn_monto_por_minutos(public.tarifa, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_monto_por_minutos(p_tarifa public.tarifa, p_minutos integer) RETURNS numeric
    LANGUAGE plpgsql IMMUTABLE
    AS $$
BEGIN
  IF p_minutos >= 1440 AND p_tarifa.valor_dia IS NOT NULL THEN
    RETURN CEIL(p_minutos / 1440.0) * p_tarifa.valor_dia;
  END IF;
  RETURN p_minutos * p_tarifa.valor_minuto;
END; $$;


--
-- Name: fn_precio_estimado(integer, integer, timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_precio_estimado(p_id_estacionamiento integer, p_id_tipo_vehiculo integer, p_inicio timestamp without time zone, p_fin timestamp without time zone) RETURNS numeric
    LANGUAGE plpgsql STABLE
    AS $$
BEGIN
  RETURN fn_monto_por_minutos(
    fn_tarifa_vigente(p_id_tipo_vehiculo, p_inicio::date, p_id_estacionamiento),
    (EXTRACT(EPOCH FROM (p_fin - p_inicio)) / 60)::integer);
EXCEPTION WHEN raise_exception THEN
  RETURN NULL;
END; $$;


--
-- Name: fn_tarifa_vigente(integer, date, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_tarifa_vigente(p_id_tipo_vehiculo integer, p_fecha date DEFAULT CURRENT_DATE, p_id_estacionamiento integer DEFAULT NULL::integer) RETURNS public.tarifa
    LANGUAGE plpgsql
    AS $$
DECLARE v_tarifa tarifa;
BEGIN
  SELECT * INTO v_tarifa FROM tarifa
  WHERE id_tipo_vehiculo = p_id_tipo_vehiculo
    AND (p_id_estacionamiento IS NULL OR id_estacionamiento = p_id_estacionamiento)
    AND fecha_vigencia_inicio <= p_fecha
    AND (fecha_vigencia_fin IS NULL OR fecha_vigencia_fin >= p_fecha)
  ORDER BY fecha_vigencia_inicio DESC LIMIT 1;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'No hay tarifa vigente para tipo_vehiculo % en fecha %', p_id_tipo_vehiculo, p_fecha;
  END IF;
  RETURN v_tarifa;
END; $$;


--
-- Name: fn_validar_capacidad_zona(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_validar_capacidad_zona() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE v_cap integer; v_actual integer;
BEGIN
  SELECT capacidad INTO v_cap FROM zona WHERE id_zona = NEW.id_zona;
  SELECT COUNT(*) INTO v_actual FROM espacios WHERE id_zona = NEW.id_zona;
  IF v_actual >= v_cap THEN
    RAISE EXCEPTION 'La zona % ya alcanzó su capacidad (%)', NEW.id_zona, v_cap;
  END IF;
  RETURN NEW;
END; $$;


--
-- Name: fn_validar_espacio_libre(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_validar_espacio_libre() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
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
END; $$;


--
-- Name: fn_validar_reserva_libre(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_validar_reserva_libre() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
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
END; $$;


--
-- Name: fn_validar_tipo_espacio(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.fn_validar_tipo_espacio() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_tipo_veh_espacio INT;
    v_tipo_veh_vehiculo INT;
    v_estado_espacio VARCHAR(10);
BEGIN
    SELECT z.id_tipo_vehiculo, e.estado
    INTO v_tipo_veh_espacio, v_estado_espacio
    FROM espacios e
    JOIN zona z ON z.id_zona = e.id_zona
    WHERE e.id_espacio = NEW.id_espacio;

    SELECT id_tipo_vehiculo INTO v_tipo_veh_vehiculo
    FROM vehiculo WHERE id_vehiculo = NEW.id_vehiculo;

    IF v_estado_espacio <> 'activo' THEN
        RAISE EXCEPTION 'El espacio % está inactivo', NEW.id_espacio;
    END IF;

    IF v_tipo_veh_espacio <> v_tipo_veh_vehiculo THEN
        RAISE EXCEPTION 'El vehículo % no corresponde a la zona del espacio %', NEW.id_vehiculo, NEW.id_espacio;
    END IF;

    RETURN NEW;
END;
$$;


--
-- Name: comprobante; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comprobante (
    id_comprobante integer NOT NULL,
    id_pago integer NOT NULL,
    numero_comprobante character varying(20) NOT NULL,
    fecha_emision timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    monto_total numeric(10,2) NOT NULL
);


--
-- Name: comprobante_id_comprobante_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comprobante_id_comprobante_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comprobante_id_comprobante_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.comprobante_id_comprobante_seq OWNED BY public.comprobante.id_comprobante;


--
-- Name: espacios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.espacios (
    id_espacio integer NOT NULL,
    id_zona integer NOT NULL,
    id_estacionamiento integer NOT NULL,
    id_tipo_espacio integer NOT NULL,
    numero_de_espacio character varying(20) NOT NULL,
    estado character varying(10) DEFAULT 'activo'::character varying NOT NULL,
    CONSTRAINT espacios_estado_check CHECK (((estado)::text = ANY (ARRAY[('activo'::character varying)::text, ('inactivo'::character varying)::text])))
);


--
-- Name: espacios_id_espacio_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.espacios ALTER COLUMN id_espacio ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.espacios_id_espacio_seq
    START WITH 501
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: estacionamiento; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estacionamiento (
    id_estacionamiento integer NOT NULL,
    nombre_parqueadero character varying(100) NOT NULL,
    identificacion character varying(20) NOT NULL,
    direccion character varying(150) NOT NULL,
    telefono character varying(20),
    capacidad_total integer NOT NULL,
    id_propietario integer
);


--
-- Name: estacionamiento_id_estacionamiento_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.estacionamiento ALTER COLUMN id_estacionamiento ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.estacionamiento_id_estacionamiento_seq
    START WITH 2
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: pago; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pago (
    id_pago integer NOT NULL,
    id_ticket integer,
    id_tarifa integer NOT NULL,
    monto_total numeric(10,2) NOT NULL,
    metodo_pago character varying(30) NOT NULL,
    estado_pago character varying(20) DEFAULT 'Pendiente'::character varying NOT NULL,
    fecha_pago timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    referencia_transaccion character varying(100),
    id_reserva integer,
    CONSTRAINT pago_estado_pago_check CHECK (((estado_pago)::text = ANY (ARRAY[('Pendiente'::character varying)::text, ('Aprobado'::character varying)::text, ('Rechazado'::character varying)::text]))),
    CONSTRAINT pago_metodo_pago_check CHECK (((metodo_pago)::text = ANY ((ARRAY['Efectivo'::character varying, 'Tarjeta Credito'::character varying, 'Tarjeta Debito'::character varying, 'PSE'::character varying, 'Nequi'::character varying, 'Daviplata'::character varying])::text[]))),
    CONSTRAINT pago_ticket_o_reserva CHECK (((id_ticket IS NOT NULL) OR (id_reserva IS NOT NULL)))
);


--
-- Name: pago_id_pago_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pago_id_pago_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pago_id_pago_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pago_id_pago_seq OWNED BY public.pago.id_pago;


--
-- Name: reserva_id_reserva_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.reserva ALTER COLUMN id_reserva ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.reserva_id_reserva_seq
    START WITH 10
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: rol; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rol (
    id_rol integer NOT NULL,
    nombre_rol character varying(30) NOT NULL,
    descripcion character varying(150)
);


--
-- Name: rol_id_rol_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.rol ALTER COLUMN id_rol ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.rol_id_rol_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tarifa_id_tarifa_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.tarifa ALTER COLUMN id_tarifa ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.tarifa_id_tarifa_seq
    START WITH 11
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: ticket; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ticket (
    id_ticket integer NOT NULL,
    id_vehiculo integer NOT NULL,
    id_espacio integer NOT NULL,
    id_reserva integer,
    fecha_hora_entrada timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_hora_salida timestamp without time zone,
    estado_ticket character varying(20) DEFAULT 'Activo'::character varying NOT NULL,
    CONSTRAINT ticket_estado_ticket_check CHECK (((estado_ticket)::text = ANY ((ARRAY['Activo'::character varying, 'Pagado'::character varying, 'Finalizado'::character varying, 'Anulado'::character varying])::text[])))
);


--
-- Name: ticket_id_ticket_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ticket_id_ticket_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ticket_id_ticket_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ticket_id_ticket_seq OWNED BY public.ticket.id_ticket;


--
-- Name: tipo_espacio; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tipo_espacio (
    id_tipo_espacio integer NOT NULL,
    nombre_tipo character varying(50) NOT NULL,
    descripcion character varying(150)
);


--
-- Name: tipo_espacio_id_tipo_espacio_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.tipo_espacio ALTER COLUMN id_tipo_espacio ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.tipo_espacio_id_tipo_espacio_seq
    START WITH 7
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tipo_vehiculo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tipo_vehiculo (
    id_tipo_vehiculo integer NOT NULL,
    nombre_tipo character varying(30) NOT NULL,
    descripcion character varying(100),
    CONSTRAINT tipo_vehiculo_nombre_tipo_check CHECK (((nombre_tipo)::text = ANY (ARRAY[('Carro'::character varying)::text, ('Moto'::character varying)::text, ('bicicleta'::character varying)::text, ('Moto electrica'::character varying)::text, ('Patineta'::character varying)::text])))
);


--
-- Name: tipo_vehiculo_id_tipo_vehiculo_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.tipo_vehiculo ALTER COLUMN id_tipo_vehiculo ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.tipo_vehiculo_id_tipo_vehiculo_seq
    START WITH 6
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuario (
    id_usuario integer NOT NULL,
    nombres character varying(50) NOT NULL,
    apellidos character varying(50) NOT NULL,
    documento_id character varying(20) NOT NULL,
    telefono character varying(15),
    correo character varying(150),
    fecha_registro date DEFAULT CURRENT_DATE NOT NULL,
    id_rol integer DEFAULT 1 NOT NULL,
    password_hash character varying(255)
);


--
-- Name: COLUMN usuario.password_hash; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.usuario.password_hash IS 'Hash bcrypt. Nunca guardar contraseñas en texto plano.';


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.usuario ALTER COLUMN id_usuario ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.usuario_id_usuario_seq
    START WITH 14
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: vehiculo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehiculo (
    id_vehiculo integer NOT NULL,
    id_usuario integer NOT NULL,
    id_tipo_vehiculo integer NOT NULL,
    placa character varying(10) NOT NULL,
    marca character varying(30),
    modelo character varying(30),
    color character varying(20)
);


--
-- Name: vehiculo_id_vehiculo_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.vehiculo ALTER COLUMN id_vehiculo ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.vehiculo_id_vehiculo_seq
    START WITH 17
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: zona; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.zona (
    id_zona integer NOT NULL,
    id_estacionamiento integer NOT NULL,
    id_tipo_vehiculo integer NOT NULL,
    nombre_zona character varying(50) NOT NULL,
    capacidad integer NOT NULL
);


--
-- Name: vw_disponibilidad_zona; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.vw_disponibilidad_zona AS
 SELECT z.id_zona,
    z.nombre_zona,
    z.capacidad AS capacidad_total,
    count(e.id_espacio) FILTER (WHERE ((e.estado)::text = 'activo'::text)) AS espacios_activos,
    count(t.id_ticket) AS espacios_ocupados,
    (count(e.id_espacio) FILTER (WHERE ((e.estado)::text = 'activo'::text)) - count(t.id_ticket)) AS espacios_libres
   FROM ((public.zona z
     JOIN public.espacios e ON ((e.id_zona = z.id_zona)))
     LEFT JOIN public.ticket t ON (((t.id_espacio = e.id_espacio) AND (t.fecha_hora_salida IS NULL))))
  GROUP BY z.id_zona, z.nombre_zona, z.capacidad;


--
-- Name: vw_historial_usuario; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.vw_historial_usuario AS
 SELECT u.id_usuario,
    u.nombres,
    u.apellidos,
    t.id_ticket,
    t.fecha_hora_entrada,
    t.fecha_hora_salida,
    p.monto_total,
    p.metodo_pago,
    p.estado_pago
   FROM (((public.usuario u
     JOIN public.vehiculo v ON ((v.id_usuario = u.id_usuario)))
     JOIN public.ticket t ON ((t.id_vehiculo = v.id_vehiculo)))
     LEFT JOIN public.pago p ON ((p.id_ticket = t.id_ticket)));


--
-- Name: vw_ingresos_diarios; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.vw_ingresos_diarios AS
 SELECT date(p.fecha_pago) AS fecha,
    tv.nombre_tipo,
    sum(p.monto_total) AS total_recaudado
   FROM (((public.pago p
     JOIN public.ticket t ON ((t.id_ticket = p.id_ticket)))
     JOIN public.vehiculo v ON ((v.id_vehiculo = t.id_vehiculo)))
     JOIN public.tipo_vehiculo tv ON ((tv.id_tipo_vehiculo = v.id_tipo_vehiculo)))
  WHERE ((p.estado_pago)::text = 'Aprobado'::text)
  GROUP BY (date(p.fecha_pago)), tv.nombre_tipo;


--
-- Name: vw_tickets_activos; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.vw_tickets_activos AS
 SELECT t.id_ticket,
    u.nombres,
    u.apellidos,
    v.placa,
    e.numero_de_espacio,
    t.fecha_hora_entrada,
    t.estado_ticket
   FROM (((public.ticket t
     JOIN public.vehiculo v ON ((v.id_vehiculo = t.id_vehiculo)))
     JOIN public.usuario u ON ((u.id_usuario = v.id_usuario)))
     JOIN public.espacios e ON ((e.id_espacio = t.id_espacio)))
  WHERE (t.fecha_hora_salida IS NULL);


--
-- Name: zona_id_zona_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.zona ALTER COLUMN id_zona ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.zona_id_zona_seq
    START WITH 6
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: comprobante id_comprobante; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobante ALTER COLUMN id_comprobante SET DEFAULT nextval('public.comprobante_id_comprobante_seq'::regclass);


--
-- Name: pago id_pago; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pago ALTER COLUMN id_pago SET DEFAULT nextval('public.pago_id_pago_seq'::regclass);


--
-- Name: ticket id_ticket; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ticket ALTER COLUMN id_ticket SET DEFAULT nextval('public.ticket_id_ticket_seq'::regclass);


--
-- Data for Name: comprobante; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.comprobante (id_comprobante, id_pago, numero_comprobante, fecha_emision, monto_total) FROM stdin;
1	1	COMP-000001	2026-09-14 09:07:00	60000.00
2	2	COMP-000002	2026-09-14 08:47:00	9000.00
3	3	COMP-000003	2026-09-14 11:03:00	6000.00
4	4	COMP-000004	2026-09-15 07:52:00	20000.00
5	5	COMP-000005	2026-09-15 11:02:00	36000.00
6	6	COMP-000006	2026-09-15 18:05:00	25000.00
7	7	COMP-000007	2026-09-15 13:32:00	15000.00
8	8	COMP-000008	2026-09-15 15:26:00	5000.00
9	10	COMP-000009	2026-09-16 06:02:00	12000.00
10	12	COMP-000010	2026-09-16 15:23:51.179767	60000.00
\.


--
-- Data for Name: espacios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.espacios (id_espacio, id_zona, id_estacionamiento, id_tipo_espacio, numero_de_espacio, estado) FROM stdin;
1	1	1	1	A-001	activo
2	1	1	1	A-002	activo
3	1	1	1	A-003	activo
4	1	1	1	A-004	activo
5	1	1	1	A-005	activo
6	1	1	1	A-006	activo
7	1	1	1	A-007	activo
8	1	1	1	A-008	activo
9	1	1	1	A-009	activo
10	1	1	1	A-010	activo
11	1	1	1	A-011	activo
12	1	1	1	A-012	activo
13	1	1	1	A-013	activo
14	1	1	1	A-014	activo
15	1	1	1	A-015	activo
16	1	1	1	A-016	activo
17	1	1	1	A-017	activo
18	1	1	1	A-018	activo
19	1	1	1	A-019	activo
20	1	1	1	A-020	activo
21	1	1	1	A-021	activo
22	1	1	1	A-022	activo
23	1	1	1	A-023	activo
24	1	1	1	A-024	activo
25	1	1	1	A-025	activo
26	1	1	1	A-026	activo
27	1	1	1	A-027	activo
28	1	1	1	A-028	activo
29	1	1	1	A-029	activo
30	1	1	1	A-030	activo
31	1	1	1	A-031	activo
32	1	1	1	A-032	activo
33	1	1	1	A-033	activo
34	1	1	1	A-034	activo
35	1	1	1	A-035	activo
36	1	1	1	A-036	activo
37	1	1	1	A-037	activo
38	1	1	1	A-038	activo
39	1	1	1	A-039	activo
40	1	1	1	A-040	activo
41	1	1	1	A-041	activo
42	1	1	1	A-042	activo
43	1	1	1	A-043	activo
44	1	1	1	A-044	activo
45	1	1	1	A-045	activo
46	1	1	1	A-046	activo
47	1	1	1	A-047	activo
48	1	1	1	A-048	activo
49	1	1	1	A-049	activo
50	1	1	1	A-050	activo
51	1	1	1	A-051	activo
52	1	1	1	A-052	activo
53	1	1	1	A-053	activo
54	1	1	1	A-054	activo
55	1	1	1	A-055	activo
56	1	1	1	A-056	activo
57	1	1	1	A-057	activo
58	1	1	1	A-058	activo
59	1	1	1	A-059	activo
60	1	1	1	A-060	activo
61	1	1	1	A-061	activo
62	1	1	1	A-062	activo
63	1	1	1	A-063	activo
64	1	1	1	A-064	activo
65	1	1	1	A-065	activo
66	1	1	1	A-066	activo
67	1	1	1	A-067	activo
68	1	1	1	A-068	activo
69	1	1	1	A-069	activo
70	1	1	1	A-070	activo
71	1	1	1	A-071	activo
72	1	1	1	A-072	activo
73	1	1	1	A-073	activo
74	1	1	1	A-074	activo
75	1	1	1	A-075	activo
76	1	1	1	A-076	activo
77	1	1	1	A-077	activo
78	1	1	1	A-078	activo
79	1	1	1	A-079	activo
80	1	1	1	A-080	activo
81	1	1	1	A-081	activo
82	1	1	1	A-082	activo
83	1	1	1	A-083	activo
84	1	1	1	A-084	activo
85	1	1	1	A-085	activo
86	1	1	1	A-086	activo
87	1	1	1	A-087	activo
88	1	1	1	A-088	activo
89	1	1	1	A-089	activo
90	1	1	1	A-090	activo
91	1	1	1	A-091	activo
92	1	1	1	A-092	activo
93	1	1	1	A-093	activo
94	1	1	1	A-094	activo
95	1	1	1	A-095	activo
96	1	1	1	A-096	activo
97	1	1	1	A-097	inactivo
98	1	1	1	A-098	activo
99	1	1	1	A-099	activo
100	1	1	1	A-100	activo
101	1	1	1	A-101	activo
102	1	1	1	A-102	activo
103	1	1	1	A-103	activo
104	1	1	1	A-104	activo
105	1	1	1	A-105	activo
106	1	1	1	A-106	activo
107	1	1	1	A-107	activo
108	1	1	1	A-108	activo
109	1	1	1	A-109	activo
110	1	1	1	A-110	activo
111	1	1	1	A-111	activo
112	1	1	1	A-112	activo
113	1	1	1	A-113	activo
114	1	1	1	A-114	activo
115	1	1	1	A-115	activo
116	1	1	1	A-116	activo
117	1	1	1	A-117	activo
118	1	1	1	A-118	activo
119	1	1	1	A-119	activo
120	1	1	1	A-120	activo
121	1	1	1	A-121	activo
122	1	1	1	A-122	activo
123	1	1	1	A-123	activo
124	1	1	1	A-124	activo
125	1	1	1	A-125	activo
126	1	1	1	A-126	activo
127	1	1	1	A-127	activo
128	1	1	1	A-128	activo
129	1	1	1	A-129	activo
130	1	1	1	A-130	activo
131	1	1	1	A-131	activo
132	1	1	1	A-132	activo
133	1	1	1	A-133	activo
134	1	1	1	A-134	activo
135	1	1	1	A-135	activo
136	1	1	1	A-136	activo
137	1	1	1	A-137	activo
138	1	1	1	A-138	activo
139	1	1	1	A-139	activo
140	1	1	1	A-140	activo
141	1	1	1	A-141	activo
142	1	1	1	A-142	activo
143	1	1	1	A-143	activo
144	1	1	1	A-144	activo
145	1	1	1	A-145	activo
146	1	1	1	A-146	activo
147	1	1	1	A-147	activo
148	1	1	1	A-148	activo
149	1	1	1	A-149	activo
150	1	1	1	A-150	activo
151	1	1	1	A-151	activo
152	1	1	1	A-152	activo
153	1	1	1	A-153	activo
154	1	1	1	A-154	activo
155	1	1	1	A-155	activo
156	1	1	1	A-156	activo
157	1	1	1	A-157	activo
158	1	1	1	A-158	activo
159	1	1	1	A-159	activo
160	1	1	1	A-160	activo
161	1	1	1	A-161	activo
162	1	1	1	A-162	activo
163	1	1	1	A-163	activo
164	1	1	1	A-164	activo
165	1	1	1	A-165	activo
166	1	1	1	A-166	activo
167	1	1	1	A-167	activo
168	1	1	1	A-168	activo
169	1	1	1	A-169	activo
170	1	1	1	A-170	activo
171	1	1	1	A-171	activo
172	1	1	1	A-172	activo
173	1	1	1	A-173	activo
174	1	1	1	A-174	activo
175	1	1	1	A-175	activo
176	1	1	1	A-176	activo
177	1	1	1	A-177	activo
178	1	1	1	A-178	activo
179	1	1	1	A-179	activo
180	1	1	1	A-180	activo
181	1	1	1	A-181	activo
182	1	1	1	A-182	activo
183	1	1	1	A-183	activo
184	1	1	1	A-184	activo
185	1	1	1	A-185	activo
186	1	1	1	A-186	activo
187	1	1	1	A-187	activo
188	1	1	1	A-188	activo
189	1	1	1	A-189	activo
190	1	1	1	A-190	activo
191	1	1	2	A-191	activo
192	1	1	2	A-192	activo
193	1	1	2	A-193	activo
194	1	1	2	A-194	inactivo
195	1	1	2	A-195	activo
196	1	1	2	A-196	activo
197	1	1	2	A-197	activo
198	1	1	2	A-198	activo
199	1	1	2	A-199	activo
200	1	1	2	A-200	activo
201	2	1	3	B-001	activo
202	2	1	3	B-002	activo
203	2	1	3	B-003	activo
204	2	1	3	B-004	activo
205	2	1	3	B-005	activo
206	2	1	3	B-006	activo
207	2	1	3	B-007	activo
208	2	1	3	B-008	activo
209	2	1	3	B-009	activo
210	2	1	3	B-010	activo
211	2	1	3	B-011	activo
212	2	1	3	B-012	activo
213	2	1	3	B-013	activo
214	2	1	3	B-014	activo
215	2	1	3	B-015	activo
216	2	1	3	B-016	activo
217	2	1	3	B-017	activo
218	2	1	3	B-018	activo
219	2	1	3	B-019	activo
220	2	1	3	B-020	activo
221	2	1	3	B-021	activo
222	2	1	3	B-022	activo
223	2	1	3	B-023	activo
224	2	1	3	B-024	activo
225	2	1	3	B-025	activo
226	2	1	3	B-026	activo
227	2	1	3	B-027	activo
228	2	1	3	B-028	activo
229	2	1	3	B-029	activo
230	2	1	3	B-030	activo
231	2	1	3	B-031	activo
232	2	1	3	B-032	activo
233	2	1	3	B-033	activo
234	2	1	3	B-034	activo
235	2	1	3	B-035	activo
236	2	1	3	B-036	activo
237	2	1	3	B-037	activo
238	2	1	3	B-038	activo
239	2	1	3	B-039	activo
240	2	1	3	B-040	activo
241	2	1	3	B-041	activo
242	2	1	3	B-042	activo
243	2	1	3	B-043	activo
244	2	1	3	B-044	activo
245	2	1	3	B-045	activo
246	2	1	3	B-046	activo
247	2	1	3	B-047	activo
248	2	1	3	B-048	activo
249	2	1	3	B-049	activo
250	2	1	3	B-050	activo
251	2	1	3	B-051	activo
252	2	1	3	B-052	activo
253	2	1	3	B-053	activo
254	2	1	3	B-054	activo
255	2	1	3	B-055	activo
256	2	1	3	B-056	activo
257	2	1	3	B-057	activo
258	2	1	3	B-058	activo
259	2	1	3	B-059	activo
260	2	1	3	B-060	activo
261	2	1	3	B-061	activo
262	2	1	3	B-062	activo
263	2	1	3	B-063	activo
264	2	1	3	B-064	activo
265	2	1	3	B-065	activo
266	2	1	3	B-066	activo
267	2	1	3	B-067	activo
268	2	1	3	B-068	activo
269	2	1	3	B-069	activo
270	2	1	3	B-070	activo
271	2	1	3	B-071	activo
272	2	1	3	B-072	activo
273	2	1	3	B-073	activo
274	2	1	3	B-074	activo
275	2	1	3	B-075	activo
276	2	1	3	B-076	activo
277	2	1	3	B-077	activo
278	2	1	3	B-078	activo
279	2	1	3	B-079	activo
280	2	1	3	B-080	activo
281	2	1	3	B-081	activo
282	2	1	3	B-082	activo
283	2	1	3	B-083	activo
284	2	1	3	B-084	activo
285	2	1	3	B-085	activo
286	2	1	3	B-086	activo
287	2	1	3	B-087	activo
288	2	1	3	B-088	activo
289	2	1	3	B-089	activo
290	2	1	3	B-090	activo
291	2	1	3	B-091	inactivo
292	2	1	3	B-092	activo
293	2	1	3	B-093	activo
294	2	1	3	B-094	activo
295	2	1	3	B-095	activo
296	2	1	3	B-096	activo
297	2	1	3	B-097	activo
298	2	1	3	B-098	activo
299	2	1	3	B-099	activo
300	2	1	3	B-100	activo
301	2	1	3	B-101	activo
302	2	1	3	B-102	activo
303	2	1	3	B-103	activo
304	2	1	3	B-104	activo
305	2	1	3	B-105	activo
306	2	1	3	B-106	activo
307	2	1	3	B-107	activo
308	2	1	3	B-108	activo
309	2	1	3	B-109	activo
310	2	1	3	B-110	activo
311	2	1	3	B-111	activo
312	2	1	3	B-112	activo
313	2	1	3	B-113	activo
314	2	1	3	B-114	activo
315	2	1	3	B-115	activo
316	2	1	3	B-116	activo
317	2	1	3	B-117	activo
318	2	1	3	B-118	activo
319	2	1	3	B-119	activo
320	2	1	3	B-120	activo
321	2	1	3	B-121	activo
322	2	1	3	B-122	activo
323	2	1	3	B-123	activo
324	2	1	3	B-124	activo
325	2	1	3	B-125	activo
326	2	1	3	B-126	activo
327	2	1	3	B-127	activo
328	2	1	3	B-128	activo
329	2	1	3	B-129	activo
330	2	1	3	B-130	activo
331	2	1	3	B-131	activo
332	2	1	3	B-132	activo
333	2	1	3	B-133	activo
334	2	1	3	B-134	activo
335	2	1	3	B-135	activo
336	2	1	3	B-136	activo
337	2	1	3	B-137	activo
338	2	1	3	B-138	activo
339	2	1	3	B-139	activo
340	2	1	3	B-140	activo
341	2	1	3	B-141	activo
342	2	1	3	B-142	activo
343	2	1	3	B-143	activo
344	2	1	3	B-144	activo
345	2	1	3	B-145	activo
346	2	1	3	B-146	activo
347	2	1	3	B-147	activo
348	2	1	3	B-148	activo
349	2	1	3	B-149	activo
350	2	1	3	B-150	activo
351	2	1	3	B-151	activo
352	2	1	3	B-152	activo
353	2	1	3	B-153	activo
354	2	1	3	B-154	activo
355	2	1	3	B-155	activo
356	2	1	3	B-156	activo
357	2	1	3	B-157	activo
358	2	1	3	B-158	activo
359	2	1	3	B-159	activo
360	2	1	3	B-160	activo
361	2	1	3	B-161	activo
362	2	1	3	B-162	activo
363	2	1	3	B-163	activo
364	2	1	3	B-164	activo
365	2	1	3	B-165	activo
366	2	1	3	B-166	activo
367	2	1	3	B-167	activo
368	2	1	3	B-168	activo
369	2	1	3	B-169	activo
370	2	1	3	B-170	activo
371	2	1	3	B-171	activo
372	2	1	3	B-172	activo
373	2	1	3	B-173	activo
374	2	1	3	B-174	activo
375	2	1	3	B-175	activo
376	2	1	3	B-176	activo
377	2	1	3	B-177	activo
378	2	1	3	B-178	activo
379	2	1	3	B-179	activo
380	2	1	3	B-180	activo
381	2	1	3	B-181	activo
382	2	1	3	B-182	activo
383	2	1	3	B-183	activo
384	2	1	3	B-184	activo
385	2	1	3	B-185	activo
386	2	1	3	B-186	activo
387	2	1	3	B-187	activo
388	2	1	3	B-188	inactivo
389	2	1	3	B-189	activo
390	2	1	3	B-190	activo
391	2	1	3	B-191	activo
392	2	1	3	B-192	activo
393	2	1	3	B-193	activo
394	2	1	3	B-194	activo
395	2	1	3	B-195	activo
396	2	1	3	B-196	activo
397	2	1	3	B-197	activo
398	2	1	3	B-198	activo
399	2	1	3	B-199	activo
400	2	1	3	B-200	activo
401	3	1	5	C-001	activo
402	3	1	5	C-002	activo
403	3	1	5	C-003	activo
404	3	1	5	C-004	activo
405	3	1	5	C-005	activo
406	3	1	5	C-006	activo
407	3	1	5	C-007	activo
408	3	1	5	C-008	activo
409	3	1	5	C-009	activo
410	3	1	5	C-010	activo
411	3	1	5	C-011	activo
412	3	1	5	C-012	activo
413	3	1	5	C-013	activo
414	3	1	5	C-014	activo
415	3	1	5	C-015	activo
416	3	1	5	C-016	activo
417	3	1	5	C-017	activo
418	3	1	5	C-018	activo
419	3	1	5	C-019	activo
420	3	1	5	C-020	activo
421	3	1	5	C-021	activo
422	3	1	5	C-022	activo
423	3	1	5	C-023	activo
424	3	1	5	C-024	activo
425	3	1	5	C-025	activo
426	3	1	5	C-026	activo
427	3	1	5	C-027	activo
428	3	1	5	C-028	activo
429	3	1	5	C-029	activo
430	3	1	5	C-030	activo
431	3	1	5	C-031	activo
432	3	1	5	C-032	activo
433	3	1	5	C-033	activo
434	3	1	5	C-034	activo
435	3	1	5	C-035	activo
436	3	1	5	C-036	activo
437	3	1	5	C-037	activo
438	3	1	5	C-038	activo
439	3	1	5	C-039	activo
440	3	1	5	C-040	activo
441	4	1	6	D-001	activo
442	4	1	6	D-002	activo
443	4	1	6	D-003	activo
444	4	1	6	D-004	activo
445	4	1	6	D-005	activo
446	4	1	6	D-006	activo
447	4	1	6	D-007	activo
448	4	1	6	D-008	activo
449	4	1	6	D-009	activo
450	4	1	6	D-010	activo
451	4	1	6	D-011	activo
452	4	1	6	D-012	activo
453	4	1	6	D-013	activo
454	4	1	6	D-014	activo
455	4	1	6	D-015	activo
456	4	1	6	D-016	activo
457	4	1	6	D-017	activo
458	4	1	6	D-018	activo
459	4	1	6	D-019	activo
460	4	1	6	D-020	activo
461	4	1	6	D-021	activo
462	4	1	6	D-022	activo
463	4	1	6	D-023	activo
464	4	1	6	D-024	activo
465	4	1	6	D-025	activo
466	4	1	6	D-026	activo
467	4	1	6	D-027	activo
468	4	1	6	D-028	activo
469	4	1	6	D-029	activo
470	4	1	6	D-030	activo
471	5	1	4	E-001	activo
472	5	1	4	E-002	activo
473	5	1	4	E-003	activo
474	5	1	4	E-004	activo
475	5	1	4	E-005	activo
476	5	1	4	E-006	activo
477	5	1	4	E-007	activo
478	5	1	4	E-008	activo
479	5	1	4	E-009	activo
480	5	1	4	E-010	activo
481	5	1	4	E-011	activo
482	5	1	4	E-012	activo
483	5	1	4	E-013	activo
484	5	1	4	E-014	activo
485	5	1	4	E-015	inactivo
486	5	1	4	E-016	activo
487	5	1	4	E-017	activo
488	5	1	4	E-018	activo
489	5	1	4	E-019	activo
490	5	1	4	E-020	activo
491	5	1	4	E-021	activo
492	5	1	4	E-022	activo
493	5	1	4	E-023	activo
494	5	1	4	E-024	activo
495	5	1	4	E-025	activo
496	5	1	4	E-026	activo
497	5	1	4	E-027	activo
498	5	1	4	E-028	activo
499	5	1	4	E-029	activo
500	5	1	4	E-030	activo
\.


--
-- Data for Name: estacionamiento; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.estacionamiento (id_estacionamiento, nombre_parqueadero, identificacion, direccion, telefono, capacidad_total, id_propietario) FROM stdin;
1	Parqueadero Central 24/7	900123456-7	Calle 45 # 13-20, Bogota D.C.	6017654321	500	\N
\.


--
-- Data for Name: pago; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pago (id_pago, id_ticket, id_tarifa, monto_total, metodo_pago, estado_pago, fecha_pago, referencia_transaccion, id_reserva) FROM stdin;
1	1	1	60000.00	Efectivo	Aprobado	2026-09-14 09:07:00	TRX-20260914-0001	\N
2	2	2	9000.00	Tarjeta Debito	Aprobado	2026-09-14 08:47:00	TRX-20260914-0002	\N
3	3	3	6000.00	PSE	Aprobado	2026-09-14 11:03:00	TRX-20260914-0003	\N
4	4	1	20000.00	Tarjeta Credito	Aprobado	2026-09-15 07:52:00	TRX-20260915-0004	\N
5	5	2	36000.00	Efectivo	Aprobado	2026-09-15 11:02:00	TRX-20260915-0005	\N
6	6	1	25000.00	PSE	Aprobado	2026-09-15 18:05:00	TRX-20260915-0006	\N
7	7	5	15000.00	Tarjeta Debito	Aprobado	2026-09-15 13:32:00	TRX-20260915-0007	\N
8	8	2	5000.00	Efectivo	Aprobado	2026-09-15 15:26:00	TRX-20260915-0008	\N
9	9	1	45000.00	Tarjeta Debito	Pendiente	2026-09-16 06:42:00	\N	\N
10	14	2	12000.00	PSE	Aprobado	2026-09-16 06:02:00	TRX-20260916-0010	\N
11	10	1	30000.00	Tarjeta Credito	Rechazado	2026-09-16 08:00:00	TRX-20260916-0011	\N
12	15	1	60000.00	Tarjeta Debito	Aprobado	2026-09-16 15:23:51.179767	TRX-SIM-0001	\N
\.


--
-- Data for Name: reserva; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reserva (id_reserva, id_usuario, id_vehiculo, id_estacionamiento, id_espacio, id_zona, fecha_reserva, fecha_hora_fin, estado_reserva) FROM stdin;
1	4	4	1	2	1	2026-09-15 07:00:00	2026-09-15 09:00:00	finalizada
2	6	7	1	3	1	2026-09-15 06:00:00	2026-09-15 18:00:00	finalizada
3	2	2	1	210	2	2026-09-14 10:00:00	2026-09-14 12:00:00	cancelada
4	11	12	1	11	1	2026-09-17 08:00:00	2026-09-17 12:00:00	activa
5	9	10	1	211	2	2026-09-17 09:00:00	2026-09-17 11:00:00	activa
6	10	11	1	410	3	2026-09-18 07:00:00	2026-09-18 10:00:00	activa
8	12	13	1	212	2	2026-09-13 14:00:00	2026-09-13 16:00:00	cancelada
9	13	16	1	6	1	2026-09-16 15:21:01.231952	2026-09-16 17:21:01.231952	finalizada
7	8	9	1	4	1	2026-09-16 05:00:00	2026-09-16 07:00:00	finalizada
\.


--
-- Data for Name: rol; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rol (id_rol, nombre_rol, descripcion) FROM stdin;
1	cliente	Registra vehículos, reserva y paga
2	dueno	Gestiona su parqueadero, espacios y tarifas
3	administrador	Supervisa toda la plataforma
\.


--
-- Data for Name: tarifa; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tarifa (id_tarifa, id_tipo_vehiculo, id_estacionamiento, valor_minuto, valor_dia, valor_mensualidad, fecha_vigencia_inicio, fecha_vigencia_fin) FROM stdin;
1	1	1	500.00	25000.00	350000.00	2026-01-01	\N
2	2	1	200.00	10000.00	150000.00	2026-01-01	\N
3	3	1	50.00	4000.00	60000.00	2026-01-01	\N
4	4	1	50.00	4000.00	60000.00	2026-01-01	\N
5	5	1	50.00	4000.00	60000.00	2026-01-01	\N
6	1	1	450.00	22000.00	320000.00	2025-01-01	2025-12-31
7	2	1	180.00	9000.00	135000.00	2025-01-01	2025-12-31
8	3	1	40.00	3500.00	55000.00	2025-01-01	2025-12-31
9	4	1	40.00	3500.00	55000.00	2025-01-01	2025-12-31
10	5	1	40.00	3500.00	55000.00	2025-01-01	2025-12-31
\.


--
-- Data for Name: ticket; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ticket (id_ticket, id_vehiculo, id_espacio, id_reserva, fecha_hora_entrada, fecha_hora_salida, estado_ticket) FROM stdin;
1	1	1	\N	2026-09-14 07:05:00	2026-09-14 09:05:00	Finalizado
2	2	201	\N	2026-09-14 08:00:00	2026-09-14 08:45:00	Finalizado
3	3	401	\N	2026-09-14 09:00:00	2026-09-14 11:00:00	Finalizado
4	4	2	1	2026-09-15 07:10:00	2026-09-15 07:50:00	Finalizado
5	5	202	\N	2026-09-15 08:00:00	2026-09-15 11:00:00	Finalizado
6	7	3	2	2026-09-15 06:00:00	2026-09-15 18:00:00	Finalizado
7	8	441	\N	2026-09-15 08:30:00	2026-09-15 13:30:00	Finalizado
8	6	203	\N	2026-09-15 15:00:00	2026-09-15 15:25:00	Finalizado
9	9	4	7	2026-09-16 05:10:00	\N	Activo
10	12	5	\N	2026-09-16 07:30:00	\N	Activo
11	10	205	\N	2026-09-16 08:15:00	\N	Activo
12	11	405	\N	2026-09-16 09:00:00	\N	Activo
13	15	471	\N	2026-09-16 09:20:00	\N	Activo
14	13	206	\N	2026-09-16 06:00:00	\N	Pagado
15	16	6	9	2026-09-16 15:21:29.707677	2026-09-16 17:21:29.707677	Finalizado
\.


--
-- Data for Name: tipo_espacio; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tipo_espacio (id_tipo_espacio, nombre_tipo, descripcion) FROM stdin;
1	Carro estandar	Celda para automovil o camioneta liviana
2	Carro accesible	Celda ampliada para personas con movilidad reducida
3	Moto estandar	Celda demarcada para motocicleta
4	Moto electrica	Celda para moto con punto de carga
5	Bicicleta	Cicloparqueadero con anclaje tipo U invertida
6	Patineta	Casillero para patineta o scooter electrico
\.


--
-- Data for Name: tipo_vehiculo; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tipo_vehiculo (id_tipo_vehiculo, nombre_tipo, descripcion) FROM stdin;
1	Carro	Automovil, camioneta o vehiculo de cuatro ruedas
2	Moto	Motocicleta de combustion con placa
3	bicicleta	Bicicleta convencional o electrica
4	Moto electrica	Motocicleta electrica liviana
5	Patineta	Patineta o scooter electrico
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuario (id_usuario, nombres, apellidos, documento_id, telefono, correo, fecha_registro, id_rol, password_hash) FROM stdin;
1	Andres Felipe	Gomez Rincon	1012345678	3001234567	andres.gomez@correo.com	2026-01-12	1	\N
2	Laura Camila	Martinez Ospina	1023456789	3109876543	laura.martinez@correo.com	2026-01-20	1	\N
3	Juan Sebastian	Ramirez Pena	1034567890	3204567890	juan.ramirez@correo.com	2026-02-03	1	\N
4	Diana Carolina	Lopez Cardenas	1045678901	3157654321	diana.lopez@correo.com	2026-02-14	1	\N
5	Carlos Alberto	Herrera Suarez	79456123	3012223344	carlos.herrera@correo.com	2026-02-27	1	\N
6	Maria Fernanda	Castro Nino	1056789012	3183334455	maria.castro@correo.com	2026-03-08	1	\N
7	Julian David	Vargas Molina	1067890123	3024445566	julian.vargas@correo.com	2026-03-19	1	\N
8	Paola Andrea	Sanchez Torres	52789456	3115556677	paola.sanchez@correo.com	2026-04-02	1	\N
9	Kevin Esteban	Moreno Quintero	1078901234	3226667788	kevin.moreno@correo.com	2026-04-21	1	\N
10	Sara Valentina	Rojas Beltran	1089012345	3137778899	sara.rojas@correo.com	2026-05-10	1	\N
11	Oscar Mauricio	Cifuentes Aguirre	80123456	3048889900	oscar.cifuentes@correo.com	2026-06-05	1	\N
12	Natalia	Guerrero Pinilla	1090123456	3169990011	natalia.guerrero@correo.com	2026-07-18	1	\N
13	Camila Andrea	Restrepo Vega	1101234567	3011112233	camila.restrepo@correo.com	2026-09-16	1	\N
\.


--
-- Data for Name: vehiculo; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vehiculo (id_vehiculo, id_usuario, id_tipo_vehiculo, placa, marca, modelo, color) FROM stdin;
1	1	1	ABC123	Chevrolet	Spark GT	Rojo
2	2	2	XYZ45C	Yamaha	FZ 2.0	Azul
3	3	3	BIC-0001	Specialized	Sirrus X	Naranja
4	4	1	DEF456	Renault	Logan	Gris
5	5	2	GHI78D	Bajaj	Pulsar NS 200	Negro
6	1	2	JKL90E	Honda	CB 125F	Blanco
7	6	1	MNO321	Mazda	3 Touring	Blanco
8	7	5	PAT-0001	Xiaomi	Mi Scooter 3	Negro
9	8	1	PQR654	Kia	Picanto	Plata
10	9	2	STU12F	Suzuki	Gixxer 150	Rojo
11	10	3	BIC-0002	Trek	FX 2 Disc	Verde
12	11	1	VWX987	Toyota	Corolla Cross	Azul
13	12	2	YZA34G	AKT	NKD 125	Negro
14	4	5	PAT-0002	Segway	Ninebot Max	Gris
15	6	4	ELE12A	Super Soco	TC Max	Blanco
16	13	1	SIM123	Chevrolet	Onix	Rojo
\.


--
-- Data for Name: zona; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.zona (id_zona, id_estacionamiento, id_tipo_vehiculo, nombre_zona, capacidad) FROM stdin;
1	1	1	Zona A - Carros	200
2	1	2	Zona B - Motos	200
3	1	3	Zona C1 - Bicicletas	40
4	1	5	Zona C2 - Patinetas	30
5	1	4	Zona C3 - Motos electricas	30
\.


--
-- Name: comprobante_id_comprobante_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.comprobante_id_comprobante_seq', 11, true);


--
-- Name: espacios_id_espacio_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.espacios_id_espacio_seq', 501, false);


--
-- Name: estacionamiento_id_estacionamiento_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.estacionamiento_id_estacionamiento_seq', 2, false);


--
-- Name: pago_id_pago_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pago_id_pago_seq', 16, true);


--
-- Name: reserva_id_reserva_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reserva_id_reserva_seq', 15, true);


--
-- Name: rol_id_rol_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.rol_id_rol_seq', 3, true);


--
-- Name: tarifa_id_tarifa_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tarifa_id_tarifa_seq', 11, false);


--
-- Name: ticket_id_ticket_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ticket_id_ticket_seq', 18, true);


--
-- Name: tipo_espacio_id_tipo_espacio_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tipo_espacio_id_tipo_espacio_seq', 7, false);


--
-- Name: tipo_vehiculo_id_tipo_vehiculo_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tipo_vehiculo_id_tipo_vehiculo_seq', 6, false);


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuario_id_usuario_seq', 14, false);


--
-- Name: vehiculo_id_vehiculo_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vehiculo_id_vehiculo_seq', 17, false);


--
-- Name: zona_id_zona_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.zona_id_zona_seq', 6, false);


--
-- Name: comprobante comprobante_id_pago_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobante
    ADD CONSTRAINT comprobante_id_pago_key UNIQUE (id_pago);


--
-- Name: comprobante comprobante_numero_comprobante_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobante
    ADD CONSTRAINT comprobante_numero_comprobante_key UNIQUE (numero_comprobante);


--
-- Name: comprobante comprobante_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobante
    ADD CONSTRAINT comprobante_pkey PRIMARY KEY (id_comprobante);


--
-- Name: espacios espacios_numero_por_parqueadero_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.espacios
    ADD CONSTRAINT espacios_numero_por_parqueadero_key UNIQUE (id_estacionamiento, numero_de_espacio);


--
-- Name: espacios espacios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.espacios
    ADD CONSTRAINT espacios_pkey PRIMARY KEY (id_espacio);


--
-- Name: estacionamiento estacionamiento_identificacion_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estacionamiento
    ADD CONSTRAINT estacionamiento_identificacion_key UNIQUE (identificacion);


--
-- Name: estacionamiento estacionamiento_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estacionamiento
    ADD CONSTRAINT estacionamiento_pkey PRIMARY KEY (id_estacionamiento);


--
-- Name: pago pago_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_pkey PRIMARY KEY (id_pago);


--
-- Name: pago pago_referencia_transaccion_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_referencia_transaccion_key UNIQUE (referencia_transaccion);


--
-- Name: reserva reserva_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_pkey PRIMARY KEY (id_reserva);


--
-- Name: reserva reserva_sin_traslape; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_sin_traslape EXCLUDE USING gist (id_espacio WITH =, tsrange(fecha_reserva, fecha_hora_fin) WITH &&) WHERE (((estado_reserva)::text = 'activa'::text));


--
-- Name: rol rol_nombre_rol_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_nombre_rol_key UNIQUE (nombre_rol);


--
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id_rol);


--
-- Name: tarifa tarifa_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tarifa
    ADD CONSTRAINT tarifa_pkey PRIMARY KEY (id_tarifa);


--
-- Name: ticket ticket_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ticket
    ADD CONSTRAINT ticket_pkey PRIMARY KEY (id_ticket);


--
-- Name: tipo_espacio tipo_espacio_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipo_espacio
    ADD CONSTRAINT tipo_espacio_pkey PRIMARY KEY (id_tipo_espacio);


--
-- Name: tipo_vehiculo tipo_vehiculo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipo_vehiculo
    ADD CONSTRAINT tipo_vehiculo_pkey PRIMARY KEY (id_tipo_vehiculo);


--
-- Name: usuario usuario_correo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_correo_key UNIQUE (correo);


--
-- Name: usuario usuario_documento_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_documento_id_key UNIQUE (documento_id);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);


--
-- Name: vehiculo vehiculo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_pkey PRIMARY KEY (id_vehiculo);


--
-- Name: vehiculo vehiculo_placa_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_placa_key UNIQUE (placa);


--
-- Name: zona zona_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.zona
    ADD CONSTRAINT zona_pkey PRIMARY KEY (id_zona);


--
-- Name: idx_pago_reserva; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pago_reserva ON public.pago USING btree (id_reserva);


--
-- Name: idx_pago_ticket; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pago_ticket ON public.pago USING btree (id_ticket);


--
-- Name: idx_reserva_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_reserva_usuario ON public.reserva USING btree (id_usuario);


--
-- Name: idx_ticket_espacio_abierto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ticket_espacio_abierto ON public.ticket USING btree (id_espacio) WHERE (fecha_hora_salida IS NULL);


--
-- Name: idx_vehiculo_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehiculo_usuario ON public.vehiculo USING btree (id_usuario);


--
-- Name: pago trg_calcular_pago; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_calcular_pago BEFORE INSERT ON public.pago FOR EACH ROW EXECUTE FUNCTION public.fn_calcular_monto_pago();


--
-- Name: espacios trg_capacidad_zona; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_capacidad_zona BEFORE INSERT ON public.espacios FOR EACH ROW EXECUTE FUNCTION public.fn_validar_capacidad_zona();


--
-- Name: pago trg_emitir_comprobante; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_emitir_comprobante AFTER INSERT OR UPDATE ON public.pago FOR EACH ROW EXECUTE FUNCTION public.fn_emitir_comprobante();


--
-- Name: ticket trg_espacio_libre; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_espacio_libre BEFORE INSERT ON public.ticket FOR EACH ROW EXECUTE FUNCTION public.fn_validar_espacio_libre();


--
-- Name: pago trg_estado_ticket; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_estado_ticket AFTER INSERT OR UPDATE ON public.pago FOR EACH ROW EXECUTE FUNCTION public.fn_actualizar_estado_ticket();


--
-- Name: ticket trg_finalizar_reserva; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_finalizar_reserva AFTER INSERT ON public.ticket FOR EACH ROW EXECUTE FUNCTION public.fn_finalizar_reserva();


--
-- Name: reserva trg_reserva_completar; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_reserva_completar BEFORE INSERT ON public.reserva FOR EACH ROW EXECUTE FUNCTION public.fn_completar_reserva();


--
-- Name: reserva trg_reserva_libre; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_reserva_libre BEFORE INSERT OR UPDATE ON public.reserva FOR EACH ROW WHEN (((new.estado_reserva)::text = 'activa'::text)) EXECUTE FUNCTION public.fn_validar_reserva_libre();


--
-- Name: reserva trg_validar_reserva; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_validar_reserva BEFORE INSERT ON public.reserva FOR EACH ROW EXECUTE FUNCTION public.fn_validar_tipo_espacio();


--
-- Name: ticket trg_validar_ticket; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_validar_ticket BEFORE INSERT ON public.ticket FOR EACH ROW EXECUTE FUNCTION public.fn_validar_tipo_espacio();


--
-- Name: comprobante comprobante_id_pago_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobante
    ADD CONSTRAINT comprobante_id_pago_fkey FOREIGN KEY (id_pago) REFERENCES public.pago(id_pago);


--
-- Name: espacios espacios_id_estacionamiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.espacios
    ADD CONSTRAINT espacios_id_estacionamiento_fkey FOREIGN KEY (id_estacionamiento) REFERENCES public.estacionamiento(id_estacionamiento);


--
-- Name: espacios espacios_id_tipo_espacio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.espacios
    ADD CONSTRAINT espacios_id_tipo_espacio_fkey FOREIGN KEY (id_tipo_espacio) REFERENCES public.tipo_espacio(id_tipo_espacio);


--
-- Name: espacios espacios_id_zona_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.espacios
    ADD CONSTRAINT espacios_id_zona_fkey FOREIGN KEY (id_zona) REFERENCES public.zona(id_zona);


--
-- Name: estacionamiento estacionamiento_id_propietario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estacionamiento
    ADD CONSTRAINT estacionamiento_id_propietario_fkey FOREIGN KEY (id_propietario) REFERENCES public.usuario(id_usuario);


--
-- Name: pago pago_id_reserva_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_id_reserva_fkey FOREIGN KEY (id_reserva) REFERENCES public.reserva(id_reserva);


--
-- Name: pago pago_id_tarifa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_id_tarifa_fkey FOREIGN KEY (id_tarifa) REFERENCES public.tarifa(id_tarifa);


--
-- Name: pago pago_id_ticket_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_id_ticket_fkey FOREIGN KEY (id_ticket) REFERENCES public.ticket(id_ticket);


--
-- Name: reserva reserva_id_espacio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_id_espacio_fkey FOREIGN KEY (id_espacio) REFERENCES public.espacios(id_espacio);


--
-- Name: reserva reserva_id_estacionamiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_id_estacionamiento_fkey FOREIGN KEY (id_estacionamiento) REFERENCES public.estacionamiento(id_estacionamiento);


--
-- Name: reserva reserva_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: reserva reserva_id_vehiculo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_id_vehiculo_fkey FOREIGN KEY (id_vehiculo) REFERENCES public.vehiculo(id_vehiculo);


--
-- Name: reserva reserva_id_zona_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reserva
    ADD CONSTRAINT reserva_id_zona_fkey FOREIGN KEY (id_zona) REFERENCES public.zona(id_zona);


--
-- Name: tarifa tarifa_id_estacionamiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tarifa
    ADD CONSTRAINT tarifa_id_estacionamiento_fkey FOREIGN KEY (id_estacionamiento) REFERENCES public.estacionamiento(id_estacionamiento);


--
-- Name: tarifa tarifa_id_tipo_vehiculo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tarifa
    ADD CONSTRAINT tarifa_id_tipo_vehiculo_fkey FOREIGN KEY (id_tipo_vehiculo) REFERENCES public.tipo_vehiculo(id_tipo_vehiculo);


--
-- Name: ticket ticket_id_espacio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ticket
    ADD CONSTRAINT ticket_id_espacio_fkey FOREIGN KEY (id_espacio) REFERENCES public.espacios(id_espacio);


--
-- Name: ticket ticket_id_reserva_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ticket
    ADD CONSTRAINT ticket_id_reserva_fkey FOREIGN KEY (id_reserva) REFERENCES public.reserva(id_reserva);


--
-- Name: ticket ticket_id_vehiculo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ticket
    ADD CONSTRAINT ticket_id_vehiculo_fkey FOREIGN KEY (id_vehiculo) REFERENCES public.vehiculo(id_vehiculo);


--
-- Name: usuario usuario_id_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.rol(id_rol);


--
-- Name: vehiculo vehiculo_id_tipo_vehiculo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_id_tipo_vehiculo_fkey FOREIGN KEY (id_tipo_vehiculo) REFERENCES public.tipo_vehiculo(id_tipo_vehiculo);


--
-- Name: vehiculo vehiculo_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: zona zona_id_estacionamiento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.zona
    ADD CONSTRAINT zona_id_estacionamiento_fkey FOREIGN KEY (id_estacionamiento) REFERENCES public.estacionamiento(id_estacionamiento);


--
-- Name: zona zona_id_tipo_vehiculo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.zona
    ADD CONSTRAINT zona_id_tipo_vehiculo_fkey FOREIGN KEY (id_tipo_vehiculo) REFERENCES public.tipo_vehiculo(id_tipo_vehiculo);


--
-- PostgreSQL database dump complete
--



-- Todas las fechas "sin zona" se interpretan en hora de Colombia.
DO $$ BEGIN
  EXECUTE format('ALTER DATABASE %I SET timezone = %L', current_database(), 'America/Bogota');
END $$;
