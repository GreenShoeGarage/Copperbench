# Changelog

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
