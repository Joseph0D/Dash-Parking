# Dockerfile esqueleto del backend — Semana 1 (Sprint 0)
# Aún NO es la imagen final: no tiene multi-stage build ni usuario no-root.
# Esas optimizaciones se agregan en el Sprint 7 (ver docs/docker-guia.md).
FROM python:3.12-slim

WORKDIR /app

# Capa de dependencias, separada del código para aprovechar la cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Capa de código de la aplicación
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
