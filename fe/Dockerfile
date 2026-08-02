# Dockerfile esqueleto del frontend — Semana 1 (Sprint 0)
# Aún NO es la imagen final: falta el multi-stage build (build -> Nginx estático),
# que se construye en el Sprint 5 (ver docs/docker-guia.md).
FROM node:24-slim

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
