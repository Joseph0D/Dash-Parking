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
| **Estado**    | Parcial; dashboard global y panel diario de dueño tienen alcances distintos |
| **Informe original** | RF14                                   |

---

## Descripción

El sistema genera reportes de vehículos atendidos, ingresos y ocupación en el alcance autorizado.
El administrador de plataforma puede consultar datos globales; el dueño solo los de sus
parqueaderos. El panel diario del dueño se define aparte en RF-020 y no equivale a un reporte
histórico.

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
| GET    | `/api/v1/reports/dashboard` | Sí (solo administrador de plataforma) | Métricas agregadas y filtrables; ver RF-017 |

---

## Reglas de negocio

- RN-015: El rol y el alcance del parqueadero se validan en backend; los reportes globales son
  exclusivos del administrador de plataforma. El panel diario de dueño verifica propiedad (RF-020).
