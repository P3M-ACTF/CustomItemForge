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

## Quick start

```powershell
cd CustomItemForge
python -m pip install -e ".[dev]"
custom-item-forge inspect path\to\item.vroidcustomitem
custom-item-forge gui
pytest
```

## Calibration samples

Real merge/recategorize operations require user-provided fixtures. See [docs/CALIBRATION.md](docs/CALIBRATION.md).

Place files under `tests/fixtures/real/` (gitignored).

## Packaging

```powershell
python scripts/build_zipapp.py
```

Produces `dist/CustomItemForge.pyz` (multi-platform zipapp; run with Python 3.12+).

## License

MIT
