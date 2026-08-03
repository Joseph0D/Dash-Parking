# RNF-006 — Compatibilidad

<!--
  ¿Qué? Requisito no funcional que define la compatibilidad del sistema con el entorno del parqueadero.
  ¿Para qué? Garantizar que el sistema funcione en los equipos y navegadores realmente disponibles en la operación.
  ¿Impacto? Una incompatibilidad bloquea directamente la operación diaria del negocio.
-->

---

## Identificación

| Campo         | Valor              |
| ------------- | ----------------------|
| **ID**        | RNF-006                 |
| **Nombre**    | Compatibilidad            |
| **Categoría** | Compatibilidad / Portabilidad |
| **Prioridad** | Media                       |
| **Estado**    | Planificado (Sprint 5 — Integración FE-BE) |

---

## Requisitos

### RNF-006.1 — Navegadores modernos
El frontend debe funcionar correctamente en las últimas dos versiones estables de Chrome,
Firefox y Edge.

### RNF-006.2 — Equipos del parqueadero
El sistema debe funcionar en los equipos actualmente disponibles en el punto de operación
(navegador web estándar, sin requerimientos de hardware especializado).

### RNF-006.3 — Contenedores portables
El sistema debe poder levantarse en cualquier equipo con Docker y Docker Compose instalados,
sin depender de configuración manual adicional (ver `docs/docker-guia.md` del bootcamp).
