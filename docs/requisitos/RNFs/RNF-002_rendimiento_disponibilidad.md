# RNF-002 — Rendimiento y disponibilidad

<!--
  ¿Qué? Requisito no funcional que define tiempos de respuesta y disponibilidad del sistema.
  ¿Para qué? Garantizar atención ágil en el flujo de ingreso/salida, donde la rapidez es crítica.
  ¿Impacto? Un sistema lento reintroduce el problema original: filas y demoras en la atención.
-->

---

## Identificación

| Campo         | Valor                             |
| ------------- | -------------------------------------|
| **ID**        | RNF-002                                |
| **Nombre**    | Rendimiento y disponibilidad            |
| **Categoría** | Rendimiento                              |
| **Prioridad** | Alta                                      |
| **Estado**    | Planificado (evaluado en Sprint 7 — Pruebas) |

---

## Requisitos

### RNF-002.1 — Tiempo de respuesta en operaciones de ingreso/salida
Las operaciones de registro de ingreso y salida deben responder en menos de 1 segundo bajo
condiciones normales de operación (sin carga concurrente alta).

### RNF-002.2 — Consultas eficientes
Las consultas de ocupación e historial deben usar índices en los campos de búsqueda frecuente
(`plate`, fechas), evitando escaneos completos de tabla a medida que crece el historial.

### RNF-002.3 — Disponibilidad en horario de operación
El sistema debe estar disponible durante todo el horario de operación del parqueadero definido
por el propietario.

### RNF-002.4 — Bajo tiempo de espera percibido
Toda operación que tarde más de 300 ms debe mostrar un indicador de carga en el frontend.
