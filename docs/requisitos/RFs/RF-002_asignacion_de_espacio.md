# RF-002 — Asignación automática de espacio

<!--
  ¿Qué? Requisito funcional que define la asignación automática de espacios disponibles.
  ¿Para qué? Evitar la asignación manual y el riesgo de doble ocupación de un mismo espacio.
  ¿Impacto? Sin esta regla, dos vehículos podrían quedar asociados al mismo espacio físico.
-->

---

## Identificación

| Campo         | Valor                                |
| ------------- | --------------------------------------|
| **ID**        | RF-002                                 |
| **Nombre**    | Asignación automática de espacio       |
| **Módulo**    | Ingreso                                |
| **Prioridad** | Alta                                   |
| **Estado**    | En progreso (Sprint 0)                 |
| **Informe original** | RF05                            |

---

## Descripción

Al registrarse el ingreso de un vehículo (RF-001), el sistema debe asignar automáticamente el
primer espacio disponible, sin intervención manual, y rechazar la operación si no hay espacios
libres.

---

## Entradas

| Campo   | Tipo | Obligatorio | Validaciones                       |
| ------- | ---- | ----------- | ------------------------------------ |
| (interno, disparado por RF-001) | — | — | Requiere al menos un `ParkingSpot` con `is_available = true` |

---

## Proceso

1. Se dispara automáticamente tras validar el ingreso (RF-001).
2. El sistema busca el primer espacio con estado disponible.
3. Si existe, se marca como ocupado y se asocia la placa del vehículo.
4. Si no existe ninguno disponible, se rechaza el registro de ingreso completo.

---

## Salidas

| Escenario                | Código HTTP | Respuesta                                  |
| -------------------------- | ----------- | --------------------------------------------- |
| Espacio asignado          | 201 (parte de RF-001) | Número de espacio asignado          |
| Sin espacios disponibles  | 422         | Mensaje: no hay espacios disponibles           |

---

## Endpoints asociados

Este requisito no expone un endpoint propio — se ejecuta como parte de `POST /api/v1/vehicles/entry` (RF-001).

---

## Reglas de negocio

- RN-004: Un espacio solo puede estar asociado a un vehículo a la vez.
- RN-005: La liberación del espacio (RF-004) es la única forma de volver a marcarlo disponible.
