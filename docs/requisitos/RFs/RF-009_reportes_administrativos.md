# RF-009 — Generación de reportes administrativos

<!--
  ¿Qué? Requisito funcional que define los reportes de ocupación, ingresos y vehículos atendidos.
  ¿Para qué? Apoyar la toma de decisiones administrativas y financieras.
  ¿Impacto? Sin reportes, el propietario no tiene visibilidad consolidada del negocio.
-->

---

## Identificación

| Campo         | Valor                                 |
| ------------- | ------------------------------------------|
| **ID**        | RF-009                                     |
| **Nombre**    | Generación de reportes administrativos     |
| **Módulo**    | Administrativo                             |
| **Prioridad** | Media                                       |
| **Estado**    | Implementado (vía RF-017) |
| **Informe original** | RF14                                   |

---

## Descripción

El sistema debe generar reportes de vehículos atendidos, ingresos económicos y ocupación para un
rango de fechas seleccionado.

---

## Entradas

| Campo        | Tipo  | Obligatorio | Validaciones                     |
| ------------ | ----- | ----------- | ------------------------------------ |
| `start_date` | Fecha | Sí          | Debe ser anterior o igual a `end_date` |
| `end_date`   | Fecha | Sí          | Debe ser posterior o igual a `start_date` |

---

## Proceso

1. El propietario selecciona un rango de fechas.
2. El sistema agrega los datos de ingresos, salidas y pagos en ese rango.
3. Se calculan los totales y promedios correspondientes.
4. Se retorna el reporte consolidado.

---

## Salidas

| Escenario            | Código HTTP | Respuesta                                |
| ------------------------ | ----------- | -------------------------------------------- |
| Reporte generado          | 200         | Vehículos atendidos, ingresos totales, ocupación promedio/máxima |
| Rango de fechas inválido  | 422         | Mensaje de validación                        |

---

## Endpoints asociados

| Método | Ruta                                                   | Auth requerida | Descripción            |
| ------ | ---------------------------------------------------------| -------------- | --------------------------|
| GET    | `/api/v1/reports?start_date=...&end_date=...`            | Sí (solo administrador) | Genera el reporte consolidado |

---

## Reglas de negocio

- RN-015: Solo el rol administrador puede generar reportes (ver RF-012).
