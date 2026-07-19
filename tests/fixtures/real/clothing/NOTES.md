# Clothing fixtures — awaiting exports

Studio version target: **2.14.0** (Outfit tab).

## Minimum to calibrate ClothingEngine

| Need | Files |
|---|---|
| Same category merge | `TopsA.vroidcustomitem`, `TopsB.vroidcustomitem` |
| Ideal extras | 1× Dresses (Onepiece), 1× Inner_Top, 1× Socks or Shoes |

## Studio Outfit map (counts TBD)

```text
Whole_Set=N (omit — no Custom)
Tops=N, Bottoms=N, Dresses=N
Neck_Accessories=N, Arm_Accessories=N  # UI under Outfit; CIF family accessory until probe
Inner_Top=N, Inner_Bottom=N            # catalog suffix unconfirmed until export
Socks=N, Shoes=N
```

Place `.vroidcustomitem` files in this folder, then run `cif inspect` and flip `ClothingEngine.calibrated` after Studio round-trip.
