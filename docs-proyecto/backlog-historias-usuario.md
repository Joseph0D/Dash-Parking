# Backlog — Historias de Usuario para GitHub Projects

Cada bloque de abajo es un Issue listo para copiar/pegar en GitHub (ver
`GUIA-CONFIGURACION-GITHUB.md`, paso 5). Todas se derivan literalmente de los Requisitos
Funcionales (RF01–RF20) y Necesidades del informe de diseño — ninguna agrega alcance nuevo.

---

### [HU-01] Registrar ingreso de vehículo

**Label:** `feature` · **Core** · **Milestone:** Sprint 1 — Dominio y persistencia

## Historia de Usuario
Como operario, quiero registrar el ingreso de un vehículo para dejar constancia digital de su llegada.

## Criterios de Aceptación
- [ ] Se registra la placa del vehículo
- [ ] Se registra el tipo de vehículo
- [ ] La fecha y hora de ingreso se registran automáticamente
- [ ] No se permite registrar una placa que ya está dentro del parqueadero

## Notas técnicas
Referencia: RF01, RF02, RF03, RF04. Necesidad 1 del informe de diseño.

---

### [HU-02] Asignar espacio disponible automáticamente

**Label:** `feature` · **Core** · **Milestone:** Sprint 1 — Dominio y persistencia

## Historia de Usuario
Como sistema, quiero asignar automáticamente un espacio disponible al vehículo que ingresa para evitar asignación doble.

## Criterios de Aceptación
- [ ] El sistema identifica espacios libres antes de asignar
- [ ] No se puede asignar un espacio ya ocupado
- [ ] El espacio queda marcado como ocupado tras la asignación

## Notas técnicas
Referencia: RF05. Necesidad 2 del informe de diseño. Depende de HU-01.

---

### [HU-03] Consultar ocupación en tiempo real

**Label:** `feature` · **Core** · **Milestone:** Sprint 3 — API CRUD entidades core

## Historia de Usuario
Como administrador, quiero consultar los vehículos actualmente dentro del parqueadero para conocer la ocupación en tiempo real.

## Criterios de Aceptación
- [ ] Se listan los vehículos actualmente dentro del parqueadero
- [ ] Se muestra el número de espacios ocupados y libres
- [ ] La información refleja el estado actual, sin recarga manual de datos

## Notas técnicas
Referencia: RF06, RF20. Depende de HU-01, HU-02.

---

### [HU-04] Registrar salida de vehículo

**Label:** `feature` · **Core** · **Milestone:** Sprint 3 — API CRUD entidades core

## Historia de Usuario
Como operario, quiero registrar la salida de un vehículo para liberar el espacio que ocupaba.

## Criterios de Aceptación
- [ ] Se busca el vehículo por placa
- [ ] Se registra la hora de salida
- [ ] El espacio asignado se libera automáticamente

## Notas técnicas
Referencia: RF07, RF10. Depende de HU-01, HU-02.

---

### [HU-05] Calcular tiempo de permanencia y valor a pagar

**Label:** `feature` · **Core** · **Milestone:** Sprint 4 — Reglas de negocio y servicios

## Historia de Usuario
Como sistema, quiero calcular automáticamente el tiempo de permanencia y el valor a pagar al momento de la salida para evitar errores de cobro.

## Criterios de Aceptación
- [ ] El cálculo del tiempo usa la hora de ingreso y salida registradas
- [ ] El valor se calcula aplicando la tarifa vigente
- [ ] El resultado se muestra antes de confirmar la salida

## Notas técnicas
Referencia: RF08, RF09. Necesidad 3 del informe de diseño. Depende de HU-04, HU-07.

---

### [HU-06] Registrar el pago del servicio

**Label:** `feature` · **Core** · **Milestone:** Sprint 4 — Reglas de negocio y servicios

## Historia de Usuario
Como operario, quiero registrar el pago realizado por el cliente para dejar trazabilidad del cobro.

