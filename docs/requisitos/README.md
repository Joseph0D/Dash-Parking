# Requisitos — Dash Parking

<!--
  ¿Qué? Índice de toda la documentación de requisitos del proyecto.
  ¿Para qué? Punto de entrada único para navegar Historias de Usuario, Requisitos Funcionales,
  No Funcionales y Restricciones.
  ¿Impacto? Sin este índice, la trazabilidad HU ↔ RF queda dispersa entre 30 archivos.
-->

Toda historia de usuario (HU) está mapeada 1 a 1 con un requisito funcional (RF) que la
sustenta técnicamente. Ambos son trazables al informe de diseño original (ver
`../../entregable-s01-plan-de-trabajo.md`, Sección 1).

## Historias de Usuario ([`HUs/`](HUs/))

| HU | Título | RF asociado | Estado |
|---|---|---|---|
| [HU-001](HUs/HU-001_registro_de_ingreso.md) | Registro de ingreso de vehículo | RF-001 | En progreso (Sprint 0) |
| [HU-002](HUs/HU-002_asignacion_de_espacio.md) | Asignación automática de espacio | RF-002 | En progreso (Sprint 0) |
| [HU-003](HUs/HU-003_consulta_de_ocupacion.md) | Consulta de ocupación en tiempo real | RF-003 | Planificado |
| [HU-004](HUs/HU-004_registro_de_salida.md) | Registro de salida de vehículo | RF-004 | Planificado |
| [HU-005](HUs/HU-005_calculo_de_cobro.md) | Cálculo de permanencia y valor a pagar | RF-005 | Planificado |
| [HU-006](HUs/HU-006_registro_de_pago.md) | Registro del pago del servicio | RF-006 | Planificado |
| [HU-007](HUs/HU-007_administrar_tarifas.md) | Administración de tarifas | RF-007 | Planificado |
| [HU-008](HUs/HU-008_busqueda_e_historial.md) | Búsqueda de vehículos e historial | RF-008 | Planificado |
| [HU-009](HUs/HU-009_reportes_administrativos.md) | Generación de reportes administrativos | RF-009 | Planificado |
| [HU-010](HUs/HU-010_administrar_clientes.md) | Administración de clientes | RF-010 | Planificado |
| [HU-011](HUs/HU-011_editar_y_eliminar_registros.md) | Actualización/eliminación de registros | RF-011 | Planificado |
| [HU-012](HUs/HU-012_autenticacion_por_rol.md) | Autenticación por rol | RF-012 | Planificado |

## Requisitos Funcionales ([`RFs/`](RFs/))

RF-001 a RF-012 — ver tabla anterior para el mapeo directo con cada HU.

## Requisitos No Funcionales ([`RNFs/`](RNFs/))

| RNF | Categoría |
|---|---|
| [RNF-001](RNFs/RNF-001_seguridad.md) | Seguridad |
| [RNF-002](RNFs/RNF-002_rendimiento_disponibilidad.md) | Rendimiento y disponibilidad |
| [RNF-003](RNFs/RNF-003_usabilidad.md) | Usabilidad |
| [RNF-004](RNFs/RNF-004_integridad_y_confiabilidad.md) | Integridad y confiabilidad |
| [RNF-005](RNFs/RNF-005_mantenibilidad_y_escalabilidad.md) | Mantenibilidad y escalabilidad |
| [RNF-006](RNFs/RNF-006_compatibilidad.md) | Compatibilidad |

## Restricciones

[`restricciones.md`](restricciones.md) — restricciones tecnológicas, de herramientas, de idioma,
organizacionales y de seguridad, no negociables durante el desarrollo.

---

> Para el backlog priorizado en formato Kanban (GitHub Projects), ver
> `GUIA-CONFIGURACION-GITHUB.md` en la raíz del proyecto — cada HU de esta carpeta es un Issue
> del tablero.
