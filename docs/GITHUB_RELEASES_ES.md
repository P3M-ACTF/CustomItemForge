# GitHub Releases — guía fácil (CustomItemForge)

[English](GITHUB_RELEASES.md) · [Español](GITHUB_RELEASES_ES.md)

Esta guía es para **ti** (quien publica). Los usuarios solo descargan el zip.

## Qué hace la Action

Workflow: **Release CustomItemForge**  
Archivo: `.github/workflows/release-custom-item-forge.yml`

1. Compila el bundle (`CustomItemForge.pyz`, launchers, `RELEASE.txt`)
2. Crea `CustomItemForge-<versión>.zip`
3. Lo sube a la release de GitHub (sustituye el zip anterior si ya existía)

Tarda unos **~5 minutos**. Es normal.

---

## Cómo publicar una release nueva

1. Entra en el repo: https://github.com/P3M-ACTF/VRoidTools
2. Pestaña **Releases** → **Draft a new release**
3. Elige o crea un **tag** (ej. `v0.1.0-preview`)
4. Título y notas → botón verde **Publish release**
5. Eso **dispara** la Action automáticamente

No hace falta subir el zip a mano.

---

## Ver el progreso (trigger en marcha)

1. Pestaña **Actions**
2. A la izquierda: **Release CustomItemForge**
3. Clic en la ejecución más reciente (suele decir el tag)
4. Clic en el job **bundle** → ves cada paso en vivo

También desde la página de la Release: mira el check / enlace a Actions.

Cuando termine, en la Release → **Assets** verás el `.zip`.

---

## Relanzar / regenerar el zip de una release que ya existe

### Opción A — Re-run (misma ejecución)

Si la Action ya corrió para esa release:

1. **Actions** → **Release CustomItemForge** → abre esa ejecución
2. Arriba a la derecha: **Re-run all jobs**
3. Espera ~5 min → el zip se sustituye (`--clobber`)

### Opción B — Botón manual (recomendado)

Sirve para regenerar el zip de **cualquier tag** sin crear una release nueva:

1. **Actions** → **Release CustomItemForge**
2. Botón **Run workflow** (derecha)
3. En **tag**, escribe el tag exacto (ej. `v0.1.0-preview`)
4. **Run workflow**
5. Espera ~5 min → el zip de esa release se actualiza

El tag debe existir ya como Release publicada. Si te equivocas de nombre, fallará en el paso de upload.

---

## Checklist rápido

| Quiero… | Hago… |
|---|---|
| Primera vez / versión nueva | Releases → Publish release |
| Ver si va bien | Actions → Release CustomItemForge |
| Falló o quiero zip nuevo del mismo tag | Re-run **o** Run workflow con el tag |
| Probar el zip en local | `python scripts/build_release.py --zip --tag vX.Y.Z` |

---

## Windows: GUI sin consola

- Abre la app con **`CustomItemForge_Win.pyw`** (doble clic).
- **No** abras `CustomItemForge.pyz` para la GUI: eso abre una ventana de consola.
- El `.pyz` es solo para la **línea de comandos** (`python CustomItemForge.pyz inspect …`).

---

## Si algo falla

1. Abre la ejecución en **Actions** y mira el paso en rojo.
2. Errores típicos:
   - Tag mal escrito en Run workflow
   - La Release no existe todavía (solo el tag suelto no basta para `gh release upload`)
   - Python / dependencias en CI (raro; el log lo dice)
3. Corrige y vuelve a **Re-run** o **Run workflow**.

Más detalle técnico del build local: [RELEASE.md](RELEASE.md).
