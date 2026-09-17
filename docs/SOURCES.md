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
