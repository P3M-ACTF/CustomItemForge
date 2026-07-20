# Hair merge format (VRoid Studio 2.x)

Internal structure of `.vroidcustomitem` hair items and what CustomItemForge rewrites on merge. Studio reference: **2.14.0**.

## Archive layout

Every hair custom item is a ZIP with these entries (see also `BASELINE_MATRIX.md`):

| Entry | Role |
|---|---|
| `meta.json` | Top-level package metadata |
| `thumbnails/thumbnail.png` | Preview image |
| `v1customitem/meta.json` | Item metadata (name, ids) |
| `v1customitem/basetransferable.basetransferable` | Shared materials / textures / **image blobs** (`TransferableType.Common.Base`) |
| `v1customitem/transferablegroups/*.transferablegroup` | Exactly one root group (category + edit type + transferable ref) |
| `v1customitem/transferables/*.transferable` | Exactly one hair transferable (strands, bones, local resource store) |

Invariants for Studio 2.14.0 strand hair fixtures:

- Single category per ZIP (no Back+Base coupling inside one file; that coupling is UI-only).
- Strand slots (`HairFront`, `HairBack`, `HairHanege` / Extra, …) use `TransferableGroupEditType.Hair` and typically `root_material_refs = 0`.
- `BaseHair` uses `TransferableGroupEditType.BaseHair` and higher probe scores / material refs.

## `basetransferable` payload (Common.Base)

Wire layout (simplified):

```text
basetransferable
  f2 = "TransferableType.Common.Base"
  f3 = payload
    f2 = material/texture store   (repeated records f1..f9 by string id)
    f4 = small header
    f5 = shared-hair-material side table (merge appends unique f5.9 ids)
    f6 = image/blob store         (repeated f1 entries: id@1 + bytes@2)
```

### Store field meanings (empirical)

| Store field | Typical content |
|---:|---|
| 1 | Material / shared-material records |
| 2 | Related parameter blocks |
| 3 | Additional material-linked records |
| 5–6 | Texture parameter wrappers (often hold **image id** references) |
| 9 | Other id-keyed records |

IDs are 32-char hex strings. Texture records reference image ids that must exist in **payload field 6** (blob store), unless the item embeds image data only inside the fat store (some custom exports leave `f6` empty and put large data under `f2`).

### Two export shapes observed

1. **Preset-like (thin store + blobs):** `f2` ~2–3 KB, `f6` ~100 KB with 2 PNG/raw blobs (ExtraA/B, BackA/B fixtures, `Extra_Cuernitos`).
2. **Custom fat-store:** `f2` ~180 KB, `f6` empty (`Extra_AlitasMurcielago`). Materials still use string image ids when merging against a blob-based add-on.

## Hair `.transferable` payload

```text
transferable
  f2 = TransferableType.N00.<HairSlot>   # e.g. HairHanege, HairBack
  f3 = payload
    f2 = local resource store (materials/textures; numeric indices)
    f4 = hair data
      f1 = Hair Bounce bone groups
      f2 = hair store
        f3* = hair strands
        f4* = geometry blocks
```

Strand material references use **numeric slots**:

- Low indices → materials in `basetransferable` store (1-based).
- Higher indices → local transferable store (`index - basetransferable_material_count`).

After merge, addon strand/geometry varints are remapped via `HairReferenceMaps` (`bt_slot`, `storage_f1` / `f8` / `f9`).

## What merge rewrites

Implemented in `engines/hair/merge.py` + `engines/hair/operations.py`:

| Target | Action |
|---|---|
| Hair transferable store (`payload.f2`) | Append unique id-keyed records; keep canonical field-number order |
| Hair Bounce groups | Append unique bone groups |
| Hair strands + geometry | Append addon strands/geometry; **remap** material/texture indices |
| `basetransferable` store (`payload.f2`) | Append unique material/texture records |
| `basetransferable` `payload.f5` | Append unique `f5.9` shared-material ids |
| `basetransferable` `payload.f6` | Append unique **image blobs** by id (required for Studio) |
| Transferable group / meta / thumbnail | Keep base group; **square overlay** merge thumbnail (512×512); copy non-colliding addon ZIP entries |

### Merge thumbnail

Studio’s custom-item grid expects a **square** preview (~512×512), matching preset exports.

CustomItemForge builds `thumbnails/thumbnail.png` by **alpha-compositing** the base and add-on embedded PNGs onto a light 512×512 canvas (`compose_overlay_square_png`). A wide side-by-side collage (e.g. 1032×512) is cropped badly in Studio and must not be written.

No 3D viewport / geometry decode: only the PNGs Studio already embedded in each item.

Category / edit-type differences:

| Kind | Suffix examples | Merge notes |
|---|---|---|
| Strand hair | HairFront, HairBack, HairHanege (Extra), … | Same-category only; remapping + full Common.Base merge |
| Base hair | BaseHair | Distinct edit type; not mixed with strand slots in one merge |

Back vs Extra: **same merge code path**. Failures that look “Extra-only” usually come from sample shape (fat-store base + blob add-on), not from `HairHanege` being special.

## Bug: Extra_AlitasMurcielago + Extra_Cuernitos

### Symptom

Importing the merged Extra item into VRoid Studio crashes while applying the custom item.

### Player.log (evidence)

```text
KeyNotFoundException: The given key '438fffaf21194d9bbd59b04729d72ede' was not present in the dictionary.
  at ... Image.DuplicateDeep ...
  at ... Texture.DuplicateDeep ...
  at ... Material.DuplicateDeep ...
  at ... SharedMaterialDuplicateUtil.DuplicateSharedHairMaterial ...
  at ... ReplaceTransferableGroupCommand.RollForwardAsync ...
```

Target group in the failing session matched the Alitas root:

`user_VRoid_CustomItem_51faac1f51cf4a5caa389e17d6ea634c.transferablegroup`

### Root cause

1. Addon (`Extra_Cuernitos`) stores image **`438fffaf21194d9bbd59b04729d72ede`** in `basetransferable` **payload field 6**, and its texture records in `payload.f2` reference that id.
2. Base (`Extra_AlitasMurcielago`) has an **empty** `f6` (textures live in a fat `f2`).
3. Older merge code merged `f2` (+ partial `f5`) but **dropped addon `f6` blobs**.
4. Merged item retained texture metadata pointing at the image id, without the blob → Studio `DuplicateSharedHairMaterial` → `KeyNotFoundException`.

The same omission also drops addon blobs when merging fixture pairs (ExtraA+ExtraB, BackA+BackB). Back merges are **not** immune; they fail the same way whenever the add-on’s image blobs are required.

### Fix (engine)

In `merge_base_transferables`, also merge `payload.f6` with `_append_unique(..., numbers={1})`, replacing an empty base blob store or inserting field 6 if absent (`_merge_base_payload_f6`).

Verification checklist:

1. `cif merge Extra_AlitasMurcielago.vroidcustomitem Extra_Cuernitos.vroidcustomitem out.vroidcustomitem --force`
2. Confirm merged `basetransferable` `f6` contains both Cuernitos blob ids (including `438fffaf…`).
3. Import in Studio 2.14.0, apply to avatar, save/reopen.
4. `pytest tests/test_real_hair.py tests/test_engines.py`

## Related docs

- [`CALIBRATION.md`](CALIBRATION.md) — sample requirements and Studio workflow
- [`../tests/fixtures/real/hair/BASELINE_MATRIX.md`](../tests/fixtures/real/hair/BASELINE_MATRIX.md) — inspect/probe matrix
- [`../tests/fixtures/real/hair/NOTES.md`](../tests/fixtures/real/hair/NOTES.md) — fixture inventory
