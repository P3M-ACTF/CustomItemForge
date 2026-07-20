# Integración con Cursor

Esta plantilla usa tres mecanismos distintos. No son intercambiables y conviene mantener sus responsabilidades separadas.

| Mecanismo | Activación | Uso adecuado |
| --- | --- | --- |
| Project Rule | Automática por alcance | Restricciones y convenciones persistentes |
| Agent Skill | Cursor la selecciona por la tarea | Procedimientos especializados y verificables |
| Hook de Git | Git lo ejecuta | Validación determinista antes de avanzar |

## Project Rules

Las reglas viven en `.cursor/rules/` y se versionan con el repositorio.

### `00-project.mdc`

Se aplica siempre. Contiene límites generales: cambios pequeños, protección de secretos, verificación honesta y respeto por el trabajo existente.

### `10-git-workflow.mdc`

Se aplica siempre. Indica a Cursor cómo consultar el estado, elegir rama, preparar archivos, redactar commits y distinguir commit, push y Pull Request.

### `20-python.mdc`

Solo se activa en contexto Python. Así no consume contexto ni impone herramientas cuando se trabaja en otro stack.

Para otro lenguaje, crea una regla equivalente con `alwaysApply: false` y `globs` limitados. Ejemplo conceptual:

```md
---
description: Convenciones TypeScript del proyecto
globs:
  - "**/*.ts"
  - "**/*.tsx"
alwaysApply: false
---
```

## Agent Skill para commits

`.cursor/skills/prepare-commit/SKILL.md` describe un procedimiento completo para peticiones como:

- `Prepara un commit con estos cambios.`
- `Haz un commit de la corrección del login.`
- `Valida los cambios antes de subirlos.`
- `Prepara el Pull Request.`

La descripción del frontmatter ayuda a Cursor a decidir cuándo cargarla. El cuerpo define límites, pasos y criterios de finalización.

## Qué puede hacer Cursor

| Petición | Autorización resultante |
| --- | --- |
| `Revisa mis cambios` | Inspeccionar y ejecutar comprobaciones no destructivas |
| `Prepara un commit` | Revisar, validar, preparar archivos relacionados y crear el commit |
| `Sube los cambios` | Hacer push de la rama actual tras validarla |
| `Abre un PR` | Preparar y abrir el Pull Request si la integración está disponible |

Una petición de commit no autoriza automáticamente push, force-push, rebase o apertura de PR.

## Evitar reglas frágiles

- Escribe instrucciones observables: `ejecuta git diff --cached` es mejor que `ten cuidado`.
- Mantén una sola fuente humana de verdad en `CONTRIBUTING.md`.
- Reserva las Rules para invariantes y la Skill para el procedimiento detallado.
- No pegues manuales completos en reglas siempre activas.
- Define qué hacer cuando una comprobación falla.
- Revisa las reglas cuando cambien las herramientas o la arquitectura.

## Prueba manual de la integración

En una rama de prueba, solicita a Cursor:

```text
Prepara un commit con los cambios actuales, pero no hagas push.
```

Comprueba que:

1. consulta la rama y el estado;
2. se niega si está en `main`;
3. revisa el diff antes de preparar archivos;
4. ejecuta las comprobaciones aplicables;
5. prepara solo archivos relacionados;
6. muestra o revisa el diff preparado;
7. usa Conventional Commits;
8. no hace push.

Las respuestas del modelo pueden variar. Los hooks y GitHub son las capas que convierten las normas importantes en controles deterministas.
