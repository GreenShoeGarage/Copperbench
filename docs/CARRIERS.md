# Controller carriers — COPPERBENCH v1.5

**v1.6.1 navigation:** catalog buttons are shortened; see the [current interface guide](QUIET_WORKBENCH.md). All workflows described here remain.

**18 new interface entries, nine host selections, 188 library entries total.**
These are footprints for the mating headers on **your** PCB. They are not PCB
layouts for rebuilding the controller board and are not castellated surface-mount
land patterns. No power circuit, level shifting, firmware, external antenna or
hidden connections are inserted.

## Start a carrier or add-on

Open **Parts → Controller carriers**, choose the exact host, then choose **Carrier
below host** or **Add-on / HAT / shield above host**. Choose a board margin and
optional mounting holes, then **Start new board**. Undo restores the previous
project. Templates lock the compound header pattern while its pads remain
selectable and routable. Unlock placement in the inspector to move it.

**Place headers on current board** leaves the board and existing geometry intact.
This action places only the interface; use **Host reference & mounting holes** to
enable its optional mounting holes. Library cards also support click placement
and drag/drop. **Examples → Controller carriers** opens the same starter picker;
the repository includes [18 native starter files](../examples/carriers/).

The default carrier has top-face sockets. The default add-on has bottom-face
headers. Both have the same coordinates when viewed from the top of your new PCB.
Flipping the part changes the connector face, not the electrical pin identity.
A camera flip is a separate operation. Header gender, tail length, plating and
engagement are purchasing/assembly choices; the app does not select a vendor part.

## Included selections

| Host selection | Contacts | Nominal reference and scope |
|---|---:|---|
| Raspberry Pi Pico | 40 | Non-wireless, USB-up, 21 × 51 mm envelope; 17.78 mm row spacing. |
| Raspberry Pi Pico 2 | 40 | Separate RP2350-labelled host; same main-header mapping. |
| Raspberry Pi Pico W | 40 | Wireless host; suggested antenna copper guard. |
| Raspberry Pi Pico 2 W | 40 | Separate wireless host; suggested antenna copper guard. |
| Arduino Nano, classic A000005 | 30 | ATmega328P Nano only; 15.24 mm row spacing. No Nano Every/33/ESP32 compatibility claim. |
| ESP32-DevKitC V4, WROOM-32E | 38 | J2/J3 banks, 25.4 mm apart. Not a generic 30-pin clone or WROVER board. |
| Adafruit Feather, classic interface | 28 | Common 16+12 header pattern; carrier or FeatherWing-style add-on. This is intentionally a common interface, not a universal MCU pin map. |
| Seeed XIAO RP2040, original | 14 | Original header-mounted board; not RP2040 Plus. |
| Seeed XIAO ESP32C3 | 14 | Variant-specific GPIO aliases and external-antenna connector access. |

Header pads default to **1.8 mm copper diameter and 1.0 mm drills**, with selected
rectangular orientation pads. Check those dimensions against the actual connector.
Pad numbers and bank identifiers are explicit and stable; pad signal labels are
editable, but do not connect nets. **Export pin map CSV** retains physical IDs,
functional names and world coordinates. Pico has physical pin numbers; Nano uses
its 1–30 numbering; ESP uses J2.1/J3.1 bank IDs. Feather L.1–L.16/U.1–U.12 are
application bank identifiers. XIAO uses its printed D0–D10 and power labels.

## What is nominal versus sourced

The header pitches, counts, electrical labels and referenced board envelopes are
transcribed from the sources below. All entries remain **unverified footprints**
until reviewed by the user. Exact board-edge offsets, mounting-hole tolerances,
connector drills, cable sizes, component heights and RF envelopes are **not**
qualified by these templates.

Pico uses a centered 48.26 mm header span within the 51 mm reference envelope;
its optional four 2.1 mm mounting drills use nominal positions. Nano uses the
43.2 × 18 mm mechanical-drawing envelope, a centered 40.64 × 15.24 mm optional
hole pattern and 1.8 mm holes. Do not substitute a marketing-length figure or
assume every clone matches it. ESP32's 27.94 × 54.30 mm reference includes a
nominal 6.04 mm antenna overhang beyond its 48.26 mm PCB; header edge offsets are
centered nominal values. Feather's optional 2.54 mm corner holes and XIAO's
centered header-to-edge offsets also require actual-board review. These notes
are deliberately visible in the interface, not only in this document.

No holes are invented for ESP32 or XIAO. No debug/ICSP, battery or test pads on the
underside of these hosts are included. The existing Uno's optional ICSP feature
is unchanged. Reflowing Pico or XIAO directly onto a board requires a different,
separately qualified surface-mount footprint and assembly review.

## RF guards and physical access

