# COPPERBENCH 1.6.0 — file compatibility and limits

## Native project

`app: "COPPERBENCH"`, `schema: 5`, `version: "1.6.0"`. JSON retains board geometry, placed footprint definitions, representative bodies, nets, copper, drills, artwork, embedded raster source images, fabrication rules, settings, assumptions, evidence and the optional baseline. A project ZIP wraps this same `project.json`; it is not a different data model.

Newer/unknown schemas, nonfinite dimensions, duplicate object identities, unsupported geometry and missing nets are rejected before replacement. Imports are reviewed; replacing a board is undoable. Schema-1/2/3/4 projects are migrated on read. Earlier editors reject new schema-5 files, preventing silent loss of module/block metadata and attached carrier constraints. Copper fills are deliberately invalidated on import and must be recalculated. Browser camera/drawer state is workspace state, not manufacturing geometry.

The UI currently caps import files at 25 MB; imported KiCad source at 20 MB; common geometry collections at 10,000 entries; pads per component at 256; raster source data at 16 MB. These bounds protect the browser; they are not performance guarantees. Large copper fills and dense designs can still be slow.

## Module interfaces and circuit blocks (schema 5)

`part.module` holds the exact model/product, CAD URL/blob reference, notes, nominal
stack gap, body visibility, review status and optional mounting-hole pattern.
`blockInstances` records groups of ordinary component/trace/via IDs, a transform
anchor, external-port net IDs and review notes. `blockLibrary` embeds project-local
circuit templates. There is no live dependency on a server or future library version.

Standalone `COPPERBENCH-BLOCK` schema-1 JSON carries components, traces, vias, nets
and ports. Input validates identities, limits and references before mutation. New
insertions remap object and net IDs; only explicit external-port mappings reuse an
existing net. Capture rejects unsupported standalone geometry rather than silently
dropping it. See [Modules and blocks](MODULES_AND_BLOCKS.md).

KiCad exchange keeps supported ordinary geometry and nets but omits module identity,
fit assumptions, group records, personal templates and editor-only illustrations.
The export dialog warns about this loss; native JSON is the lossless master.

## Attached controller constraints (schema 4)

The carrier extension introduced in v1.5 reads old schemas 1–3 without rewriting embedded footprint geometry. New
saves now use schema 5 so older editors cannot silently ignore the constraints.
Part field `carrier` has its own schema 1, model/source/date, USB direction,
wireless type, display flag, enforcement flag, required override reason when
disabled, assumed `stackGap`, and bounded local rectangular `regions`.
A region's `kind` is `antenna` or `access`. Effective enforced copper keepouts are
derived through `CB.keepouts(document)` from part transforms; they are not stored
as independently movable document keepouts. Editing constraints invalidates pours.
KiCad exports active guards as ordinary per-face keepout zones without linkage.
Reference appearance, access zones, gap assumptions and host metadata do not
survive that exchange. See [CARRIERS.md](CARRIERS.md).

## Polarity metadata and automatic markings

Optional pad field `polarity` is one of `anode`, `cathode`, `positive`, `negative`
or `none`. Missing roles on recognized built-in diode/LED/capacitor packages may
be inferred from their original literal A/K or +/− pin identities only. Numeric,
imported and custom roles require explicit assignment. `none` suppresses that
legacy inference. No rule infers roles from a net name or changes a pin number.

Optional part field `polaritySilk` holds `visible`, `size`, `gap`, `x` and `y`.
v1.6.2 defaults print 0.9 mm symbols with 0.16 mm strokes, 0.7 mm beyond the
body/pad bounds, with zero local offsets. Explicit existing settings are preserved.
Four-terminal rows are spaced to avoid overlapping glyphs. Native schema is 5;
v1.6.2 reads all earlier supported projects. Older releases may render automatic
labels differently; use v1.6.2 to reproduce these marks. Save a backup first.

Gerber contains the resulting vector strokes. KiCad/SVG exchange receives geometry,
not editable electrical-role or automatic-label metadata. Imported KiCad markings
may therefore be ordinary independent artwork; do not assume moving a component
will move flattened imported silk. Native JSON remains the lossless master.

## Managed planes

A zone with `boardPlane: true` is a managed board-following pour. At most one is
permitted per face; it must have a known net and use top or bottom, not both.
The zone retains `thermal`, `gap`, `spoke`, `step` and derived `fill` geometry.
Project setting `autoPlanes` controls automatic refill. Schema migration does
not invent managed zones in old files.

Gerber contains filled copper; Excellon contains real vias. KiCad exports a
managed plane as an ordinary copper zone: reimport does not restore its
board-following semantics. The export dialog discloses this loss. Native JSON
is the lossless backup. See [PLANES.md](PLANES.md).

## Via native fields

Each via retains `id`, `x`, `y`, `net`, `diameter`, `drill`, `tented` and optional
`locked`. Settings retain default `viaDiameter`, `viaDrill`, and `viaTented`.
The latter defaults to false for older projects. Tenting applies to both faces;
there is no independent per-face tenting or filled/capped-via process field.
Native JSON is the lossless backup. See [VIAS.md](VIAS.md).

## Gerber

**Export:** metric RS-274X image geometry with optional X2 file attributes, 4.6 coordinate format, leading-zero omission, absolute coordinates, circular/rectangular apertures, regions and straight stroked segments. Filenames identify F/B copper, mask, silkscreen, optional paste, and Edge_Cuts. Solder-mask images describe openings and have the appropriate negative file-polarity attribute in X2 mode. Bottom layers share the physical coordinates of top layers; no manufacturing-file mirror is applied.

