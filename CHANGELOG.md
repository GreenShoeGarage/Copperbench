# Changelog

## 1.3.1 — Polarity labels and repaired silkscreen export — 2026-09-17

Fixed the nested clear-region frame that could erase the complete top/bottom
silkscreen in a conforming Gerber reader. The writer now emits single-contour
exterior trapezoids and bounds them around all artwork. Fixed the Fabrication
viewer and Python test reader to union region contours, not XOR them. Added
mandatory negative regressions reproducing the old blank layer and positive
checks retaining source artwork while clearing board edges, masks and holes.
Regenerated the bundled golden manufacturing example with the corrected writer.

Added explicit anode/cathode roles for built-in diodes and LEDs, positive/negative
roles for polarized capacitors, legible selectable pin badges, inspector/tooltip/
pin-table names, and a per-part role/printing dialog. A/K and +/− vector marks
print on the component face, independent of its reference-label visibility.
Rotation, flipping, native save/import and undo preserve pin identity and nets.
Custom and imported numeric roles are explicit, not guessed. Native schema stays 3.

Added Top silk only / Bottom silk only views and source-marking counts in the
export dialog. Re-export existing manufacturing ZIPs before ordering. The old
preview and test-reader flaw means historical test passes did not establish
silkscreen correctness. No external CAM or manufacturer acceptance is claimed.

## 1.3.0 — Easy power and ground planes — 2026-09-17

Added a Planes panel with independent per-face net assignments, bottom-ground
and dual-ground presets, whole-board outline following and automatic refill.
Manual zones keep priority. Trace/via edits can carve clearance through managed
pours; actual-geometry checks expose any split copper regions.

Added checked lead attachments: direct pad contact, short routes to existing
vias, or short stub/new-via proposals for opposite-side SMT leads. Conflicting
nets and hard-copper violations are rejected. Preview/accept/discard, picked
multi-lead groups, context and inspector pin actions, cancellation and one-step
undo preserve explicit circuit intent. Keyboard Enter/Space now activate focused
buttons instead of being intercepted by canvas drawing shortcuts.

Native saves use schema 3; schema-1/2 imports migrate without changing source
files. KiCad exchange preserves ordinary zone geometry, not automatic plane
semantics. Added engine, Chromium and independent manufacturing geometry checks.
No external CAM/manufacturer acceptance or physical fabrication is claimed.


## 1.2.0 — Visible, editable through vias — 2026-09-17

Added standalone repeat-placement via tools, a labelled context-bar button,
Shift+V, net selection/inheritance, size presets, exact pad/drill controls,
annular-ring feedback, both-side mask tenting and a management table
for selecting existing vias. Via positions, nets, sizes and locks are editable.

Manual traces now start/end on vias and existing copper. A routing layer change
commits the incoming trace and through via as one undoable action, then continues
on the opposite face. Failed placement rolls back without partial copper. Via
picking takes priority over overlapping trace endpoints. Dialog focus is set
synchronously so a delayed focus callback cannot redirect fast input.

New pure via proposals check both faces, board edges/cutouts, keepouts and all
drill spacing. Automatic routing uses tenting defaults and extra drill checks.
KiCad exchange now explicitly warns that per-via tenting/locks are not preserved.
Native JSON retains schema 2 and preserves full via data. Gerber/Excellon tests
cover both copper layers, a single plated drill, and mask-open/tented variants.

Added 27 via engine tests, 21 via browser tests and 7 independent output checks.
All existing suites remain in CI. No manufacturer upload or physical test is claimed.


## 1.1.0 — HATs, shields and carriers — 2026-09-17

Added Raspberry Pi 40-pin, Arduino Uno R3 and Arduino MKR 28-pin mating interfaces,
with add-on and carrier library variants and a new blank-board template workflow.
Preserved exact nominal contact positions, named signals, Uno header offset,
linked optional mounting holes, pin-map CSV, and reference-only host visuals.

Schema 2 prevents old readers silently omitting component-linked NPTH geometry;
schema-1 projects migrate on read. Gerber, drill, mask and KiCad export include
real linked holes. Metadata and aliases remain lossless in native JSON only.

Added 23 platform engine tests, 13 browser interaction tests and 12 independent
Python export checks. Existing suites remain in CI. Physical fit/fabrication,
external CAM and hosted/offline browser lifecycle are not verified.


## 1.0.0 — GitHub repository packaging revision — 2026-09-17

The application remains version 1.0.0. This revision packages the supplied release
for source control and repeatable verification; it is not a new PCB feature release.

Added GitHub CI, opt-in Pages deployment, tag-triggered draft releases, issue and
pull-request templates, dependency update configuration, contribution/security
guides, development dependency pins, a lockfile, integrity checks, deterministic
release ZIPs and checksums. The illustrated README and original license notices
are retained.

Removed the browser test's hard-coded executable requirement. Test results,
generated fixtures and test screenshots now go to ignored output directories
instead of rewriting the release examples and documentation images. Original
v1.0.0 test evidence is retained separately.

The optional packaging command now derives the service-worker cache revision
from application contents and scopes cache ownership to the deployment path.
It includes a non-writing `--check` mode. No PCB model, geometry, rendering,
routing, importer or manufacturing-exporter source logic was changed.

## 1.0.0 — Initial application release — 2026-09-17

Two-layer physical PCB workbench, generic parts, manual/assisted routing, board
geometry, copper zones, silkscreen tools, native project backups, Gerber/Excellon
output, bounded KiCad interchange, design findings and review records.

See [the original release notes](docs/RELEASE_NOTES.md),
[compatibility limits](docs/COMPATIBILITY.md) and [test coverage](docs/TESTING.md).
