# Release notes — v1.1.0

**17 September 2026 · HATs, shields and carriers**

Six new interface parts cover Raspberry Pi 40-pin, Arduino Uno R3, and Arduino
MKR 28-pin in add-on and carrier roles. A new chooser can create a blank board
or place just the mating header pattern on an existing layout. Named pins work
with normal manual/automatic routing, the inspector and pin table; CSV pin maps
are available. Optional mounting holes belong to the compound part.

Reference illustrations and pin captions never enter manufacturing copper or
silkscreen. Real requested mounting holes do enter DRC, routing obstacles, masks,
drill output and KiCad subset export. Native projects now use schema 2; v1.0
projects migrate on read, while v1.0 readers safely reject new schema-2 saves.

All built-in platform definitions remain nominal and review-required. The MKR
reference envelope does not guarantee all MKR variants. Uno ICSP and automatic
Pi HAT+ EEPROM/power implementation are outside this release. Read
[FORM_FACTORS.md](FORM_FACTORS.md) before fabrication.

[Verification](TESTING.md) documents executed tests and boundaries. No remote
repository, deployment, manufacturing order or physical fit check is claimed.

---

# Release notes — v1.0.0

**17 September 2026. First packaged release. Working title: COPPERBENCH.**

The core workflow is implemented: place representative physical parts, define connections, manually draw or preview selected-lead routes, work across two copper layers, shape the board, add markings and generate inspection/fabrication files.

This release includes both a no-build static source tree and a fully embedded portable HTML. All processing remains local. Native JSON embeds placed footprints and raster assets; the project ZIP wraps that data. The static service-worker shell is optional.

Notable corrections made during release testing include trace-width propagation into selected-pin routing, a spurious numeric-input step constraint that prevented valid text/wizard actions, overlapping mobile inspection space, microscopic-gap connectivity, native import rollback/validation, inner-layer import detection, net-zero interchange, filled silkscreen polygon preservation, physical component mesh occlusion, and avoidance of redundant routes between already connected pins.

Release verification: **32/32 JavaScript engine tests, 20/20 Chromium interaction tests and 12/12 separate Python/Shapely manufacturing-geometry checks.** Consult TESTING.md for environment limits. Actual file-origin persistence, unrestricted browser download navigation, hosted service-worker lifecycle, Safari/Firefox, external KiCad/CAM acceptance, manufacturer upload acceptance and physical fabrication remain unverified.

The included parts are generic and initially unverified against any specific purchased part. The tool has geometric checks, not circuit simulation or electrical safety certification. Manufacturing exports are inspectable files, not a guarantee of board functionality or acceptance by every fabricator.
