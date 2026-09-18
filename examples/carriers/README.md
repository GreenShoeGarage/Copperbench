# Header-mounted controller starters

Open a JSON file with **Open → Native JSON** in COPPERBENCH v1.5 or later.
Each is an unconnected mating interface, not a complete working circuit. The
carrier role puts sockets on the top; the add-on role puts headers on the bottom.
Native schema 4 preserves attached antenna guards and physical reference notes.

| Host ID | Files |
|---|---|
| pico | `pico-carrier.json`, `pico-addon.json` |
| pico2 | `pico2-carrier.json`, `pico2-addon.json` |
| pico-w | `pico-w-carrier.json`, `pico-w-addon.json` |
| pico2-w | `pico2-w-carrier.json`, `pico2-w-addon.json` |
| nano-classic | `nano-classic-carrier.json`, `nano-classic-addon.json` |
| esp32-devkitc-v4 | `esp32-devkitc-v4-carrier.json`, `esp32-devkitc-v4-addon.json` |
| feather-classic | `feather-classic-carrier.json`, `feather-classic-addon.json` |
| xiao-rp2040 | `xiao-rp2040-carrier.json`, `xiao-rp2040-addon.json` |
| xiao-esp32c3 | `xiao-esp32c3-carrier.json`, `xiao-esp32c3-addon.json` |

The compound connector is locked by default. Select it, then use **Carrier
clearances & fit** to review assumptions, antenna guards and access regions.
Check actual host dimensions, pin mappings, holes and connector requirements
before fabrication. Header outlines/holes and RF projections are nominal and
unverified for physical fit. No extra underside pads are implied.

See `docs/CARRIERS.md` in the source repository. The static-site distribution
contains these examples but does not publish developer documentation.

`node tools/generate_carrier_examples.js` deterministically regenerates the
18 JSON starter files from the checked-in catalog. Tests do not rewrite them.
