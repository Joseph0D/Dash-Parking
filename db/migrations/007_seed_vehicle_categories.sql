-- Categorías requeridas por el formulario de inventario de parqueaderos de dueños.
BEGIN;

INSERT INTO vehicle_categories (id, code, name, is_active)
VALUES
    (gen_random_uuid(), 'car', 'Carro', TRUE),
    (gen_random_uuid(), 'motorcycle', 'Moto', TRUE),
    (gen_random_uuid(), 'bicycle', 'Bicicleta', TRUE),
    (gen_random_uuid(), 'electric_motorcycle', 'Moto eléctrica', TRUE),
    (gen_random_uuid(), 'scooter', 'Patineta eléctrica', TRUE),
    (gen_random_uuid(), 'truck', 'Camión', TRUE)
ON CONFLICT (code) DO NOTHING;

COMMIT;
