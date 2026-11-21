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
| **Estado**    | Parcial; base implementada y criterios adicionales pendientes de validación |

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
Cada endpoint sensible valida el rol y el alcance del recurso en el backend. Los roles incluyen
cliente, dueño, operador y administrador de plataforma. Un dueño solo puede consultar o modificar
parqueaderos de su propiedad; un operador solo los parqueaderos que tenga asignados.

### RNF-001.8 — Restablecimiento seguro de contraseña
Los tokens de recuperación se generan aleatoriamente, se almacenan solo como hash, tienen un solo
uso y vencen en 30 minutos. El endpoint no revela si una cuenta existe y limita solicitudes a
tres por correo y diez por IP en una ventana móvil de una hora.

### RNF-001.9 — Protección de secretos y enlaces
Las credenciales SMTP y de base de datos se guardan solo en variables de entorno no versionadas.
Los enlaces de recuperación se generan con la URL configurada del frontend y se sirven mediante
HTTPS en producción.

### RNF-001.10 — Minimización de datos en registros
Los logs no incluyen contraseñas, tokens de recuperación, claves SMTP ni datos personales que no
sean necesarios para diagnosticar el servicio.
