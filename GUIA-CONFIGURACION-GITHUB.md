# Guía de Configuración en GitHub — Dash Parking (Semana 1)

Esta guía cierra las partes del checklist de la Semana 1 que requieren la cuenta de GitHub real
del equipo (esto no se puede automatizar desde aquí). Síguela en orden — cada paso depende del
anterior. El repositorio local ya viene con la estructura, el código de Sprint 0 y el historial de
Git (`main` + `develop` + `feature/vehicle-domain-model` ya mergeada) listo para subir.

---

## 1. Crear el repositorio en GitHub

1. Ve a [github.com/new](https://github.com/new)
2. Nombre sugerido: `dash-parking`
3. Visibilidad: la que defina el equipo (privado recomendado mientras es un proyecto académico)
4. **No** marques "Add a README" ni ".gitignore" ni licencia — el repo local ya los trae

## 2. Subir el repositorio local

Desde la carpeta `dash-parking/` que te entregué:

```bash
git remote add origin https://github.com/<tu-organizacion-o-usuario>/dash-parking.git
git push -u origin main
git push -u origin develop
git push origin feature/vehicle-domain-model   # opcional, solo si quieres verla en remoto
```

## 3. Branch protection

**Settings → Branches → Add branch protection rule**, repetir para `main` y `develop`:

- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging (lo activas después de que corra el primer
  workflow — paso 6, ya que GitHub necesita ver el check al menos una vez para poder listarlo)

## 4. Crear el GitHub Project (Board)

1. En el repositorio → pestaña **Projects** → **New project** → plantilla **Board**
2. Crea las columnas: `Backlog`, `Sprint Actual`, `En Progreso`, `En Revisión (PR)`, `Hecho`

## 5. Cargar el backlog como Issues

Usa `docs-proyecto/backlog-historias-usuario.md`: por cada historia (HU-01 a HU-12), crea un
Issue nuevo copiando título, historia, criterios de aceptación y notas técnicas. Asigna:

- **Label**: `feature` (ya sugerido en cada bloque)
- **Milestone**: crea un milestone por sprint (`Sprint 1 — Dominio y persistencia`, ...
  `Sprint 8 — Cierre y avance 90%`) según lo indicado en cada historia
- Agrega el issue al Project, columna `Backlog`

> Con los 12 issues cargados ya superas el mínimo de 5 historias reales priorizadas que pide la
> rúbrica de Desempeño.

## 6. Activar el workflow de CI

El archivo `.github/workflows/ci.yml` ya viene en el repo. En cuanto hagas `git push`, correrá
automáticamente en el primer Pull Request que abras. No necesitas crearlo manualmente.

## 7. Prueba real de bloqueo de CI (obligatoria para la rúbrica)

1. Crea una rama de prueba: `git checkout -b test/lint-failure`
2. Rompe una regla de lint a propósito, por ejemplo en `be/app/main.py` agrega una línea con un
   import sin usar: `import os` sin usarlo en ningún lado
3. `git add . && git commit -m "test(ci): trigger intentional lint failure"` y
   `git push -u origin test/lint-failure`
4. Abre un PR de `test/lint-failure → develop` — confirma que el check `backend` falla en rojo
5. Corrige el error (quita el import), push de nuevo, confirma que el check pasa en verde
6. Cierra el PR **sin mergear** (era solo una prueba) y borra la rama

Esto satisface el ítem de rúbrica: *"Un PR de prueba con un error de lint intencional fue
bloqueado por CI (verificación real, no solo config)"*.

## 8. Verificación de Docker por cada integrante

Cada integrante del equipo corre en su máquina y comparte el resultado en el canal del equipo:

```bash
docker --version
docker compose version
```

## 9. Confirmar el PR real de Sprint 0

El merge de `feature/vehicle-domain-model → develop` ya está hecho localmente (`--no-ff`). Al
hacer `git push -u origin develop` en el paso 2, ese historial —y por tanto el "PR" ya
resuelto— queda reflejado en `develop`. Si tu equipo prefiere que quede como un Pull Request
visible y revisado por un compañero (recomendado para la disciplina de revisión desde ya):

```bash
git checkout main
git checkout -b feature/vehicle-domain-model-pr origin/develop  # opcional
```

o, más simple: antes de hacer el merge local, empuja solo la rama `feature/vehicle-domain-model`,
abre el PR contra `develop` en GitHub, pide revisión a un compañero, y mergea desde la interfaz en
lugar de local. Cualquiera de las dos formas cumple el criterio de rúbrica; la segunda dokumenta
mejor la revisión por pares para sprints futuros.

## 10. Completa el plan de trabajo

Actualiza en `entregable-s01-plan-de-trabajo.md`:
- Sección 5: el enlace real del PR mergeado
- Sección 6: los nombres reales del equipo por rol

---

Con esto los 7 ítems del bloque "Alistamiento" + los 2 del bloque "Arranque" del checklist de la
Semana 1 quedan cerrados.
