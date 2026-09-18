# Primary references

Reviewed during development on **17 September 2026**. The application does not fetch these at runtime. Confirm fabrication rules for the service you actually order; the included profile is a dated snapshot, not an automatically updated contract.

| Reference | Purpose |
|---|---|
| [OSH Park two-layer service specifications](https://docs.oshpark.com/services/two-layer/) | Initial editable two-layer rule profile. |
| [OSH Park board outlines](https://docs.oshpark.com/submitting-orders/board-outline/) | Closed centerline outline and internal-cutout considerations. |
| [OSH Park drill specifications](https://docs.oshpark.com/submitting-orders/drill-specs/) | Drill output conventions. |
| [OSH Park slots](https://docs.oshpark.com/submitting-orders/slots/) | Native Excellon slot expectations. |
| [Ucamco Gerber resources](https://www.ucamco.com/en/gerber) | Gerber specification and reference resources. |
| [Ucamco X2 introduction](https://www.ucamco.com/en/gerber/demo-1) | File attributes and image compatibility. |
| [KiCad public board format](https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/) | Bounded S-expression board interchange. |
| [KiCad S-expression introduction](https://dev-docs.kicad.org/en/file-formats/sexpr-intro/) | Footprint/pad/graphic conventions. |

The rules profile in `src/core.js` retains source URL and verification date. Generic parts in this app are original parametric examples, not a redistributed certified manufacturer or KiCad footprint library. Their package/source notes explicitly request verification against the actual purchased part.

## Plane workflow reference

[KiCad PCB Editor manual, version 9](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html)
was consulted for zone/net, thermal-relief and disconnected-island concepts.
COPPERBENCH uses its own implementation and a more limited cell-fill/helper
algorithm; citing that manual does not claim KiCad-equivalent DRC or routing.

## v1.3.1 polarity and Gerber correction

[Ucamco Gerber Layer Format Specification, revision 2026.05](https://www.ucamco.com/files/downloads/file_en/554/gerber-layer-format-specification-revision-2026-05_en.pdf),
section 4.10 (printed pp. 96, 103–104), is the primary reference for filled-contour
union semantics. The former writer/reader nested-frame/XOR assumption contradicted
this rule; see [the fix record](POLARITY_AND_SILKSCREEN.md).

[Vishay 1N4148](https://www.vishay.com/docs/81857/1n4148.pdf) documents cathode-band
identification for that diode; [Kingbright WP7113ID](https://www.kingbrightusa.com/images/catalog/SPEC/WP7113ID.pdf)
provides a specific LED package orientation example. Generic application models
are not manufacturer-certified footprints. Always verify the purchased part.