Select the interface and open **Carrier clearances & fit**. The dialog separates:

- **Copper guard:** a suggested antenna rectangle for Pico W, Pico 2 W or the
  selected ESP32 host. When enabled it blocks pads, traces, vias and copper fills
  on **both** faces. Existing violating copper receives a blocking keepout finding.
- **Access reference:** an amber USB, battery or coax-access rectangle. It creates
  advisory host-side body-overlap findings but is not a copper prohibition.
- **Assumed underside stack gap:** an editable planning value. Other components
  on the connector face that overlap the host envelope and exceed this height
  receive an advisory. The default **8.5 mm is an application assumption**, not
  a measured connector dimension or an assembly approval.

Each rectangle's X/Y/width/height is editable in **part-local coordinates**.
Move, rotate, flip and duplicate the interface: its constraints follow. Delete
the interface: no orphan constraints remain. Changing constraints invalidates
fills and invokes the normal refill/check workflow. Display controls do not
disable enforcement. Disabling a present antenna guard requires a recorded reason
and leaves a persistent warning. A part locked against placement can still have
its constraints deliberately edited in this dialog.

**The RF defaults reserve suggested antenna projections with an extension; they
are not full manufacturer-specified keepout envelopes or RF-performance guarantees.**
Review side clearance, board-edge placement, standoffs/screws, metal and the final
enclosure. Espressif's guidance also addresses baseboard cuts/antenna overhang and
clearance in the final housing; the small template rectangle does not certify all
of that. Edit/enlarge it or add normal keepouts/cutouts as required.

XIAO ESP32C3 has an **external antenna**, so its coax-access reference is not a
fictional on-board antenna exclusion. The generic Feather interface cannot infer
where a particular wireless Feather puts its antenna; it issues a review warning
rather than fabricating that constraint. Plan those external/variant-specific
antennas separately. None of the host renderings is an accurate 3D collision model.

## Power, ground and signal handling

Use the existing plane picker and per-pin **Plane ↗** actions. A through-hole
header contact can connect to an opposite-face pour without an unnecessary via.
Connections retain the existing preview/accept/undo behavior. RF guards apply to
managed planes, manual pours, manual traces, autorouting, and standalone vias.

Repeated GND/RESET/power labels are not implicit virtual wires. AGND is not
silently merged with GND. Reserved ESP flash contacts and Feather FREE assignments
produce warnings. Input-only and boot-pin roles are named; this is not a full
schematic/electrical rule checker. Feather FREE has no universal role and must not
be treated as ground by assumption.

## Persistence and exchange

**Back up before upgrading. v1.5 reads schemas 1–3 but writes schema 4.** The bump
ensures old editors reject new projects instead of ignoring attached copper
guards. Migration retains embedded footprints and does not change old pad
geometry. Custom host data travels with JSON; there is no live library lookup that
can silently change a saved board. Unknown future carrier schemas and malformed
rectangles are rejected before import replaces the document.

Gerbers contain actual pads and filled copper; drills contain only real pad/via
bores and enabled mounting holes. Host bodies, editor pin captions, RF overlays
and access labels do not become manufacturing silk. Enable a real reference label
or create silk artwork when you want printed markings.

KiCad exchange **flattens active copper guards into ordinary top/bottom keepout
zones** at the current coordinates. They no longer follow the host, and reference
bodies, access areas, stack-gap assumptions and source metadata are not preserved.
The export dialog warns about this. Native JSON remains the lossless master.

## Primary references reviewed

- Raspberry Pi: [Pico-series documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html)
  and [Pico 2 mechanical/pinout datasheet](https://pip.raspberrypi.com/documents/RP-008299-DS).
- Arduino: [classic Nano](https://docs.arduino.cc/hardware/nano/),
  [A000005 pinout](https://docs.arduino.cc/resources/pinouts/A000005-full-pinout.pdf),
  [A000005 mechanical datasheet](https://docs.arduino.cc/resources/datasheets/A000005-datasheet.pdf).
- Espressif: [DevKitC V4 user guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html),
  [dimensions](https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.pdf),
  [RF/baseboard layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html).
- Adafruit: [Feather interface specification](https://learn.adafruit.com/adafruit-feather/feather-specification).
- Seeed: [original XIAO RP2040](https://wiki.seeedstudio.com/XIAO-RP2040/),
  [XIAO ESP32C3](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/),
  [XIAO PCB design guide](https://wiki.seeedstudio.com/PCB_Design_XIAO/).

Sources reviewed 18 September 2026. No source PDFs, board photos or vendor CAD
files are redistributed as artwork. Interface records and procedural drawings
are part of the app source. **External CAM acceptance, manufacturer upload
acceptance, physical fit, RF performance and electrical operation are unverified.**
