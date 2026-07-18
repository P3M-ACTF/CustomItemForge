# Calibration guide

CustomItemForge family engines need real `.vroidcustomitem` exports before merge and recategorize can be marked **calibrated**.

## Minimum samples

| Family | Files needed |
|---|---|
| Hair | 2 distinct extra/strand items + 1 re-saved unchanged export |
| Clothing | ≥2 items from the **same** category (e.g. two Tops) |
| Accessory | 2 items sharing a template (e.g. Glasses Thin + Thick) + 1 different template |

## Where to put them

```
tests/fixtures/real/
  hair/
  clothing/
  accessory/
```

This folder is gitignored. Add a short `NOTES.md` beside each file describing origin and Studio version.

## Validation workflow

1. `cif inspect` / GUI inspect
2. Run planned transform (recategorize or merge)
3. Import in VRoid Studio
4. Edit lightly, save as new item
5. Close and reopen Studio
6. Confirm visuals and editability

## After calibration

Engine modules flip `calibrated = True` and implement real logic with golden tests against your fixtures.
