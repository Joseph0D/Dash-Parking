# Imagen de producción del backend. docker-compose.yml la reutiliza con un comando de desarrollo.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MIGRATIONS_DIR=/db/migrations

WORKDIR /app

# Capa de dependencias, separada del código para aprovechar la cache de Docker.
COPY be/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# La imagen necesita las migraciones porque se aplican antes de iniciar la API.
COPY be/app ./app
COPY db/migrations /db/migrations

RUN useradd --system --uid 10001 --create-home app
USER 10001

EXPOSE 8000

CMD ["sh", "-c", "python -m app.scripts.migrate_production && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
