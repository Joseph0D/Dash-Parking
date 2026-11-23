# RNF-007 — Privacidad y protección de datos personales

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RNF-007 |
| **Categoría** | Privacidad y protección de datos |
| **Prioridad** | Alta |
| **Estado** | Requerido; retención y eliminación requieren definición del responsable |

## Requisitos

### RNF-007.1 — Acceso mínimo necesario
Cada cliente consulta solo sus vehículos, reservas y pagos. Cada dueño consulta solo los datos de
sus parqueaderos. Las restricciones se validan en el backend en cada endpoint.

### RNF-007.2 — Minimización y propósito
Solo se solicitan datos necesarios para registro, operación, cobro y recuperación de cuenta.
Los datos de ubicación del usuario no se recogen por defecto; la búsqueda de dirección se inicia
por acción explícita.

### RNF-007.3 — Protección de tokens y credenciales
No se almacenan tokens de recuperación en texto claro ni se escriben en logs. Las claves de
proveedores SMTP y las cadenas de conexión no se versionan ni se exponen en la interfaz.

### RNF-007.4 — Retención y derechos del titular
Antes de producción, el responsable debe definir los periodos de retención, eliminación o
anonimización de cuentas, reservas, pagos y registros de seguridad, y el canal para atender
solicitudes de titulares.

### RNF-007.5 — Proveedores externos
El correo transaccional y los servicios de mapas deben limitarse a los datos indispensables. La
configuración de proveedores y sus condiciones de tratamiento se revisan antes del despliegue.
