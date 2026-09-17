# Release roadmap — COPPERBENCH 1.1.0

## Shipped in v1.1

Raspberry Pi 40-pin / Uno R3 / MKR 28-pin interfaces, six add-on/carrier variants,
new-board templates, compound mounting holes, pin aliases/CSV, reference-only
rendering, schema migration and dedicated regression suites.

## Follow-on candidates, not implemented

Variant-specific Pi port/cooler/PoE and MKR antenna clearance models; a sourced
Uno ICSP header option; additional board families; explicit stack-height checking;
editable per-variant mechanical templates; manufacturer/physical coupon validation.

---

# Cumulative batch record — COPPERBENCH 1.0.0

The initial 12-batch plan was implemented as one cumulative first release. Entries below describe what actually shipped, not a claim that every possible feature in an industrial PCB editor is complete. The detailed compatibility and verification records control the scope.

| Batch | Planned checkpoint | Delivered in this package |
|---|---|---|
| 1 | v0.1 foundation | Canonical two-layer model, embedded pad/body definitions, board workspace, selection, snapping, undo, native JSON and autosave state. |
| 2 | v0.2 fabrication proof | Gerber/Excellon writers and strict file read-back; a labelled two-layer geometric coupon for regression. External CAM/upload proof remains a validation step. |
| 3 | v0.3 parts workshop | Curated generic through-hole/SMD families, parametric footprint wizard, advanced pad editor, rotation/side changes and bounded footprint import. |
| 4 | v0.4 board shapes | Standard rectangular/rounded/elliptical shapes, polygon outline/cutout/keepout tools, vertex editing, holes/slots and dimension changes that preserve parts. Curves use the supported shape tools or polyline import rather than a full Bézier sketch system. |
| 5 | v0.5 manual copper | Lead-based traces, width controls, waypoints/segment editing, explicit net intent, connection tracking and geometric checks. |
| 6 | v0.6 two-pin assistance | Rule-aware selected-pin routing in a cancellable worker with a keep/discard preview and safe failure paths. |
| 7 | v0.7 multi-pin/two-sided | Shared-net selected groups, guarded merges, connector pairing, through vias and opposite-face routing. |
| 8 | v0.8 copper zones | Cell-derived vector pours, thermal reliefs, keepouts, island removal and refill invalidation. Not arbitrary exact polygon fills. |
| 9 | v0.9 silkscreen | Stroke text, lines/shapes, mirror/rotate, raster/SVG conversion, retained raster sources, reprocessing and clipping/feature checks. |
| 10 | v0.10 interchange | Native/project ZIP, bounded KiCad board import/export and footprint import, SVG/BOM output, safe import review and simplification notices. Standalone KiCad footprint export is deferred. |
| 11 | v0.11 fabrication workflow | Editable sourced profile, complete fabrication ZIP, export gate/diagnostic override, actual-file preview, reports and baseline comparison. |
| 12 | v1.0 release | Browser-interaction tests, pure-engine tests, separate Python output-geometry checks, responsive themes, recovery/error exercises, documentation, screenshots and static/portable packaging. |

## Evidence still needed beyond the release environment

Open the actual downloaded file in target desktop browsers; exercise real local storage and actual downloads. Test hosted service-worker installation/offline reload at the final deployment path. Load the exported coupon in an independent CAM product and an installed KiCad version. Check the intended fabrication service's upload preview. Order and measure a coupon before describing the tool as physically fabrication-validated.

These steps are explicitly **not completed** in the delivered verification record. No order or upload has been placed on the user's behalf.

## Sensible post-v1 work

Push-and-shove/elastic routing, more extensive exact-geometry and exporter interoperability checks, richer vetted footprint collections, footprint-attached imported artwork, standalone footprint export, improved typography/vector artwork editing, mechanical-model interchange and file exchange with other Field Instruments can follow. Multilayer routing, simulation, cloud collaboration and subscriptions are not prerequisites for this local two-layer workbench.
