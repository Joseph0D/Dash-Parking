# RF-012 — Autenticación por rol

<!--
  ¿Qué? Requisito funcional que define la autenticación y el control de acceso por rol.
  ¿Para qué? Restringir acciones sensibles (tarifas, reportes, eliminación) solo a usuarios autorizados.
  ¿Impacto? Sin autenticación, cualquier persona con acceso al sistema podría alterar tarifas o eliminar historial.
-->

---

## Identificación

| Campo         | Valor                    |
| ------------- | ----------------------------|
| **ID**        | RF-012                       |
| **Nombre**    | Autenticación por rol         |
| **Módulo**    | Autenticación                  |
| **Prioridad** | Alta                            |
| **Estado**    | Implementado |
| **Informe original** | RNF de seguridad (Acceso mediante autenticación, Control de permisos) |

---

## Descripción

El sistema autentica mediante correo y contraseña e identifica uno de estos roles: cliente,
dueño, operador o administrador de plataforma. Cada endpoint comprueba el rol y, para recursos
propios, la propiedad o asignación del parqueadero.

---

## Entradas

| Campo      | Tipo  | Obligatorio | Validaciones            |
| ---------- | ----- | ----------- | ---------------------------|
| `email`    | Email | Sí          | Debe existir en el sistema  |
| `password` | Texto | Sí          | Se valida contra el hash almacenado |

---

## Proceso

1. El usuario ingresa correo y contraseña.
2. El backend valida las credenciales contra el hash almacenado (bcrypt).
3. Si son válidas, se emite un token de sesión (JWT) que incluye el rol del usuario.
4. Cada endpoint protegido valida el token y, cuando corresponde, el rol requerido.
5. Los mensajes de error de login son genéricos, sin revelar si el usuario existe.
6. El autorregistro solo permite cliente o dueño; los roles operador y administrador se asignan
   por una vía autorizada.

---

## Salidas

| Escenario              | Código HTTP | Respuesta                       |
| --------------------------- | ----------- | ------------------------------------ |
| Login exitoso                | 200         | Token de sesión + rol del usuario     |
| Credenciales inválidas       | 401         | Mensaje genérico de error             |
| Acceso a recurso sin permiso | 403         | Mensaje: acción reservada a otro rol   |

---

## Endpoints asociados

| Método | Ruta                    | Auth requerida | Descripción            |
| ------ | --------------------------| -------------- | --------------------------|
| POST   | `/api/v1/auth/login`      | No             | Autentica y retorna el token |
| POST   | `/api/v1/auth/register` | No | Crea una cuenta cliente o dueño (ver RF-016) |
| GET    | `/api/v1/auth/me` | Sí | Consulta el usuario autenticado |
| PUT    | `/api/v1/auth/me` | Sí | Actualiza el perfil propio |

---

## Reglas de negocio

- RN-019: Las contraseñas nunca se almacenan en texto plano — se hashean con bcrypt.
- RN-020: Los mensajes de error de autenticación no deben permitir enumerar usuarios existentes.
- RN-021: Cada endpoint sensible (tarifas, reportes, eliminar registros) valida explícitamente el rol requerido, no solo la autenticación.
- RNF-001.7: Dueños y operadores solo acceden a parqueaderos propios o asignados,
  respectivamente; la verificación se ejecuta en cada endpoint del backend.
