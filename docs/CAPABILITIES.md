# Capabilities

## Supported now

| Operation | Status |
|---|---|
| Open / read `.vroidcustomitem` | Yes |
| Inspect (VRoid / VRoidCustomItem / File) | Yes |
| Thumbnail viewer (missing / unreadable / ok) | Yes |
| Validate ZIP + metadata + CRC | Yes |
| Clone / repackage | Yes |
| Compare structure | Yes |
| Probe root group | Yes |
| Compatibility report | Yes (honest stubs when not calibrated) |
| GUI unified shell | Yes |
| i18n EN / ES | Yes |

## Family engines

| Family | Inspect | Recategorize | Merge |
|---|---|---|---|
| Hair | Yes | Yes (golden-tested on Studio 2.14.0 fixtures) | Yes (same category; Common.Base includes image blob store `f6`) |
| Clothing | Yes | Yes (category rewrite; Studio round-trip pending) | Awaiting calibration samples |
| Accessory | Yes | Yes (category rewrite; Studio round-trip pending) | Awaiting calibration samples |
| Cross-family | Blocked | Blocked | Blocked |

Hair notes (2.14.0):

- Fixtures under `tests/fixtures/real/hair/` cover Front/Back/Base/Overall/Extensions/Side/Ahoge/Extra
- Back↔Base coupling is **UI selection only** (H1); each export is a single category
- `BaseHair` uses `TransferableGroupEditType.BaseHair` (distinct from strand hair)

## Explicitly not supported

- Converting hair items into accessory templates by category change alone
- Editing full `.vroid` model archives
- External Blender / Unity / VRM conversion pipeline
- Cloud / marketplace features
- Inventing protobuf suffixes for unconfirmed Studio slots (Inner Top, FurryEars, etc.)

## UI themes

- **Simple** and **Kawaii** skins are planned; the current shell uses the default Tk theme.
