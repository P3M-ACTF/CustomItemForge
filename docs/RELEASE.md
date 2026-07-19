# Release build (users)

End-user artifacts are generated in the **CustomItemForge project root** (gitignored). Regenerate with the build script; do not edit by hand.

## Build

```powershell
cd CustomItemForge
python scripts/build_release.py
# or
.\scripts\build_release.ps1
```

Add **`--zip`** to produce a GitHub-ready archive:

```powershell
python scripts/build_release.py --zip
# optional: match a release tag name
python scripts/build_release.py --zip --tag v0.1.1-alpha.0
```

Output: `dist/CustomItemForge-<label>.zip` containing a single folder with all release files.

## Output (project root)

| File | Purpose |
|---|---|
| `CustomItemForge.pyz` | App bundle (Python 3.12+). No args → GUI; with args → CLI |
| `CustomItemForge_Win.pyw` | Windows double-click GUI launcher (no console) |
| `CustomItemForge.sh` | macOS/Linux GUI launcher |
| `RELEASE.txt` | Short instructions for users |

## Distribute

### GitHub Releases (recommended)

Maintainer guide (release-please + zip):

- [GITHUB_RELEASES.md](GITHUB_RELEASES.md) (English)
- [GITHUB_RELEASES_ES.md](GITHUB_RELEASES_ES.md) (Español — guía fácil)

Short version:

1. Merge conventional commits to `main` — **Release Please** opens/updates a Release PR.
2. Merge that Release PR when you want an alpha — CI creates the tag/prerelease and uploads `dist/CustomItemForge-<label>.zip` (see [`.github/workflows/release-please.yml`](../../.github/workflows/release-please.yml)).
3. To **rebuild** a zip later: Actions → **Release CustomItemForge** → **Run workflow** with the same tag.
4. Users download that zip from the release page.

Config: [`release-please-config.json`](../../release-please-config.json) (alphas via `prerelease` + `prerelease-type: alpha`).

### Windows GUI (no console)

End users should open **`CustomItemForge_Win.pyw`**, not the `.pyz`. The `.pyz` is for CLI only; double-clicking it opens a console.

### Manual zip (local testing)

Same as CI:

```powershell
python scripts/build_release.py --zip --tag v0.1.1-alpha.0
```

Share `dist/CustomItemForge-0.1.1-alpha.0.zip`. Extracting creates `CustomItemForge-0.1.1-alpha.0/` with the four files inside.

## Development vs release

| Audience | Workflow |
|---|---|
| Developers | `pip install -e ".[dev]"` then `custom-item-forge gui` |
| Users | Download release zip; run `CustomItemForge_Win.pyw` / `.sh` or `python CustomItemForge.pyz` |

The release build installs the `[gui]` extra so **Pillow** is bundled for thumbnail previews.
