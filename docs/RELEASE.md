# Release build (users)

End-user artifacts are generated in the **CustomItemForge project root** (gitignored). Regenerate with the build script; do not edit by hand.

## Build

```powershell
cd CustomItemForge
python scripts/build_release.py
# or
.\scripts\build_release.ps1
```

## Output (project root)

| File | Purpose |
|---|---|
| `CustomItemForge.pyz` | App bundle (Python 3.12+). No args → GUI; with args → CLI |
| `CustomItemForge_Win.pyw` | Windows double-click GUI launcher (no console) |
| `CustomItemForge.sh` | macOS/Linux GUI launcher |
| `RELEASE.txt` | Short instructions for users |

## Distribute

Zip these four files (plus any future assets) and share. Users need **Python 3.12+ with Tkinter** installed.

### GitHub Releases (CI)

Publishing a [GitHub Release](https://github.com/P3M-ACTF/VRoidTools/releases) runs [`.github/workflows/release-custom-item-forge.yml`](../../.github/workflows/release-custom-item-forge.yml), which:

1. Runs `scripts/build_release.py`
2. Packs the four artifacts into `CustomItemForge-<tag>.zip`
3. Uploads the zip as a release asset

End users should download that zip from the release page (see the project README).

## Development vs release

| Audience | Workflow |
|---|---|
| Developers | `pip install -e ".[dev]"` then `custom-item-forge gui` |
| Users | Copy release files; run `CustomItemForge_Win.pyw` / `.sh` or `python CustomItemForge.pyz` |

The release build installs the `[gui]` extra so **Pillow** is bundled for thumbnail previews.
