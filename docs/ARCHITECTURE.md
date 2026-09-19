# Architecture — v1.6.0

## One model, three views

`src/core.js` owns a schema-5 document, with explicit schema-1/2/3/4 migration on read. Coordinates are millimetres quantized to 0.0001 mm, represented as JavaScript numbers. This is a quantized floating-point model, **not** an integer-only exact-geometry kernel. Gerber writing uses a 0.000001 mm output grid; finer output notation does not add information to the native model.

A component owns its exact local pads and a separate representative body. Position, rotation and face determine world pad geometry. Pin identity does not change on rotation/flip. The renderer never supplies authoritative manufacturing coordinates.

Nets express intention. Pads, traces, vias and filled zones express physical copper. Removing copper preserves net assignment. Connectivity is recalculated from touching copper and plated transitions, not inferred from a line's net label alone. Different-face surface pads remain separate until a valid through connection joins them.

## Modules

| File | Responsibility |
|---|---|
| `core.js` | Model, native validation, embedded generic parts, transforms, nets, snapshots, example documents. |
| `geometry.js` | Contours, distances, copper primitives, spatial indexing, connectivity, findings and routing clearances. |
| `vias.js` | Pure through-via proposals, net inference, both-face copper/edge/hole validation, guarded add/edit, size presets and trace-center snapping. |
| `platforms.js` | Nominal platform interface library, template factories, linked mounting holes, signal aliases, metadata validation and review findings. |
| `maker-parts.js` | Maker catalog, named terminal functions, internal-terminal conflicts and optional Uno ICSP. |
| `carriers.js` | Controller mating interfaces, attached antenna copper guards, access projections and source metadata. |
| `modules.js` | Vendor/revision-specific module interfaces, optional mounting holes, reference metadata and nominal gap findings. |
| `block-catalog.js` | Bundled, reproducibly generated routed starter circuits; no runtime request. |
| `blocks.js` | Validated reusable templates, fresh-net insertion/copy, explicit ports, group transforms, membership and project-local library. |
| `modules-renderer.js` | Reference-only 3D module bodies and editable-block placement overlays. |
| `font.js` | Original geometric stroke alphabet and transformed silkscreen primitives. |
| `router.js` | Selected-connection routing and conservative connected-cell copper fills. |
| `planes.js` | Managed per-face zones, outline sync, real-region status/findings and pure all-or-nothing lead attachments. |
| `manufacturing.js` | Gerber/Excellon writers, strict generated-file readers, BOM and SVG. |
| `interchange.js` | Bounded KiCad parsing/writing with explicit failure/report paths. |
| `renderer.js` | Projection/picking, 3D representative bodies, software depth rasterizer, Copper view and parsed-file Fabrication view. |
| `app.js` | Commands, dialogs, placement, tools, imports/exports, storage, undo, workers and interface state. |
| `worker-entry.js` | Worker message entry point for checks, routing and fills. |
| `worker-source.js` | Generated embedded worker source. Rebuild with `tools/package.py`. |

## Rendering

Canvas2D handles the board plane, copper overlays, drafting and UI geometry. Component bodies are actual generated 3D meshes transformed by the view camera and software-rasterized with a depth buffer. This avoids a WebGL dependency and the incorrect occlusion of a simple average-depth painter. It is not a photorealistic renderer or external CAD-model importer.

Bench supports orthographic tilt/orbit and unprojects pointer picks to the board plane. Copper keeps the editing surface unobstructed. Fabrication consumes objects parsed from generated file text. The views share a model, not separate editable copies.

## Routing and fill boundaries

A direct route is tried before two-layer, eight-direction A*. Obstacles incorporate copper clearance, board boundaries, holes, cutouts and keepouts. Via transitions are explicit physical through vias. Proposed segments are checked before acceptance. Routing can fail; it does not force illegal copper or promise global optimality. Already connected selected pins are not given redundant routes.

Copper fills occupy conservative rule-checked cells. Connected seed cells come from actual net copper; disconnected islands are removed. Thermal reliefs introduce permitted spoke cells. Horizontal runs become explicit vector rectangles used identically by checks, rendering and export. Grid-based stair steps and resolution dependence are real tradeoffs, disclosed in the UI. This is not a general-purpose polygon boolean engine.

Circular curves and some distance calculations use polygonal approximations/tolerances. The test suite addresses known edge, gap, drill and collision cases, but it does not prove all possible geometry. Manufacturer tool accessibility, detailed courtyard/mechanical checks, RF behavior and circuit function remain outside the checker.

## State, storage and cancellation

All mutations pass document validation and enter undo history. Copper-affecting edits invalidate fills and background results. Worker results carry revision context; cancellation terminates the job so stale results cannot overwrite newer work. Downloadable JSON remains independent of browser storage. A saved-state failure is visible. Imports review the document before replacement, with undo as another recovery path.

