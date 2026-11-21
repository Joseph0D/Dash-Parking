# Preparación de demo pública

## Alcance y límites

La configuración usa [Vercel Hobby](https://vercel.com/pricing) para el frontend,
[Render Free](https://render.com/docs/free) para la API y [Neon Free](https://neon.com/pricing)
para PostgreSQL. Es una demo pública de costo cero, no un servicio de producción con
disponibilidad garantizada:

- Render Free suspende la API tras inactividad; la primera petición puede tardar en responder.
- Neon Free tiene límites de uso y no ofrece SLA. No cargues datos sensibles ni dependas de este
  entorno como único respaldo.
- Render Free bloquea SMTP saliente. En el despliegue, la recuperación usa la API HTTPS de Brevo.
  El envío SMTP local sigue disponible.
- Neon soporta `btree_gist`, requerido por la migración de reservas
  ([extensiones](https://neon.com/docs/extensions/pg-extensions)).
- La API y la base pueden tener arranques en frío. La pantalla puede necesitar reintentar una
  petición inicial después de un periodo sin uso.

Para usuarios reales o disponibilidad continua, migra a planes pagos y configura copias
automáticas, retención y una restauración probada antes de anunciar el servicio como producción.

## Recursos preparados

- `render.yaml`: servicio Docker de Render Free, con despliegue automático desactivado y las
  variables sensibles marcadas para cargarlas directamente en el panel.
- `be/Dockerfile`: imagen backend no-root; aplica las migraciones versionadas y luego escucha el
  puerto `PORT` del proveedor. No ejecuta seed ni `--reload`.
- `be/app/scripts/migrate_production.py`: serializa despliegues con un advisory lock de PostgreSQL,
  crea el esquema inicial solo en una base vacía y registra las migraciones aplicadas.
- `fe/vercel.json`: fallback de rutas SPA de React Router.
- `VITE_API_BASE_URL`: obligatorio en builds de producción y debe usar HTTPS. En desarrollo local
  se conserva `http://localhost:8000`.

El esquema nuevo se crea con `db/migrations/000_uuid_initial_schema.sql`; después se aplican las
migraciones UUID 004, 005 y 006. Las migraciones 001–003 corresponden a `dash_parking_v2` y no se
ejecutan contra la base pública UUID. Una base existente con un esquema parcial detiene el arranque
para evitar cambios ambiguos.

## Configuración manual (sin compartir secretos)

No se han creado cuentas, servicios ni despliegues. Antes de publicar, sigue este orden:

1. **Neon:** crea una base PostgreSQL en AWS US East (N. Virginia), región `aws-us-east-1`, para
   mantenerla cerca del backend Render Virginia. Neon no permite cambiar la región después de
   crear el proyecto. Copia su URL pooled con SSL y guárdala en Render como `DATABASE_URL`. El backend
   normaliza URLs `postgres://` y `postgresql://` al driver psycopg.
2. **Vercel:** importa el repositorio y selecciona `fe` como directorio raíz. Usa `npm run build`
   y `dist` como salida. Configura temporalmente `VITE_API_BASE_URL` con una URL HTTPS válida,
   despliega para obtener el dominio asignado y copia ese dominio exacto.
3. **Brevo:** desde la cuenta existente, genera una API key y verifica el correo remitente. No la
   pegues en el repositorio ni en el chat.
4. **Render:** importa el Blueprint desde `render.yaml`. Antes de crear el servicio, completa los
   valores marcados `sync: false` en el panel; el despliegue aplicará las migraciones antes de
   arrancar la API. Despliegue automático está desactivado.
5. **Render ↔ Vercel:** en Render configura `CORS_ORIGINS` y `FRONTEND_BASE_URL` con el dominio
   HTTPS exacto de Vercel. En Vercel reemplaza `VITE_API_BASE_URL` por la URL HTTPS de Render y
   vuelve a desplegar.
6. **Prueba antes de compartir:** abre `/health` en la URL de Render y valida registro, inicio de
   sesión, recuperación de contraseña (incluido el correo real), mapa, consulta de disponibilidad
   y flujo de reserva. Verifica también una ruta interna del frontend al recargar la página.

Genera `JWT_SECRET` localmente y pégalo directamente en el panel, sin enviarlo por el chat. En
PowerShell:

```powershell
$rng = [Security.Cryptography.RandomNumberGenerator]::Create()
$bytes = New-Object byte[] 48
$rng.GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

### Variables del backend

| Variable | Configuración |
|---|---|
| `APP_ENV` | `production` (definida en `render.yaml`) |
| `DATABASE_URL` | URL pooled de Neon con SSL |
| `JWT_SECRET` | Secreto aleatorio de al menos 32 caracteres |
| `CORS_ORIGINS` | Origen HTTPS exacto de Vercel, sin comodines |
| `FRONTEND_BASE_URL` | URL HTTPS de Vercel; se usa en los enlaces de recuperación |
| `EMAIL_PROVIDER` | `brevo` (definida en `render.yaml`) |
| `BREVO_API_KEY` | API key de Brevo |
| `EMAIL_FROM_EMAIL` | Remitente verificado en Brevo |
| `EMAIL_FROM_NAME` | Nombre mostrado como remitente |
| `EMAIL_TIMEOUT_SECONDS` | Timeout HTTP; el Blueprint usa 10 segundos |

### Variable del frontend

| Variable | Configuración |
|---|---|
| `VITE_API_BASE_URL` | URL HTTPS pública de la API de Render; se inyecta en el build de Vercel |

## Verificación y operación

- Render `/health` debe responder `{"status":"ok"}` y la URL del frontend debe cargar por HTTPS.
- La primera petición tras inactividad puede tardar por la suspensión del plan gratuito; vuelve a
  intentar y comprueba los logs del servicio si persiste.
- Confirma en los logs que el runner completó `000`, `004`, `005` y `006`. Si una migración falla,
  el contenedor no inicia; revisa el error antes de reintentar.
- Exporta periódicamente la base fuera del proveedor y antes de cambios de esquema. No consideres
  la copia de la base gratuita como un plan de recuperación garantizado.
- Nunca publiques `DATABASE_URL`, `JWT_SECRET` ni `BREVO_API_KEY`; rota cualquier secreto expuesto.
