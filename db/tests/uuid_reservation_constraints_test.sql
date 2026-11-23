-- PostgreSQL integration test for exclusion constraints; all rows are rolled back.
-- Run against an isolated/test dash_parking database after migration 005.
BEGIN;

DO $$
DECLARE
  test_user uuid := 'b628cc9f-6a45-4df8-9392-d12e290fc55e';
  category_id uuid := 'b628cc9f-6a45-4df8-9392-d12e290fc561';
  lot_id uuid := 'b628cc9f-6a45-4df8-9392-d12e290fc562';
  zone_id uuid := 'b628cc9f-6a45-4df8-9392-d12e290fc563';
  spot_one uuid := 'b628cc9f-6a45-4df8-9392-d12e290fc564';
  spot_two uuid := 'b628cc9f-6a45-4df8-9392-d12e290fc565';
  vehicle_one uuid := 'b628cc9f-6a45-4df8-9392-d12e290fc566';
  vehicle_two uuid := 'b628cc9f-6a45-4df8-9392-d12e290fc567';
  reservation_one uuid := 'b628cc9f-6a45-4df8-9392-d12e290fc568';
  reservation_adjacent uuid := 'b628cc9f-6a45-4df8-9392-d12e290fc569';
  start_at timestamptz := now() + interval '1 day';
  end_at timestamptz := now() + interval '1 day 2 hours';
BEGIN
  INSERT INTO users (id, name, email, password_hash, role, created_at)
  VALUES (test_user, 'Reservation constraint test', 'reservation-constraint-test@example.invalid',
          'not-a-real-password-hash', 'CLIENT', now());
  INSERT INTO vehicle_categories (id, code, name, is_active)
  VALUES (category_id, 'constraint_test_car', 'Constraint test car', true);
  INSERT INTO parking_lots (
    id, name, identification, address, total_capacity, is_active, created_at
  ) VALUES (
    lot_id, 'Constraint test lot', 'RESERVATION-CONSTRAINT-TEST', 'Bogota', 2, true, now()
  );
  INSERT INTO parking_zones (
    id, parking_lot_id, vehicle_category_id, name, capacity
  ) VALUES (zone_id, lot_id, category_id, 'Test zone', 2);
  INSERT INTO parking_spots (
    id, code, zone, vehicle_type, is_active, parking_lot_id, parking_zone_id,
    vehicle_category_id, status
  ) VALUES
    (spot_one, 'T-01', 'Test zone', 'CAR', true, lot_id, zone_id, category_id, 'AVAILABLE'),
    (spot_two, 'T-02', 'Test zone', 'CAR', true, lot_id, zone_id, category_id, 'AVAILABLE');
  INSERT INTO vehicles (id, plate, vehicle_type, vehicle_category_id, owner_id, created_at)
  VALUES
    (vehicle_one, 'RCT001', 'CAR', category_id, test_user, now()),
    (vehicle_two, 'RCT002', 'CAR', category_id, test_user, now());

  INSERT INTO reservations (
    id, vehicle_id, spot_id, parking_lot_id, vehicle_type, start_time, end_time, status
  ) VALUES (
    reservation_one, vehicle_one, spot_one, lot_id, 'CAR', start_at, end_at, 'CONFIRMED'
  );

  BEGIN
    INSERT INTO reservations (
      id, vehicle_id, spot_id, parking_lot_id, vehicle_type, start_time, end_time, status
    ) VALUES (
      gen_random_uuid(), vehicle_two, spot_one, lot_id, 'CAR',
      start_at + interval '1 hour', end_at + interval '1 hour', 'CONFIRMED'
    );
    RAISE EXCEPTION 'Expected overlapping spot reservation to fail';
  EXCEPTION WHEN exclusion_violation THEN
    NULL;
  END;

  BEGIN
    INSERT INTO reservations (
      id, vehicle_id, spot_id, parking_lot_id, vehicle_type, start_time, end_time, status
    ) VALUES (
      gen_random_uuid(), vehicle_one, spot_two, lot_id, 'CAR',
      start_at + interval '1 hour', end_at + interval '1 hour', 'CONFIRMED'
    );
    RAISE EXCEPTION 'Expected overlapping vehicle reservation to fail';
  EXCEPTION WHEN exclusion_violation THEN
    NULL;
  END;

  INSERT INTO reservations (
    id, vehicle_id, spot_id, parking_lot_id, vehicle_type, start_time, end_time, status
  ) VALUES (
    reservation_adjacent, vehicle_one, spot_one, lot_id, 'CAR', end_at,
    end_at + interval '1 hour', 'CONFIRMED'
  );
END $$;

ROLLBACK;
