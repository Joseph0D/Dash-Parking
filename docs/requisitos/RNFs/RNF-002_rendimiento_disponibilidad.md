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
| **Estado**    | Parcial; los objetivos de producción y el SLO están pendientes |

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

### RNF-002.5 — Frescura de disponibilidad
El resumen del mapa se actualiza al menos cada cinco segundos y la consulta detallada se puede
actualizar manualmente. El resultado de una reserva siempre se valida nuevamente en el backend;
la frecuencia de refresco del navegador no garantiza ni sustituye un cupo.

### RNF-002.6 — Reservas concurrentes
La base de datos impide confirmar dos reservas solapadas para el mismo espacio o vehículo, incluso
si las solicitudes llegan simultáneamente. El conflicto se comunica sin dejar una reserva parcial.

### RNF-002.7 — Objetivo de disponibilidad pública
Antes de habilitar el servicio público, el responsable debe acordar y medir un objetivo de
disponibilidad mensual, la ventana de mantenimiento y los tiempos de recuperación. No se asigna
un porcentaje como compromiso contractual hasta que se apruebe.
