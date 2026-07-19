# GitHub Releases — simple guide (CustomItemForge)

[English](GITHUB_RELEASES.md) · [Español](GITHUB_RELEASES_ES.md)

For **maintainers** who publish. End users only download the zip.

## What the Action does

Workflow: **Release CustomItemForge**  
File: `.github/workflows/release-custom-item-forge.yml`

1. Builds the bundle (`.pyz`, launchers, `RELEASE.txt`)
2. Creates `CustomItemForge-<version>.zip`
3. Uploads it to the GitHub Release (replaces a previous zip if present)

Takes about **~5 minutes**. That is normal.

---

## Publish a new release

1. Open https://github.com/P3M-ACTF/VRoidTools
2. **Releases** → **Draft a new release**
3. Choose/create a **tag** (e.g. `v0.1.0-preview`)
4. Title + notes → **Publish release**
5. That **triggers** the Action automatically

You do not need to upload the zip by hand.

---

## Watch progress

1. **Actions** tab
2. Left: **Release CustomItemForge**
3. Open the latest run
4. Open job **bundle** → live steps

When it finishes, the Release **Assets** list includes the `.zip`.

---

## Rebuild the zip for an existing release

### A — Re-run the same run

1. **Actions** → open that run → **Re-run all jobs**
2. Wait ~5 min → zip is replaced (`--clobber`)

### B — Manual Run workflow (recommended)

1. **Actions** → **Release CustomItemForge**
2. **Run workflow**
3. Enter the exact **tag** (e.g. `v0.1.0-preview`)
4. **Run workflow** → wait ~5 min

The tag must already be a published Release.

---

## Quick checklist

| Goal | Do this |
|---|---|
| New version | Releases → Publish release |
| See status | Actions → Release CustomItemForge |
| Regenerate zip for same tag | Re-run **or** Run workflow with tag |
| Local zip test | `python scripts/build_release.py --zip --tag vX.Y.Z` |

---

## Windows: GUI without a console

- Open the app with **`CustomItemForge_Win.pyw`** (double-click).
- Do **not** double-click `CustomItemForge.pyz` for the GUI (console window).
- Use the `.pyz` only for the **CLI**.

Local build details: [RELEASE.md](RELEASE.md).
