# Contributing to COPPERBENCH

Keep the primary interaction tactile and the manufacturing geometry explicit.
The app must remain runnable from the checked-in static files without accounts,
a CDN, telemetry, a backend, or a required frontend build.

## Development

Use Node.js 22+ and Python 3.13. Create a virtual environment, install
`requirements-dev.txt`, and install Chromium through Playwright. The full
commands and test limitations are in [the testing guide](docs/TESTING.md).

`python3 tools/serve.py` serves the repository on loopback. Edit `src/`,
`styles.css` and `index.html`, then run `python3 tools/package.py` to regenerate
the embedded worker, portable HTML and offline cache. Do not hand-edit generated
files. Run `python3 tools/test.py` before submitting a change.

## Engineering boundaries

Preserve pad identity and explicit connection intent. Camera geometry must never
drive manufacturing output. Never silently drop unsupported manufacturing data
on import. A failed or cancelled worker must leave the design intact. A storage
failure must keep JSON backup available. Keep Easy and Advanced modes on the
same underlying checks; do not hide geometry errors in Easy mode.

Add focused regression fixtures for changed geometry, copper, drill, mask,
silkscreen, routing and interoperability behavior. Real-origin browser tests,
manufacturer acceptance and physical fabrication are different levels of
evidence; document exactly which occurred.

New dependencies need a documented purpose, compatible license, bundled offline
runtime assets where applicable, and updated notices. Review bundled JSZip
manually; it is not installed from npm at runtime. Do not edit its integrity
manifest simply to silence a mismatch.

## Pull requests

Describe the problem, the interaction, the tests and any remaining limitations.
Use a small non-sensitive example. Do not commit `tests/output/`, `dist/`, local
customer boards, credentials or a virtual environment. Review screenshot changes
manually before replacing the images in `docs/images/`.

Keep discussions welcoming. Experience, tools and budget are not measures of a
person's right to participate. Submissions should be work you have permission
to contribute under this repository's existing MIT license.
