# Hair calibration fixtures (VRoid Studio 2.14.0)

Exports from Studio **Presets** (not Custom). Naming: `{Category}{Letter}.vroidcustomitem`.

## Inventory

| File pattern | Count | Category ID suffix | Edit type |
|---|---|---|---|
| FrontA–G | 7 | HairFront | Hair |
| BackA–C | 3 | HairBack | Hair |
| BaseA–B | 2 | BaseHair | **BaseHair** |
| OverallA–D | 4 | AllHair | Hair |
| ExtensionsA–C | 3 | HairTied | Hair |
| SideA–C | 3 | HairSideburns | Hair |
| AhogeA–C | 3 | HairAhoge | Hair |
| ExtraA, ExtraB, ExtraA_resaved, ExtraC_resaved | 4 | HairHanege | Hair |

Every inspected file has **exactly one** transferable + one transferable group. No multi-category ZIPs.

Full inspect/probe dump: **[BASELINE_MATRIX.md](BASELINE_MATRIX.md)** / [BASELINE_MATRIX.json](BASELINE_MATRIX.json).

## Back ↔ Base (H1 confirmed)

Studio may **auto-select** a linked Base when choosing some Back presets. That is UI selection, not a coupled export:

- `BackB` → only `HairBack` (no `BaseHair` inside the archive)
- `BaseB` → separate file, `BaseHair`, higher probe score / material refs

Do not build merge logic that assumes Back+Base share one `.vroidcustomitem`.

## Studio preset counts (2.14.0)

| UI | Presets | Fixtures here |
|---|---|---|
| Hairstyle_Sets | 37 | 0 (omit; no Custom) |
| Front | 49 | 7 |
| Back | 30 | 3 |
| Overall | 40 | 4 |
| Extensions | 71 | 3 |
| Side | 66 | 3 |
| Ahoge | 25 | 3 |
| Extra | 65 | 2 + 2 resaved |
| Base | 2 | 2 (full set) |

## Golden checks (code)

- Merge `ExtraA` + `ExtraB` → valid HairHanege item
- Recategorize `FrontA` → `hair-back`
- Resaved Extra: IDs change on re-export; treat as distinct object IDs, same category
