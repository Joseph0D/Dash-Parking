-- Pruebas del ciclo Disponible -> Reservado -> Ocupado -> Disponible, cancelación y reembolso.
-- Corren en una transacción y terminan en ROLLBACK (no modifican datos).
-- Uso: psql -d dash_parking_v2 -f reservation_lifecycle_test.sql
\pset pager off
BEGIN;
SELECT LOCALTIMESTAMP AS ahora, LOCALTIMESTAMP + interval '1 hour' AS en1h,
       date_trunc('day', LOCALTIMESTAMP) + interval '1 day 10 hours' AS m10,
       date_trunc('day', LOCALTIMESTAMP) + interval '1 day 11 hours' AS m11 \gset

\echo '1) Reservar espacio 1 (ahora -> +1 h) y pagar con Nequi: monto 30000 + comprobante'
SELECT id_reserva FROM fn_crear_reserva(1,1,1,:'ahora',:'en1h',1) \gset
INSERT INTO pago (id_reserva, id_tarifa, monto_total, metodo_pago, estado_pago, referencia_transaccion)
VALUES (:id_reserva, 1, 0, 'Nequi', 'Aprobado', 'TRX-LC-1');
SELECT estado_visible, monto_total, estado_pago, id_comprobante FROM vw_reservas_detalle WHERE id_reserva = :id_reserva;

\echo '2) Ingreso: ticket Pagado y espacio 1 pasa a Ocupado ahora'
SELECT id_ticket, estado_ticket FROM fn_registrar_ingreso(:id_reserva) \gset
SELECT :'estado_ticket' AS estado_ticket;
SELECT estado FROM fn_estado_espacios(1,1,:'ahora',:'en1h') WHERE id_espacio = 1;
SELECT estado_visible FROM vw_reservas_detalle WHERE id_reserva = :id_reserva;

\echo '3) El resto de la franja NO queda libre mientras el carro está adentro (Reservado)'
SELECT estado FROM fn_estado_espacios(1,1,:'ahora'::timestamp + interval '30 min',:'ahora'::timestamp + interval '45 min') WHERE id_espacio = 1;

\echo '4) FALLA esperada: otro cliente no puede reservar ese espacio en la franja restante'
SAVEPOINT s4;
SELECT fn_crear_reserva(4,4,1,:'ahora'::timestamp + interval '30 min',:'en1h',1);
ROLLBACK TO s4;

\echo '5) FALLA esperada: segundo ingreso de la misma reserva'
SAVEPOINT s5;
SELECT fn_registrar_ingreso(:id_reserva);
ROLLBACK TO s5;

\echo '6) FALLA esperada: cancelar una reserva que ya ingresó'
SAVEPOINT s6;
SELECT fn_cancelar_reserva(:id_reserva, 1);
ROLLBACK TO s6;

\echo '7) Salida: ticket Finalizado, reserva finalizada y espacio Disponible'
SELECT estado_ticket FROM fn_registrar_salida(:id_ticket);
SELECT estado_visible FROM vw_reservas_detalle WHERE id_reserva = :id_reserva;
SELECT estado FROM fn_estado_espacios(1,1,:'ahora',:'en1h') WHERE id_espacio = 1;

\echo '8) FALLA esperada: segunda salida del mismo ticket'
SAVEPOINT s8;
SELECT fn_registrar_salida(:id_ticket);
ROLLBACK TO s8;

\echo '9) Cancelar con reembolso: reserva de mañana 10-11 pagada con Daviplata'
SELECT id_reserva AS rid2 FROM fn_crear_reserva(4,4,1,:'m10',:'m11',2) \gset
INSERT INTO pago (id_reserva, id_tarifa, monto_total, metodo_pago, estado_pago, referencia_transaccion)
VALUES (:rid2, 1, 0, 'Daviplata', 'Aprobado', 'TRX-LC-2');

\echo '9a) FALLA esperada: otro usuario intenta cancelarla'
SAVEPOINT s9;
SELECT fn_cancelar_reserva(:rid2, 1);
ROLLBACK TO s9;

\echo '9b) FALLA esperada: ingreso antes de tiempo (mañana)'
SAVEPOINT s9b;
SELECT fn_registrar_ingreso(:rid2);
ROLLBACK TO s9b;

\echo '9c) La dueña la cancela: reembolso 30000, pago Reembolsado, espacio libre'
SELECT fn_cancelar_reserva(:rid2, 4) AS reembolso;
SELECT estado_visible, estado_pago FROM vw_reservas_detalle WHERE id_reserva = :rid2;
SELECT estado FROM fn_estado_espacios(1,1,:'m10',:'m11') WHERE id_espacio = 2;

\echo '10) FALLA esperada: cancelar dos veces'
SAVEPOINT s10;
SELECT fn_cancelar_reserva(:rid2, 4);
ROLLBACK TO s10;
ROLLBACK;
