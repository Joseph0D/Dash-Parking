# RNF-001 — Seguridad

<!--
  ¿Qué? Requisito no funcional que define los estándares de seguridad del sistema.
  ¿Para qué? Proteger contraseñas, sesiones y datos operativos del parqueadero.
  ¿Impacto? Un fallo de seguridad podría exponer credenciales o permitir manipular tarifas/registros sin autorización.
-->

---

## Identificación

| Campo         | Valor                          |
| ------------- | ---------------------------------|
| **ID**        | RNF-001                           |
| **Nombre**    | Seguridad                          |
| **Categoría** | Seguridad de la información        |
| **Prioridad** | Crítica                             |
| **Estado**    | Planificado (Sprint 2)               |

---

## Requisitos

### RNF-001.1 — Hashing de contraseñas
Las contraseñas se almacenan con **bcrypt**. Nunca en texto plano ni en respuestas de la API.

### RNF-001.2 — Autenticación mediante token
El acceso a endpoints protegidos requiere un token de sesión válido (JWT), con expiración
definida. Ver RF-012.

### RNF-001.3 — Prevención de enumeración de usuarios
Los mensajes de error en login deben ser genéricos, sin distinguir si el usuario existe.

### RNF-001.4 — Validación de entradas
Toda entrada se valida en frontend y backend (Pydantic en backend).

### RNF-001.5 — Protección contra inyección SQL
Toda consulta a la base de datos se hace vía SQLAlchemy ORM; no se permite SQL crudo sin
parametrizar.

### RNF-001.6 — Variables de entorno
Toda credencial sensible (claves, cadenas de conexión) vive en `.env`, no versionado, con
`.env.example` como plantilla.

### RNF-001.7 — Control de permisos por rol
Cada endpoint sensible valida explícitamente el rol requerido (administrador/operario), no solo
la autenticación.
