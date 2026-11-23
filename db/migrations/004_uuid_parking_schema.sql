-- Dash Parking: catálogo de parqueaderos en la base UUID/SQLAlchemy.
-- Ejecutar contra dash_parking después de que existan las tablas base.
-- Repetible; no elimina ni modifica datos de dash_parking_v2.
BEGIN;

ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'OWNER';
ALTER TYPE vehicle_type ADD VALUE IF NOT EXISTS 'TRUCK';

-- Alinea cambios anteriores del modelo ORM con bases ya existentes.
ALTER TABLE users ADD COLUMN IF NOT EXISTS surname varchar(120);
ALTER TABLE users ADD COLUMN IF NOT EXISTS document_type varchar(30);
ALTER TABLE users ADD COLUMN IF NOT EXISTS document_number varchar(30);
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone varchar(30);
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS brand varchar(120);
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS color varchar(60);
ALTER TABLE vehicles ALTER COLUMN plate DROP NOT NULL;
ALTER TABLE parking_spots ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true;
ALTER TABLE parking_spots ALTER COLUMN zone TYPE varchar(100);

CREATE TABLE IF NOT EXISTS vehicle_categories (
  id uuid PRIMARY KEY,
  legacy_id integer UNIQUE,
  code varchar(40) NOT NULL UNIQUE,
  name varchar(100) NOT NULL,
  description varchar(255),
  is_active boolean NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS parking_space_types (
  id uuid PRIMARY KEY,
  legacy_id integer UNIQUE,
  code varchar(60) NOT NULL UNIQUE,
  name varchar(100) NOT NULL,
  description varchar(255)
);

CREATE TABLE IF NOT EXISTS parking_lots (
  id uuid PRIMARY KEY,
  legacy_id integer UNIQUE,
  owner_id uuid REFERENCES users(id) ON DELETE SET NULL,
  name varchar(100) NOT NULL,
  identification varchar(40) NOT NULL UNIQUE,
  address varchar(255) NOT NULL,
  phone varchar(30),
  total_capacity integer NOT NULL CHECK (total_capacity > 0),
  latitude double precision CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
  longitude double precision CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS parking_zones (
  id uuid PRIMARY KEY,
  legacy_id integer UNIQUE,
  parking_lot_id uuid NOT NULL REFERENCES parking_lots(id),
  vehicle_category_id uuid NOT NULL REFERENCES vehicle_categories(id),
  name varchar(100) NOT NULL,
  capacity integer NOT NULL CHECK (capacity > 0),
  CONSTRAINT uq_parking_zones_lot_name UNIQUE (parking_lot_id, name)
);

CREATE TABLE IF NOT EXISTS parking_lot_schedules (
  id uuid PRIMARY KEY,
  parking_lot_id uuid NOT NULL REFERENCES parking_lots(id) ON DELETE CASCADE,
  day_of_week smallint NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
  opens_at time,
  closes_at time,
  is_closed boolean NOT NULL DEFAULT false,
  is_24_hours boolean NOT NULL DEFAULT false,
  CONSTRAINT uq_parking_schedule_day UNIQUE (parking_lot_id, day_of_week),
  CONSTRAINT ck_parking_schedule_hours CHECK (
    (is_closed AND opens_at IS NULL AND closes_at IS NULL AND NOT is_24_hours) OR
    (NOT is_closed AND (
      (is_24_hours AND opens_at IS NULL AND closes_at IS NULL) OR
      (NOT is_24_hours AND opens_at IS NOT NULL AND closes_at IS NOT NULL AND opens_at <> closes_at)
    ))
  )
);

CREATE TABLE IF NOT EXISTS parking_rates (
  id uuid PRIMARY KEY,
  legacy_id integer UNIQUE,
  parking_lot_id uuid NOT NULL REFERENCES parking_lots(id) ON DELETE CASCADE,
  vehicle_category_id uuid NOT NULL REFERENCES vehicle_categories(id),
  price_per_minute numeric(10,2) NOT NULL CHECK (price_per_minute > 0),
  price_per_day numeric(10,2) CHECK (price_per_day IS NULL OR price_per_day > 0),
  price_per_month numeric(10,2) CHECK (price_per_month IS NULL OR price_per_month > 0),
  valid_from date NOT NULL,
  valid_to date CHECK (valid_to IS NULL OR valid_to >= valid_from),
  CONSTRAINT uq_parking_rates_lot_category_start
    UNIQUE (parking_lot_id, vehicle_category_id, valid_from)
);

CREATE TABLE IF NOT EXISTS parking_lot_members (
  id uuid PRIMARY KEY,
  parking_lot_id uuid NOT NULL REFERENCES parking_lots(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_by uuid NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_parking_lot_member UNIQUE (parking_lot_id, user_id)
);

ALTER TABLE parking_spots ADD COLUMN IF NOT EXISTS parking_lot_id uuid;
ALTER TABLE parking_spots ADD COLUMN IF NOT EXISTS parking_zone_id uuid;
ALTER TABLE parking_spots ADD COLUMN IF NOT EXISTS vehicle_category_id uuid;
ALTER TABLE parking_spots ADD COLUMN IF NOT EXISTS space_type_id uuid;
ALTER TABLE parking_spots ADD COLUMN IF NOT EXISTS legacy_id integer;
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS vehicle_category_id uuid;
ALTER TABLE reservations ADD COLUMN IF NOT EXISTS parking_lot_id uuid;
ALTER TABLE parking_spots DROP CONSTRAINT IF EXISTS parking_spots_code_key;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_parking_spots_lot') THEN
    ALTER TABLE parking_spots ADD CONSTRAINT fk_parking_spots_lot
      FOREIGN KEY (parking_lot_id) REFERENCES parking_lots(id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_parking_spots_zone') THEN
    ALTER TABLE parking_spots ADD CONSTRAINT fk_parking_spots_zone
      FOREIGN KEY (parking_zone_id) REFERENCES parking_zones(id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_parking_spots_vehicle_category') THEN
    ALTER TABLE parking_spots ADD CONSTRAINT fk_parking_spots_vehicle_category
      FOREIGN KEY (vehicle_category_id) REFERENCES vehicle_categories(id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_parking_spots_space_type') THEN
    ALTER TABLE parking_spots ADD CONSTRAINT fk_parking_spots_space_type
      FOREIGN KEY (space_type_id) REFERENCES parking_space_types(id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_parking_spots_legacy_id') THEN
    ALTER TABLE parking_spots ADD CONSTRAINT uq_parking_spots_legacy_id UNIQUE (legacy_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_parking_spots_lot_code') THEN
    ALTER TABLE parking_spots ADD CONSTRAINT uq_parking_spots_lot_code
      UNIQUE (parking_lot_id, code);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_vehicles_vehicle_category') THEN
    ALTER TABLE vehicles ADD CONSTRAINT fk_vehicles_vehicle_category
      FOREIGN KEY (vehicle_category_id) REFERENCES vehicle_categories(id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_reservations_parking_lot') THEN
    ALTER TABLE reservations ADD CONSTRAINT fk_reservations_parking_lot
      FOREIGN KEY (parking_lot_id) REFERENCES parking_lots(id);
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_parking_lots_owner_id ON parking_lots(owner_id);
CREATE INDEX IF NOT EXISTS ix_parking_zones_parking_lot_id ON parking_zones(parking_lot_id);
CREATE INDEX IF NOT EXISTS ix_parking_zones_vehicle_category_id
  ON parking_zones(vehicle_category_id);
CREATE INDEX IF NOT EXISTS ix_parking_spots_parking_lot_id ON parking_spots(parking_lot_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_parking_spots_unassigned_code
  ON parking_spots(code) WHERE parking_lot_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_parking_spots_parking_zone_id ON parking_spots(parking_zone_id);
CREATE INDEX IF NOT EXISTS ix_parking_spots_vehicle_category_id
  ON parking_spots(vehicle_category_id);
CREATE INDEX IF NOT EXISTS ix_parking_spots_space_type_id ON parking_spots(space_type_id);
CREATE INDEX IF NOT EXISTS ix_vehicles_vehicle_category_id ON vehicles(vehicle_category_id);
CREATE INDEX IF NOT EXISTS ix_reservations_parking_lot_id ON reservations(parking_lot_id);
CREATE INDEX IF NOT EXISTS ix_parking_rates_parking_lot_id ON parking_rates(parking_lot_id);
CREATE INDEX IF NOT EXISTS ix_parking_rates_vehicle_category_id
  ON parking_rates(vehicle_category_id);
CREATE INDEX IF NOT EXISTS ix_parking_lot_members_user_id ON parking_lot_members(user_id);

COMMIT;
