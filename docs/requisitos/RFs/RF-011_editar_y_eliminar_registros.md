# RF-011 — Actualización y eliminación de registros según permisos

<!--
  ¿Qué? Requisito funcional que define la edición/eliminación de registros con control de permisos.
  ¿Para qué? Permitir corregir errores de digitación sin perder trazabilidad de la operación.
  ¿Impacto? Sin control, cualquier usuario podría alterar el historial y romper la trazabilidad.
-->

---

## Identificación

| Campo         | Valor                                                     |
| ------------- | --------------------------------------------------------------|
| **ID**        | RF-011                                                          |
| **Nombre**    | Actualización y eliminación de registros según permisos         |
| **Módulo**    | Administrativo                                                  |
| **Prioridad** | Media                                                            |
| **Estado**    | Planificado (Sprint 6)                                            |
| **Informe original** | RF17, RF18                                                 |

---

## Descripción

El sistema debe permitir a un administrador editar o eliminar registros de ingreso/salida,
dejando auditoría de quién, cuándo y qué se modificó, y exigiendo confirmación explícita antes
de eliminar un registro con pago asociado.

---

## Entradas

| Campo    | Tipo  | Obligatorio | Validaciones                    |
| -------- | ----- | ----------- | ----------------------------------|
| `record_id` | UUID | Sí       | Debe existir                       |
| `confirm`   | Boolean | Solo si tiene pago asociado | Debe ser `true` para proceder con la eliminación |

---

## Proceso

1. El administrador solicita editar o eliminar un registro.
2. El sistema valida el rol (solo administrador).
3. Si el registro tiene pago asociado y la acción es eliminar, se exige confirmación explícita.
4. Se aplica el cambio y se guarda una entrada de auditoría (usuario, fecha, campo modificado).

---

## Salidas

| Escenario                | Código HTTP | Respuesta                        |
| ---------------------------- | ----------- | ------------------------------------ |
| Registro actualizado          | 200         | Registro actualizado + entrada de auditoría |
| Registro eliminado             | 204         | Sin contenido                        |
| Falta confirmación (con pago)  | 409         | Mensaje: requiere confirmación explícita |
| Sin permisos                   | 403         | Mensaje: acción reservada al administrador |

---

## Endpoints asociados

| Método | Ruta                          | Auth requerida         | Descripción            |
| ------ | -------------------------------- | -------------------------- | --------------------------|
| PATCH  | `/api/v1/records/{record_id}`   | Sí (solo administrador)     | Edita un registro           |
| DELETE | `/api/v1/records/{record_id}`   | Sí (solo administrador)     | Elimina un registro          |

---

## Reglas de negocio

- RN-017: Toda edición o eliminación genera una entrada de auditoría inmutable.
- RN-018: No se puede eliminar un registro con pago asociado sin `confirm=true`.
