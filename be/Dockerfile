# Dockerfile del backend — Dash Parking
# Imagen funcional de desarrollo: instala dependencias, corre el seed y levanta uvicorn con
# --reload (ver docker-compose.yml, que monta ./be/app como volumen para hot-reload).
# Optimización a multi-stage build + usuario no-root queda para antes de un despliegue real
# (ver docs/docker-guia.md del bootcamp) — no es necesaria para desarrollo en equipo.
FROM python:3.12-slim

WORKDIR /app

# Capa de dependencias, separada del código para aprovechar la cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Capa de código de la aplicación
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