The static edition bundles dependencies and registers a same-origin service worker where permitted. The portable edition embeds everything and does not register a service worker. No database, API key, account, analytics, model download or telemetry endpoint exists.

## Trust boundary

Manufacturing generation consumes the canonical model only. Its own read-back is useful but correlated with the writer. The separate Python/Shapely golden-coupon regression reconstructs expected geometry without importing application JavaScript. Neither replaces an external CAM inspection, manufacturer preview, datasheet review or a physical build.

## Platform interfaces and linked holes

A platform is a real component with ordinary plated pads and additional
`mountingHoles` in local footprint coordinates. `C.mountingHoles()` transforms
those into the common top-view coordinate system; `G.holes()` includes them in
DRC, routing obstacles, render inspection, masks and Excellon output. They are
not part of `C.pads()` and cannot become electrical nets.

`platform.outline`, reference bodies and on-screen pin captions are visual only.
The add-on library variant stores mirrored local X coordinates and starts on the
bottom face; the carrier variant is top-mounted with unmirrored local X. Both
therefore share the same initial top-view contact coordinates. Ordinary later
rotation/flip operations use the existing transform and preserve pin identity.

Schema 2 deliberately makes old v1.0 readers reject new files: ignoring unknown
mounting-hole fields would be unsafe. Schema-1 imports are cloned and migrated
in memory; the original file is not overwritten. Native schema 2 embeds all
placed geometry, so future library changes cannot silently move saved pins.

The platform module runs in the worker too. Reference warning findings do not
substitute for a physical clearance solver or electrical rule checker.

## Via transactions

`CB.V.propose()` never changes the document. It derives the net from touching
copper on either face or an explicit choice, validates pad/drill/ring values,
checks both-layer clearance and all hole spacing, then returns an accepted
through-via object or an actionable rejection. Unassigned copper is an obstacle.
The UI commits only accepted proposals and rolls back invalid edits.

Manual layer transitions validate the draft incoming trace and proposed via
before one shared undo transaction. The editor then starts the next route on the
opposite face. Existing copper is never stretched implicitly when a via moves.
The renderer prioritizes via picks above traces and their vertex handles.

## Managed planes and derived fills

Schema 3 adds the `boardPlane` zone marker and `settings.autoPlanes`. All managed
geometry remains ordinary zone copper at export time. Outline synchronization
runs during commits/import/fill. Manual zones have fill priority. Routing ignores
old managed fills as obstacles but never ignores hard copper: the next fill
carves the corresponding different-net clearances.

Automatic refill is a separately cancellable worker with revision gating,
coalesced after edits and paused during active draws/proposals. Applied fills
are derived state, not separate undo commands. Ordinary user edits remain
transactional. `zoneGroups` and per-rectangle `zoneRoots` expose actual electrical
components for plane status, rather than treating a zone ID as one conductor.

`planConnections` works on a clone, rejects conflicting nets and selected-lead
hard-copper violations, then tries existing contact, local routes/existing vias,
or offset through-via candidates. Every successful attachment is rechecked after
fill; multi-lead plans are rechecked as a whole. UI acceptance commits the full
proposal once. Native managed-plane semantics are not KiCad round-trip metadata.

## v1.3.1 terminal roles and legend compositing

`core.js` owns explicit polarity roles, legacy-safe role inference and physical
symbol anchors. `font.js` turns print-enabled symbols into normal source strokes.
`renderer.js` adds independent clickable editor badges. `app.js` edits roles and
printing options without changing electrical intent. Native schema remains 3.

`manufacturing.js` clips silk using a horizontal sweep of simple outline edges,
emitting single-contour exterior regions. Gerber region contours combine by union;
the Canvas interpreter composites each contour accordingly, and the separate
Python oracle uses union rather than symmetric difference. Negative old-frame
fixtures guard against reinstating the exporter and reader's former shared bug.

## v1.4 catalog module

`src/maker-parts.js` loads after platforms in both the browser and the embedded worker. It appends immutable-on-placement catalog definitions, validates metadata, adds conservative internal-group conflict findings, exposes label editing and manages optional appended ICSP contacts. Functional captions belong to the renderer, not the manufacturing geometry. `catalog` schema 1 and `platform.icsp` live inside the native schema-3 project; footprint placement deep-copies definitions. All maker data and bodies are bundled locally. No runtime library fetch or cloud catalog is required.

## v1.5 attached carrier geometry

`src/carriers.js` extends the family registry without replacing existing records.
It runs in both the window and worker. `CB.keepouts(doc)` is the shared accessor
for ordinary keepouts plus enabled part-local antenna rectangles transformed by
`CB.world`. Geometry obstacles, DRC, standalone via proposals, zone fill and
KiCad export use it. Access rectangles remain advisory. JSON schema 4 prevents
older readers from accepting constraints they do not understand. All placed
carrier data is embedded; live catalog changes cannot alter it.


