# Revisión de alcance y matriz de trazabilidad

## Alcance revisado

Se contrastaron las 42 HUs existentes, RF-001 a RF-017 y RNF-001 a RNF-006 con el alcance
aprobado: reservas por fecha y parqueadero, operación de dueños con aislamiento, recuperación por
correo, revisión de seguridad/rendimiento/disponibilidad/usabilidad móvil/privacidad y preparación
para publicación.

La relación HU↔RF es de muchos a muchos. La etiqueta «Implementado» se usa solo cuando hay código
o pruebas visibles para el flujo; no implica que todos los criterios de aceptación de la HU hayan
sido verificados. Las casillas de criterios permanecen como pendientes de validación individual.

## Historias de usuario

| HU | Decisión | RF relacionado(s) | Justificación y estado conocido |
|---|---|---|---|
| HU-01 | Mantener | RF-016 | Registro de cliente. El registro de dueño se separa en HU-32 para hacer explícita la autorización. |
| HU-02 | Mantener | RF-012 | Inicio de sesión por correo y contraseña; no se elimina el mensaje genérico. |
| HU-03 | Mantener | RF-018 | Perfil propio; se conserva separación entre datos de cuenta y administración del parqueadero. |
| HU-04 | Modificar | RF-018 | Incluir las categorías admitidas, incluido camión; el QR de vehículo se especifica aparte. |
| HU-05A | Mantener | RF-018 | Lista de vehículos propios y protección de datos por usuario. |
| HU-05B | Mantener | RF-018 | Edición de vehículo propio, sujeta a las reglas de reservas y sesiones activas. |
| HU-05C | Modificar | RF-018 | Conservar el historial al retirar un vehículo; verificar que la estrategia de borrado no elimine relaciones históricas. |
| HU-06 | Modificar | RF-019 | El catálogo de categorías es global y administrado por la plataforma; el dueño elige tipos admitidos, no define tipos arbitrarios. |
| HU-07A | Modificar | RF-019 | El dueño registra parqueaderos propios y define ubicación/horarios; el panel de plataforma no sustituye la propiedad. |
| HU-07B | Modificar | RF-019 | Limitar cambios y desactivación a parqueaderos propios y conservar protecciones ante reservas activas. |
| HU-08 | Modificar | RF-019 | El dueño configura zonas de sus parqueaderos y sus capacidades por tipo de vehículo. |
| HU-09 | Mantener | RF-019 | Los tipos globales de espacio permanecen bajo control de plataforma para mantener un catálogo coherente. |
| HU-10 | Modificar | RF-019 | El dueño administra inventario de sus parqueaderos; no se permite reducirlo si contradice reservas/sesiones vigentes. |
| HU-11 | Modificar | RF-022 | Mantener mapa y etiquetas de demostración; búsqueda por nombre, dirección y filtros se reporta parcial hasta validar la interfaz. |
| HU-12 | Modificar | RF-022 | Disponibilidad por fecha/rango, espacios inactivos excluidos y actualización del resumen del mapa cada cinco segundos. |
| HU-13 | Modificar | RF-013 | El cliente elige parqueadero, vehículo e intervalo; el backend asigna el espacio y la BD evita solapamientos simultáneos. |
| HU-14 | Eliminar como HU independiente | RF-013 | Compatibilidad es regla de reserva y sus criterios se conservan en HU-13; el archivo se mantiene para referencias históricas. |
| HU-15A | Mantener | RF-013 | Consulta de reservas propias; conservar filtros/estados como criterios pendientes hasta su validación. |
| HU-15B | Modificar | RF-013 | La consulta global queda para administrador de plataforma; el dueño solo ve reservas de sus parqueaderos. |
| HU-16 | Mantener | RF-013 | Cancelación de reserva propia antes del inicio; liberar solo su intervalo y conservar historial. |
| HU-17 | Modificar | RF-013 | La finalización automática no está cubierta por los endpoints revisados; la tolerancia de 15 minutos sigue siendo supuesto por aprobar. |
| HU-18 | Mantener | RF-001, RF-002, RF-013 | Entrada con reserva permanece ligada al ciclo operativo; validar ventana/tolerancia antes de aceptar todos los criterios. |
| HU-19 | Mantener | RF-001, RF-002 | Entrada sin reserva sigue siendo un flujo operativo distinto de una reserva futura. |
| HU-20 | Mantener | RF-004, RF-005, RF-006 | Salida y cobro se conservan; la regla de acceso al pago debe corresponder al estado real del ticket. |
| HU-21 | Modificar | RF-007, RF-019 | Las tarifas son por parqueadero y tipo de vehículo y las administra su dueño; no son tarifas globales. |
| HU-22 | Modificar | RF-005 | Fija tarifa por minuto y tope diario; redondeo de fracciones y minutos de gracia permanecen pendientes. |
| HU-23 | Mantener | RF-014 | El pago en línea continúa documentado como simulación hasta integrar una pasarela real. |
| HU-23A | Mantener en backlog | RF-014 | PSE requiere integración real, credenciales y pruebas de conciliación; no está activo en producción. |
| HU-23B | Mantener en backlog | RF-014 | Nequi/Daviplata requieren integración real y manejo de estados asíncronos. |
| HU-23C | Mantener en backlog | RF-014 | Tarjeta requiere proveedor tokenizado; no almacenar PAN completo ni CVV. |
| HU-24 | Mantener | RF-006 | El pago en efectivo sigue separado de los medios virtuales. |
| HU-25 | Modificar | RF-014 | Mantener estados aprobado/pendiente/rechazado; los estados reales dependen de la pasarela futura. |
| HU-26 | Mantener en backlog | RF-024 | Comprobante/PDF y requisitos tributarios no se consideran completos por tener un pago registrado. |
| HU-27A | Modificar | RF-024 | Historial de pagos solo del cliente; filtros y descarga requieren validación específica. |
| HU-27B | Modificar | RF-024 | El administrador puede consultar el conjunto global; dueño limitado a sus parqueaderos. |
| HU-28A | Mantener en backlog | RF-025 | Avisos de reserva no se confunden con los correos de recuperación. |
| HU-28B | Mantener en backlog | RF-025 | Recordatorios/vencimientos necesitan un planificador y política de tolerancia aprobada. |
| HU-28C | Mantener en backlog | RF-025 | Avisos de pago dependen de eventos de pasarela y política de reintentos. |
| HU-29 | Modificar | RF-003, RF-017, RF-020 | Separar ocupación operativa, disponibilidad futura y panel diario; las cifras deben usar el mismo parqueadero/periodo. |
| HU-30A | Modificar | RF-012, RF-016 | Incorporar cliente, dueño, operador y administrador de plataforma; operador/admin no pueden autorregistrarse. |
| HU-30B | Modificar | RF-012, RF-020 | Validar permisos y propiedad en backend; operador limitado a parqueaderos asignados y dueño a los propios. |
| HU-31 | Modificar | RF-009, RF-017, RF-020 | Reportes globales para plataforma y reportes acotados del dueño; distinguirlos del resumen diario. |
| HU-32 | Agregar | RF-016, RF-019 | Historia explícita para registro de dueño y asignación segura de rol. |
| HU-33 | Agregar | RF-019 | Historia para crear parqueaderos, ubicación en mapa, horarios, inventario por tipo y tarifas. |
| HU-34 | Agregar | RF-020 | Historia para panel diario aislado por parqueadero y verificación de propiedad en API. |
| HU-35 | Agregar | RF-021 | Historia para recuperación de contraseña con correo real, token hash, expiración y límites. |
| HU-36 | Agregar | RF-023 | Documenta el QR permanente por vehículo, distinto del QR de sesión/pago. |
| HU-37 | Agregar | RF-015 | Recupera la trazabilidad del QR temporal de sesión/pago, distinto del QR de vehículo. |

