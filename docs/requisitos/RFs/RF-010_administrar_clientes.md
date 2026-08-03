# RF-010 — Administración de información de clientes

<!--
  ¿Qué? Requisito funcional que define el registro y consulta de clientes frecuentes.
  ¿Para qué? Asociar vehículos a un cliente para dar mejor trazabilidad y atención personalizada.
  ¿Impacto? Sin este registro, no se puede identificar clientes recurrentes.
-->

---

## Identificación

| Campo         | Valor                                      |
| ------------- | -----------------------------------------------|
| **ID**        | RF-010                                          |
| **Nombre**    | Administración de información de clientes       |
| **Módulo**    | Clientes                                        |
| **Prioridad** | Media                                            |
| **Estado**    | Planificado (Sprint 6)                            |
| **Informe original** | RF16                                        |

---

## Descripción

El sistema debe permitir registrar clientes (nombre, contacto) y asociarlos a una o más placas,
de forma que los ingresos de esas placas se vinculen automáticamente al cliente.

---

## Entradas

| Campo    | Tipo  | Obligatorio | Validaciones            |
| -------- | ----- | ----------- | -------------------------- |
| `name`   | Texto | Sí          | Mínimo 2 caracteres          |
| `contact`| Texto | No          | Formato de teléfono o email si se provee |
| `plate`  | Texto | No          | Debe existir como vehículo registrado, si se asocia |

---

## Proceso

1. El administrador registra un cliente con su nombre y datos de contacto.
2. Opcionalmente, asocia una o más placas a ese cliente.
3. Los ingresos posteriores de esas placas quedan vinculados automáticamente al cliente.

---

## Salidas

| Escenario         | Código HTTP | Respuesta               |
| --------------------- | ----------- | ----------------------------|
| Cliente registrado     | 201         | Datos del cliente creado     |
| Placa ya asociada a otro cliente | 409 | Mensaje de conflicto        |

---

## Endpoints asociados

| Método | Ruta                              | Auth requerida | Descripción                |
| ------ | ------------------------------------| -------------- | ------------------------------|
| POST   | `/api/v1/customers`                 | Sí             | Registra un cliente            |
| POST   | `/api/v1/customers/{id}/vehicles`   | Sí             | Asocia una placa al cliente     |
| GET    | `/api/v1/customers/{id}/history`    | Sí             | Historial de vehículos del cliente |

---

## Reglas de negocio

- RN-016: Una placa solo puede estar asociada a un cliente a la vez.
