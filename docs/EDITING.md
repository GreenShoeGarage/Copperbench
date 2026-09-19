# Editing and export review — v1.7

All 193 existing parts, six circuit blocks, controller/module interfaces, planes,
vias, compact printed polarity and camera controls remain available. Native
projects still use schema 5. This release changes how you edit a board; it does
not add more layers, simulate circuits or introduce a runtime network dependency.

## Pick the intended object

The compact selector at the bottom of the workbench limits selection to **All
objects**, **Parts**, **Copper**, **Markings**, or **Board features**. Copper includes
pads as well as traces and vias, so you can still start at an actual terminal.
Markings includes standalone artwork and the printed reference/polarity groups
attached to each component. Board features includes holes, cutouts, keepouts and
zones. Drawing tools retain their own pad/trace picking rules.

Click a crowded location, then press **]** or the overlapping-object button beside
the filter to cycle through the candidates at that location. This avoids deleting
or hiding a part simply to reach a trace beneath it. Selection filters do not
hide layers or change manufacturing output. Box selection follows the active
filter; a trace is included when all its points lie within the selection box.

## Edit copper directly

Select a trace in Copper view. The inspector provides a segment selector, width
scope, connected-copper selection, corner insertion/removal, section replacement
and cleanup. Lower-level net/layer/coordinate fields remain under a closed
**Net, layer & coordinates** section.

Drag a trace segment to slide it sideways. A first or last segment receives
end doglegs so its original endpoints stay fixed. Drag an existing corner handle
to reposition that point. Use **Insert corner** to create a handle anywhere on a
selected segment; a collinear handle is deliberately retained for later editing.
**Remove corner** protects endpoints. **Replace section** fixes the chosen endpoints
and accepts intermediate `x,y` waypoints in millimetres (one per line); leaving
that list empty proposes a direct connection.

**Clean up** removes repeated points and forward collinear points. It does not
erase a reversing/folded path merely because three points are collinear.

Every operation is a proposal on a copy of the document. During a gesture, the
outline is an unchecked ghost; release runs the checks. A valid proposal appears
with **Keep edit / Cancel**. The existing route is muted/dashed and the proposed
route is bright. Only **Keep edit** changes the board. Escape cancels. With focus
on the canvas, Enter accepts a pending edit. Accepting is one undo transaction.
A later document change invalidates the proposal instead of overwriting newer work.
Undo or a concurrent command cancels an unfinished preview-only drag without
restoring its earlier document over the newer revision. Cancelling a staged
edit also resumes automatic managed-plane refilling when needed.

The geometry engine checks affected hard copper, board edges, holes and keepouts
and preserves the existing hard-copper connection groups. An edit that loses a
branch or pad attachment is rejected, even if the net name still matches. It does
not shove other routes aside. Existing unrelated design findings are not treated
as permission to create a new problem. Pours are invalidated after accepted copper
changes and must be refilled; plane-based connections are checked after refill.

### Width scopes

| Scope | Affected geometry |
| --- | --- |
| Selected segment | Splits the trace as needed; only the chosen segment changes width. |
| This trace | All segments of this stored polyline. |
| Touching traces & vias | Trace widths in the physically touching copper group; vias keep their diameters. |
| All traces on this net | Every assigned trace on that net, including disconnected pieces. |

A locked trace anywhere in the selected scope blocks the change rather than being
silently skipped. Segment splitting preserves circuit-block membership. Physically
connected selection follows traces/vias, not airwires or copper pours; it also does
not cross an otherwise disconnected gap through a component pad. An explicit
whole-net scope is separate. An unassigned route cannot use whole-net width.

## Move a part or via with its connections

Turn on **Drag connected** beside the selection filter, then drag one component
or via. Its attachment proposal is checked on release and waits for **Keep edit**.
Alternatively, select the object and use **Drag connected…** in the inspector to
enter an exact target position. Ordinary movement remains available with the
switch off; it does not silently repair unselected traces.

The first version supports one unlocked component or via, with traces attached
at the exact centres of its pads/endpoints. Trace identities, layers, widths, pin
numbers and net assignments are retained. For multi-segment traces the existing
interior route is retained and the moved end legs are rerouted on the same layer.
No new vias or layer changes are invented. Via movement can update both top and
bottom trace attachments in the same transaction.

