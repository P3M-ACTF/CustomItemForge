# Configuración recomendada de GitHub

Los archivos del repositorio no pueden activar por sí solos todas las protecciones. Esta guía cubre la configuración manual.

## 1. Método de merge

En `Settings > General > Pull Requests`:

- habilita **Allow squash merging**;
- deshabilita merge commits y rebase merge si quieres un historial uniforme;
- usa como mensaje del squash el título del Pull Request;
- habilita la eliminación automática de ramas integradas.

El título del Pull Request se valida como Conventional Commit porque será el mensaje visible en `main`.

## 2. Ruleset para `main`

En `Settings > Rules > Rulesets`, crea un ruleset dirigido a la rama predeterminada.

Configuración recomendada:

- restringir eliminaciones;
- bloquear force-push;
- exigir Pull Request antes de integrar;
- exigir que las conversaciones estén resueltas;
- exigir el check **Quality checks**;
- exigir historial lineal;
- impedir bypass salvo para administradores de emergencia claramente definidos.

Para equipos, exige al menos una aprobación. En repositorios personales puede omitirse para no bloquear al único mantenedor.

## 3. Primera activación del check

GitHub suele necesitar que un check se ejecute al menos una vez antes de poder seleccionarlo en un Ruleset.

1. Integra inicialmente el workflow o ejecútalo mediante `workflow_dispatch`.
2. Confirma que aparece el job **Quality checks**.
3. Añádelo como required status check.
4. Abre un Pull Request de prueba y verifica que el merge queda bloqueado si el check falla.

## 4. Actions

El workflow aplica permisos mínimos:

```yaml
permissions:
  contents: read
```

Las Actions externas están fijadas mediante SHA completo. Los comentarios conservan la versión legible. Dependabot puede proponer actualizaciones, que deben revisarse antes de integrar.

Para GitHub Enterprise Server, verifica que la versión del runner soporte las versiones actuales de `actions/checkout` y `actions/setup-python`.

## 5. Dependabot

`.github/dependabot.yml` comprueba:

- GitHub Actions semanalmente;
- herramientas Python de `tools/workflow/` mensualmente.

Crea las etiquetas `dependencies`, `ci` y `python`, o adapta la configuración si no quieres que Dependabot las aplique.

## 6. Propiedad y seguridad opcionales

En proyectos de equipo, considera añadir:

- `.github/CODEOWNERS` para áreas sensibles;
- `SECURITY.md` con un canal privado de reporte;
- firma de commits o reglas de metadatos cuando el riesgo lo justifique;
- entornos protegidos para despliegues.

Estas medidas no se activan en la plantilla porque requieren identidades, ramas y modelos de riesgo específicos.

## Verificación final

- [ ] El push directo a `main` está bloqueado.
- [ ] Un PR con título inválido falla.
- [ ] Una rama con nombre inválido falla.
- [ ] Un archivo con clave privada de prueba es rechazado localmente.
- [ ] El check **Quality checks** es obligatorio.
- [ ] El método de integración es Squash Merge.
- [ ] Las excepciones de bypass están documentadas.

## CustomItemForge � checks requeridos

Adem�s de **Quality checks** (incluye pytest en el mismo job), configura el Ruleset de main como en la secci�n 2.

Este repositorio publica releases con **Release Please**; no migra tags/releases hist�ricas del monorepo VRoidTools.
