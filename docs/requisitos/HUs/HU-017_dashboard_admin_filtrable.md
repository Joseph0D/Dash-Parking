# HU-017 — Dashboard administrativo filtrable

<!--
  ¿Qué? Historia que amplía RF-009 (reportes) con un dashboard interactivo y filtros dinámicos.
  ¿Para qué? Permitir al administrador explorar la información sin generar un reporte estático cada vez.
  ¿Impacto? Sin filtros, el administrador solo vería totales fijos, no podría analizar por vehículo o fecha.
-->

## Identificación

| Campo | Valor |
|---|---|
| **ID** | HU-017 |
| **Módulo** | Administrativo |
| **Prioridad** | Alta (Core — solicitado explícitamente por el cliente) |
| **Estado** | Implementado |
| **RF asociados** | RF-017 (extiende RF-009) |

## Historia

**Como** administrador, **quiero** ver un dashboard con la ganancia total y poder filtrarlo por tipo de vehículo y por rango de fechas, **para** analizar el desempeño del parqueadero sin exportar un reporte cada vez.

## Criterios de aceptación

### CA-017.1 — Ganancia total por defecto
Dado que entro al dashboard sin filtros, cuando carga, entonces veo la ganancia total acumulada, el número de sesiones y la ocupación actual.

### CA-017.2 — Filtro por tipo de vehículo
Dado que selecciono un tipo de vehículo (carro/moto/bicicleta), cuando aplico el filtro, entonces las métricas se recalculan solo con las sesiones de ese tipo.

### CA-017.3 — Filtro por rango de fechas
Dado que selecciono una fecha de inicio y fin, cuando aplico el filtro, entonces las métricas se recalculan solo con las sesiones/pagos dentro de ese rango.

### CA-017.4 — Combinación de filtros
Dado que aplico tipo de vehículo y rango de fechas a la vez, cuando se procesa la consulta, entonces ambos filtros se combinan (AND), no se reemplazan entre sí.
