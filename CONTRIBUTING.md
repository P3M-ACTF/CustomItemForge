# Guía de contribución

Gracias por contribuir. Este repositorio usa GitHub Flow, Conventional Commits y validaciones automáticas para mantener `main` estable y revisable.

El uso de Cursor es opcional. Las mismas normas se aplican a cambios escritos manualmente o mediante cualquier otro agente.

## Antes de empezar

1. Lee `README.md` y la documentación relacionada con el área que modificarás.
2. Busca un Issue o Pull Request existente para evitar trabajo duplicado.
3. Para cambios amplios o incompatibles, acuerda primero el diseño mediante un Issue.
4. Instala las herramientas:

   ```bash
   python -m pip install -r tools/workflow/requirements.txt
   pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push
   ```

## Flujo de trabajo

1. Actualiza `main` sin crear un merge local:

   ```bash
   git switch main
   git pull --ff-only origin main
   ```

2. Crea una rama:

   ```bash
   git switch -c feat/descripcion-corta
   ```

3. Realiza un cambio pequeño y centrado.
4. Añade o actualiza pruebas y documentación cuando corresponda.
5. Ejecuta las comprobaciones del proyecto y los hooks:

   ```bash
   pre-commit run --all-files
   ```

6. Prepara únicamente archivos relacionados y revisa el diff:

   ```bash
   git add ruta/al/archivo
   git diff --cached
   ```

7. Crea un commit mediante Commitizen o escribe un mensaje válido:

   ```bash
   cz commit
   ```

8. Sube la rama y abre un Pull Request hacia `main`.
9. Corrige los checks y comentarios de revisión sin desactivar protecciones.
10. Integra mediante Squash Merge cuando se cumplan las reglas del repositorio.

## Nombres de rama

Las ramas humanas usan `tipo/descripcion-corta`, en minúsculas y kebab-case.

Tipos admitidos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`, `style`, `hotfix` y `revert`.

Ejemplos válidos:

```text
feat/add-user-login
fix/handle-empty-token
docs/update-installation
```

Ejemplos inválidos:

```text
feature/AddLogin
mis-cambios
fix_error
```

## Commits

Formato:

```text
tipo(ámbito-opcional): descripción en imperativo
```

Cada commit debe:

- representar un propósito único;
- describir el cambio preparado;
- evitar mensajes genéricos como `cambios`, `update` o `WIP`;
- identificar cambios incompatibles mediante `!` o un pie `BREAKING CHANGE:`.

## Pull Requests

El título debe ser un Conventional Commit válido. La descripción debe incluir:

- qué cambia y por qué;
- cómo se ha validado;
- riesgos conocidos y estrategia de reversión;
- Issues relacionados mediante `Closes #123` cuando corresponda;
- evidencia visual con texto alternativo para cambios de interfaz.

Mantén el Pull Request dentro de un alcance revisable. Si aparecen cambios no relacionados, sepáralos.

## Calidad y seguridad

- No confirmes secretos, credenciales, datos personales ni archivos `.env`.
- No desactives hooks con `--no-verify`.
- No hagas force-push sobre ramas compartidas sin coordinación explícita.
- No introduzcas dependencias sin explicar su necesidad y revisar su procedencia.
- Si detectas una vulnerabilidad, usa el canal privado de seguridad del proyecto en lugar de un Issue público.

## Accesibilidad documental

- Usa encabezados en orden y enlaces con texto significativo.
- Añade texto alternativo a imágenes y capturas.
- Incluye una explicación textual para diagramas que contengan información necesaria.
- No transmitas estados únicamente mediante colores o iconos.
