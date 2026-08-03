# RF-001 — Registro de ingreso de vehículo

<!--
  ¿Qué? Requisito funcional que define el registro del ingreso de un vehículo al parqueadero.
  ¿Para qué? Documentar formalmente el proceso que reemplaza el registro manual actual.
  ¿Impacto? Es la base de todo el flujo: sin ingreso registrado no hay ocupación, cobro ni historial.
-->

---

## Identificación

| Campo         | Valor                       |
| ------------- | ------------------------------|
| **ID**        | RF-001                        |
| **Nombre**    | Registro de ingreso de vehículo |
| **Módulo**    | Ingreso                       |
| **Prioridad** | Alta                          |
| **Estado**    | En progreso (Sprint 0)        |
| **Informe original** | RF01, RF02, RF03, RF04 |

---

## Descripción

El sistema debe permitir que un operario registre el ingreso de un vehículo indicando su placa y
tipo de vehículo. La fecha y hora de ingreso se registran automáticamente, sin intervención
manual del operario, para eliminar el error humano identificado en el diagnóstico del parqueadero.

---

## Entradas

| Campo          | Tipo   | Obligatorio | Validaciones                                             |
| -------------- | ------ | ----------- | ---------------------------------------------------------- |
| `plate`        | Texto  | Sí          | 1–10 caracteres, se normaliza a mayúsculas sin espacios     |
| `vehicle_type` | Enum   | Sí          | Uno de: `car`, `motorcycle`, `truck`                        |

---

## Proceso

1. El operario ingresa la placa y selecciona el tipo de vehículo.
2. El backend normaliza la placa (mayúsculas, sin espacios).
3. El backend valida que la placa no tenga ya un ingreso activo (sin salida registrada).
4. El backend registra la fecha y hora de ingreso automáticamente (UTC).
5. El sistema dispara la asignación de espacio (ver RF-002).
6. Se retorna la confirmación del ingreso con el espacio asignado.

---

## Salidas

| Escenario                     | Código HTTP | Respuesta                                          |
| ------------------------------ | ----------- | ---------------------------------------------------- |
| Ingreso registrado exitosamente | 201         | Placa, tipo de vehículo, hora de ingreso, espacio asignado |
| Placa ya está dentro           | 409         | Mensaje: vehículo ya se encuentra dentro del parqueadero |
| Sin espacios disponibles       | 422         | Mensaje: no hay espacios disponibles en este momento |
| Datos inválidos                | 422         | Detalle de los errores de validación                 |

---

## Endpoints asociados

| Método | Ruta                          | Auth requerida | Descripción                              |
| ------ | ----------------------------- | -------------- | ------------------------------------------ |
| POST   | `/api/v1/vehicles/entry`      | Sí (operario/administrador) | Registra el ingreso y asigna espacio |

> Sprint 0: el endpoint existe y funciona sobre datos en memoria, sin autenticación aún — la
> autenticación se agrega en el Sprint 2 (ver RF-012).

---

## Reglas de negocio

- RN-001: La placa es el identificador de negocio único mientras el vehículo está dentro.
- RN-002: No puede existir más de un ingreso activo (sin salida) para la misma placa.
- RN-003: La hora de ingreso siempre la asigna el sistema — nunca la digita el operario.
