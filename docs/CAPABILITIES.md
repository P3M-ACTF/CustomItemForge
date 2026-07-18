# Capabilities

## Supported now (Phase 0)

| Operation | Status |
|---|---|
| Open / read `.vroidcustomitem` | Yes |
| Inspect (VRoid / VRoidCustomItem / File) | Yes |
| Thumbnail viewer (missing / unreadable / ok) | Yes |
| Validate ZIP + metadata + CRC | Yes |
| Clone / repackage | Yes |
| Compare structure | Yes |
| Probe root group | Yes |
| Compatibility report | Yes (honest stubs) |
| GUI unified shell | Yes |
| i18n EN / ES | Yes |

## Family engines

| Family | Inspect | Recategorize | Merge |
|---|---|---|---|
| Hair | Yes | Yes (VRoidHairComposer 0.4.x logic) | Yes (same category) |
| Clothing | Yes | Awaiting calibration | Awaiting calibration |
| Accessory | Yes | Awaiting calibration | Awaiting calibration |
| Cross-family | Blocked | Blocked | Blocked |

## Explicitly not supported

- Converting hair items into accessory templates by category change alone
- Editing full `.vroid` model archives
- External Blender / Unity / VRM conversion pipeline
- Cloud / marketplace features

## UI themes

- **Simple** and **Kawaii** skins are planned; the current shell uses the default Tk theme.
