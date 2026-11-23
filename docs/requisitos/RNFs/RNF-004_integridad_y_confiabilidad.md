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
| **Estado**    | Parcial; restricciones de reserva y migraciones existen, restauración pendiente de prueba |

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

### RNF-004.5 — Integridad temporal de reservas
Los rangos se interpretan como `[inicio, fin)`, se convierten de la hora de Bogotá a UTC para
persistencia y no se solapan para un mismo espacio o vehículo. Cancelar libera únicamente el
rango de esa reserva y conserva su historial.

### RNF-004.6 — Consumo único de tokens
Un token de recuperación solo puede cambiar la contraseña una vez. Los tokens vencidos,
inexistentes o consumidos se rechazan con una respuesta uniforme.

### RNF-004.7 — Recuperación de la base de datos
Las copias de seguridad de producción deben tener una restauración de prueba documentada antes
de declarar disponible el servicio público.
