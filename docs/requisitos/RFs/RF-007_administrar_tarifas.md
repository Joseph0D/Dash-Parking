# RF-007 — Administración de tarifas

<!--
  ¿Qué? Requisito funcional que define la creación y actualización de tarifas por tipo de vehículo.
  ¿Para qué? Dar al cálculo de cobro (RF-005) una fuente de verdad administrable por el negocio.
  ¿Impacto? Sin tarifas administrables, el sistema no tendría con qué calcular el cobro.
-->

---

## Identificación

| Campo         | Valor                       |
| ------------- | -------------------------------|
| **ID**        | RF-007                          |
| **Nombre**    | Administración de tarifas       |
| **Módulo**    | Tarifas                         |
| **Prioridad** | Alta                             |
| **Estado**    | Planificado (Sprint 1)           |
| **Informe original** | RF15                       |

---

## Descripción

El sistema debe permitir que un administrador cree y actualice tarifas por tipo de vehículo. El
cálculo de cobro (RF-005) siempre debe usar la tarifa vigente al momento de la salida.

---

## Entradas

| Campo          | Tipo    | Obligatorio | Validaciones                    |
| -------------- | ------- | ----------- | ---------------------------------- |
| `vehicle_type` | Enum    | Sí          | `car`, `motorcycle`, `truck`        |
| `rate`         | Decimal | Sí          | Mayor a cero                        |

---

## Proceso

1. El administrador crea o actualiza una tarifa para un tipo de vehículo.
2. El sistema valida que el valor sea mayor a cero.
3. Se guarda como tarifa vigente para ese tipo de vehículo.

---

## Salidas

| Escenario           | Código HTTP | Respuesta                  |
| ---------------------- | ----------- | ------------------------------ |
| Tarifa creada/actualizada | 200/201  | Datos de la tarifa vigente      |
| Valor inválido          | 422         | Mensaje de validación           |
| Sin permisos            | 403         | Mensaje: acción reservada al administrador |

---

## Endpoints asociados

| Método | Ruta                       | Auth requerida        | Descripción              |
| ------ | ----------------------------- | ------------------------ | ---------------------------|
| POST   | `/api/v1/rates`               | Sí (solo administrador)   | Crea una tarifa             |
| PUT    | `/api/v1/rates/{vehicle_type}`| Sí (solo administrador)   | Actualiza la tarifa vigente |

---

## Reglas de negocio

- RN-012: Solo el rol administrador puede crear o modificar tarifas (ver RF-012).
- RN-013: No pueden existir dos tarifas vigentes simultáneas para el mismo tipo de vehículo.
