# GitHub Releases — simple guide (CustomItemForge)

[English](GITHUB_RELEASES.md) · [Español](GITHUB_RELEASES_ES.md)

For **maintainers** who publish. End users only download the zip.

## Happy path (release-please)

1. Merge to `main` using **Conventional Commits** (`feat:`, `fix:`, …).
2. The **Release Please** workflow opens or updates a **Release PR** (version bump + `CHANGELOG.md`).
3. When you want an alpha: **merge that Release PR**.
4. That creates the tag (`vX.Y.Z-alpha.N`), a GitHub Release marked **prerelease**, and in the same job builds and uploads the `.zip` (~5 min).

You do not need to create the Release by hand in the UI.

### Watch progress

1. **Actions** → **Release Please**
2. After merging the Release PR, check the zip build/upload steps on that run
3. **Releases** → Assets → `CustomItemForge-*.zip`

### Conventional Commits (required)

| Prefix | Effect (0.x + alpha) |
|---|---|
| `feat:` | bump (patch / alpha) |
| `fix:` | bump (patch / alpha) |
| `feat!:` or `BREAKING CHANGE:` | bump minor (pre-major) |
| `docs:`, `chore:`, `ci:` | no release |

Examples:

```text
feat: add clothing merge preview
fix: prevent crash when material slot is missing
docs: clarify calibration sample layout
```

### Leaving alpha later

In [`release-please-config.json`](../release-please-config.json), set `"prerelease": false` (and drop `prerelease-type` if needed). Later releases will no longer be alpha/prerelease.

---

## Rebuild the zip for an existing release

Workflow: **Release CustomItemForge**  
File: `.github/workflows/release-custom-item-forge.yml`

- **Re-run** the run that uploaded the zip, or
- **Run workflow** with the exact tag (e.g. `v0.1.1-alpha.1`)

Takes ~5 minutes; the asset is replaced (`--clobber`).

---

## Manual release (escape hatch)

A hand-published Release still triggers **Release CustomItemForge** (`release: published`). Prefer release-please for the happy path.

---

## Quick checklist

| Goal | Do this |
|---|---|
| Prepare next alpha | Conventional commits on `main` → review Release PR |
| Publish alpha | Merge the Release PR |
| Check status | Actions → Release Please |
| Regenerate zip for same tag | Run workflow on Release CustomItemForge |
| Local zip test | `python scripts/build_release.py --zip --tag vX.Y.Z-alpha.N` |

---

## Windows: GUI without a console

- Open the app with **`CustomItemForge_Win.pyw`** (double-click).
- Do **not** double-click `CustomItemForge.pyz` for the GUI.
- Use the `.pyz` only for the **CLI**.

Local build details: [RELEASE.md](RELEASE.md).
