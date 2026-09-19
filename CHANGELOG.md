# Changelog

## 1.7.1 — 2026-09-18 · CaseBench board export

- Added compact export-format access and a dedicated CaseBench JSON handoff in the export menu, Board panel, manufacturing dialog and mobile Project files.
- Export retains native schema 5 with explicit millimetres, embedded part geometry, active holes, slots/cutouts, both-side placement, module/carrier metadata and circuit-block records.
- Board-only default omits artwork/assets, saved baseline and unused circuit-block templates; optional project extras preserve them. Save JSON remains the full backup.
- Added preflight for known native-adapter limits and malformed boundaries, reviewed-revision guards and pending-edit protection without blocking unrouted boards or unfilled planes.
- Added geometry-preservation regressions across all 193 library entries and the native example projects, plus desktop/mobile download UI coverage.
- CaseBench importer execution and physical fit remain unverified; no unit guessing, double transform or second stack-height addition.

## 1.7.0 — 2026-09-18 · Editing and export review

- Added selection filters and overlap cycling without permanent instruction banners.
- Added reversible segment/corner edits, section replacement, conservative cleanup,
  and trace/segment/connected/whole-net width scopes with lock/clearance checks.
- Added limited connected part/via dragging and exact-position previews; centered
  endpoint attachments only, no pour-net movement or push-and-shove.
- Added attached reference/polarity positioning without changing physical pins.
- Added generated-file review, sampled silk-clipping inspection, drill/outline
  consistency checks and a revision-bound manufacturing manifest.
- Added autosave conflict/unreadable-record safeguards and explicit two-copy recovery.
- Supplied opt-in native-browser and independent-parser qualification scripts and
  a manual workflow. Release-environment gates remain blocked, not passed.
- Retained all 193 parts, six blocks, schema 5 and the no-build/offline packaging.

## 1.6.3 — 2026-09-18

- Added a labelled Pan view control and P shortcut across Bench, Copper and
  Fabrication, with grab/grabbing cursors, keyboard panning and Fit/Home recovery.
- Space-drag and middle-drag preserve selection and unfinished editing operations.
  Pan mode scrolls the view; Ctrl/Command-wheel zooms and Shift-wheel pans sideways.
- Added centroid-anchored two-finger panning/pinch and touch-safe edit deferral.
  Focus/capture loss and cancelled gestures release navigation safely.
- Kept all navigation outside document commands, history and manufacturing output.
  Project schema remains 5; existing component and printed polarity data is retained.
- Added dedicated Chromium mouse, keyboard, wheel, touch and narrow-screen tests.


## 1.6.2 — 2026-09-18 · Compact polarity markings

- Removed always-on polarity overlays and expanding full-name badges. Idle Bench
  shows the small physical silk; selection/hover/routing uses fixed 9-pixel A/K or
  +/− tags outside projected bodies and solder pads. Crowded tags are omitted
  rather than covering a component. Full role names remain in tooltips/inspector.
- Default printable polarity is 0.9 mm high with 0.16 mm strokes; explicit saved
  size, gap, offset and opt-out settings are preserved. Added an inspector print
  checkbox and a compact-defaults action in the existing polarity dialog.
- Fixed overprinted polarity glyphs on four-lead RGB LEDs by spacing the printed
  row in pin order. Printable geometry still rotates/flips with its component.
- Added engine, separate-language Gerber-ink and Chromium regression checks plus
  a six-component demonstration and desktop/mobile/read-back screenshots.
- Native schema stays at 5. No runtime dependencies, accounts or telemetry added.

## 1.6.1 — 2026-09-18 · Quieter workbench

- Removed welcome-card and canvas slogans, repeated introductory paragraphs, and duplicate empty-inspector statistics.
- Put parts search and category selection first, with compact catalog buttons and a keyboard-operable Library tools disclosure.
- Added on-demand tool help; show short hints only during active workflows. Removed duplicate part/block placement instruction toasts.
- Kept polarity, storage errors, live design findings, clearance checks, and manufacturing export gates visible.
- Preserved native schema 5, all 193 part entries, six block templates, and the routing/manufacturing engine.
- Added 18 Chromium interface regressions; updated legacy tests only for the new category control, disclosure and removed introductory overlay.


## 1.6.0 — Module interfaces and reusable circuit blocks

- Added five specific, source-referenced Adafruit module mating interfaces with
  pin names, optional mounting holes, representative bodies and fit/source inspector.
- Added six routed circuit-block starters and explicit per-port mapping. New IDs
  and nets prevent accidental joins between copies; no GND name-based auto-merge.
- Added reversible insertion, checked placement, whole-group move/rotate/flip/nudge,
  isolated-net copies, detach, project-local capture/library, and block JSON exchange.
- Added export-template controls, two samplers and editable module/board examples.
- Native schema 5 reads schemas 1–4 and preserves new group/library metadata.
- KiCad export warns that module metadata and reusable grouping do not survive.
- Preserved per-component footprint geometry, all v1.5 controllers, vias, planes,
  polarity markings and corrected Gerber silkscreen clipping.
- Updated expected current-schema/count regressions and added module, block,
  independent manufacturing-coordinate and actual-browser tests.
- Adapted module coordinate data is CC BY-SA 3.0; retained notices accompany the
  source, static and portable editions. Engine and original blocks remain MIT.


## 1.5.0 — 2026-09-18

- Added 18 header-mounted controller interfaces across nine host selections: Pico/Pico 2 and wireless variants, classic Nano, ESP32-DevKitC V4 WROOM-32E, common Feather/FeatherWing, original XIAO RP2040 and XIAO ESP32C3. All 170 prior library entries are retained.
- Added controller-first selection, 18 native starters, functional contact maps and nominal host/cable references. No-hole hosts receive no invented mounting drills.
- Added attached, editable antenna guards enforced by routing, vias, fill and geometry checks on both faces. Move/rotate/flip/duplicate/delete preserve the attachment; hiding an overlay never disables enforcement.
- Added editable access regions, advisory stack-gap/body-overlap checks and source cautions. RF guard overrides require a saved reason and remain findings. Defaults are suggested projections, not qualified RF envelopes.
- Bumped native JSON to schema 4 so older apps reject unknown attached-guard semantics. Schemas 1–3 still open without library-driven footprint replacement. KiCad exports active guards as independent keepout zones with an explicit loss-of-linkage warning.
- Added carrier engine, separate-language manufacturing and real Chromium workflow regression suites. Existing Uno ICSP, vias, planes, polarity and corrected silkscreen export remain covered.


## 1.4.0 — 2026-09-18

- Added 134 maker variants in 17 families, retaining all 36 existing entries.
- Added family-first selection, searchable names/manufacturers/functions, and representative bodies for new part types.
- Added functional pin-name editing, editor-only selected-part captions, per-part source/caution/review dialogs and pin-map CSV.
- Added internal-common-terminal conflict findings without automatic net joins or invisible copper.
- Added optional Uno R3 ICSP as six appended contacts; existing pads/indices/nets and default templates remain unchanged. Assigned or copper-touched ICSP cannot be silently removed.
- Added Everyday Maker sampler and Uno ICSP example, schema-3 metadata preservation, and an explicit KiCad metadata-loss warning.
- Kept prior polarity and Gerber-silkscreen fixes, vias, planes and host-platform support.
- Added targeted engine, independent-language manufacturing and Chromium UI regressions. See current verification record for executed results and limitations.


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