## Criterios de Aceptación
- [ ] Se registra el valor pagado
- [ ] Se asocia el pago al vehículo/registro de salida correspondiente
- [ ] El pago queda consultable en el historial

## Notas técnicas
Referencia: RF11. Depende de HU-05.

---

### [HU-07] Administrar tarifas del parqueadero

**Label:** `feature` · **Core** · **Milestone:** Sprint 1 — Dominio y persistencia

## Historia de Usuario
Como administrador, quiero definir y actualizar las tarifas del parqueadero para que el cálculo del cobro use valores vigentes.

## Criterios de Aceptación
- [ ] Se puede crear una tarifa (valor por unidad de tiempo)
- [ ] Se puede actualizar una tarifa existente
- [ ] El cálculo de cobro siempre usa la tarifa vigente al momento de la salida

## Notas técnicas
Referencia: RF15, módulo de tarifas.

---

### [HU-08] Buscar vehículos y consultar historial

**Label:** `feature` · **Secundaria** · **Milestone:** Sprint 6 — Flujos y funcionalidades secundarias

## Historia de Usuario
Como administrador, quiero buscar vehículos por placa y consultar el historial de ingresos/salidas para resolver reclamos y auditar la operación.

## Criterios de Aceptación
- [ ] Se puede buscar por placa exacta o parcial
- [ ] El historial muestra ingresos, salidas y pagos asociados
- [ ] Los resultados están ordenados por fecha

## Notas técnicas
Referencia: RF12, RF13. Depende de HU-01, HU-04.

---

### [HU-09] Generar reportes administrativos

**Label:** `feature` · **Secundaria** · **Milestone:** Sprint 8 — Cierre y avance 90%

## Historia de Usuario
Como propietario, quiero generar reportes de ingresos económicos, ocupación y vehículos atendidos para apoyar decisiones administrativas.

## Criterios de Aceptación
- [ ] Reporte de vehículos ingresados/retirados en un rango de fechas
- [ ] Reporte de ingresos económicos totales del periodo
- [ ] Reporte de ocupación histórica

## Notas técnicas
Referencia: RF14. Necesidad 5 del informe de diseño. Depende de HU-06, HU-08.

---

### [HU-10] Administrar información de clientes

**Label:** `feature` · **Secundaria** · **Milestone:** Sprint 6 — Flujos y funcionalidades secundarias

## Historia de Usuario
Como administrador, quiero registrar y consultar información de clientes frecuentes para asociarlos a sus vehículos.

## Criterios de Aceptación
- [ ] Se puede registrar un cliente (nombre, contacto)
- [ ] Se puede asociar un vehículo a un cliente
- [ ] Se puede consultar el historial de un cliente

## Notas técnicas
Referencia: RF16, módulo de clientes. Depende de HU-01.

---

### [HU-11] Actualizar y eliminar registros según permisos

**Label:** `feature` · **Secundaria** · **Milestone:** Sprint 6 — Flujos y funcionalidades secundarias

## Historia de Usuario
Como administrador, quiero actualizar o eliminar registros según permisos para corregir errores de digitación sin perder trazabilidad.

## Criterios de Aceptación
- [ ] Solo el rol administrador puede eliminar registros
- [ ] Toda edición queda registrada (quién, cuándo, qué cambió)
- [ ] No se permite eliminar un registro con pago asociado sin confirmación explícita

## Notas técnicas
Referencia: RF17, RF18.

---

### [HU-12] Autenticación por rol

**Label:** `feature` · **Core** · **Milestone:** Sprint 2 — Autenticación y autorización

## Historia de Usuario
Como usuario del sistema, quiero autenticarme con un rol (administrador/operario) para que el sistema controle permisos de acceso.

## Criterios de Aceptación
- [ ] Existe login con usuario y contraseña
- [ ] El sistema distingue al menos los roles administrador y operario
- [ ] Las acciones restringidas (tarifas, reportes, eliminar) solo están disponibles para administrador

## Notas técnicas
Referencia: RNF de seguridad ("Acceso mediante autenticación", "Control de permisos").