**Read-back:** own-exporter subset only. It is not a general Gerber viewer or an editable Gerber-to-project reconstruction tool. Unsupported commands, macros, arc interpolation and ambiguous formats are rejected. The generated files are parsed for the Fabrication view; the renderer does not merely reuse the original project copper.

**v1.3.1 corrective note:** region contours are unioned. The former nested
clear-frame implementation and matching reader/XOR behavior are no longer used.
Exterior clipping is emitted as separate single-contour regions, including for
concave, rounded and offset outlines. Previously exported ZIPs must be regenerated.
Open or incomplete region contours are rejected by read-back.

Silkscreen output clears expanded pad mask openings, exposed vias, holes, cutouts and the outside of the board. Those clear operations can change artwork: inspect them. Mask expansion is global in this release. Optional paste follows supported SMD pads without stencil reduction rules.

## Excellon

**Export:** metric, explicit-decimal coordinates, tool diameter declarations, absolute positioning, separate PTH/NPTH files when there are corresponding holes, and G85 straight slots. Through-via and through-hole pad bores are plated; standalone and component-linked mounting holes are NPTH. Slot size is cutter diameter plus centerline travel, not a second independent oval dimension.

**Read-back:** this explicit-decimal tool/hole/G85 subset only. Not every drill dialect, routing command or zero-suppression convention is supported. Arc slots and blind/buried via drill stacks are outside scope.

## KiCad

**Board import/export:** `.kicad_pcb`, public S-expression subset. Export declares the 20240108 file version. This has been tested by COPPERBENCH round-trip tests, not loaded in a installed KiCad application in the release environment.

**Footprint import:** `.kicad_mod`, circular/rectangular/oval supported pads and a generic representative body. Standalone-library placement does not place the original footprint artwork; the import dialog reports this. There is no standalone `.kicad_mod` exporter in v1.3; placed footprints are included in exported boards.

Supported board content includes two copper layers, simple through/SMD pads, straight traces, through vias, simple non-plated holes and supported straight slots, closed outlines/cutouts, simple silkscreen drawing and text, zones and conservative keepouts. Board origins are normalized to the outer outline bounding box. Component/pad identity and physical geometry are retained for the supported subset; application-specific metadata and graphical object grouping are not lossless.

The importer stops on detected inner layers, custom/round-rectangle or other unsupported pads, offset drills, per-pad mask/paste overrides, explicit mask/paste graphics, graphical copper, unsupported via spans, embedded objects, open outlines and other unsupported manufacturing geometry. Vertically defined plated oval drills need an equivalent supported orientation before import. Do not use repeated import/export as a substitute for reviewing the resulting geometry.

Reported simplifications include:

- Copper and outline arcs become polylines (at most 0.2 mm arc-length steps, quantized to the native grid).
- Board-import footprint artwork becomes independent board artwork. Moving a component does not move that flattened artwork.
- Text uses the built-in drafting alphabet; inspect position, justification, mirroring, size and appearance.
- External 3D paths are not fetched or embedded; package bodies are representative.
- Copper fills are discarded and regenerated. Local manufacturer rules replace project-level KiCad rules. Per-via tenting and locks are not preserved by this subset: imported vias use open masks. This is stated before via-bearing board export and in the import report. Pad-mask/paste handling is limited as described above.
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
options. Old schema-1/2/3 projects remain readable; v1.6 writes schema 5.

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

## v1.4 maker library and ICSP metadata

See [Maker Parts](MAKER_PARTS.md). Native schema 5 retains the schema-3 support for embedded variant/source/pin metadata and optional ICSP contacts. Older versions do not apply the new internal-terminal conflict checks or ICSP edit rules. KiCad geometry export does not preserve catalog identity, named-pin captions, internal-group checks or compound ICSP behavior; its dialog warns before export. Generic/reference body models are not mechanical collision checks, and named parts are not complete electrical reference circuits.


## v1.7 additions

Project schema remains 5. Selection filters, edit ghosts and navigation do not
serialize. Accepted edits serialize as ordinary parts, traces, vias and mark
properties; supported KiCad geometry export continues using those objects.
`manufacturing-manifest.json` is review metadata, not an editable PCB file. It is
ignored as a native-project candidate when opening a Gerber/drill ZIP.
The two-copy storage-recovery bundle is likewise an archive envelope; extract
its `currentBoard` value as JSON to import that board. `storedRaw` retains the
other record without guessing how to repair invalid data. New browser controls
do not change the existing restricted KiCad/footprint interchange boundaries.

## CaseBench JSON (v1.7.1)

Dedicated export emits native CopperBench schema 5 with explicit millimetres,
not a newly invented mechanical schema. Existing schema-5-capable CaseBench
imports are the target. The exported snapshot retains raw local footprints and
world part placements so the target importer performs its transform exactly once.
Early CaseBench builds that reject schema 5 must be updated; do not edit the schema
number by hand. Export preflight follows the retrieved adapter 2.0.1 bounds:
8 MiB JSON, 512 placed parts, 8192 pads, 1024 standalone holes, 128 cutouts,
512 vertices per custom outline/cutout. These are known bounds, not a substitute
for the target's full validation. End-to-end target execution is unverified.
