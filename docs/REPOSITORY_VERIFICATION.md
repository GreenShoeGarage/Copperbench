# Repository verification — COPPERBENCH v1.7.0

All **695 standard regression checks passed in the working source tree**, with
unchanged runtime hashes. The result is recorded in [TESTING.md](TESTING.md) and
[the frozen execution record](verification/editing-v1.7.0/summary.json). This is
separate from native-browser and third-party CAM qualification, which were blocked.

The source archive includes all application files, new edit/review modules, existing
library assets, test scripts, references, screenshots, qualification workflow and
build/release tools. Runtime dependencies are local. No compile step is needed to
run either the static site or portable HTML. Native schema stays 5.

`tools/check_repo.py` verifies version consistency, generated worker/portable/cache
assets, runtime script syntax, local file links and bundled dependency hashes.
The final archive is extracted into a clean directory before delivery, its integrity
and packaging checks run there, and `tools/release.py` rebuilds source/static ZIPs
and portable HTML for byte-for-byte comparison. The full regression run is not
claimed to have run a second time in that extraction.

Frozen records and documentation were added without changing the tested runtime.
Stable archive ordering, permissions, compression and timestamps make this source
tree reproducible. The supplied SHA-256 checksum file identifies the delivered
artifacts. No `.git` history, virtual environment, transient test output or working
customer file is packaged.

No remote repository was created or modified. Included GitHub workflows have not
been run in an account, and no board was uploaded or ordered.