**Explicit limits:** locked attached traces, off-centre/through-middle terminal
contacts, interior junctions at the moved terminal and more than 24 attached
routes are not supported. If any moved terminal shares a net and compatible layer
with a copper pour, the operation is conservatively rejected, even when that
specific pad has no direct pour contact. Use ordinary Move and then refill/reconnect
that plane. The search is local, finite and non-exhaustive: failure does not prove
that a legal route cannot exist. This is not a full push-and-shove router. Connected
drag applies to these drag/position operations, not rotation, flipping or ordinary
keyboard nudging. Multi-object and block transforms keep their existing behavior.

## Position printed reference and polarity marks

Select a component and choose **Position marks**. Switch between **Reference** and
**Polarity**, then drag the marking's selected outline. Its local offset changes;
the component, pads, leads and nets stay unchanged. A group includes all of that
component's polarity symbols, preserving their relative pin association.

The compact inspector exposes print visibility, local X/Y offset and print
height. Local offsets rotate and mirror with the component. Height is a physical
silkscreen measurement, not the contextual screen-tag size. Locked parts require
unlocking before moving their markings. Pin roles themselves remain in the
existing **Polarity & pin roles** dialog; unknown roles are not inferred.

Inspect **Fabrication → Top silk only / Bottom silk only** after positioning marks.
The markup comes from the same physical text/stroke geometry used by the exporter,
not a decorative screen label. The redesigned small A/K and +/− tags are retained.

## Review the actual export package

**Export board** captures a design snapshot and displays board dimensions, copper
layer count, plated/non-plated drill counts, slots and the session revision. The
app reads the generated Gerber and Excellon text, checks required files and outline
bounds, and compares drill count, diameter and coordinates to that snapshot.
A missing required layer or a demonstrable content mismatch cannot be bypassed
with diagnostic export. Stale/unfilled zones still block all manufacturing exports.

Each silkscreen face reports source strokes/shapes and sampled ink retention after
clear operations. Source artwork with no dark export geometry is an error. If no
sampled points survive on a face that has artwork, review must be acknowledged
before download. Partial clipping is shown for inspection, not treated as a proof
of poor print quality. Intended clipping at openings or board edges can be valid.

**Sampling is not exact ink area.** It samples stroke centrelines and interior
points, does not prove minimum printed line width, and can miss small defects.
Overlapping artwork can make a sample appear present even if its individual mark
is absent. Both the generator and this browser readback are maintained in the same
codebase; this check is not independent CAM validation.

The ZIP includes `manufacturing-manifest.json`: design identity/update time,
session revision, file inventory, design-finding counts, sampled silk results and
explicit qualification boundaries. The file contains no account or telemetry
information. Download remains tied to the reviewed snapshot; a design change
requires opening review again. A manufacturing ZIP with this manifest remains
importable as read-only Gerber/drill artwork, not an editable native project.

## Autosave safeguards

Autosave compares the stored raw record with the last version this tab read/wrote.
Unreadable startup data and detected changes by another tab pause autosave rather
than overwrite that record. Quota errors leave the previous saved copy intact.
The open board can still be downloaded through **Save JSON**.

Use **Log → Recovery snapshots** to resolve a paused save. Download the recovery
bundle containing the open native board and the other raw saved copy. Only after
confirming the download, choose **Replace local autosave**. A further change to
the stored copy cancels replacement until you download the copies again. The bundle
is an archive envelope, not a directly importable board: its `currentBoard` value
is a native project and `storedRaw` retains the other record exactly as read.

This is conservative conflict detection, not transactional multi-user storage or
collaboration. Browser persistence can still fail or be cleared. Keep independent
JSON backups. Native browser/file-origin qualification is documented separately;
the injected-storage tests do not establish real-origin reliability.

## Updating

Save JSON before replacing the complete hosted app folder or portable HTML.
v1.7 reads and writes schema 5, with no migration required for v1.6 projects.
Older versions will not have the new edit controls or package-review UI. Already
downloaded Gerbers are unchanged; regenerate them after approving your edits.

[Qualification and reproduction](QUALIFICATION.md) · [Executed results](TESTING.md)
