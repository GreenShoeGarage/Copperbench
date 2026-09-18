# Vias — COPPERBENCH v1.2.0

A through via joins copper on the top and bottom of this two-layer board. The
editor represents its two copper pads and single plated drill explicitly. A
mounting hole is a different object and is not an electrical connection.

## Place a via without drawing a trace

Choose **＋ Via** in the context bar beside the trace-width control, the concentric-circle Via tool in the
left rail, **Nets → Place via**, or **Shift+V**. This opens placement controls in
the inspector. Set a net, copper-pad diameter, drill diameter and mask setting.
The fields use millimetres even when workspace distance display is set to mil.

Click the board to place a via. The tool stays active for repeated placement;
press **Esc** when finished. Placing on a trace snaps to the actual trace center,
not merely the nearest board grid point. Clicking an existing via selects it
instead of adding a duplicate hole.

**Auto / from touching copper** inspects both layers for a net. Two different
nets beneath a proposed via are a conflict, not permission to short them.
Unassigned copper is an obstacle, not one implicit shared net. Use an explicit
net in empty areas, or create one from the placement inspector. An unassigned
via is saved and editable but is flagged as a blocking design error.

The preview displays the copper disk, drill and clearance halo. Red means the
proposal was rejected; the reason is shown. No geometry is committed on rejection.
Checks include minimum drill, annular ring, edge/cutout clearance, both-layer
copper and keepouts, mounting holes, and drill-to-drill spacing including same-net
plated holes. These checks do not certify every possible manufacturing condition.

## Continue a route onto the other face

Start **Trace** from a lead, via or existing trace. Move the pointer to the desired
transition. Press **V** to insert the via there. Alternatively, click the visible
**Via → other side** button (or Via tool) while routing and click the transition
point. The current trace width and the inspector's via defaults are used.

The incoming trace and via commit together as one undoable action. The editing
side switches and the route continues from the via. Click the destination lead,
via or trace to finish. A blocked via does not place a partial trace or change
the editing side. Existing nets are not silently merged; conflicting endpoint
assignments need explicit confirmation.

This is manual routing through existing vias. The selected-pin automatic router
continues to use component leads as its selectable endpoints; it may insert its
own through vias. It now uses the chosen mask-tenting default and checks drill
spacing before layer transitions. Full-board via stitching is not included.

## Dimensions and solder mask

| Preset | Pad diameter | Drill diameter | Nominal annular ring |
|---|---:|---:|---:|
| Compact | 0.70 mm | 0.30 mm | 0.20 mm |
| Standard | 0.90 mm | 0.40 mm | 0.25 mm |
| Large | 1.20 mm | 0.60 mm | 0.30 mm |

The ring is `(pad diameter − drill diameter) / 2`. The selected profile remains
authoritative, so a preset can be invalid under a stricter custom profile. An
inspector edit does not automatically change default sizes for future vias;
**Use these sizes** does that explicitly. These dimensions are not current ratings.

**Tent both sides** controls file geometry: omit the via's mask opening on both
faces. Unchecked means create openings using the project's mask expansion.
Neither selection changes the copper or plated drill. Tenting does not fill the
hole and does not guarantee the manufacturer's finished mask bridges it. Separate
top/bottom tenting, filled/capped vias and blind/buried vias are outside this release.

The project's existing manufacturer profile and current service capability must
be reviewed before ordering. Manufacturer reference: [OSH Park two-layer service](https://docs.oshpark.com/services/two-layer/)
and [drill specification](https://docs.oshpark.com/submitting-orders/drill-specs/),
reviewed 17 September 2026. Refer to the manufacturer's actual upload preview.

## Edit, find and remove

Use **Select**, then click the via. Via picking takes priority over a trace vertex
at the same point. The inspector exposes X/Y, net, pad/drill sizes, mask coverage,
locking, duplication, deletion and **Start trace here**. **Manage vias** lists all
vias with their net, coordinates, dimensions and state; selecting a row opens the
same inspector. Clear a lock before changing the via.

Moving or deleting a via leaves the attached copper where it was. The connection
checker exposes the resulting break; use undo or reroute. This is not elastic or
push-and-shove routing. Illegal drag, coordinate or arrow-key moves are rolled
back. Copper-affecting changes invalidate fills, requiring refill before export.

## Save and manufacture

Native JSON and project ZIP retain each via's position, net, pad/drill diameters,
mask state and lock, plus placement defaults. v1.3 saves schema 3 and reads
schema-1/2 designs; missing optional tenting defaults become false. Older apps
reject schema-3 saves rather than discard managed-plane behavior. Keep backups
before upgrading; see [PLANES.md](PLANES.md).

Gerber export contains via copper on both layers. Excellon contains one plated
hole per via; it is not duplicated as NPTH or mirrored on the bottom. Fabrication
view reads these actual generated files. Open and tented mask outputs are tested
separately with an independent Python/Shapely reader.

KiCad subset import/export preserves through-via center, pad diameter, drill
size and net geometry only. Per-via tenting and locking are not preserved; imported
vias use open masks. The export confirmation and import report disclose this.
Use native JSON as the editable master and review any KiCad-derived output.

## Evidence and boundaries

See [TESTING.md](TESTING.md) for executed counts and retained raw evidence. Browser
tests use real Chromium UI/canvas/workers, simulated storage and inspected download
blobs. They are not hosted offline/cache, actual browser save-dialog, Safari,
Firefox or mobile-hardware certification. No external CAM, OSH Park upload,
physical fabrication, electrical or thermal test was performed for this release.
