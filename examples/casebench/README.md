# CaseBench JSON handoff examples

These are **unrouted demonstration boards**, not the user's current design or
qualified hardware. Import either JSON into CaseBench as a CopperBench board.

- `two-sided-carrier-casebench.json`: mixed top/bottom placement, a rotated bottom connector, four mounting holes and a cutout.
- `rtc-carrier-casebench.json`: rotated bottom DS3231 module interface with two enabled linked mounting holes and its unmodified representative body/stack metadata.

Native app/schema: `COPPERBENCH`, 5; explicit millimetres. No parts, hole coordinates
or module heights are pre-transformed. The default export omits images, standalone
artwork, saved baseline and the unused block library. Keep a normal Save JSON
backup for complete PCB editing. These fixtures have not been imported into the
full target CaseBench app in the release environment. Physical fit remains untested.
