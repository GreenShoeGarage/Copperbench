# Example boards and test files

These are editable software demonstrations, not manufacturer-approved reference designs.

- `starter.json`: small through-hole learning board with explicit nets to route.
- `little-light-routed.json`: that board routed through the actual browser interface during release testing; no blocking geometry findings in that exercised state. Its generic parts still require datasheet verification.
- `smd.json`: surface-mount layout exercise.
- `mixed.json`: mixed through-hole/SMD and two-face exercise.
- `golden-coupon.json`: 40 × 30 mm geometric regression fixture with top, bottom and via-linked nets, through pads, one NPTH round hole, one NPTH slot and text.
- `golden-coupon.kicad_pcb` and `golden-fabrication/`: generated interchange/manufacturing files for that regression fixture.

The golden coupon's `verified` part flag identifies controlled **software test geometry**, not a certification against a particular purchased component. It is labelled as a software fixture in its evidence record. No example has been physically fabricated or submitted to a manufacturer as part of this release.

The Node suite regenerates examples/coupon outputs; the browser suite regenerates the routed example. IDs may change between generated runs without changing their geometric purpose.