No se eliminan requisitos de operación, cobro o seguridad. La única retirada es HU-14 como
funcionalidad independiente; sus reglas permanecen como criterios de HU-13.

## Requisitos funcionales

| RF | Decisión | Justificación |
|---|---|---|
| RF-001 | Mantener | Registro de ingreso operativo. |
| RF-002 | Mantener | Asignación de espacio para ingreso operativo; no sustituye la reserva temporal. |
| RF-003 | Modificar | Distinguir ocupación actual de disponibilidad futura y limitar resultados por alcance. |
| RF-004 | Mantener | Salida y liberación operativa. |
| RF-005 | Modificar | Aplicar tarifa por minuto y tope diario de HU-21/HU-22; redondeo/minutos de gracia siguen abiertos. |
| RF-006 | Mantener | Registro de pago y efectivo; comprobar asociación con ticket/parqueadero. |
| RF-007 | Modificar | Tarifa vigente por parqueadero y categoría, bajo propiedad del dueño. |
| RF-008 | Modificar | Mantener historial de placa; no confundirlo con historial financiero ni abrirlo a otros usuarios. |
| RF-009 | Modificar | Separar reportes globales de plataforma y panel diario aislado del dueño. |
| RF-010 | Mantener | Administración de clientes queda como función de plataforma, no reemplaza autoconsulta. |
| RF-011 | Mantener pendiente | Auditoría inmutable de modificaciones/eliminaciones todavía requiere verificar implementación. |
| RF-012 | Modificar | Ampliar a cuatro roles y exigir autorización por propiedad/asignación en cada endpoint. |
| RF-013 | Modificar | UUID, parqueadero, inicio/fin, horarios, cancelación por intervalo y exclusión DB contra concurrencia. |
| RF-014 | Mantener como simulación | No presentar el pago virtual simulado como pasarela real. |
| RF-015 | Modificar | Delimitar QR temporal de sesión; el QR permanente por vehículo es RF-023. |
| RF-016 | Modificar | Permitir autorregistro client/owner y prohibir admin/operator. |
| RF-017 | Modificar | Dashboard global de plataforma; panel diario de dueño en RF-020. |
| RF-018 | Agregar | Perfil y gestión de vehículos propios. |
| RF-019 | Agregar | Registro de dueño y gestión de parqueaderos propios. |
| RF-020 | Agregar | Panel diario por parqueadero con aislamiento de propietario. |
| RF-021 | Agregar | Solicitud y confirmación de recuperación segura por correo. |
| RF-022 | Agregar | Mapa, consulta por dirección y disponibilidad por fecha/horario. |
| RF-023 | Agregar | Identificación del vehículo mediante QR permanente. |
| RF-024 | Agregar | Historial de pagos y comprobantes con alcance por titular/propietario. |
| RF-025 | Agregar | Notificaciones de reserva y pago; pendiente de implementación. |

