-- Versioned initial PostgreSQL schema for the UUID application database.
BEGIN;
CREATE TYPE session_status AS ENUM ('ACTIVE', 'COMPLETED');
CREATE TYPE vehicle_type AS ENUM ('CAR', 'MOTORCYCLE', 'BICYCLE', 'ELECTRIC_MOTORCYCLE', 'SCOOTER', 'TRUCK');
CREATE TYPE spot_status AS ENUM ('AVAILABLE', 'OCCUPIED', 'RESERVED');
CREATE TYPE payment_method AS ENUM ('CASH', 'VIRTUAL', 'QR');
CREATE TYPE payment_status AS ENUM ('PENDING', 'PAID', 'REJECTED');
CREATE TYPE reservation_status AS ENUM ('CONFIRMED', 'CANCELLED', 'COMPLETED');
CREATE TYPE user_role AS ENUM ('CLIENT', 'OPERATOR', 'OWNER', 'ADMIN');

CREATE TABLE parking_space_types (
	id UUID NOT NULL, 
	legacy_id INTEGER, 
	code VARCHAR(60) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description VARCHAR(255), 
	PRIMARY KEY (id), 
	UNIQUE (legacy_id), 
	UNIQUE (code)
)

;

CREATE TABLE password_reset_attempts (
	id UUID NOT NULL, 
	email_hash VARCHAR(64) NOT NULL, 
	ip_hash VARCHAR(64) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
)

;
CREATE INDEX ix_password_reset_attempts_created ON password_reset_attempts (created_at);
CREATE INDEX ix_password_reset_attempts_email_created ON password_reset_attempts (email_hash, created_at);
CREATE INDEX ix_password_reset_attempts_ip_created ON password_reset_attempts (ip_hash, created_at);

CREATE TABLE rates (
	id UUID NOT NULL, 
	vehicle_type vehicle_type NOT NULL, 
	price_per_hour NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (vehicle_type)
)

;

CREATE TABLE users (
	id UUID NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	surname VARCHAR(120), 
	document_type VARCHAR(30), 
	document_number VARCHAR(30), 
	phone VARCHAR(30), 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role user_role NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
)

;
CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE vehicle_categories (
	id UUID NOT NULL, 
	legacy_id INTEGER, 
	code VARCHAR(40) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description VARCHAR(255), 
	is_active BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (legacy_id), 
	UNIQUE (code)
)

;

CREATE TABLE parking_lots (
	id UUID NOT NULL, 
	legacy_id INTEGER, 
	owner_id UUID, 
	name VARCHAR(100) NOT NULL, 
	identification VARCHAR(40) NOT NULL, 
	address VARCHAR(255) NOT NULL, 
	phone VARCHAR(30), 
	total_capacity INTEGER NOT NULL, 
	latitude FLOAT, 
	longitude FLOAT, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_parking_lots_capacity_positive CHECK (total_capacity > 0), 
	CONSTRAINT ck_parking_lots_latitude_range CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90), 
	CONSTRAINT ck_parking_lots_longitude_range CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180), 
	UNIQUE (legacy_id), 
	FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE SET NULL, 
	UNIQUE (identification)
)

;
CREATE INDEX ix_parking_lots_owner_id ON parking_lots (owner_id);

CREATE TABLE password_reset_tokens (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	token_hash VARCHAR(64) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	used_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_password_reset_tokens_hash UNIQUE (token_hash), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)

;
CREATE INDEX ix_password_reset_tokens_user_used ON password_reset_tokens (user_id, used_at);

CREATE TABLE vehicles (
	id UUID NOT NULL, 
	plate VARCHAR(10), 
	vehicle_type vehicle_type NOT NULL, 
	vehicle_category_id UUID, 
	brand VARCHAR(120), 
	model VARCHAR(120), 
	color VARCHAR(60), 
	owner_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_vehicles_plate UNIQUE (plate), 
	CONSTRAINT fk_vehicles_vehicle_category FOREIGN KEY(vehicle_category_id) REFERENCES vehicle_categories (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id)
)

