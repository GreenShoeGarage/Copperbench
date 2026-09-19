# Compact polarity and silkscreen — COPPERBENCH v1.6.2

## Small labels, visible components

The idle Bench view has no floating A/K badges. It shows the actual physical
silkscreen, which can naturally be obscured by an assembled component in a tilted
view. When selecting a component, hovering a lead, or connecting/routing, small
A/K or +/− pin tags identify the terminals without covering the component body.

Tags use fixed **9-pixel type in a 12 × 13 pixel capsule**, with a 14 × 14 pixel
pick target. They do not grow when selected, zoomed in or assigned a larger print
size. Their layout accounts for projected component height, other bodies, pads,
and previously placed tags. A crowded tag can be omitted when no safe on-canvas
position is found; the actual pad and full pin-inspector information remain usable.
Tags are editor-only and cannot add artwork to a Gerber.

Full **Anode / Cathode / Positive / Negative** names remain in tooltips, the pin
table and inspector. Clicking a tag selects its associated electrical pad. A/K
identify diode terminals, not assumed fixed supply-voltage signs. Custom pin
roles are explicit; they are not inferred from net names or numerical pin order.

![Selected LED with unobtrusive contextual tags](images/compact-polarity-selected.png)

## Printed polarity is a separate setting

All library parts with explicit terminal roles default to printing A/K or +/−
on their component-side silkscreen. The new default is **0.9 mm print height,
0.16 mm stroke, and 0.7 mm body/pad gap**. These are default geometry settings,
not a guarantee of fabrication legibility. Review your manufacturer's requirements.

Use the selected-part inspector's **Print polarity on silkscreen** checkbox for
a quick change. Use **Polarity & pin roles** to change print size, gap, offsets,
or the terminal roles themselves. **Compact print defaults** restores the small
sizes, zero offsets and enabled printing in that dialog; click **Apply polarity
labels** to commit, or Cancel to leave the project unchanged.

Reference text such as D1 has its own visibility control. Hiding a component
reference does not disable its polarity marks. Disabling polarity printing does
not remove the editor's pin identification. Existing projects' explicit print
settings and intentional opt-outs are preserved. A saved opt-out must be enabled
explicitly when printed marks are desired.

Two-terminal marks sit outside the component and solder-pad extents. Four-lead
RGB LEDs receive an aligned row with one ordered symbol per terminal, rather
than overlapping A and K at the body ends. Enlarged marks are spaced to avoid
self-overprint. Custom layouts, nearby parts, edges or cutouts can still require
manual offset adjustments and fabrication inspection.

![Small A/K and +/− symbols in the actual generated top Gerber](images/compact-polarity-silkscreen.png)

## Review both fabrication faces

Open **Fabrication → Top silk only** or **Bottom silk only**. These render generated
Gerber text, not editor tag overlays. The exporter still clears openings, cutouts,
and off-board artwork; a symbol placed in one of those areas can be clipped.
Existing design findings remain active. Printed symbols rotate/flip with the
component, and manufacturing board coordinates are not screen-mirrored.

Regenerate the manufacturing ZIP after updating. Previously exported files do
not change. Back up native JSON first and replace the complete static application
folder, not just index.html. Native schema remains 5, and all electrical pin
identities, copper geometry, drills and assigned nets are unchanged by this update.

Open [compact-polarity.json](../examples/compact-polarity.json) for the unconnected
six-component demonstration. The supplied browser checks use a storage/blob
harness; physical fit, physical print quality, manufacturer acceptance and
independent CAM-product review are not established by those tests.

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
