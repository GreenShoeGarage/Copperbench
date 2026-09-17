# Verification record — COPPERBENCH 1.1.0

**Release: 17 September 2026.** Raw results for this update are retained in
`docs/verification/platforms-v1.1.0/`. Original v1.0 application and repository
records remain under their own historical directories; they were not overwritten.

| Suite | Result | Coverage |
|---|---:|---|
| Core JavaScript engine | 32 / 32 | Model, transforms, nets, DRC, routing, pours, import/export and coupon. |
| Platform JavaScript | 23 / 23 | Six interface variants, exact nominal coordinates, pin mapping, schema migration, linked mounts, routing, native/KiCad/CSV and manufacturing output. |
| Core Chromium interactions | 20 / 20 | Actual application DOM/canvas/workers, placement, routing, files, geometry, imagery, recovery, themes and responsive layout. |
| Platform Chromium interactions | 13 / 13 | Catalogue, chooser, template creation/undo, transforms, reference options, current-board placement, named pin search/routing, CSV/JSON and narrow layout. |
| Independent coupon geometry | 12 / 12 | Python/Shapely reader and expected-geometry checks of the generated coupon. |
| Independent platform exports | 12 / 12 | Literal nominal expected positions versus actual Excellon/Gerber, both roles, mask coverage, NPTH clearances and no bottom mirror. |
| Packaging | 9 / 9 | Generated assets, embedded worker, portable runtime, vendor/paths, deployment staging and reproducible archive algorithm. |
| **Total** | **121 / 121** | Executed local regression tests, not a hardware certification. |

Source syntax, version/lockfile/header consistency, documentation links, bundled
vendor hashes and generated-runtime integrity are checked separately by
`tools/check_repo.py`. Screenshots of the actual app were visually reviewed.

## Platform-specific evidence

Tests exercise physical contact identities separately from their signal aliases.
They check the Pi 40-pin order; the Uno 4.064 mm D8–D7 gap; MKR 28 contacts,
2.54 mm pitch and 20.32 mm row spacing; and the add-on/carrier initial top-view
coordinate equivalence. Later rotation and face flips preserve pin identities.

Optional NPTH holes move with the interface and participate in routing obstacles,
clearances, masks and drill export. Separate exported drill counts are checked
against 40/32/28 plated contacts and four requested mounts. Turning the host
illustration or pin captions off produces byte-identical manufacturing output.
Native JSON retains the compound relationship and aliases. KiCad subset export
retains pad/hole geometry, but reimport does not recreate platform metadata.

A dedicated independent Python script reads exported text using the existing
Python Gerber/Excellon parser. It compares against literal expected nominal
coordinates rather than calling the JavaScript transforms/export readers. This
is stronger than a self-round-trip, but it still cannot prove the reference
dimensions match an actual purchased host, clone or connector.

Schema-1 files migrate to schema 2 without changing the source file. New saves
use schema 2 so old v1.0 readers reject them instead of ignoring linked holes.

## Browser environment and limits

The browser suites run the complete portable HTML in Chromium using Playwright’s
`page.set_content` embedded `about:blank` harness. Canvas rendering, DOM input,
actual worker jobs, file inputs and generated Blob contents really execute.
The harness injects a Storage-shaped test double and intercepts download anchors.
No browser policy is changed or bypassed.

These tests do **not** verify unrestricted file/HTTP navigation, real-origin
local storage, operating-system download/save dialogs, hosted service-worker
installation/update/offline lifecycle, Safari/Firefox, or mobile device hardware.
Narrow viewport checks are desktop Chromium layout checks, not iOS certification.
“No external runtime requests” applies to the exercised flows only.

## Not verified

No mechanical fit test, host-board measurement, manufactured PCB, electrical
function test, RF/thermal validation, installed KiCad/CAM check or manufacturer
upload/acceptance is claimed. The official Arduino CAD archives could not be
retrieved; geometry is source-derived nominal data, not a CAD extraction claim.

Pi port/cooler/PoE placement, MKR antenna/battery clearance, connector genders,
tail engagement and stack heights require review of the actual hardware. No
automatic HAT+ EEPROM/power implementation or Uno ICSP header is included.
Review [FORM_FACTORS.md](FORM_FACTORS.md) before fabricating an add-on.

No GitHub remote was created or pushed and no Actions workflow was run in the
user’s account. The delivered repository and workflow definitions were checked
locally. No deployment, external upload or board order occurred.

## Reproduce

The application itself needs no development dependency install or build. For
testing, use Node.js 22+ and Python 3.13 in a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
python3 tools/package.py
python3 tools/test.py
```

On Windows, use `py -3 -m venv .venv` and activate
`.venv\Scripts\Activate.ps1`. npm shortcuts are optional. An already installed
Chromium can be selected with `CHROMIUM_EXECUTABLE`; no path is hard-coded.

Targeted commands:

```sh
node tests/core.test.js          # generates the test-only coupon
node tests/platforms.test.js     # generates test-only platform export fixtures
python3 tests/verify_manufacturing.py
python3 tests/verify_platforms.py
python3 tests/browser_test.py
python3 tests/platform_browser_test.py
python3 -m unittest discover -s tests -p 'test_packaging.py'
python3 tools/check_repo.py
python3 tools/release.py
```

New outputs go to ignored `tests/output/`. Tests do not rewrite checked-in example
projects or README screenshots. The explicit optional
`node tools/make_platform_examples.js` command regenerates the six example files
with stable IDs/timestamps; it is not part of the test run. Runtime source edits
require `tools/package.py` to refresh portable HTML, worker and scoped offline
cache before commit. See [GitHub setup](GITHUB.md) and [deployment](DEPLOYMENT.md).
