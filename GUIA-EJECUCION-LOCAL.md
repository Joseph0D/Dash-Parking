# Guía de Ejecución Local — Dash Parking

Levanta el sistema completo (base de datos, backend y frontend) en tu máquina. Requiere tener
**Docker Desktop** instalado y corriendo (ver `GUIA-COLABORACION-EQUIPO.md` si no lo tienes).

---

## 1. Configurar las variables de entorno

Solo la primera vez, o si `.env.example` cambió:

```bash
cd dash-parking
cp be/.env.example be/.env
cp fe/.env.example fe/.env
```

No necesitas editar nada para desarrollo local — los valores por defecto ya apuntan a los
servicios del `docker-compose.yml`. Si vas a exponer el backend a internet, cambia `JWT_SECRET`
en `be/.env` por un valor propio (nunca subas ese archivo a git — ya está en `.gitignore`).

## 2. Levantar todo con un solo comando

```bash
docker compose up --build
```

Esto hace, en orden:
1. Descarga y arranca PostgreSQL 16, espera a que esté saludable (`healthcheck`)
2. Construye la imagen del backend, corre el **seed** (crea admin, tarifas y espacios de
   ejemplo — ver `be/app/scripts/seed.py`) y levanta FastAPI con recarga automática
3. Construye la imagen del frontend y levanta Vite en modo desarrollo

La primera vez tarda unos minutos (descarga de imágenes). Las siguientes veces es mucho más
rápido porque Docker reutiliza la caché.

## 3. Verificar que todo está arriba

| Servicio | URL | Qué deberías ver |
|---|---|---|
| Frontend | http://localhost:5173 | La landing page de Dash Parking |
| Backend (docs interactivos) | http://localhost:8000/docs | Swagger UI con todos los endpoints |
| Backend (health) | http://localhost:8000/health | `{"status": "ok"}` |
| PostgreSQL | `localhost:5432` | (no tiene interfaz web; usa un cliente como DBeaver/TablePlus si quieres inspeccionarlo) |

## 4. Iniciar sesión con el usuario de prueba

El seed crea un administrador automáticamente:

- **Correo**: `admin@dashparking.dev`
- **Contraseña**: `Admin123!`

Úsalo para entrar a `/admin` y probar tarifas, entrada/salida y el dashboard. Para probar el
flujo de cliente (reservar, pagar), crea una cuenta nueva desde `/registro` — el autoregistro
siempre asigna rol `client` (RF-016).

## 5. Flujo de prueba sugerido (de punta a punta)

1. Entra con el admin a `/admin` → pestaña **Tarifas** → confirma que ya hay valores (el seed
   los crea, pero puedes cambiarlos)
2. Crea una cuenta cliente en `/registro`, entra a `/cuenta` → **Mis vehículos** → registra una
   placa
3. Vuelve a `/admin` (en otra pestaña del navegador, o cierra sesión y entra de nuevo con el
   admin) → **Entrada/Salida** → registra el ingreso de esa placa
4. Como cliente, entra a `/cuenta` → **Sesión activa** → verás el cronómetro corriendo y el
   valor estimado subiendo → prueba **Pagar virtual** o **Generar QR**
5. Si generaste QR: como admin, pestaña **Validar QR** → pega el token → confirma el cobro
6. Como admin, pestaña **Dashboard** → verás la ganancia reflejada, filtra por tipo de vehículo
   o por fecha

## 6. Apagar todo

```bash
docker compose down
```

Los datos de PostgreSQL persisten entre reinicios (quedan en un volumen de Docker). Si quieres
empezar desde cero (borrar toda la base de datos):

```bash
docker compose down -v
```

## 7. Ver logs de un servicio específico

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

## 8. Ejecutar los tests del backend sin levantar todo el compose

Los tests usan SQLite en memoria (no dependen de PostgreSQL corriendo), así que puedes correrlos
directo:

```bash
cd be
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

## 9. Problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `port is already allocated` | Ya tienes algo corriendo en el puerto 5432/8000/5173 | Cierra ese proceso, o cambia el puerto host en `docker-compose.yml` (ej. `"5433:5432"`) |
| El frontend no conecta con el backend | `VITE_API_BASE_URL` no coincide | Verifica `fe/.env`, debe ser `http://localhost:8000` |
| `NoActiveRateError` al registrar ingreso | El seed no corrió o falló | Revisa `docker compose logs backend`, confirma que veas las líneas `[seed] ...` |
| Cambios en el código no se reflejan | El volumen no está montado bien | Confirma que `docker-compose.yml` monte `./be/app` y `./fe/src` (ya viene así) |
