# Resolución de problemas

## `pre-commit: command not found`

Instala las herramientas y confirma la versión:

```bash
python -m pip install -r tools/workflow/requirements.txt
pre-commit --version
```

## Los hooks no se ejecutan al hacer commit

Cada clonación necesita instalar los hooks:

```bash
pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push
```

Comprueba que existen en `.git/hooks/`. No copies manualmente esos archivos entre repositorios.

## Commitizen rechaza el mensaje

Usa el asistente interactivo:

```bash
cz commit
```

O valida un ejemplo sin crear un commit:

```bash
cz check --message "fix(api): rechazar identificadores vacíos"
```

## La rama es rechazada

Consulta el nombre actual:

```bash
git branch --show-current
```

Debe usar `tipo/descripcion-corta`, por ejemplo `feat/add-login`. Para renombrarla antes del push:

```bash
git branch -m feat/add-login
```

Si la rama ya se compartió, coordina el cambio antes de modificar el remoto.

## Estoy en `main` con cambios sin confirmar

No descartes los cambios. Crea una rama desde el estado actual:

```bash
git switch -c fix/descripcion-corta
```

Después revisa el diff y continúa normalmente.

## `pre-commit` modifica archivos

Algunos hooks corrigen espacios, finales de archivo o saltos de línea.

1. Revisa `git diff`.
2. Ejecuta de nuevo `pre-commit run --all-files`.
3. Prepara los archivos corregidos.

No uses `--no-verify`; el segundo pase confirma que el resultado ya es estable.

## El check funciona localmente pero falla en GitHub

Compara:

- versión de Python;
- archivos sin seguimiento que existan solo localmente;
- variables de entorno;
- mayúsculas y minúsculas en rutas;
- saltos de línea;
- comandos exactos mostrados en el log del job.

Reproduce primero la parte genérica:

```bash
python -m unittest discover -s tools/workflow/tests -v
SKIP=branch-policy pre-commit run --all-files --show-diff-on-failure
```

En PowerShell, define temporalmente la variable con:

```powershell
$env:SKIP = "branch-policy"
pre-commit run --all-files --show-diff-on-failure
Remove-Item Env:SKIP
```

## GitHub no permite seleccionar `Quality checks`

Ejecuta primero `Quality gate` desde `Actions` mediante `workflow_dispatch`. GitHub solo ofrece como obligatorios checks que ya conoce.

## Cursor no aplica una regla

1. Confirma que el archivo está en `.cursor/rules/` y termina en `.mdc`.
2. Revisa el frontmatter YAML.
3. Comprueba `alwaysApply` y los `globs`.
4. Inicia una conversación nueva si el contexto se creó antes de añadir la regla.
5. Menciona explícitamente la regla para diagnosticar, pero corrige su activación en lugar de depender de ese recordatorio.

## Cursor intenta hacer push sin permiso

La regla y la Skill distinguen commit de push. Si ocurre:

1. cancela la operación;
2. comprueba que `10-git-workflow.mdc` está activa;
3. revisa si otra regla contradice la política;
4. conserva el control remoto en GitHub, que es la barrera efectiva.
