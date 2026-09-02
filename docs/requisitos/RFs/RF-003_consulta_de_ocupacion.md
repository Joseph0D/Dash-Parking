# RF-003 — Consulta de ocupación en tiempo real

<!--
  ¿Qué? Requisito funcional que define la consulta del estado de ocupación del parqueadero.
  ¿Para qué? Dar visibilidad administrativa de la capacidad disponible en cualquier momento.
  ¿Impacto? Sin esta consulta, la administración no puede monitorear la operación en curso.
-->

---

## Identificación

| Campo         | Valor                                    |
| ------------- | -------------------------------------------|
| **ID**        | RF-003                                      |
| **Nombre**    | Consulta de ocupación en tiempo real        |
| **Módulo**    | Administrativo                              |
| **Prioridad** | Alta                                        |
| **Estado**    | Implementado |
| **Informe original** | RF06, RF20                           |

---

## Descripción

El sistema debe exponer el listado de vehículos actualmente dentro del parqueadero y un resumen
de ocupación (espacios totales, ocupados y libres), consultable en cualquier momento.

---

## Entradas

Ninguna obligatoria; opcionalmente filtros por tipo de vehículo o espacio.

---

## Proceso

1. El administrador solicita el estado de ocupación.
2. El sistema consulta los vehículos sin salida registrada y los espacios ocupados.
3. Se calcula el resumen (totales, ocupados, libres).
4. Se retorna el listado y el resumen.

---

## Salidas

| Escenario           | Código HTTP | Respuesta                                     |
| ---------------------- | ----------- | ------------------------------------------------ |
| Consulta exitosa       | 200         | Listado de vehículos dentro + resumen de ocupación |

---

## Endpoints asociados

| Método | Ruta                        | Auth requerida | Descripción                          |
| ------ | ---------------------------- | -------------- | --------------------------------------- |
| GET    | `/api/v1/parking/occupancy`  | Sí             | Retorna vehículos dentro y resumen de ocupación |

---

## Reglas de negocio

- RN-006: Un vehículo se considera "dentro" mientras no tenga `exit_time` registrado.