;
CREATE INDEX ix_vehicles_plate ON vehicles (plate);

CREATE TABLE parking_lot_members (
	id UUID NOT NULL, 
	parking_lot_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	created_by UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_parking_lot_member UNIQUE (parking_lot_id, user_id), 
	FOREIGN KEY(parking_lot_id) REFERENCES parking_lots (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(created_by) REFERENCES users (id)
)

;
CREATE INDEX ix_parking_lot_members_user_id ON parking_lot_members (user_id);
CREATE INDEX ix_parking_lot_members_parking_lot_id ON parking_lot_members (parking_lot_id);

CREATE TABLE parking_lot_schedules (
	id UUID NOT NULL, 
	parking_lot_id UUID NOT NULL, 
	day_of_week SMALLINT NOT NULL, 
	opens_at TIME WITHOUT TIME ZONE, 
	closes_at TIME WITHOUT TIME ZONE, 
	is_closed BOOLEAN NOT NULL, 
	is_24_hours BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_parking_schedule_day CHECK (day_of_week BETWEEN 0 AND 6), 
	CONSTRAINT ck_parking_schedule_hours CHECK ((is_closed AND opens_at IS NULL AND closes_at IS NULL AND NOT is_24_hours) OR (NOT is_closed AND ((is_24_hours AND opens_at IS NULL AND closes_at IS NULL) OR (NOT is_24_hours AND opens_at IS NOT NULL AND closes_at IS NOT NULL AND opens_at <> closes_at)))), 
	CONSTRAINT uq_parking_schedule_day UNIQUE (parking_lot_id, day_of_week), 
	FOREIGN KEY(parking_lot_id) REFERENCES parking_lots (id) ON DELETE CASCADE
)

;
CREATE INDEX ix_parking_lot_schedules_parking_lot_id ON parking_lot_schedules (parking_lot_id);

CREATE TABLE parking_rates (
	id UUID NOT NULL, 
	legacy_id INTEGER, 
	parking_lot_id UUID NOT NULL, 
	vehicle_category_id UUID NOT NULL, 
	price_per_minute NUMERIC(10, 2) NOT NULL, 
	price_per_day NUMERIC(10, 2), 
	price_per_month NUMERIC(10, 2), 
	valid_from DATE NOT NULL, 
	valid_to DATE, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_parking_rates_minute_positive CHECK (price_per_minute > 0), 
	CONSTRAINT ck_parking_rates_day_positive CHECK (price_per_day IS NULL OR price_per_day > 0), 
	CONSTRAINT ck_parking_rates_month_positive CHECK (price_per_month IS NULL OR price_per_month > 0), 
	CONSTRAINT ck_parking_rates_valid_dates CHECK (valid_to IS NULL OR valid_to >= valid_from), 
	CONSTRAINT uq_parking_rates_lot_category_start UNIQUE (parking_lot_id, vehicle_category_id, valid_from), 
	UNIQUE (legacy_id), 
	FOREIGN KEY(parking_lot_id) REFERENCES parking_lots (id) ON DELETE CASCADE, 
	FOREIGN KEY(vehicle_category_id) REFERENCES vehicle_categories (id)
)

;
CREATE INDEX ix_parking_rates_parking_lot_id ON parking_rates (parking_lot_id);
CREATE INDEX ix_parking_rates_vehicle_category_id ON parking_rates (vehicle_category_id);

CREATE TABLE parking_zones (
	id UUID NOT NULL, 
	legacy_id INTEGER, 
	parking_lot_id UUID NOT NULL, 
	vehicle_category_id UUID NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	capacity INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_parking_zones_capacity_positive CHECK (capacity > 0), 
	CONSTRAINT uq_parking_zones_lot_name UNIQUE (parking_lot_id, name), 
	UNIQUE (legacy_id), 
	FOREIGN KEY(parking_lot_id) REFERENCES parking_lots (id), 
	FOREIGN KEY(vehicle_category_id) REFERENCES vehicle_categories (id)
)

;
CREATE INDEX ix_parking_zones_vehicle_category_id ON parking_zones (vehicle_category_id);
CREATE INDEX ix_parking_zones_parking_lot_id ON parking_zones (parking_lot_id);

CREATE TABLE vehicle_qr_tokens (
	id UUID NOT NULL, 
	vehicle_id UUID NOT NULL, 
	token VARCHAR(64) NOT NULL, 
	used_for_entry BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (vehicle_id), 
	FOREIGN KEY(vehicle_id) REFERENCES vehicles (id)
)

;
CREATE UNIQUE INDEX ix_vehicle_qr_tokens_token ON vehicle_qr_tokens (token);

CREATE TABLE parking_spots (
	id UUID NOT NULL, 
	code VARCHAR(10) NOT NULL, 
	zone VARCHAR(100) NOT NULL, 
	vehicle_type vehicle_type NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	parking_lot_id UUID, 
	parking_zone_id UUID, 
	vehicle_category_id UUID, 
	space_type_id UUID, 
	legacy_id INTEGER, 
	status spot_status NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_parking_spots_legacy_id UNIQUE (legacy_id), 
	CONSTRAINT uq_parking_spots_lot_code UNIQUE (parking_lot_id, code), 
	CONSTRAINT fk_parking_spots_lot FOREIGN KEY(parking_lot_id) REFERENCES parking_lots (id), 
	CONSTRAINT fk_parking_spots_zone FOREIGN KEY(parking_zone_id) REFERENCES parking_zones (id), 
	CONSTRAINT fk_parking_spots_vehicle_category FOREIGN KEY(vehicle_category_id) REFERENCES vehicle_categories (id), 
	CONSTRAINT fk_parking_spots_space_type FOREIGN KEY(space_type_id) REFERENCES parking_space_types (id)
)

;
CREATE UNIQUE INDEX uq_parking_spots_unassigned_code ON parking_spots (code) WHERE parking_lot_id IS NULL;

CREATE TABLE reservations (
	id UUID NOT NULL, 
	vehicle_id UUID NOT NULL, 
	spot_id UUID NOT NULL, 
	parking_lot_id UUID, 
	vehicle_type vehicle_type NOT NULL, 
	start_time TIMESTAMP WITH TIME ZONE NOT NULL, 
	end_time TIMESTAMP WITH TIME ZONE NOT NULL, 
	status reservation_status NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_reservations_time_order CHECK (end_time > start_time), 
	FOREIGN KEY(vehicle_id) REFERENCES vehicles (id), 
	FOREIGN KEY(spot_id) REFERENCES parking_spots (id), 
	CONSTRAINT fk_reservations_parking_lot FOREIGN KEY(parking_lot_id) REFERENCES parking_lots (id)
)

;

CREATE TABLE parking_sessions (
	id UUID NOT NULL, 
	vehicle_id UUID NOT NULL, 
	spot_id UUID NOT NULL, 
	reservation_id UUID, 
	entry_time TIMESTAMP WITH TIME ZONE NOT NULL, 
	exit_time TIMESTAMP WITH TIME ZONE, 
	status session_status NOT NULL, 
	amount NUMERIC(10, 2), 
	PRIMARY KEY (id), 
	FOREIGN KEY(vehicle_id) REFERENCES vehicles (id), 
	FOREIGN KEY(spot_id) REFERENCES parking_spots (id), 
	FOREIGN KEY(reservation_id) REFERENCES reservations (id)
)

;

CREATE TABLE payments (
	id UUID NOT NULL, 
	session_id UUID NOT NULL, 
	amount NUMERIC(10, 2) NOT NULL, 
	method payment_method NOT NULL, 
	status payment_status NOT NULL, 
	reference VARCHAR(60) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(session_id) REFERENCES parking_sessions (id), 
	UNIQUE (reference)
)

;

CREATE TABLE qr_tokens (
	id UUID NOT NULL, 
	session_id UUID NOT NULL, 
	token VARCHAR(64) NOT NULL, 
	used BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(session_id) REFERENCES parking_sessions (id)
)

;
CREATE UNIQUE INDEX ix_qr_tokens_token ON qr_tokens (token);
COMMIT;