## Requisitos no funcionales

| RNF | Decisión | Cambio |
|---|---|---|
| RNF-001 | Modificar | Añadir autorización por propiedad, recuperación segura, protección de secretos y minimización de datos en logs. |
| RNF-002 | Modificar | Medir frescura del mapa, integridad concurrente y acordar un SLO público antes del lanzamiento. |
| RNF-003 | Modificar | Añadir criterios verificables de uso móvil y distinguir disponibilidad consultada de reserva confirmada. |
| RNF-004 | Modificar | Explicitar intervalos `[inicio, fin)`, transacciones, tokens de un solo uso y restauración probada. |
| RNF-005 | Modificar | Exigir trazabilidad HU→RF→módulo/prueba y fuente UUID canónica. |
| RNF-006 | Mantener/ampliar | Mantener compatibilidad y portabilidad; documentar Leaflet/OpenStreetMap y su atribución. |
| RNF-007 | Agregar | Minimización, alcance de acceso, retención y derechos de titulares. |
| RNF-008 | Agregar | HTTPS, CORS limitado, PostgreSQL, migraciones, secretos, salud y restauración para producción. |

## Trazabilidad de funcionalidad y evidencia

| Funcionalidad / HUs | Backend y persistencia | Frontend y pruebas | Estado |
|---|---|---|---|
| Autenticación, registro y perfil (HU-01 a HU-03, HU-30A/B) | `be/app/routers/auth.py`, `be/app/core/deps.py` | `fe/src/App.tsx`, `fe/src/context/AuthContext.tsx` | Cliente/dueño y permisos base implementados; auditar criterios por rol. |
| Vehículos (HU-04 a HU-05C, HU-36) | `be/app/routers/vehicles.py`, `be/app/services/qr_service.py`, `be/app/models/vehicle_qr_token.py` | `fe/src/pages/client/VehiclesPanel.tsx`, `fe/src/pages/admin/EntryExitPanel.tsx` | CRUD y QR existen; confirmar retención del historial al borrar. |
| Parqueaderos del dueño (HU-06 a HU-10, HU-21, HU-32/33) | `be/app/routers/owner_parking_lots.py`, `be/app/services/owner_parking_lot_service.py` | `fe/src/pages/owner/OwnerDashboard.tsx`, `be/tests/test_owner_parking_lots.py` | Configuración y aislamiento implementados; catálogos globales no son editables por dueño. |
| Mapa y disponibilidad (HU-11/12) | `be/app/routers/availability.py`, `be/app/services/availability_service.py` | `fe/src/components/ParkingMap.tsx`, `fe/src/pages/AvailabilityPage.tsx`, `be/tests/test_availability.py` | Mapa/disponibilidad implementados; búsqueda completa y filtros pendientes de aceptación. |
| Reservas (HU-13 a HU-17) | `be/app/routers/reservations.py`, `be/app/services/reservation_service.py`, `db/migrations/005_uuid_reservation_constraints.sql` | `fe/src/pages/AvailabilityPage.tsx`, `fe/src/pages/client/ReservationsPanel.tsx`, pruebas de reserva/concurrencia | Reserva, cancelación y exclusión concurrente implementadas; vencimiento automático pendiente. |
| Operación y pagos (HU-18 a HU-27B, HU-37) | `be/app/routers/sessions.py`, `be/app/routers/payments.py`, servicios de sesión/pago | panel operativo y pagos; validar por endpoint | QR de sesión y flujo virtual simulado; pasarela, comprobantes PDF e historial detallado pendientes/parciales. |
| Recuperación (HU-35) | `be/app/routers/auth.py`, servicios de password reset/email, migración `006_password_reset.sql` | páginas de recuperación/restablecimiento; `be/tests/test_password_reset.py` | Implementado; usuario confirmó entrega real por Brevo. |
| Panel y reportes (HU-29/31, HU-34) | `owner_parking_lots.py`, `reports.py` | panel de dueño y dashboard admin; pruebas de aislamiento | Panel diario implementado; reportes históricos/exports requieren validación separada. |

