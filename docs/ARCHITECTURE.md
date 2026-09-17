# Architecture — v1.1.0

## One model, three views

`src/core.js` owns a schema-2 document, with explicit schema-1 migration on read. Coordinates are millimetres quantized to 0.0001 mm, represented as JavaScript numbers. This is a quantized floating-point model, **not** an integer-only exact-geometry kernel. Gerber writing uses a 0.000001 mm output grid; finer output notation does not add information to the native model.

A component owns its exact local pads and a separate representative body. Position, rotation and face determine world pad geometry. Pin identity does not change on rotation/flip. The renderer never supplies authoritative manufacturing coordinates.

Nets express intention. Pads, traces, vias and filled zones express physical copper. Removing copper preserves net assignment. Connectivity is recalculated from touching copper and plated transitions, not inferred from a line's net label alone. Different-face surface pads remain separate until a valid through connection joins them.

## Modules

| File | Responsibility |
|---|---|
| `core.js` | Model, native validation, embedded generic parts, transforms, nets, snapshots, example documents. |
| `geometry.js` | Contours, distances, copper primitives, spatial indexing, connectivity, findings and routing clearances. |
| `platforms.js` | Nominal platform interface library, template factories, linked mounting holes, signal aliases, metadata validation and review findings. |
| `font.js` | Original geometric stroke alphabet and transformed silkscreen primitives. |
| `router.js` | Selected-connection routing and conservative connected-cell copper fills. |
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
