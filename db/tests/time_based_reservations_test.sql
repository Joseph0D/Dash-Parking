-- Pruebas de reservas por tiempo. Todo corre dentro de una transacción y termina en ROLLBACK,
-- por lo que NO modifica los datos. Cada caso que debe fallar usa un SAVEPOINT.
-- Uso: psql -d dash_parking -f time_based_reservations_test.sql
\pset pager off
BEGIN;
SELECT (date_trunc('day', LOCALTIMESTAMP) + interval '1 day 10 hours') AS i,
       (date_trunc('day', LOCALTIMESTAMP) + interval '1 day 11 hours') AS f,
       (date_trunc('day', LOCALTIMESTAMP) + interval '1 day 12 hours') AS g \gset

\echo '1) OK: usuario 1 reserva espacio 1 (carro) de 10:00 a 11:00'
SELECT id_reserva, id_espacio, id_zona, id_estacionamiento, fecha_reserva, fecha_hora_fin, estado_reserva
FROM fn_crear_reserva(1,1,1,:'i',:'f',1);

\echo '2) OK: misma franja sin indicar espacio -> asigna otro libre (esperado: 2)'
SELECT id_espacio FROM fn_crear_reserva(4,4,1,:'i',:'f');

\echo '3) FALLA esperada: espacio 1, franja cruzada 10:30-11:30'
SAVEPOINT s3;
SELECT fn_crear_reserva(6,7,1,:'i'::timestamp + interval '30 min',:'f'::timestamp + interval '30 min',1);
ROLLBACK TO s3;

\echo '4) OK: espacio 1 pegado, 11:00-12:00 (franja [inicio,fin) permite back-to-back)'
SELECT id_espacio, fecha_reserva, fecha_hora_fin FROM fn_crear_reserva(6,7,1,:'f',:'g',1);

\echo '5) Estado del espacio 1: 9-10 Disponible | 10-11 Reservado | 12-13 Disponible'
SELECT '09-10' franja, estado FROM fn_estado_espacios(1,1,:'i'::timestamp - interval '1 hour',:'i') WHERE id_espacio=1
UNION ALL SELECT '10-11', estado FROM fn_estado_espacios(1,1,:'i',:'f') WHERE id_espacio=1
UNION ALL SELECT '12-13', estado FROM fn_estado_espacios(1,1,:'g',:'g'::timestamp + interval '1 hour') WHERE id_espacio=1;

\echo '6) Resumen por zona 10-11 (Zona Carros: 2 reservados)'
SELECT nombre_zona, capacidad, libres, reservados, ocupados FROM fn_disponibilidad_franja(1,:'i',:'f');

\echo '7) FALLA esperada: reserva en el pasado'
SAVEPOINT s7;
SELECT fn_crear_reserva(1,1,1,LOCALTIMESTAMP - interval '3 hours',LOCALTIMESTAMP - interval '2 hours');
ROLLBACK TO s7;

\echo '8) FALLA esperada: carro en espacio de motos (201)'
SAVEPOINT s8;
SELECT fn_crear_reserva(1,1,1,:'i',:'f',201);
ROLLBACK TO s8;

\echo '9) FALLA esperada: vehículo 1 pertenece al usuario 1, no al 2'
SAVEPOINT s9;
SELECT fn_crear_reserva(2,1,1,:'i',:'f');
ROLLBACK TO s9;

\echo '10) FALLA esperada: parqueadero inexistente'
SAVEPOINT s10;
SELECT fn_crear_reserva(1,1,99,:'i',:'f');
ROLLBACK TO s10;

\echo '11) Cancelar la reserva 10-11 del espacio 1 -> vuelve a Disponible'
UPDATE reserva SET estado_reserva='cancelada'
WHERE id_espacio=1 AND fecha_reserva=:'i'::timestamp AND estado_reserva='activa';
SELECT estado FROM fn_estado_espacios(1,1,:'i',:'f') WHERE id_espacio=1;

\echo '12) FALLA esperada: la restricción EXCLUDE bloquea el cruce aun con triggers apagados'
SELECT id_reserva FROM fn_crear_reserva(1,1,1,:'i',:'f',3) \gset
SAVEPOINT s12;
SET LOCAL session_replication_role = replica;
INSERT INTO reserva(id_usuario,id_vehiculo,id_estacionamiento,id_espacio,id_zona,fecha_reserva,fecha_hora_fin)
VALUES (4,4,1,3,1,:'i',:'f');
ROLLBACK TO s12;
SET LOCAL session_replication_role = origin;

\echo '13) OK: pago Nequi de esa reserva -> monto 60 min x 500 = 30000 y comprobante'
INSERT INTO pago (id_reserva, id_tarifa, monto_total, metodo_pago, estado_pago, referencia_transaccion)
VALUES (:id_reserva, 1, 0, 'Nequi', 'Aprobado', 'TRX-PRUEBA-0001');
SELECT p.monto_total, p.id_tarifa, c.numero_comprobante
FROM pago p JOIN comprobante c USING (id_pago) WHERE p.referencia_transaccion='TRX-PRUEBA-0001';

\echo '14) FALLA esperada: pago sin ticket ni reserva'
SAVEPOINT s14;
INSERT INTO pago (id_tarifa, monto_total, metodo_pago, estado_pago) VALUES (1,0,'Efectivo','Aprobado');
ROLLBACK TO s14;

\echo '15) FALLA esperada: entrada sin reserva a un espacio reservado en ese momento'
SAVEPOINT s15;
SELECT id_reserva AS r15 FROM fn_crear_reserva(1,1,1,LOCALTIMESTAMP + interval '1 minute',LOCALTIMESTAMP + interval '2 hours',2) \gset
INSERT INTO ticket (id_vehiculo, id_espacio, fecha_hora_entrada) VALUES (16,2,LOCALTIMESTAMP + interval '30 minutes');
ROLLBACK TO s15;
ROLLBACK;