## v1.6 modules and reusable circuit blocks

The five new module entries are ordinary components: their mating pads and enabled
mounting holes are manufacturing geometry. The source module's circuit, artwork,
body, displayed terminal captions and underside-gap illustration are not copied
to carrier Gerbers. The OLED uses a display-face reference transform rather than
silently relabeling the supplier's numbered header. Header/drill decisions and
body envelopes remain nominal and require comparison with the purchased assembly.

The `COPPERBENCH-BLOCK` schema-1 format contains embedded parts, traces, vias,
net definitions, named external ports and review notes. `blocks.js` stages every
insertion in a clone, remaps IDs and nets, and validates before changing the
working document. No net-name matching is performed. Only explicitly selected
external-port mappings share a project net. Placement preflight rejects new
physical copper violations; intentionally missing routes remain normal DRC
findings instead of making copper-free block insertion impossible.

Native schema 5 adds `blockInstances` and `blockLibrary`. Membership records
reference ordinary objects rather than creating another authoritative geometry
model. Copies capture current edited geometry and allocate fresh nets. Whole-block
transforms apply the same translation/rotation/reflection to parts, copper and
vias; independent edits remain possible. External attached routes are never
silently stretched. Explicit whole-net merges update port records. Deleted members
are pruned; detaching membership leaves geometry unchanged.

The standalone exchange subset deliberately rejects standalone artwork, zones,
board cutouts/holes, keepouts and image assets rather than silently discarding them.
Part-attached holes/keepouts stay inside embedded components. Personal templates
are project-local and included in native backups; there is no remote catalog or
implicit update of saved components. KiCad output keeps supported ordinary
geometry, but not block grouping, the personal library or module fit metadata.

`tools/build_blocks.js` regenerates the six bundled circuit starters and checks
routing. It is a development tool, not a runtime dependency. A packaging test
rebuilds the catalog in a temporary tree and compares bytes. Source/portable and
worker execution share module and block validation; the renderer extension runs
only in the UI.

## v1.6.2 compact terminal annotation

`core.js` supplies small default silk settings and pin-ordered multi-terminal
mark positions. `font.js` includes owner/pad/role metadata on derived polarity
strokes; exporters still receive ordinary line geometry. These tags are not
new persistent fields. The document schema stays at 5.

`renderer.js` shows physical silk while idle, and fixed 9-pixel context pin tags
while selecting/hovering/routing. Screen-space exclusion bounds include actual
projected body height and visible pads. Printable size/offsets never affect tag
type size. A lack of clear screen space omits a tag rather than covering a body.
`app.js` provides the existing role editor plus direct print visibility and compact
print defaults, all undoable and independent of electrical/copper edits.


## v1.7 edit proposals and export review

`editing.js` is a DOM-independent proposal engine. It clones the document, preserves
hard-copper connection groups, checks relevant physical violations and returns a
candidate. `edit-renderer.js` performs filtered/overlap picking and draws ghosts;
none of these view objects enter the native project. The shell accepts only a
proposal whose revision and original document snapshot still match. Connected
moves invoke same-layer routing for moved endpoints; legacy ordinary moves retain
their explicit disconnect-and-review behavior. Width splitting updates block
membership. Printed mark offsets are local to the component transform.

`export-review.js` reads generated text, checks file/outline/drill invariants and
samples composited ink. It intentionally does not claim independently developed
CAM validation or exact-area/printability analysis. The export dialog freezes a
snapshot and includes review metadata in the manufacturing ZIP. The import path
distinguishes that manifest from a native project. Local saving adds a raw-record
comparison and explicit resolution, not a transactional storage engine.

[Implementation behavior and limits](EDITING.md) · [Qualification](QUALIFICATION.md)

## v1.7.1 native CaseBench handoff

`src/casebench-export.js` prepares a validated clone of the native project. The
output root remains `COPPERBENCH` schema 5, with explicit `units: "mm"`;
`CASEBENCH-MECHANICAL` is **not** the output format. Part pads and mounting holes
stay local, and part x/y/rotation/side remain unchanged. Placed circuit-block
members are not transformed again. No derived body/envelope replaces the native
body, and module stackGap is not added to body.z.

Geometry-derived summary counts are UI-only. The export does not append flattened
holes or a second components list to the file. Board-only mode clears art/assets,
baseline and the unused block library; project-extras mode retains the full native
snapshot. `Save JSON` is unchanged. Export neither mutates the editor nor writes
its autosave. UI guards block pending geometry and a changed revision at download.
Native schema/units and mechanical limits are preflighted; fabrication DRC is not
an enclosure-export gate. The CaseBench importer itself remains external.
