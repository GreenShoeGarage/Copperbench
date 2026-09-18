# Repository verification — COPPERBENCH v1.6.1

**547 / 547 checks passed in the separate extracted source tree:** 250 JavaScript
engine/catalog checks, 110 separate Python/Shapely geometry checks, 174 Chromium
workflows and 13 packaging checks. The same suites were exercised in the working
tree. The final general-browser, syntax/integrity and packaging checks were
repeated; repeat runs are not added to the count.

[Detailed record](TESTING.md) · [Fresh summary](verification/quiet-ui-v1.6.1/fresh-summary.json) ·
[Fresh console](verification/quiet-ui-v1.6.1/fresh-tests.txt)

The extracted tree's `git status --porcelain` was empty after testing. Tests did
not rewrite tracked source, examples or documentation images. Final screenshots,
verification logs and release documentation were then reconciled between both
trees. All non-documentation release inputs were byte-identical. Generated-file
integrity and packaging checks were repeated after documentation reconciliation.

Rebuilding the reconciled source and extracted trees produced **byte-identical
GitHub repository ZIP, static-site ZIP and portable HTML**. SHA-256 checksums
accompany the downloads. This is local reproducibility evidence; GitHub Actions
has not run in the user's account as part of this update.

The source ZIP contains the no-build static app, self-contained portable edition,
complete source, examples, documentation, screenshots, tests and hidden GitHub
workflows. Transient test output, virtual environments and `.git` are excluded.
No runtime dependency was added. Native schema remains 5, with the existing 193
parts, six circuit blocks, vias, planes, carrier interfaces, polarity labels and
manufacturing exporters retained. The core module changes only its app version;
geometry, routing, catalogs and manufacturing modules are unchanged from v1.6.0.

Browser suites use simulated storage and captured download blobs. A localhost
navigation attempt was blocked by the managed browser before app startup. No
browser policy was changed. Real-origin storage/downloads and hosted offline
lifecycle, external CAM, manufacturer acceptance, connector fit, circuit operation
and physical-board fabrication are not claimed. No remote repository, deployment
or board order was changed.
