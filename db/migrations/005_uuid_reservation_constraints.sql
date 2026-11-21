-- Garantiza que reservas confirmadas no se crucen por espacio ni por vehículo.
-- Requiere 004_uuid_parking_schema.sql y una base PostgreSQL con btree_gist disponible.
BEGIN;

CREATE EXTENSION IF NOT EXISTS btree_gist;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM reservations a
    JOIN reservations b
      ON a.id < b.id
     AND a.status = 'CONFIRMED'
     AND b.status = 'CONFIRMED'
     AND a.spot_id = b.spot_id
     AND tstzrange(a.start_time, a.end_time, '[)')
         && tstzrange(b.start_time, b.end_time, '[)')
  ) THEN
    RAISE EXCEPTION 'Hay reservas confirmadas solapadas por espacio; corrígelas antes de aplicar esta migración';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM reservations a
    JOIN reservations b
      ON a.id < b.id
     AND a.status = 'CONFIRMED'
     AND b.status = 'CONFIRMED'
     AND a.vehicle_id = b.vehicle_id
     AND tstzrange(a.start_time, a.end_time, '[)')
         && tstzrange(b.start_time, b.end_time, '[)')
  ) THEN
    RAISE EXCEPTION 'Hay reservas confirmadas solapadas por vehículo; corrígelas antes de aplicar esta migración';
  END IF;

  IF EXISTS (
    SELECT 1 FROM reservations WHERE end_time <= start_time
  ) THEN
    RAISE EXCEPTION 'Hay reservas con rangos de tiempo inválidos; corrígelas antes de aplicar esta migración';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'reservations'::regclass
      AND conname = 'ck_reservations_time_order'
  ) THEN
    ALTER TABLE reservations
      ADD CONSTRAINT ck_reservations_time_order CHECK (end_time > start_time);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'reservations'::regclass
      AND conname = 'ex_reservations_spot_time_overlap'
  ) THEN
    ALTER TABLE reservations
      ADD CONSTRAINT ex_reservations_spot_time_overlap
      EXCLUDE USING gist (
        spot_id WITH =,
        tstzrange(start_time, end_time, '[)') WITH &&
      )
      WHERE (status = 'CONFIRMED');
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'reservations'::regclass
      AND conname = 'ex_reservations_vehicle_time_overlap'
  ) THEN
    ALTER TABLE reservations
      ADD CONSTRAINT ex_reservations_vehicle_time_overlap
      EXCLUDE USING gist (
        vehicle_id WITH =,
        tstzrange(start_time, end_time, '[)') WITH &&
      )
      WHERE (status = 'CONFIRMED');
  END IF;
END $$;

COMMIT;
