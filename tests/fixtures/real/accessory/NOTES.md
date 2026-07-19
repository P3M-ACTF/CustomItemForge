# Accessory fixtures — awaiting exports

Studio version target: **2.14.0** (Accessories tab).

## Minimum to calibrate AccessoryEngine

| Need | Files |
|---|---|
| Same template | `GlassesA.vroidcustomitem`, `GlassesB.vroidcustomitem` (e.g. Thin/Thick) |
| Other template | 1× Hats **or** FurryEars **or** Tail |

## Studio Accessories map (counts TBD)

```text
Glasses=N, FurryEars=N, Tail=N, Hats=N, Custom=N
```

Protobuf suffixes for FurryEars / Tail / Hats are **unconfirmed** until a real export is probed. Do not invent `TransferableGroupType` strings.

Neck / Arm accessories appear under **Outfit** in Studio UI; CIF currently lists them as family `accessory` — reconcile with `rootTransferableGroupTypeId` from exports.
