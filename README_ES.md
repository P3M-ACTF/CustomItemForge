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

## Inicio rápido

```powershell
cd CustomItemForge
python -m pip install -e ".[dev]"
custom-item-forge inspect ruta\al\item.vroidcustomitem
custom-item-forge gui
pytest
```

## Muestras de calibración

Las operaciones reales de fusión y recategorización requieren fixtures aportados por el usuario. Consulta [docs/CALIBRATION.md](docs/CALIBRATION.md).

Coloca los archivos en `tests/fixtures/real/` (gitignored).

## Empaquetado

```powershell
python scripts/build_zipapp.py
```

Genera `dist/CustomItemForge.pyz` (zipapp multiplataforma; ejecutar con Python 3.12+).

## Licencia

MIT
