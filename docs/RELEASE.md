# Release build (users)

End-user artifacts are generated into `dist/` (gitignored). Do not edit files in `dist/` by hand; regenerate with the build script.

## Build

```powershell
cd CustomItemForge
python scripts/build_release.py
# or
.\scripts\build_release.ps1
```

## Output

| File | Purpose |
|---|---|
| `CustomItemForge.pyz` | App bundle (Python 3.12+). No args → GUI; with args → CLI |
| `CustomItemForge.pyw` | Windows double-click GUI launcher (no console) |
| `CustomItemForge.sh` | macOS/Linux GUI launcher |
| `README.txt` | Short instructions for users |

## Distribute

Zip the contents of `dist/` and share. Users need **Python 3.12+ with Tkinter** installed.

## Development vs release

| Audience | Workflow |
|---|---|
| Developers | `pip install -e ".[dev]"` then `custom-item-forge gui` |
| Users | Copy `dist/` bundle; run `.pyw` / `.sh` or `python CustomItemForge.pyz` |
