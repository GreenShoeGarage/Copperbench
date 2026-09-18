# Release notes — v1.3.1

**17 September 2026 · Polarity labels and repaired silkscreen export**

**Re-export existing fabrication ZIPs.** The old nested clear frame could remove
all on-board silk under Gerber's union rule. The exporter now clears only explicit
exterior pieces; both the on-screen reader and separate Python regression reader
have been corrected as well. Source text, references, shapes and image conversions
remain ink, subject to intentional mask/hole/edge clipping.

Diodes/LEDs have A/K labels and full Anode/Cathode pin names. Polarized capacitors
have +/− and Positive/Negative names. Select a part → **Polarity & pin roles** for
explicit pin-role assignment and printable-mark controls. Printing is independent
of reference-label visibility, and roles never automatically change electrical
connections. Existing built-in A/K and +/− parts gain labels without pad changes.

**Fabrication → Top silk only / Bottom silk only** isolates actual Gerber artwork.
The original editable projects do not need their silk redrawn. Reopen and inspect
them in v1.3.1, adjust any newly printed polarity marks in dense layouts, then
regenerate manufacturing files. Replace the complete static app, not just index.html.
The portable HTML is self-contained. Native schema remains 3. All platform, via
and plane functionality is retained.

[Fix guide](POLARITY_AND_SILKSCREEN.md) · [Verification](TESTING.md) · [Compatibility](COMPATIBILITY.md)

No remote repository change, external CAM application review, manufacturer upload
or physical fabrication is claimed.

---

# Release notes — v1.3.0

**17 September 2026 · Easy power and ground planes**

Assign a net to either board face from **Planes**. Start with **Bottom ground ·
top routing**, then use **Connect a lead** to propose direct contact or a short
trace/via attachment. Explicit acceptance commits one undoable transaction.
Changing plane assignments never silently reassigns component leads.

Automatic refill follows edits and board resizing. Actual copper-region status
reveals isolated areas and disconnected leads. Manual local pours remain intact.
All v1.2 vias and v1.1 HAT/shield/carrier parts remain included.

**Back up before upgrading:** v1.3 writes schema 3. Schema-1/2 projects open, but
older apps reject new saves rather than discard managed-plane behavior. KiCad
exports ordinary zones, not automatic-follow metadata.

[Plane guide](PLANES.md) · [Verification](TESTING.md) · [Compatibility](COMPATIBILITY.md)

The local helper and cell-derived fills have deliberate limits. No remote repo
change, external CAM validation, manufacturer upload or physical test is claimed.

---

# Release notes — v1.2.0

**17 September 2026 · Visible, editable through vias**

Click **＋ Via** or press **Shift+V** to place a standalone through via. Choose a
net, dimensions and both-side mask tenting, preview its clearances, then click
the board. Repeated placement, precise editing, locking and a Manage vias table
make vias discoverable rather than a hidden tracing shortcut.

During manual routing, **V** inserts at the cursor; **Via → other side** arms the
next board click. The trace and via are one undoable edit. Routes can start/end
on existing vias and copper. A via at a trace endpoint remains selectable.

Native JSON remains schema 2. Old designs open; all v1.1 HAT/shield/carrier parts
are retained. The KiCad geometry subset does not preserve via tenting or locks;
this is disclosed before export and in import reports. Direct Gerber and Excellon
preserve selected masks, both copper pads and one plated drill.

[Via guide](VIAS.md) · [Verification](TESTING.md) · [Compatibility](COMPATIBILITY.md)

No remote repository, deployment, external CAM check, manufacturer upload,
physical board or electrical test is claimed.

---

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
