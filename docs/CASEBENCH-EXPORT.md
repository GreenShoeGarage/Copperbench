# CopperBench → CaseBench board JSON

## Use it

1. Finish or cancel any active placement, trace, automatic route or connected edit.
2. Click **▾ next to Export board → CaseBench JSON**. The same action is in
   **Board → CaseBench JSON**, the manufacturing dialog, and mobile **Project files**.
3. Check the board dimensions, face counts and hole summary. Click
   **Download CaseBench JSON** and import that file as a CopperBench board in CaseBench.

The name is `<board-title>-casebench.json`. The file stays on your device. Camera
pan, zoom, view face and a mil display preference never change its physical units.
An unrouted board or unfilled ground plane can be exported before fabrication is ready.
If a pending edit exists, finish/cancel it rather than exporting an ambiguous state.
A changed revision invalidates the open export review.

## What the JSON contains

This is the native **COPPERBENCH schema 5** project structure with **units: mm**.
It is not a `CASEBENCH` saved enclosure project or a `CASEBENCH-MECHANICAL` file.
No extra coordinate system or duplicate flat components/holes list is introduced.

| Native field | Mechanical information retained |
|---|---|
| `board` | Rectangle/rounded rectangle/ellipse/custom polygon, original datum and points, thickness |
| `parts` | Stable IDs and references, raw x/y, rotation and board face, representative body w/h/z |
| `parts[].pads` | Exact local positions/shapes, drill and slot geometry, pin identity |
| `parts[].mountingHoles` | Active local mounting holes; not duplicated into root holes |
| `parts[].module`, `carrier`, `platform` | Existing reference, stack/gap, active keepout and fit metadata |
| `holes`, `cutouts`, `vias` | Standalone holes/slots, native cutout polygons and via drills |
| `blockInstances` | Group provenance with already-positioned native components and copper |
| Native copper/nets, assumptions/evidence | Kept without re-routing or modifying the design |

Unused mounting-hole patterns stay reference metadata; they do not become new holes.
Hiding a host model does not delete its envelope. Through-hole pads and vias remain
plated drills, not automatic screw or standoff locations.

### Default versus project extras

Default **board snapshot** clears `art`, `assets`, `baseline`, and `blockLibrary`.
These contain non-mechanical artwork/images, an old comparison snapshot and unused
reusable circuit templates. All placed parts keep their embedded footprints.
**File contents & options → Include project extras** retains these records.
The default snapshot is not a full project backup; keep the ordinary **Save JSON**
backup for further PCB artwork/library work. No data is removed from the open project.

### Coordinates: apply once

Native board-space X points right, Y down in the source top view. A part's local
X is mirrored when its `side` is `bottom`, then rotated by its clockwise angle and
translated by x/y. Export leaves these native values alone. CaseBench owns the
conversion into its enclosure XYZ axes, including reversing native Y and placing
bottom components below the PCB. The active viewport never becomes a file transform.

Do not apply a block's transform to its members again: members are already positioned.
`body.h` is body depth; `body.z` is the representative height. Module body.z already
includes its modeled stack. Export does not add `module.stackGap` a second time or
pretend a representative package mesh is a measured clearance envelope.

## Limits and qualification

Known adapter bounds are preflighted: JSON 8 MiB; parts 512; component pads 8192;
standalone holes 1024; cutouts 128; custom outline/cutout vertices 512 each. The
UTF-8 byte count is checked before downloading. No oversized geometry is truncated
or simplified silently. Turning off project extras may help a large image-heavy file.
Invalid/self-crossing boundaries are rejected. Off-board part centres are reported
but preserved, since overhanging connectors may be intentional.

The existing CaseBench native importer supports schemas 1–5; old builds that stop
at schema 3 need updating. Never change a schema number to force acceptance.
The exact full target app was not locally available for an end-to-end import run.
The tests verify the exported native structure, raw geometry, body heights, active
hole identities, templates and browser controls; they do not qualify the enclosure fit.

Measure actual components, sockets, connector access, fastener sizes and installed
heights in CaseBench before fabricating an enclosure. Existing CaseBench measurements
and fit evidence should remain there; an export is not an automatic replacement of them.

## Developer tests

```sh
npm run test:casebench
# Optional real local navigation/persistence gate, when the environment permits it:
npm run test:native
```

See [the verification record](TESTING.md) for executed tests and boundaries.
