# CustomItemForge

Parte de [VRoidTools](../README_ES.md).

Herramientas para inspeccionar y transformar archivos `.vroidcustomitem` **for VRoid Studio**.  
Este proyecto es independiente de la marca VRoid; la compatibilidad se describe como *for VRoid*.

[English](README.md) · [Español](README_ES.md)

## Funcionalidades (bases v0.1.0)

- **Inspeccionar** con tres secciones: VRoid / VRoidCustomItem / Archivo
- **Validar**, **clonar**, **comparar**, **probe**, **compatibilidad**
- **GUI unificada** (Tkinter) — inglés por defecto, español disponible
- **Motores por familia** (cabello / ropa / accesorio) con stubs honestos hasta recibir muestras de calibración
- **CLI**: `cif` / `custom-item-forge`

## Inicio rápido (desarrolladores)

```powershell
cd CustomItemForge
python -m pip install -e ".[dev]"
custom-item-forge inspect ruta\al\item.vroidcustomitem
custom-item-forge gui
pytest
```

Durante el desarrollo puedes hacer doble clic en `scripts/CustomItemForge.pyw` (ejecuta desde el código fuente, no el bundle de release).

## Muestras de calibración

Las operaciones reales de fusión y recategorización requieren fixtures aportados por el usuario. Consulta [docs/CALIBRATION.md](docs/CALIBRATION.md).

Coloca los archivos en `tests/fixtures/real/` (gitignored).

## Bundle de release (usuarios finales)

Compila una vez y comprime o copia `dist/` para distribuir:

```powershell
python scripts/build_release.py
# o: .\scripts\build_release.ps1
```

| Artefacto | Uso |
|---|---|
| `dist/CustomItemForge.pyw` | GUI en Windows — doble clic, sin consola |
| `dist/CustomItemForge.sh` | GUI en macOS / Linux |
| `dist/CustomItemForge.pyz` | CLI, o GUI si se ejecuta sin argumentos |

Requiere **Python 3.12+ con Tkinter** en la máquina destino. Consulta [docs/RELEASE.md](docs/RELEASE.md).

## Licencia

MIT
