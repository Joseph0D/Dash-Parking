-- Ubicaciones demo de Bogotá para el mapa y la consulta de disponibilidad por franja.
-- Repetible: no duplica parqueaderos, zonas, espacios ni tarifas.
BEGIN;

ALTER TABLE estacionamiento
  ADD COLUMN IF NOT EXISTS latitud double precision,
  ADD COLUMN IF NOT EXISTS longitud double precision;

UPDATE estacionamiento
SET latitud = 4.6340, longitud = -74.0640
WHERE id_estacionamiento = 1
  AND (latitud IS NULL OR longitud IS NULL);

INSERT INTO estacionamiento
  (nombre_parqueadero, identificacion, direccion, telefono, capacidad_total)
SELECT datos.nombre, datos.identificacion, datos.direccion, datos.telefono, datos.capacidad
FROM (VALUES
  ('Dash Parking Parque 93 (Demo)', 'DEMO-BOG-001', 'Carrera 11A # 93A-10, Bogota', '6017001001', 63, 4.6767, -74.0481),
  ('Dash Parking Centro Internacional (Demo)', 'DEMO-BOG-002', 'Carrera 13 # 28-01, Bogota', '6017001002', 63, 4.6128, -74.0692),
  ('Dash Parking Unicentro (Demo)', 'DEMO-BOG-003', 'Carrera 15 # 124-30, Bogota', '6017001003', 63, 4.7028, -74.0420)
) AS datos(nombre, identificacion, direccion, telefono, capacidad, latitud, longitud)
WHERE NOT EXISTS (
  SELECT 1 FROM estacionamiento e WHERE e.identificacion = datos.identificacion
);

UPDATE estacionamiento e
SET latitud = datos.latitud, longitud = datos.longitud
FROM (VALUES
  ('DEMO-BOG-001', 4.6767, -74.0481),
  ('DEMO-BOG-002', 4.6128, -74.0692),
  ('DEMO-BOG-003', 4.7028, -74.0420)
) AS datos(identificacion, latitud, longitud)
WHERE e.identificacion = datos.identificacion
  AND (e.latitud IS NULL OR e.longitud IS NULL);

DO $$
DECLARE
  lot RECORD;
  vehicle_type RECORD;
  new_zone_id integer;
  zone_capacity integer;
BEGIN
  FOR lot IN
    SELECT id_estacionamiento
    FROM estacionamiento
    WHERE identificacion IN ('DEMO-BOG-001', 'DEMO-BOG-002', 'DEMO-BOG-003')
  LOOP
    FOR vehicle_type IN
      SELECT id_tipo_vehiculo, nombre_tipo
      FROM tipo_vehiculo
      ORDER BY id_tipo_vehiculo
    LOOP
      zone_capacity := CASE
        WHEN vehicle_type.id_tipo_vehiculo = 1 THEN 24
        WHEN vehicle_type.id_tipo_vehiculo = 2 THEN 15
        ELSE 8
      END;

      SELECT id_zona INTO new_zone_id
      FROM zona
      WHERE id_estacionamiento = lot.id_estacionamiento
        AND id_tipo_vehiculo = vehicle_type.id_tipo_vehiculo
      LIMIT 1;

      IF new_zone_id IS NULL THEN
        INSERT INTO zona
          (id_estacionamiento, id_tipo_vehiculo, nombre_zona, capacidad)
        VALUES (
          lot.id_estacionamiento,
          vehicle_type.id_tipo_vehiculo,
          'Zona ' || vehicle_type.nombre_tipo,
          zone_capacity
        )
        RETURNING id_zona INTO new_zone_id;
      END IF;

      IF NOT EXISTS (
        SELECT 1 FROM espacios
        WHERE id_estacionamiento = lot.id_estacionamiento
          AND id_zona = new_zone_id
      ) THEN
        INSERT INTO espacios
          (id_zona, id_estacionamiento, id_tipo_espacio, numero_de_espacio, estado)
        SELECT
          new_zone_id,
          lot.id_estacionamiento,
          CASE vehicle_type.id_tipo_vehiculo
            WHEN 1 THEN 1
            WHEN 2 THEN 3
            WHEN 3 THEN 5
            WHEN 4 THEN 4
            ELSE 6
          END,
          'D' || lot.id_estacionamiento || '-' || vehicle_type.id_tipo_vehiculo || '-' || n,
          'activo'
        FROM generate_series(1, zone_capacity) AS n;
      END IF;

      INSERT INTO tarifa
        (id_tipo_vehiculo, id_estacionamiento, valor_minuto, valor_dia,
         valor_mensualidad, fecha_vigencia_inicio, fecha_vigencia_fin)
      SELECT base.id_tipo_vehiculo, lot.id_estacionamiento, base.valor_minuto,
             base.valor_dia, base.valor_mensualidad, CURRENT_DATE, NULL
      FROM tarifa base
      WHERE base.id_estacionamiento = 1
        AND base.id_tipo_vehiculo = vehicle_type.id_tipo_vehiculo
        AND base.fecha_vigencia_fin IS NULL
        AND NOT EXISTS (
          SELECT 1 FROM tarifa actual
          WHERE actual.id_estacionamiento = lot.id_estacionamiento
            AND actual.id_tipo_vehiculo = vehicle_type.id_tipo_vehiculo
            AND actual.fecha_vigencia_fin IS NULL
        )
      ORDER BY base.fecha_vigencia_inicio DESC
      LIMIT 1;
    END LOOP;
  END LOOP;
END $$;

COMMIT;
