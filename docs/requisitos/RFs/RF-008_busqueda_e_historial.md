# RF-008 — Búsqueda de vehículos y consulta de historial

<!--
  ¿Qué? Requisito funcional que define la búsqueda de vehículos por placa y consulta de historial.
  ¿Para qué? Permitir auditoría y resolución de reclamos sobre operaciones pasadas.
  ¿Impacto? Sin esta consulta no hay forma de verificar información histórica ante un reclamo.
-->

---

## Identificación

| Campo         | Valor                                          |
| ------------- | --------------------------------------------------|
| **ID**        | RF-008                                              |
| **Nombre**    | Búsqueda de vehículos y consulta de historial       |
| **Módulo**    | Administrativo                                      |
| **Prioridad** | Media                                                |
| **Estado**    | Planificado (Sprint 6)                               |
| **Informe original** | RF12, RF13                                    |

---

## Descripción

El sistema debe permitir buscar vehículos por placa (exacta o parcial) y consultar su historial
completo de ingresos, salidas y pagos, ordenado cronológicamente.

---

## Entradas

| Campo   | Tipo  | Obligatorio | Validaciones          |
| ------- | ----- | ----------- | ------------------------ |
| `plate` | Texto | Sí          | Mínimo 2 caracteres       |

---

## Proceso

1. El usuario ingresa un criterio de búsqueda por placa.
2. El sistema busca coincidencias exactas o parciales.
3. Se retorna el listado de vehículos coincidentes.
4. Al seleccionar uno, se retorna su historial completo (ingresos, salidas, pagos).

---

## Salidas

| Escenario         | Código HTTP | Respuesta                    |
| --------------------- | ----------- | -------------------------------- |
| Coincidencias encontradas | 200      | Listado de vehículos              |
| Sin coincidencias      | 200         | Listado vacío                     |

---

## Endpoints asociados

| Método | Ruta                              | Auth requerida | Descripción                  |
| ------ | ------------------------------------ | -------------- | -------------------------------|
| GET    | `/api/v1/vehicles?plate={query}`    | Sí             | Busca vehículos por placa       |
| GET    | `/api/v1/vehicles/{plate}/history`  | Sí             | Retorna el historial del vehículo |

---

## Reglas de negocio

- RN-014: La búsqueda no distingue mayúsculas/minúsculas, dado que las placas se normalizan al registrarse (RF-001).
