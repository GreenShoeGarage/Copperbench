# Verification record — COPPERBENCH v1.7.1

This release adds a dedicated CaseBench native-JSON export without changing schema 5.

**741 / 741 automated regression checks passed**: 348 engine/model,
118 separate-language manufacturing, 262 Chromium interaction and
13 packaging checks. The complete retained suite plus both new suites ran
against the final v1.7.1 runtime, with unchanged runtime hashes before/after.
Browser tests were split across four concurrent groups; the supplied
`python3 tools/test.py` runs the same commands sequentially.

The new tests comprise **31 engine checks and 15 browser checks**. They cover all
**193 library variants** and **43 shipped native example projects**, exact raw
placement/pad/active-hole preservation, bottom-side rotations, module heights,
block records, both output modes, file/geometry limits, native reimport, pending
edits and revision guards, camera/unit independence, and mobile access.

[Execution summary](verification/casebench-v1.7.1/summary.json) ·
[Commands and runtime SHA-256](verification/casebench-v1.7.1/execution.json)

One retained browser startup assertion initially expected the literal version
1.7.0. It was corrected to compare the application version against package.json;
all 29 editing interaction tests were rerun and passed on the unchanged runtime.
The initial log and retry log are both retained in the execution record.

Extracted-archive smoke tests and reproducible rebuilding are recorded separately
in the accompanying release verification record. They are not another complete
741-check run.

## Scope

The export uses the native CopperBench contract accepted by the retrieved
CaseBench native-adapter definition (adapter 2.0.1, retained in CaseBench v2.3.0).
The complete CaseBench application was not available in the working environment.
No copy of its importer is embedded or claimed to have run. Geometry-preservation
and native CopperBench round-trip tests are **not** an end-to-end CaseBench test.

Browser regression tests use real Chromium controls, canvas and workers with an
injected storage double and captured download blobs. The native HTTP and portable
file tests were attempted separately: both returned ERR_BLOCKED_BY_ADMINISTRATOR,
so save/reopen/download/offline qualification could not execute. No policy was
altered and blocked cases are not counted as passes.

Component envelopes and stack gaps remain representative, not physically measured
assemblies. No physical enclosure fit, manufacturing acceptance, electrical operation,
independent CAM validation, Safari or Firefox qualification is claimed.

See [v1.7.0 verification](TESTING-v1.7.0.md) for the retained earlier test history.
