# CustomItemForge

Part of [VRoidTools](../README.md).

Tools to inspect and transform `.vroidcustomitem` files **for VRoid Studio**.  
This project is independent from VRoid branding; compatibility is described as *for VRoid*.

[English](README.md) · [Español](README_ES.md)

## Features (v0.1.0 foundations)

- **Inspect** with three sections: VRoid / VRoidCustomItem / File
- **Validate**, **clone**, **compare**, **probe**, **compatibility**
- **Unified GUI** (Tkinter) — English default, Spanish available
- **Family engines** (hair / clothing / accessory) with honest stubs until calibration samples arrive
- **CLI**: `cif` / `custom-item-forge`

## Quick start (developers)

```powershell
cd CustomItemForge
python -m pip install -e ".[dev]"
custom-item-forge inspect path\to\item.vroidcustomitem
custom-item-forge gui
pytest
```

Double-click `scripts/CustomItemForge.pyw` during development (runs from source, not the release bundle).

## Calibration samples

Real merge/recategorize operations require user-provided fixtures. See [docs/CALIBRATION.md](docs/CALIBRATION.md).

Place files under `tests/fixtures/real/` (gitignored).

## Release bundle (end users)

Build once, then zip or copy `dist/` for distribution:

```powershell
python scripts/build_release.py
# or: .\scripts\build_release.ps1
```

| Artifact | Use |
|---|---|
| `dist/CustomItemForge.pyw` | Windows GUI — double-click, no console |
| `dist/CustomItemForge.sh` | macOS / Linux GUI |
| `dist/CustomItemForge.pyz` | CLI, or GUI when run with no arguments |

Requires **Python 3.12+ with Tkinter** on the target machine. See [docs/RELEASE.md](docs/RELEASE.md).

## License

MIT
