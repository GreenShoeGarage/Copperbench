# Repository verification — COPPERBENCH v1.3.1

All **308 / 308** local regressions passed against the patched application:
245 retained tests and 63 added polarity/silkscreen checks. Generated-runtime,
source syntax, local-link, version and dependency-integrity checks passed too.
See [the detailed record](TESTING.md) for exact scopes and frozen test logs.

The independent Python reader's former XOR bug is explicitly corrected. Previous
passes do not establish old silkscreen correctness. New negative/positive Gerber
contracts, independently derived clipping geometry and actual Canvas pixels guard
against repeating the exporter/reader's shared defect.

The source ZIP includes the no-build app, portable edition, source, documentation,
reviewed screenshots, editable examples, test suites and hidden GitHub workflows.
The bundled golden Gerbers were regenerated with the corrected exporter. Transient
outputs, .git directories and local environments do not enter release packages.
Native schema remains 3. `tools/release.py` supplies SHA-256 checksums and fixed ZIP
metadata/order for byte-reproducible packages from a fixed source tree.

No remote repository, Actions run, deployment or board order is claimed. Browser
storage/downloads are test doubles; external CAM/manufacturer/physical acceptance
is unverified. [Regenerate prior fabrication ZIPs](POLARITY_AND_SILKSCREEN.md).
