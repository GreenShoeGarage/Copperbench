# COPPERBENCH 1.1 — file compatibility and limits

## Native project

`app: "COPPERBENCH"`, `schema: 2`, `version: "1.1.0"`. JSON retains board geometry, placed footprint definitions, representative bodies, nets, copper, drills, artwork, embedded raster source images, fabrication rules, settings, assumptions, evidence and the optional baseline. A project ZIP wraps this same `project.json`; it is not a different data model.

Newer/unknown schemas, nonfinite dimensions, duplicate object identities, unsupported geometry and missing nets are rejected before replacement. Imports are reviewed; replacing a board is undoable. Schema-1 v1.0 projects are migrated on read. v1.0 readers reject new schema-2 files, preventing silent loss of linked mounting-hole geometry. Copper fills are deliberately invalidated on import and must be recalculated. Browser camera/drawer state is workspace state, not manufacturing geometry.

The UI currently caps import files at 25 MB; imported KiCad source at 20 MB; common geometry collections at 10,000 entries; pads per component at 256; raster source data at 16 MB. These bounds protect the browser; they are not performance guarantees. Large copper fills and dense designs can still be slow.

## Gerber

**Export:** metric RS-274X image geometry with optional X2 file attributes, 4.6 coordinate format, leading-zero omission, absolute coordinates, circular/rectangular apertures, regions and straight stroked segments. Filenames identify F/B copper, mask, silkscreen, optional paste, and Edge_Cuts. Solder-mask images describe openings and have the appropriate negative file-polarity attribute in X2 mode. Bottom layers share the physical coordinates of top layers; no manufacturing-file mirror is applied.

**Read-back:** own-exporter subset only. It is not a general Gerber viewer or an editable Gerber-to-project reconstruction tool. Unsupported commands, macros, arc interpolation and ambiguous formats are rejected. The generated files are parsed for the Fabrication view; the renderer does not merely reuse the original project copper.

Silkscreen output clears expanded pad mask openings, exposed vias, holes, cutouts and the outside of the board. Those clear operations can change artwork: inspect them. Mask expansion is global in this release. Optional paste follows supported SMD pads without stencil reduction rules.

## Excellon

**Export:** metric, explicit-decimal coordinates, tool diameter declarations, absolute positioning, separate PTH/NPTH files when there are corresponding holes, and G85 straight slots. Through-via and through-hole pad bores are plated; standalone and component-linked mounting holes are NPTH. Slot size is cutter diameter plus centerline travel, not a second independent oval dimension.

**Read-back:** this explicit-decimal tool/hole/G85 subset only. Not every drill dialect, routing command or zero-suppression convention is supported. Arc slots and blind/buried via drill stacks are outside scope.

## KiCad

**Board import/export:** `.kicad_pcb`, public S-expression subset. Export declares the 20240108 file version. This has been tested by COPPERBENCH round-trip tests, not loaded in a installed KiCad application in the release environment.

**Footprint import:** `.kicad_mod`, circular/rectangular/oval supported pads and a generic representative body. Standalone-library placement does not place the original footprint artwork; the import dialog reports this. There is no standalone `.kicad_mod` exporter in v1.1; placed footprints are included in exported boards.

Supported board content includes two copper layers, simple through/SMD pads, straight traces, through vias, simple non-plated holes and supported straight slots, closed outlines/cutouts, simple silkscreen drawing and text, zones and conservative keepouts. Board origins are normalized to the outer outline bounding box. Component/pad identity and physical geometry are retained for the supported subset; application-specific metadata and graphical object grouping are not lossless.

The importer stops on detected inner layers, custom/round-rectangle or other unsupported pads, offset drills, per-pad mask/paste overrides, explicit mask/paste graphics, graphical copper, unsupported via spans, embedded objects, open outlines and other unsupported manufacturing geometry. Vertically defined plated oval drills need an equivalent supported orientation before import. Do not use repeated import/export as a substitute for reviewing the resulting geometry.

Reported simplifications include:

- Copper and outline arcs become polylines (at most 0.2 mm arc-length steps, quantized to the native grid).
- Board-import footprint artwork becomes independent board artwork. Moving a component does not move that flattened artwork.
- Text uses the built-in drafting alphabet; inspect position, justification, mirroring, size and appearance.
- External 3D paths are not fetched or embedded; package bodies are representative.
- Copper fills are discarded and regenerated. Local manufacturer rules replace project-level KiCad rules. Via tenting and pad-mask/paste handling follow COPPERBENCH's supported model rather than every source-file option.
- Keepouts are conservative copper exclusions, not the full range of selective KiCad keepout semantics.

**Use native JSON for lossless COPPERBENCH work. Use KiCad interchange for explicitly reviewed geometry exchange.**

## Images and SVG

PNG, JPEG and other browser-decodable raster input are converted locally to raster source plus vector rectangles. Threshold, inversion, scale and cleanup are visible conversion settings. Tiny features are reported; do not assume automatic conversion guarantees legibility.

Self-contained SVG artwork is rasterized in a browser image and then follows the same controlled conversion. Scripts, external references, stylesheets, executable/embed-capable constructs and entity declarations are rejected. This is not unrestricted SVG editing. SVG outline import uses its supported drawing conversion and requires explicit physical scale. SVG output contains outline/cutouts and the chosen face's silkscreen; it is not a copper manufacturing format.

## Reports

BOM CSV, editable native JSON, and an HTML design-review report are generated locally. Print/Save as PDF uses the browser print dialog. There is no embedded PDF engine. The report includes findings, footprint check status, assumptions, evidence and baseline comparison. It is a design record, not a fabrication certificate.

## Platform / form-factor interchange

Native JSON includes each placed interface’s signal labels, local pads,
reference outline, optional local mounting holes, review status and display
options. Old schema-1 projects remain readable. v1.1 writes schema 2.

Gerber/Excellon exports include only real PCB manufacturing geometry: connector
pads, requested NPTH holes and the user’s board/circuit. Reference host chips,
port illustrations and on-screen captions do not export. A blank starter has
no automatic EEPROM, internal host nets or power connections.

KiCad subset export writes actual contact and mounting-hole geometry. Linked
holes become independent mounting-hole footprints, and host-reference/alias
metadata is not round-tripped. Use native JSON as the lossless master.

Pin-map CSV is documentation, not a schematic/netlist import. Compound headers
appear as one assembly row in the existing BOM; select actual connector SKUs and
quantities separately. See [form factors](FORM_FACTORS.md) for coverage limits.
