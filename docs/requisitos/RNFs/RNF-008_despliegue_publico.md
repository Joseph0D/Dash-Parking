# RNF-008 — Despliegue y operación pública

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RNF-008 |
| **Categoría** | Operación, disponibilidad y despliegue |
| **Prioridad** | Alta |
| **Estado** | Pendiente; corresponde a la fase de despliegue |

## Requisitos

### RNF-008.1 — Transporte seguro
Todo acceso público y enlace de recuperación usa HTTPS. CORS permite únicamente los orígenes
configurados para cada entorno.

### RNF-008.2 — Configuración y secretos
La configuración de producción se inyecta por variables de entorno o un gestor de secretos. No
se incluyen credenciales reales, archivos `.env` ni claves privadas en la imagen o el repositorio.

### RNF-008.3 — Persistencia y migraciones
Producción usa PostgreSQL administrado o respaldado, migraciones versionadas e idempotentes, y
un procedimiento de reversión o recuperación probado. El arranque del servicio no sustituye las
migraciones de producción.

### RNF-008.4 — Salud y observabilidad
El despliegue expone una verificación de salud, centraliza logs sin secretos ni tokens y define
alertas para fallos de base de datos, correo y disponibilidad.

### RNF-008.5 — Operación y restauración
Antes de publicar la URL se documentan el responsable operativo, las copias de seguridad, la
retención, la restauración de prueba, los dominios y el origen CORS del frontend.
