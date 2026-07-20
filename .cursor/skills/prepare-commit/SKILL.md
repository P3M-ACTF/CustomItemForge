---
name: prepare-commit
description: Usa esta skill cuando el usuario pida preparar, crear, validar o subir un commit, o preparar un Pull Request con los cambios actuales.
---

# Preparar un commit seguro

## Límites

- No hagas commit en `main`.
- No incluyas secretos, archivos de entorno, credenciales ni cambios no relacionados.
- No uses `--no-verify`, `--amend`, rebase o force-push sin autorización explícita.
- Un pedido de commit no autoriza por sí solo el push ni la apertura de un Pull Request.

## Procedimiento

1. Ejecuta `git status --short --branch` y confirma que la rama cumple la política.
2. Revisa `git diff` y clasifica los cambios por propósito.
3. Identifica las comprobaciones exigidas por `CONTRIBUTING.md` y la configuración del proyecto.
4. Ejecuta las comprobaciones aplicables. Si alguna falla, detén el commit y explica el fallo.
5. Prepara archivos individualmente con `git add <ruta>`.
6. Revisa `git diff --cached --stat` y `git diff --cached`.
7. Redacta un mensaje Conventional Commit que describa el cambio preparado, no la intención original.
8. Crea el commit y deja que los hooks se ejecuten.
9. Comprueba el resultado con `git status --short --branch` y comunica el hash y el mensaje.
10. Solo si se pidió explícitamente, realiza el push y prepara el Pull Request.

## Criterios de finalización

- La rama no es una rama protegida.
- El contenido preparado coincide con el alcance comunicado.
- Las comprobaciones ejecutadas y omitidas están identificadas.
- El mensaje describe un cambio atómico y cumple Conventional Commits.
- No se ha eludido ninguna protección.
