# Release notes — v1.6.1

## Quieter workbench

Removed welcome overlays, canvas slogans and redundant introductory copy. The
parts drawer now leads with search and a category selector, followed by compact
catalog buttons. Additional block/footprint actions are under **Library tools**.
The empty inspector no longer repeats the board statistics or view descriptions.

Active tools have brief context hints and a **?** for full instructions. Select
mode has no idle how-to sentence. Header **?** and **H** still open the complete
guide. Keyboard activation works for the native Library tools disclosure.

This is a presentation update: the same 193 parts, six circuit blocks, carrier
interfaces, vias, planes, polarity labeling and corrected silkscreen export remain.
Source/manufacturing cautions, autosave failures, DRC findings and export gates
have not been hidden. Native schema stays at **5**; v1.6 projects need no migration.

Back up your JSON first. Replace all hosted application files, not only index.html,
or use the replacement self-contained portable file. No new runtime dependency,
network requirement or telemetry was added. No remote repository was modified.

[Interface guide](QUIET_WORKBENCH.md) · [Verification](TESTING.md) ·
[Compatibility](COMPATIBILITY.md) · [Earlier changes](../CHANGELOG.md)
