# Repository packaging verification

**App version:** 1.0.0. **Packaging revision:** GitHub-ready source tree.

The existing app implementation was preserved. All ten files in `src/`, the
static entry point, CSS, portable HTML, application license, bundled JSZip and
its retained license were byte-compared with the supplied v1.0.0 release and
were unchanged. Generated `sw.js` now uses content-derived, deployment-scoped
cache names; `manifest.webmanifest` has a formatting-only newline change.

## Locally observed results

| Check | Outcome |
|---|---:|
| Node engine / geometry / routing / interchange | 32 / 32 passed |
| Chromium interaction harness | 20 / 20 passed |
| Independent Python/Shapely manufacturing geometry | 12 / 12 passed |
| Repository / portable / cache-generation / ZIP packaging regressions | 9 / 9 passed |
| **Total automated test cases** | **73 / 73 passed** |
| Source syntax, generated-file consistency, asset/link integrity, vendor hashes | Passed |
| Workflow and issue-template YAML parse / local workflow-reference checks | Passed locally |

Recorded environment: Node v22.16.0, Python 3.13.5,
Chromium 144.0.7559.96 built on Debian GNU/Linux 13 (trixie). Python dependencies match `requirements-dev.txt`. The browser was
selected through the `CHROMIUM_EXECUTABLE` override for this local run.

The source/packaging/engine/manufacturing runner was executed first with the
browser explicitly skipped; the browser suite was then executed separately and
all 20 interactions passed. Neither command's scope is misrepresented as the
other. A fresh routed-board screenshot was also inspected during packaging.

Raw records: [summary](verification/repository-v1.0.0/summary.json),
[engine](verification/repository-v1.0.0/core-results.json),
[browser](verification/repository-v1.0.0/browser-results.json),
[manufacturing](verification/repository-v1.0.0/manufacturing-results.json),
[core/packaging console](verification/repository-v1.0.0/repository-core-run.txt)
and [browser console](verification/repository-v1.0.0/repository-browser-run.txt).
The original release records remain separate in `docs/verification/original-v1.0.0/`.

## What this does not establish

No remote GitHub repository was created or pushed. The workflows are configured
and locally inspected, not claimed to have succeeded in a remote GitHub account.
The first remote run still depends on GitHub settings, Actions permissions and
dependency installation. Pages is opt-in and no domain or live URL is assumed.

The browser harness uses a storage test double and captures download blobs.
It does not test real-origin persistence, unrestricted file launch, operating
system downloads, Safari/Firefox or hosted service-worker installation/update.
The new cache tests exercise generated source properties, not a complete browser
cache lifecycle. See [the full testing guide](TESTING.md).

Manufacturing checks remain software geometry regressions. External CAM review,
manufacturer upload acceptance and physical fabrication have not occurred.
