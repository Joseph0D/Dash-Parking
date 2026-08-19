# HU-009 — Generación de reportes administrativos

<!--
  ¿Qué? Historia de usuario que describe la generación de reportes de ocupación, ingresos y vehículos atendidos.
  ¿Para qué? Apoyar la toma de decisiones administrativas y financieras del propietario.
  ¿Impacto? Sin reportes, el propietario no tiene visibilidad consolidada del desempeño del negocio.
-->

---

## Identificación

| Campo            | Valor                                    |
| ---------------- | ------------------------------------------|
| **ID**           | HU-009                                     |
| **Título**       | Generación de reportes administrativos     |
| **Módulo**       | Administrativo                             |
| **Prioridad**    | Media (Secundaria)                         |
| **Estado**       | Implementado (vía dashboard filtrable RF-017) |
| **RF asociados** | RF-009                                     |

---

## Historia

**Como** propietario,
**quiero** generar reportes de ingresos económicos, ocupación y vehículos atendidos en un rango de fechas,
**para** apoyar decisiones administrativas y financieras sobre el parqueadero.

---

## Criterios de aceptación

### CA-009.1 — Reporte de vehículos atendidos

- **Dado que** selecciono un rango de fechas,
- **cuando** genero el reporte,
- **entonces** veo el número de vehículos ingresados y retirados en ese periodo.

### CA-009.2 — Reporte de ingresos económicos

- **Dado que** selecciono un rango de fechas,
- **cuando** genero el reporte,
- **entonces** veo el valor total recaudado por pagos registrados en ese periodo.

### CA-009.3 — Reporte de ocupación histórica

- **Dado que** selecciono un rango de fechas,
- **cuando** genero el reporte,
- **entonces** veo la ocupación promedio y máxima registrada en ese periodo.

### CA-009.4 — Rango de fechas inválido

- **Dado que** selecciono una fecha de inicio posterior a la fecha de fin,
- **cuando** intento generar el reporte,
- **entonces** el sistema rechaza la solicitud con un mensaje de validación.
