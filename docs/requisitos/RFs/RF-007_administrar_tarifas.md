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
| **Estado**    | Parcial; tarifas por parqueadero y tipo configurables en el panel de dueño |
| **Informe original** | RF15                       |

---

## Descripción

El sistema permite que un dueño cree y actualice tarifas para sus parqueaderos y tipos de
vehículo. El cálculo de cobro (RF-005) usa la tarifa vigente correspondiente al parqueadero y
vehículo.

---

## Entradas

| Campo          | Tipo    | Obligatorio | Validaciones                    |
| -------------- | ------- | ----------- | ---------------------------------- |
| `parking_lot_id` | UUID | Sí | Debe pertenecer al dueño autenticado |
| `vehicle_type` | Enum | Sí | Categoría admitida por el parqueadero |
| `rate_per_minute` | Decimal | Sí | Mayor a cero |
| `daily_cap` | Decimal | Sí | Mayor a cero |
| Vigencia | Fechas | Sí | Fin posterior al inicio; sin cruces para el mismo parqueadero/tipo |

---

## Proceso

1. El dueño crea o actualiza una tarifa de un parqueadero propio para un tipo de vehículo.
2. El sistema valida que el valor sea mayor a cero.
3. Se guarda como tarifa vigente para ese tipo de vehículo.

---

## Salidas

| Escenario           | Código HTTP | Respuesta                  |
| ---------------------- | ----------- | ------------------------------ |
| Tarifa creada/actualizada | 200/201  | Tarifa vigente del parqueadero y categoría      |
| Valor inválido          | 422         | Mensaje de validación           |
| Sin permisos            | 403         | Mensaje: no puede modificar tarifas de un parqueadero ajeno |

---

## Endpoints asociados

| Método | Ruta                       | Auth requerida        | Descripción              |
| ------ | ----------------------------- | ------------------------ | ---------------------------|
| PUT | Endpoints de `be/app/routers/owner_parking_lots.py` | Sí (dueño propietario) | Actualiza inventario y tarifas del parqueadero propio |

---

## Reglas de negocio

- RN-012: Solo el dueño propietario del parqueadero o un administrador autorizado puede crear o
  modificar tarifas.
- RN-013: No pueden existir dos tarifas vigentes simultáneas para el mismo parqueadero y tipo de
  vehículo.
