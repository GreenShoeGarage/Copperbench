# COPPERBENCH v1.2.0 via release evidence

Executed local regression records and the full-suite console log accompany this
release. See [the current verification record](../../TESTING.md) for suite counts,
methods and exclusions. The screenshot files under `docs/images/via-*.png` show
the actual application exercised by `tests/via_browser_test.py`.

Browser storage is a test double; downloads are inspected as generated Blobs.
Real Chromium controls, Canvas and worker code run. The independent Python
geometry reader does not call the app's JavaScript writer or reader. Neither
approach is an external CAM, manufacturer acceptance or physical PCB test.

These are a retained release snapshot. New test runs write ignored
`tests/output/` rather than replacing this historical evidence. No remote
repository, GitHub Actions run, deployment or manufacturer upload occurred.
