# Polarity and silkscreen — COPPERBENCH v1.3.1

## Identify the terminal, not a guessed voltage

Built-in diodes and LEDs expose **A = Anode** and **K = Cathode**. Polarized radial
capacitors expose **+ = Positive** and **− = Negative**. Compact pin badges become
full-name labels when a part or pin is selected/hovered. Full names also appear
in the pin inspector, tooltip and searchable pin table. Badges have leaders to
their physical pads and are clickable in selection/connection workflows.

The diode's representative cathode band follows its assigned cathode; the radial
capacitor's stripe follows its negative terminal. These are generic drawings,
not evidence that a purchased package has the same pinout. Consult its datasheet.
A/K are terminal identities, not fixed supply-voltage signs.

Select a part and choose **Polarity & pin roles**. Each pad can be Anode, Cathode,
Positive, Negative or None/unknown. The last choice explicitly removes a role.
Numeric/custom/imported pins are not guessed from the package shape or net names.
Changing a role clears the user-checked status but never renumbers, swaps or moves
a pad or changes its net. Label-only size/visibility changes retain that status.

## Print useful assembly marks

The same dialog has an independent **Print A/K or +/−** setting. Marks default to
1.2 mm tall, with a 0.7 mm gap beyond the relevant body/pad bounds. Set size, gap
and local X/Y offsets for crowded boards. Local offsets and glyphs rotate and
flip with the part. Printing occurs on the component's actual board face.

Hiding a reference such as D1 does not hide its polarity mark. Turning off printed
polarity does not remove the editor's terminal identification. The dark editor
badges and full-name popovers themselves are not printed: the exporter receives
small vector symbols. Normal silkscreen checks still apply and clipping can trim
marks that overlap another mask opening or a board edge. Always inspect the result.

Native schema-3 JSON preserves pad roles and printing options. Existing built-in
A/K and +/− footprints gain default marks when opened in v1.3.1 without pad/net
changes. Back up a project before upgrading; review newly generated marks before
ordering. No new trace routing is performed by this feature.

## What made silk disappear

The previous exporter drew the silk, then attempted to clear only the outside of
the board using one region containing an oversized rectangle and a second board
contour. That relies on an even-odd interpretation. Gerber section 4.10 instead
fills the contours individually and unions them. Consequently that clear operation
covered the board interior as well: its silk was erased.

The old Canvas viewer and separate Python reader repeated the XOR assumption.
They could show apparently correct ink despite incorrect files. Their historical
passes therefore did not verify this particular Gerber behavior. Both readers are
now corrected, and a mandatory old-frame reproducer must render as empty.

The new exporter sweeps the board outline by vertex heights and emits individual
simple exterior trapezoids. It retains the original source strokes/regions and
clears mask openings, exposed vias, non-plated holes/slots, cutouts and only the
actual board exterior. Bounds include all artwork, even far outside the board.
Rounded and elliptical outlines use the application's existing polygonal outline
approximation; the clipping itself is not a raster/grid fill.

The regression suite checks rectangles, rounded and elliptical boards, concave
outlines, reversed winding, off-origin outlines, both faces, holes/slots, masks,
text, reference labels, role glyphs, strokes, outline/filled shapes and converted
image regions. X2 and RS-274X compatibility modes retain identical image geometry.

## Inspect and regenerate

Open the editable project, then **Fabrication → Top silk only** and **Bottom silk
only**. These read generated Gerber text, not the workbench drawing or badge layer.
The fabrication export dialog reports source strokes and filled shapes on each
face; these counts describe source artwork, not a promise that clipping retained
all of it. Empty silk is valid when the project actually contains no marks.

Export a new manufacturing ZIP. **Previously generated ZIPs must not be reused:**
an application update cannot fix files already downloaded. Native project artwork
was not erased by this bug, so it does not need to be redrawn. The corrected
`examples/golden-fabrication/` is regenerated in this release. Open
`examples/polarity-and-silkscreen.json` for a visual software demonstration.

Independent CAM/manufacturer preview and physical review remain required. The
corrected Python/Shapely reader is a separate-language test oracle, not an installed
external CAM product. No manufacturer upload or fabricated-board validation has
been performed for this release.

## Sources and evidence

[Ucamco Gerber Layer Format Specification, revision 2026.05](https://www.ucamco.com/files/downloads/file_en/554/gerber-layer-format-specification-revision-2026-05_en.pdf),
section 4.10, particularly the region overview (printed p. 96) and overlapping
contours example (printed pp. 103–104). The specification defines union semantics.

[Vishay 1N4148 datasheet](https://www.vishay.com/docs/81857/1n4148.pdf) documents the
cathode band for that device. [Kingbright WP7113ID datasheet](https://www.kingbrightusa.com/images/catalog/SPEC/WP7113ID.pdf)
illustrates that part's LED orientation. These are reference examples, not claims
that the app's generic footprints have been fit-tested against those products.

[Executed verification](TESTING.md) · [Format limits](COMPATIBILITY.md)
