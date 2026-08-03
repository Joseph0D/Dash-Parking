# RNF-004 — Integridad y confiabilidad

<!--
  ¿Qué? Requisito no funcional que define la consistencia e integridad de la información almacenada.
  ¿Para qué? Garantizar que el historial y los cobros reflejen fielmente lo ocurrido en el parqueadero.
  ¿Impacto? Una inconsistencia aquí compromete directamente la confianza del propietario en los reportes financieros.
-->

---

## Identificación

| Campo         | Valor                        |
| ------------- | --------------------------------|
| **ID**        | RNF-004                          |
| **Nombre**    | Integridad y confiabilidad         |
| **Categoría** | Calidad del dato                    |
| **Prioridad** | Alta                                 |
| **Estado**    | Planificado (Sprint 1 — Dominio y persistencia) |

---

## Requisitos

### RNF-004.1 — Sin registros duplicados
No pueden existir dos ingresos activos para la misma placa (validado en RF-001).

### RNF-004.2 — Validación de datos en cada capa
Todo dato se valida tanto en el frontend como en el backend (Pydantic), antes de persistirse.

### RNF-004.3 — Almacenamiento permanente
Toda operación confirmada (ingreso, salida, pago, tarifa) se persiste en PostgreSQL — nada
relevante para la trazabilidad vive solo en memoria una vez pasado el Sprint 1.

### RNF-004.4 — Recuperación ante fallos
Ante un error durante una operación (ej. falla al liberar espacio tras registrar salida), el
sistema no debe dejar datos a medio actualizar — las operaciones que afectan más de una entidad
se ejecutan de forma transaccional.
