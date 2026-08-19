# Guía de Colaboración en Equipo — Dash Parking

Para cualquier integrante del equipo que va a trabajar en el proyecto desde una PC que no tiene
nada instalado todavía. Sigue los pasos en orden — cada uno depende del anterior.

---

## 1. Instalar las herramientas necesarias

Solo necesitas 3 cosas instaladas en tu máquina (todo lo demás — Python, Node, PostgreSQL — corre
dentro de Docker, no necesitas instalarlo aparte):

### Git
- **Windows**: descarga desde [git-scm.com](https://git-scm.com/downloads), instala con las
  opciones por defecto
- **Mac**: abre la Terminal y escribe `git --version` — si no lo tienes, te ofrece instalarlo
- **Linux**: `sudo apt install git` (Ubuntu/Debian) o el gestor de paquetes de tu distro

Verifica: abre una terminal (o Git Bash en Windows) y corre:
```bash
git --version
```

### Docker Desktop
- Descarga desde [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
- Instala y ábrelo — debe quedar corriendo en segundo plano (ícono de ballena en la barra de
  tareas/menú)
- Windows: puede pedirte activar WSL2 durante la instalación — acepta, es normal

Verifica:
```bash
docker --version
docker compose version
```

### Un editor de código
Cualquiera sirve, pero si no tienes uno, [Visual Studio Code](https://code.visualstudio.com/) es
el más usado por el equipo — instálalo con las opciones por defecto.

### Cuenta de GitHub
Si no tienes una, créala en [github.com](https://github.com). Pide al administrador del
repositorio que te agregue como colaborador del repo `dash-parking` (o que te dé el link si es
público).

---

## 2. Configurar Git con tu identidad (solo la primera vez)

Abre una terminal y corre (reemplaza con tus datos reales):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@example.com"
```

Esto hace que tus commits queden identificados como tuyos, no como "Dash Parking Team" (el
nombre genérico que se usó al preparar este entregable).

---

## 3. Clonar el repositorio

```bash
git clone https://github.com/<organizacion-o-usuario>/dash-parking.git
cd dash-parking
```

Si es la primera vez que usas GitHub desde esa máquina, te pedirá iniciar sesión — sigue las
instrucciones en pantalla (usualmente abre el navegador para autenticarte).

---

## 4. Levantar el proyecto

Sigue `GUIA-EJECUCION-LOCAL.md` — en resumen:

```bash
cp be/.env.example be/.env
cp fe/.env.example fe/.env
docker compose up --build
```

Abre http://localhost:5173 y confirma que ves la app funcionando.

---

## 5. Flujo de trabajo para hacer un cambio (día a día)

Este proyecto usa **Conventional Commits** y el flujo `feature/<slug> → develop → main`
(ver `docs/git-workflow.md`... — nota: esa guía vive en el repo del bootcamp, no en este; aquí
el resumen práctico):

### Paso 1 — Actualiza tu copia local antes de empezar
```bash
git checkout develop
git pull origin develop
```

### Paso 2 — Crea una rama para tu tarea
Usa el nombre de la HU o una descripción corta, en inglés y en minúsculas:
```bash
git checkout -b feature/reservation-cancel-confirmation
```

### Paso 3 — Haz tus cambios y pruébalos localmente
Con `docker compose up` corriendo, los cambios en `be/app/` y `fe/src/` se recargan solos
(hot-reload). Prueba en el navegador que funciona antes de seguir.

Si tocaste el backend, corre los tests:
```bash
cd be
pytest
```

### Paso 4 — Confirma tus cambios (commit)
```bash
git add .
git commit -m "feat(reservations): add confirmation dialog before cancelling"
```

Prefijos que usamos: `feat:` (funcionalidad nueva), `fix:` (corrección de bug), `docs:`
(documentación), `test:` (pruebas), `chore:` (tareas de mantenimiento).

### Paso 5 — Sube tu rama a GitHub
```bash
git push -u origin feature/reservation-cancel-confirmation
```

### Paso 6 — Abre un Pull Request
1. Ve al repositorio en GitHub — te va a aparecer un aviso para crear el PR desde tu rama recién
   subida, o entra a **Pull requests → New pull request**
2. Base: `develop` ← Compare: tu rama
3. Escribe un título claro y, si aplica, referencia la HU (ej. "Closes HU-013")
4. Pide revisión a un compañero
5. Espera a que el check de CI (`ci.yml`) pase en verde — corre lint y tests automáticamente
6. Cuando esté aprobado, mergea con **Squash and merge** o **Merge commit** (lo que el equipo
   prefiera, pero sé consistente)

### Paso 7 — Actualiza el tablero Kanban
Mueve el Issue correspondiente a la columna que refleje su nuevo estado (si usan Automated
Kanban, esto puede pasar solo al abrir/cerrar el PR — ver `GUIA-CONFIGURACION-GITHUB.md`).

### Paso 8 — Borra tu rama local (opcional, mantiene todo limpio)
```bash
git checkout develop
git pull origin develop
git branch -d feature/reservation-cancel-confirmation
```

---

## 6. Reglas rápidas para evitar conflictos

- **Nunca** trabajes directo sobre `main` o `develop` — siempre en una rama `feature/*`
- Antes de empezar una tarea nueva, actualiza `develop` (Paso 1) — evita que tu rama nazca
  desactualizada
- Si tu PR tarda varios días, actualiza tu rama con los cambios de `develop` a mitad de camino:
  ```bash
  git checkout feature/tu-rama
  git merge develop
  ```
- Si `ci.yml` falla en tu PR, no lo ignores — revisa el log del check en GitHub (pestaña
  **Checks** del PR), corrige y vuelve a subir

---

## 7. ¿Dónde está cada cosa?

| Necesito... | Voy a... |
|---|---|
| Ver qué falta por hacer | El tablero Kanban del GitHub Project |
| Entender una funcionalidad | `docs/requisitos/HUs/` (busca el número de la HU) |
| Ver el contrato exacto de un endpoint | `docs/requisitos/RFs/` (mismo número que la HU) |
| Saber qué convención de nombres usar | `CODING_STANDARDS.md` |
| Levantar el proyecto | `GUIA-EJECUCION-LOCAL.md` |
| Configurar GitHub (repo/Project/CI) | `GUIA-CONFIGURACION-GITHUB.md` |
| Ver el plan de sprints completo | `entregable-s01-plan-de-trabajo.md` |

Si algo no está claro después de leer esto, pregunta en el canal del equipo antes de adivinar —
es más rápido que deshacer un PR mal encaminado.