## Mejoras priorizadas y pendientes

| Prioridad | Mejora | Estado / dependencia |
|---|---|---|
| P0 antes de publicar | Despliegue público con HTTPS, PostgreSQL, migraciones, CORS, secretos y restauración | Requisito de RNF-008; fase pendiente y requiere proveedor/cuentas. |
| P1 | Pasarela real para PSE, billeteras y tarjetas | HU-23A/B/C; requiere elegir proveedor, credenciales seguras y webhooks idempotentes. |
| P1 | Recordatorios y notificaciones de reserva/pago | RF-025/HU-28A/B/C; definir canal, preferencias y reintentos. |
| P1 | Verificar historiales/comprobantes y aislamiento por titular | RF-024/HU-26/27A/27B; PDF y alcance tributario pendientes. |
| P2 | QR de reserva | Mejora futura distinta a QR de vehículo (RF-023) y QR de sesión (RF-015). |
| P2 | Filtros por distancia/precio y búsqueda completa | HU-11/RF-022; la búsqueda geográfica debe respetar límites del proveedor. |
| P2 | Calificaciones y reseñas | Nueva historia futura; definir moderación, abuso y privacidad antes de crear el RF. |
| Continuo | Pruebas automáticas de concurrencia de reservas y recuperación | Ya existen pruebas focalizadas; mantenerlas como bloqueantes de regresión. |

## Decisiones que no se deben inventar

- El objetivo de disponibilidad mensual, mantenimiento y tiempos de recuperación quedan por
  aprobar antes del lanzamiento; RNF-002.7 registra esta decisión abierta.
- La tarifa por minuto y el tope diario están especificados en HU-21/HU-22; el redondeo de
  fracciones y los minutos de gracia siguen pendientes.
- La tolerancia para finalizar reservas sin ingreso (15 minutos en HU-17) es un supuesto y
  necesita aprobación del responsable del parqueadero.
- La retención/eliminación de datos personales y el alcance legal del comprobante requieren
  definición antes de producción.
