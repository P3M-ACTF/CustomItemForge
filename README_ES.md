# CustomItemForge

Herramientas para inspeccionar y transformar archivos `.vroidcustomitem` **for VRoid Studio**.  
Este proyecto es independiente de la marca VRoid; la compatibilidad se describe como *for VRoid*.

Parte del índice [VRoidTools](https://github.com/P3M-ACTF/VRoidTools).

[English](README.md) · [Español](README_ES.md)

## Funcionalidades (v0.1.1-alpha.0)

- **Inspeccionar** con tres secciones: VRoid / VRoidCustomItem / Archivo
- **Validar**, **clonar**, **comparar**, **probe**, **compatibilidad**
- **GUI unificada** (Tkinter) — inglés por defecto, español disponible
- **Motores por familia** — cabello calibrado (Studio 2.14.0); ropa/accesorio con recategorizar; merge de ropa/accesorio espera muestras
- **CLI**: `cif` / `custom-item-forge`

## Descarga (usuarios finales)

1. Descarga el `.zip` de la [última release](https://github.com/P3M-ACTF/CustomItemForge/releases/latest) (`CustomItemForge-*.zip`).
2. Descomprímelo donde quieras.
3. Sigue las indicaciones de `RELEASE.txt` dentro del zip.

| Artefacto | Uso |
|---|---|
| `CustomItemForge_Win.pyw` | GUI en Windows — doble clic, sin consola |
| `CustomItemForge.sh` | GUI en macOS / Linux |
| `CustomItemForge.pyz` | CLI, o GUI si se ejecuta sin argumentos |

Requiere **Python 3.12+ con Tkinter**. El build de release incluye Pillow para miniaturas.

Cada GitHub Release publicada genera y adjunta este zip automáticamente.
Quien publica: ver [docs/GITHUB_RELEASES_ES.md](docs/GITHUB_RELEASES_ES.md) (guía fácil).

En Windows, abre la GUI con **`CustomItemForge_Win.pyw`** (no el `.pyz` — eso abre una consola).

## Inicio rápido (desarrolladores)

```powershell
git clone https://github.com/P3M-ACTF/CustomItemForge.git
cd CustomItemForge
python -m pip install -e ".[dev]"
custom-item-forge inspect ruta\al\item.vroidcustomitem
custom-item-forge gui
pytest
```

Durante el desarrollo puedes hacer doble clic en `scripts/CustomItemForge.pyw` (ejecuta desde el código fuente, no el bundle de release).

### Generar el bundle de release en local

```powershell
python scripts/build_release.py
# o: .\scripts\build_release.ps1
```

Consulta [docs/RELEASE.md](docs/RELEASE.md).

## Muestras de calibración

Cabello calibrado con fixtures en `tests/fixtures/real/hair/` (binarios gitignored; ver `NOTES.md`). Ropa / accesorio aún necesitan exports — [docs/CALIBRATION.md](docs/CALIBRATION.md).

## Licencia

MIT
