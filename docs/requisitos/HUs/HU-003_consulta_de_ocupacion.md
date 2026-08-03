# HU-003 — Consulta de ocupación en tiempo real

<!--
  ¿Qué? Historia de usuario que describe la consulta del estado de ocupación del parqueadero.
  ¿Para qué? Permitir que el administrador conozca en todo momento cuántos espacios están libres/ocupados.
  ¿Impacto? Sin esta consulta, no hay forma de controlar la capacidad ni de planificar la operación diaria.
-->

---

## Identificación

| Campo            | Valor                                |
| ---------------- | -------------------------------------- |
| **ID**           | HU-003                                 |
| **Título**       | Consulta de ocupación en tiempo real   |
| **Módulo**       | Administrativo                         |
| **Prioridad**    | Alta (Core)                            |
| **Estado**       | Planificado (Sprint 3 — API CRUD)      |
| **RF asociados** | RF-003                                 |

---

## Historia

**Como** administrador,
**quiero** consultar los vehículos actualmente dentro del parqueadero y el número de espacios libres/ocupados,
**para** conocer la ocupación en tiempo real sin recorrer el parqueadero físicamente.

---

## Criterios de aceptación

### CA-003.1 — Listado de vehículos dentro

- **Dado que** hay vehículos con ingreso registrado y sin salida,
- **cuando** consulto el listado de ocupación,
- **entonces** veo cada vehículo con su placa, tipo, hora de ingreso y espacio asignado.

### CA-003.2 — Conteo de disponibilidad

- **Dado que** consulto el estado del parqueadero,
- **cuando** la pantalla carga,
- **entonces** veo el número total de espacios, cuántos están ocupados y cuántos libres.

### CA-003.3 — Actualización sin recarga manual

- **Dado que** un vehículo ingresa o sale mientras tengo la pantalla de ocupación abierta,
- **cuando** ocurre ese evento,
- **entonces** la información reflejada corresponde al estado real del sistema (vía refresco automático o al reconsultar).

### CA-003.4 — Parqueadero lleno

- **Dado que** todos los espacios están ocupados,
- **cuando** consulto el estado,
- **entonces** veo un indicador explícito de "parqueadero lleno".
