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

## Development vs release

| Audience | Workflow |
|---|---|
| Developers | `pip install -e ".[dev]"` then `custom-item-forge gui` |
| Users | Copy release files; run `CustomItemForge_Win.pyw` / `.sh` or `python CustomItemForge.pyz` |

The release build installs the `[gui]` extra so **Pillow** is bundled for thumbnail previews.
