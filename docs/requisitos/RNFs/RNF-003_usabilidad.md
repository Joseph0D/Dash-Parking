# RNF-003 — Usabilidad

<!--
  ¿Qué? Requisito no funcional que define los estándares de usabilidad de la interfaz.
  ¿Para qué? Garantizar que operarios sin formación técnica puedan usar el sistema sin fricción.
  ¿Impacto? Una interfaz confusa reintroduce errores humanos, justo lo que el sistema busca eliminar.
-->

---

## Identificación

| Campo         | Valor            |
| ------------- | -------------------|
| **ID**        | RNF-003              |
| **Nombre**    | Usabilidad            |
| **Categoría** | Usabilidad / UX         |
| **Prioridad** | Alta                    |
| **Estado**    | Parcial; la experiencia móvil requiere validación sistemática |

---

## Requisitos

### RNF-003.1 — Interfaz intuitiva
Las pantallas de ingreso y salida deben poder usarse sin capacitación previa extensa —
formularios cortos, con el menor número de campos posible.

### RNF-003.2 — Menú organizado por rol
El menú principal debe mostrar solo las opciones habilitadas para el rol de la sesión activa
(operario ve ingreso/salida; administrador ve además tarifas, reportes y clientes).

### RNF-003.3 — Retroalimentación inmediata
Toda acción del usuario (registrar, buscar, confirmar pago) debe dar una confirmación visual
clara de éxito o error.

### RNF-003.4 — Mensajes de error entendibles
Los mensajes de error deben describir el problema en lenguaje claro, sin jerga técnica ni
códigos internos.

### RNF-003.5 — Uso móvil
Los flujos principales (registro, consulta de disponibilidad, reserva y recuperación de
contraseña) deben poder completarse en una pantalla de 360 × 640 píxeles sin desplazamiento
horizontal. El mapa y sus controles deben seguir siendo utilizables con interacción táctil.
Este criterio requiere validación visual en navegadores móviles antes de aceptarse.

### RNF-003.6 — Retroalimentación sobre disponibilidad
La interfaz distingue claramente la disponibilidad consultada de una reserva confirmada y
explica los conflictos de horario, tipo de vehículo o inventario sin depender solo del color.
