# Dockerfile del frontend — Dash Parking
# Imagen funcional de desarrollo: sirve con el servidor de Vite en modo dev, con hot-reload
# (ver docker-compose.yml, que monta ./fe/src como volumen).
# El build de producción (multi-stage -> Nginx estático) queda para antes de un despliegue real
# (ver docs/docker-guia.md del bootcamp) — no es necesario para desarrollo en equipo.
FROM node:24-slim

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
