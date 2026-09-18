# Example boards and test files

These are editable software demonstrations, not manufacturer-approved reference designs.

- `polarity-and-silkscreen.json`: visual software proof of diode/LED/capacitor role labels, both-face text, drawings and filled image geometry. It is not a working circuit.
- `power-ground-planes.json`: small software fixture with top +5V and bottom GND pours, a through-hole ground seed and a surface-mount ground attachment through a short trace and via. Imported pours refill automatically. This is a geometry demonstration, not a powered circuit.
- `starter.json`: small through-hole learning board with explicit nets to route.
- `little-light-routed.json`: that board routed through the actual browser interface during release testing; no blocking geometry findings in that exercised state. Its generic parts still require datasheet verification.
- `smd.json`: surface-mount layout exercise.
- `mixed.json`: mixed through-hole/SMD and two-face exercise.
- `golden-coupon.json`: 40 × 30 mm geometric regression fixture with top, bottom and via-linked nets, through pads, one NPTH round hole, one NPTH slot and text.
- `golden-coupon.kicad_pcb` and `golden-fabrication/`: generated interchange/manufacturing files for that regression fixture.

The golden coupon's `verified` part flag identifies controlled **software test geometry**, not a certification against a particular purchased component. It is labelled as a software fixture in its evidence record. No example has been physically fabricated or submitted to a manufacturer as part of this release.

Regression suites write new fixtures, files and screenshots under ignored `tests/output/`, not these checked-in examples. IDs in test outputs may change without changing their geometric purpose.

The golden manufacturing files were regenerated with v1.3.1 to remove the old
silkscreen clear-frame defect. Re-export any older manufacturing ZIPs; see
[the correction guide](../docs/POLARITY_AND_SILKSCREEN.md).
