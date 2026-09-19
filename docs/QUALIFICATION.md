# Qualification is separate from regression testing

The ordinary suite checks model geometry, transformations, connection preservation,
rendered interactions, explicit error paths, and generated files. The browser
harness uses real Chromium DOM/canvas/workers, but injects a storage-shaped object
and captures download blobs before navigation. The separate Python/Shapely parser
is maintained in this repository; it is not independently developed CAM software.

## Additional gates supplied with v1.7

`tests/native_browser_test.py` uses normal HTTP and file navigation, genuine browser
storage, actual file downloads, page closure/reopening, persistent-profile
closure/reopening and an HTTP service-worker offline reload. It runs without request
routing or storage replacement. It does not attempt to modify browser policies.

In the release environment, both ordinary local HTTP navigation and portable-file
navigation returned `ERR_BLOCKED_BY_ADMINISTRATOR`. These two cases are recorded
as **blocked**, not passed. The associated native-save/download/offline checks could
not be reached. The testing environment's policy was left unchanged.

`tests/external_cam_check.py` is an opt-in third-party parser/rendering smoke gate
using **Gerbonara 1.6.3**. This dependency is not bundled with the runtime or required
to use the application. The release environment does not contain the dependency,
and the attempted installation could not resolve the package host. This gate is
also **blocked**, not passed. The adapter's successful external execution is not
claimed merely because the file is included.

The manual GitHub workflow **Optional native browser and CAM qualification** runs
both gates and retains evidence. It fails if either gate fails; no account-side
execution is claimed by providing the workflow. A parsing pass alone still would
not prove visual ink correctness, electrical function, component fit, or manufacturer
acceptance. Inspect the rendered layers and the manufacturer upload preview; a
physically fabricated and inspected test board remains a distinct milestone.

## Reproduce the regression checks

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
python3 tools/test.py
```

The runtime itself is already built. `CHROMIUM_EXECUTABLE` can select an installed
browser; it does not change administrator restrictions.

## Run the additional gates in an authorized development environment

```sh
python3 tests/native_browser_test.py
python3 -m pip install gerbonara==1.6.3
python3 tests/external_cam_check.py
# Optional: inspect another generated board folder
python3 tests/external_cam_check.py examples/golden-fabrication
```

Generate the default reference board first with `node tests/editing.test.js`.
Results and rendered SVGs are written under ignored `tests/output/`. No PCB design
is uploaded by either script. Existing fixtures include both-face pads, vias,
slots, cutouts, pours and silkscreen. The default new fixture demonstrates a
connected move and retained pad/trace contact.

## Primary tool references

- Playwright browser contexts and native storage behavior:
  https://playwright.dev/python/docs/api/class-browsercontext
- Playwright persistent browser contexts:
  https://playwright.dev/python/docs/api/class-browsertype
- Gerbonara file/API model:
  https://gerbolyze.gitlab.io/gerbonara/file-api.html
  https://gerbolyze.gitlab.io/gerbonara/api-concepts.html

[Editing guide](EDITING.md) · [Release test record](TESTING.md)
