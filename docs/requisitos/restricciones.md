# Restricciones del Proyecto — Dash Parking

<!--
  ¿Qué? Documento que define las restricciones técnicas, organizacionales y de diseño del proyecto.
  ¿Para qué? Establecer los límites y condiciones no negociables bajo las cuales se desarrolla el sistema.
  ¿Impacto? Violar una restricción puede comprometer la calidad, seguridad o coherencia del proyecto.
-->

---

## 1. Restricciones Tecnológicas

### RT-001 — Stack de backend obligatorio
El backend se desarrolla exclusivamente con:
- **Python 3.12+** como lenguaje.
- **FastAPI** como framework web.
- **Pydantic 2.0+** para validación de datos.
- **SQLAlchemy** como ORM (a partir del Sprint 1 — ver `docs/estandar-codigo-template.md` del bootcamp).

No se permite el uso de otros frameworks web (Django, Flask, etc.) ni ORMs alternativos.

### RT-002 — Stack de frontend obligatorio
El frontend se desarrolla exclusivamente con:
- **React 18+** como biblioteca de UI.
- **TypeScript 5.0+** como lenguaje (modo estricto).
- **Vite 5+** como bundler y servidor de desarrollo.

No se permite el uso de otros frameworks (Angular, Vue, Svelte, etc.) salvo decisión explícita
del equipo documentada en este archivo.

### RT-003 — Base de datos obligatoria
La base de datos es **PostgreSQL 16+**, ejecutada en contenedor Docker durante el desarrollo. No
se permiten bases de datos alternativas (MySQL, SQLite en producción, MongoDB, etc.).

### RT-004 — Método de autenticación
La autenticación se implementa mediante **JWT (JSON Web Tokens)** con enfoque stateless (ver
RF-012). No se permiten sesiones basadas en cookies de servidor ni proveedores de identidad
externos, salvo necesidad futura documentada.

### RT-005 — Algoritmo de hashing
Las contraseñas se hashean exclusivamente con **bcrypt**. No se permiten otros algoritmos (MD5,
SHA-256 sin salt, etc.).

---

## 2. Restricciones de Herramientas y Entorno

### RH-001 — Gestor de paquetes Python
El entorno de Python se gestiona con **venv** (módulo estándar) + **pip**.

### RH-002 — Gestor de paquetes Node.js
Las dependencias del frontend se gestionan con **npm**.

### RH-003 — Linter y formatter Python
Se usa exclusivamente **ruff** como linter y formatter. No se permiten linters alternativos
(pylint, flake8) ni formatters (black, autopep8).

### RH-004 — Linter y formatter Frontend
Se usan **ESLint** para linting y **Prettier** (o el formateo por defecto del proyecto) para
formateo. No se permiten herramientas alternativas.

### RH-005 — Contenedores
**Docker + Docker Compose** son obligatorios desde el diseño del proyecto (requisito del
bootcamp), sin alternativa.

---

## 3. Restricciones de Idioma

### RI-001 — Código en inglés
Todo el código fuente se escribe en inglés: variables, funciones, clases, métodos, constantes,
nombres de archivos y carpetas de código, endpoints, tablas y columnas de base de datos, nombres
de ramas.

### RI-002 — Documentación en español
Toda la documentación y comentarios se escriben en español: comentarios en el código,
docstrings, archivos `.md`, descripciones en configuración.

---

## 4. Restricciones Organizacionales

### RO-001 — Proyecto académico
Este es un proyecto académico del bootcamp de Asesoría Desarrollo — Codificación. Cada
funcionalidad debe mantenerse trazable al informe de diseño original (ver `docs/requisitos/`);
no se agrega alcance no sustentado en ese informe sin dejarlo explícito como pendiente de
aclarar.

### RO-002 — Conventional Commits
Todos los mensajes de commit siguen el formato **Conventional Commits** (`feat:`, `fix:`,
`docs:`, `test:`, `chore:`, etc.), ver `docs/git-workflow.md` del bootcamp.

### RO-003 — Versionamiento de API
Todos los endpoints están bajo el prefijo `/api/v1/`. Cambios incompatibles requerirían una
nueva versión (`/api/v2/`).

### RO-004 — Flujo de ramas
`feature/<slug> → develop → main`, con branch protection y CI obligatorio en cada Pull Request
(ver `GUIA-CONFIGURACION-GITHUB.md`).

### RO-005 — Backlog en GitHub Projects (Kanban)
El backlog del proyecto se gestiona en un GitHub Project con vista **Kanban**, no en
herramientas externas (Trello, Jira, etc.), para mantener todo el flujo de trabajo dentro de
GitHub.

---

## 5. Restricciones de Seguridad

### RS-001 — Credenciales en variables de entorno
Toda información sensible (claves secretas, credenciales de BD) se almacena en archivos `.env`
no versionados en git. Nunca se hardcodean valores sensibles en el código.

### RS-002 — Archivo `.env.example` obligatorio
Siempre debe existir un `.env.example` actualizado con las variables necesarias y valores de
ejemplo no sensibles (ya presente en `be/` y `fe/`).

### RS-003 — No exponer contraseñas
Las contraseñas (hasheadas o en texto plano) nunca aparecen en respuestas de la API, logs del
servidor ni mensajes de error al cliente.

---

## 6. Pendientes explícitos (no inventados)

Estos puntos requieren definición del propietario del parqueadero o del instructor antes del
Sprint correspondiente — se dejan aquí para no inventar una respuesta:

- **RN-010 (RF-005)**: unidad exacta de cobro (por hora completa, por fracción, por minuto).
- Horario formal de operación del parqueadero (RNF-002.3 lo referencia, pero el informe de
  diseño no especifica un horario concreto).
- Estructura societaria/roles adicionales más allá de administrador y operario, si los hubiera.
