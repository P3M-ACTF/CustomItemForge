# Calibration guide

CustomItemForge family engines need real `.vroidcustomitem` exports before merge and recategorize can be marked **calibrated**.

Studio reference: **2.14.0**.

## Minimum samples

| Family | Files needed | Status |
|---|---|---|
| Hair | 2 Extra + 1 resaved (+ coverage across slots) | **Done** — see `tests/fixtures/real/hair/` |
| Clothing | ≥2 items from the **same** category (e.g. two Tops) | Awaiting — `clothing/NOTES.md` |
| Accessory | 2 same template (Glasses) + 1 different template | Awaiting — `accessory/NOTES.md` |

## Where to put them

```
tests/fixtures/real/
  hair/          # populated
  clothing/      # awaiting
  accessory/     # awaiting
```

Binaries are gitignored. `NOTES.md` files are tracked.

## Studio 2.14.0 preset map

### Hairstyle (counted)

| UI | Presets | Fixtures |
|---|---|---|
| Hairstyle_Sets | 37 | 0 (no Custom — skip) |
| Front | 49 | 7 |
| Back | 30 | 3 |
| Overall | 40 | 4 |
| Extensions | 71 | 3 |
| Side | 66 | 3 |
| Ahoge | 25 | 3 |
| Extra | 65 | 2 + 2 resaved |
| Base | 2 | 2 |

Editables without Sets: **348**. Do **not** export the full catalog; samples suffice.

### Outfit / Accessories (counts TBD)

```text
Outfit: Whole_Set=N, Tops=N, Bottoms=N, Dresses=N, Neck_Accessories=N, Arm_Accessories=N, Inner_Top=N, Inner_Bottom=N, Socks=N, Shoes=N
Accessories: Glasses=N, FurryEars=N, Tail=N, Hats=N, Custom=N
```

## Back ↔ Base (calibration finding)

**H1 confirmed:** selecting some Back presets in Studio may also select a linked Base in the UI. Exports remain **single-category** ZIPs (`HairBack` vs `BaseHair`). No multi-category Back+Base file.

Full hair inspect/probe matrix: [`tests/fixtures/real/hair/BASELINE_MATRIX.md`](../tests/fixtures/real/hair/BASELINE_MATRIX.md).

## Validation workflow

1. `cif inspect` / GUI inspect
2. Run planned transform (recategorize or merge)
3. Import in VRoid Studio
4. Edit lightly, save as new item
5. Close and reopen Studio
6. Confirm visuals and editability

## After calibration

Engine modules flip `calibrated = True` and add golden tests against fixtures.

Hair is calibrated for merge and recategorize (Studio 2.14.0 fixtures). Clothing / accessory support **recategorize** via shared category rewrite; **merge** stays `NotCalibratedError` until samples land and Studio round-trip passes.

## Unconfirmed catalog slots

`Inner_Top`, `Inner_Bottom`, `FurryEars`, `Tail`, `Hats`, `Custom` appear in Studio 2.14.0 UI but lack confirmed `TransferableGroupType` suffixes. See `UNCONFIRMED_STUDIO_SLOTS` in `catalog/categories.py`. Add entries only after `cif probe` on a real export.
