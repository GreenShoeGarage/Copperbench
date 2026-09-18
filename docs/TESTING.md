# Verification record — COPPERBENCH v1.6.1

**547 / 547 local regression checks passed.** The retained 529 checks are joined
by 18 focused Chromium tests for the quieter interface. Detailed results and logs
are frozen in `docs/verification/quiet-ui-v1.6.1/`.

| Test group | Result |
|---|---:|
| JavaScript engine and catalog checks — eight suites | 250 / 250 |
| Separate Python/Shapely geometry checks — eight suites | 110 / 110 |
| Chromium workflows — nine suites | 174 / 174 |
| Packaging and deterministic rebuild checks | 13 / 13 |
| **Total** | **547 / 547** |

`tools/check_repo.py` additionally verifies source syntax, generated portable,
worker and offline-cache assets, visible/runtime/package versions, documentation
links and bundled dependency hashes. These integrity checks are not added to the
547-test total.

## Interface coverage

Fresh and previously saved preferences have no welcome/canvas slogans. Search and
catalog controls sit ahead of the part grid, with all six launchers reachable.
The category dropdown retains module/controller discovery. Exceptional plane states (including a required refill) remain visible on the board rather than being hidden in tooltips. Library tools is
keyboard-operable and remains open across current-panel refreshes. Modal tool help
preserves the active tool and document. Only active tools show a short hint;
placement no longer adds a second instructional toast.

The complete guide retains displaced instructions, keyboard commands and
manufacturing limits. Live error/warning counts, unassigned-via cautions, autosave
failure messages and blocked fabrication export remain visible. Fabrication layer
selection and its independent-CAM caution remain. View changes do not change
manufacturing-file bytes. Native schema-5 JSON and all 193 parts are retained.
The dark/contrast active-tool foregrounds are explicit and tested. Layouts at
360, 390, 430, 700 and 900 pixels are checked for page-level overflow; actual
screenshots include desktop, mobile, dark, contrast and silkscreen views.

Only application UI code, markup/styles, the core app version and generated assets
change at runtime. Geometry, routing, via, plane, manufacturing, interchange,
component catalogs and rendering modules are unchanged from v1.6.0. The source
comparison is recorded in `source-scope.json`. Existing regression suites still
exercise carrier keepouts, modules, reusable blocks, connection intent, polarity,
and exported silkscreen clipping.

## Reproduction

The app runs without a build. Developer verification uses the pinned development
dependencies; it writes results to ignored `tests/output/`, not checked-in source,
examples or documentation images.

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
python3 tools/package.py
python3 tools/test.py
```

On Windows use `py -3` and `.venv\Scripts\Activate.ps1`. Set
`CHROMIUM_EXECUTABLE` to an existing Chromium executable when needed.

```sh
python3 tests/quiet_ui_browser_test.py
python3 tools/check_repo.py
python3 tools/release.py
```

[Repository verification](REPOSITORY_VERIFICATION.md) records the separate
extraction run and final byte comparison. Source/static ZIPs use sorted paths,
fixed timestamps and allowlisted input. Transient outputs, virtual environments
and `.git` are excluded. Local reproduction is not a GitHub Actions execution.

## Environment and limits

Node 22.16.0, Python 3.13.5, Chromium 144.0.7559.96, Playwright 1.57.0,
Shapely 2.1.2 and Pillow 12.3.0 were used.

Browser suites execute real DOM, canvas and workers in embedded portable HTML,
using a local-storage test double and intercepted export blobs. A localhost
navigation attempt was blocked with ERR_BLOCKED_BY_ADMINISTRATOR before startup;
no browser policy was changed. It is not counted as a passing test. Real-origin
storage/downloads, hosted offline installation/update, Safari/Firefox and actual
mobile devices remain unverified.

External CAM, manufacturer acceptance, physical fabrication, connector fit, RF
performance and circuit operation were not validated. The independent parser
covers the emitted subset, not arbitrary Gerber. Bodies/clearance envelopes and
library footprints retain their documented qualifications. Circuit blocks remain
editable starting topologies, not electrically certified or rated protection
circuits. No remote repository, deployment or board order was changed.

[Interface guide](QUIET_WORKBENCH.md) · [Compatibility](COMPATIBILITY.md) ·
[Results](verification/quiet-ui-v1.6.1/summary.json) · [Fresh extraction](verification/quiet-ui-v1.6.1/fresh-summary.json) ·
[Quiet UI tests](verification/quiet-ui-v1.6.1/quiet-ui-browser-results.json)
