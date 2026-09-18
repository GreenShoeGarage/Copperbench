# Verification record — COPPERBENCH v1.3.1

**308 / 308 local regression tests passed.** The full runner executed every prior
suite plus 30 new engine tests, 17 separate Python/Shapely checks and 16 new
Chromium interactions. Frozen logs and per-test records are in
`docs/verification/polarity-silk-v1.3.1/`.

| Suite | Executed result |
|---|---:|
| Core JavaScript | 32 / 32 |
| Platform JavaScript | 23 / 23 |
| Via JavaScript | 27 / 27 |
| Plane JavaScript | 31 / 31 |
| Polarity / silkscreen JavaScript | 30 / 30 |
| Independent coupon geometry | 12 / 12 |
| Independent platform geometry | 12 / 12 |
| Independent via geometry | 7 / 7 |
| Independent plane geometry | 15 / 15 |
| Independent silkscreen geometry | 17 / 17 |
| Core Chromium interactions | 20 / 20 |
| Platform Chromium interactions | 13 / 13 |
| Via Chromium interactions | 21 / 21 |
| Plane Chromium interactions | 23 / 23 |
| Polarity / silkscreen Chromium interactions | 16 / 16 |
| Packaging | 9 / 9 |

`tools/check_repo.py` also passed source syntax, generated portable/worker/cache
integrity, visible/runtime/package version agreement, local links and vendor hashes.
Screenshots from the actual application were visually reviewed. No runtime
dependencies were added. The root app and portable edition are generated from the
same source. The included golden manufacturing sample was regenerated.

## Correction to the previous manufacturing evidence

**The old Python reader was independent in language, not in its mistaken Gerber
interpretation.** Like the old Canvas viewer, it XORed contours in a region. The
specification requires their union. The old exporter used a nested clear frame
which erased the board's legend under correct semantics. Historical pass counts
are retained as historical records, not evidence that that silk output was correct.

The new suites require the old-frame reproducer to produce an empty layer and an
overlapping-dark-contour example to remain filled. The Canvas viewer and the
Python reader pass both contracts. New exports must retain real on-board ink;
tests do not merely count draw commands before a later clear operation erases it.

A diagnostic using the original v1.3.0 source confirmed that the all-tools example
had zero final ink area on both faces. Corrected v1.3.1 output has approximately
95.8611 mm² on top and 13.4503 mm² on bottom in the separate reader. The new marks
are included in those areas. Captured old/new files and exact areas are stored in
`verification/polarity-silk-v1.3.1/historical-blank-reproducer/`; this diagnostic is
not counted as extra regression tests.

## New coverage

The engine checks known/legacy roles, explicit-none overrides, unknown/numeric
pins, preserved pin/net/geometry identity, print/reference independence, rotation,
side changes, safe schema-3 round trips and invalid-metadata rejection. It checks
actual retained ink, all-one-contour exterior pieces, pad/hole/cutout exclusion,
X2/compatibility parity, deterministic export, KiCad vector-mark interchange and
closed-contour validation. Fixtures cover both faces and all supported artwork
kinds: text, references, role strokes, lines, outline/filled shapes and image regions.

The Python suite independently derives substrate, mask, hole, slot and cutout
geometry for rectangular, rounded, elliptical, concave, reversed and offset
outlines. Large flood artwork must resolve to exactly the permitted board area.
Tented/open vias are distinguished. Other checks compare final ink with separate
stroke buffers and clipped source shapes. These are bounded geometric tests,
not proof for every possible arbitrary polygon or malformed third-party file.

Chromium tests use actual pointer/keyboard controls, clickable polarity badges,
full-name hover/search, role/print dialogs, undo/redo, real file-input import,
JSON and fabrication ZIP blobs, narrow layout, and Canvas pixels. They require
nonblank top and bottom silk-only views and correctly blank old-frame rendering.
All existing parts/platforms/vias/planes suites run against the same patched app.

## Environment and limits

Recorded environment: Node 22.16.0, Python 3.13.5, Chromium 144.0.7559.96,
Playwright 1.57.0, Shapely 2.1.2 and Pillow 12.3.0.

The complete app is loaded with Playwright `page.set_content`; real DOM, canvas
and workers execute. Browser storage is an explicit Storage-shaped test double.
Download links are intercepted to inspect actual generated blobs. Real-origin
persistence, unrestricted file launch, OS download navigation, hosted service-worker
installation/update/offline lifecycle, Safari/Firefox and mobile hardware remain
unverified. No policy restrictions were bypassed. Narrow screens are desktop
Chromium viewport tests. No network requests occurred in the exercised flows.

The independent Python reader is limited to the generated format subset. No
installed external CAM product or KiCad application, manufacturer upload/acceptance,
physical fabrication, assembly fit or electrical-function validation was performed.
Generic parts remain review-required. Existing conservative plane-fill and local
routing limitations still apply. Copper, drills and mask behavior have regression
coverage, not manufacturing certification. No remote GitHub repository, workflow,
deployment or board order was changed by this update.

## Reproduce

The delivered application itself needs no build or dependency installation.
Development/testing requires the pinned dependencies:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
python3 tools/package.py
python3 tools/test.py
```

On Windows use `py -3` and `.venv\Scripts\Activate.ps1`. Set
`CHROMIUM_EXECUTABLE` to an existing Chromium executable when necessary; no machine
path is hard-coded. The complete runner includes all suites in fixture order.
Targeted new checks are:

```sh
node tests/silkscreen.test.js
python3 tests/verify_silkscreen.py
python3 tests/silkscreen_browser_test.py
python3 tools/check_repo.py
python3 tools/release.py
```

Tests write only ignored `tests/output/`; they do not refresh checked-in example
files, screenshots or frozen logs. Source edits require `tools/package.py`.

[Fix guide](POLARITY_AND_SILKSCREEN.md) · [Compatibility](COMPATIBILITY.md) ·
[Summary](verification/polarity-silk-v1.3.1/summary.json) ·
[Console log](verification/polarity-silk-v1.3.1/full-tests.txt)
