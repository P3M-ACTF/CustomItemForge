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

## Download (end users)

1. Get the `.zip` from the [latest release](https://github.com/P3M-ACTF/VRoidTools/releases/latest) (`CustomItemForge-*.zip`).
2. Extract it anywhere.
3. Follow `RELEASE.txt` inside the zip.

| Artifact | Use |
|---|---|
| `CustomItemForge_Win.pyw` | Windows GUI — double-click, no console |
| `CustomItemForge.sh` | macOS / Linux GUI |
| `CustomItemForge.pyz` | CLI, or GUI when run with no arguments |

Requires **Python 3.12+ with Tkinter**. The release build bundles Pillow for thumbnails.

Each published GitHub Release builds and attaches this zip automatically.

## Quick start (developers)

```powershell
git clone https://github.com/P3M-ACTF/VRoidTools.git
cd VRoidTools\CustomItemForge
python -m pip install -e ".[dev]"
custom-item-forge inspect path\to\item.vroidcustomitem
custom-item-forge gui
pytest
```

Double-click `scripts/CustomItemForge.pyw` during development (runs from source, not the release bundle).

### Build the release bundle locally

```powershell
python scripts/build_release.py
# or: .\scripts\build_release.ps1
```

See [docs/RELEASE.md](docs/RELEASE.md).

## Calibration samples

Hair is calibrated against Studio **2.14.0** fixtures under `tests/fixtures/real/hair/` (gitignored binaries; see `NOTES.md`). Clothing / accessory merge still need samples — [docs/CALIBRATION.md](docs/CALIBRATION.md).

## License

MIT
