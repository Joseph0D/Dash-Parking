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
| **Estado**    | Planificado (Sprint 5 — Integración FE-BE) |

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
