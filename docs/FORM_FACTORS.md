# HATs, shields and carriers — v1.1.0

## Workflow

Open **Parts → HATs, shields & carriers**. Pick a family, then choose **HAT /
shield above host** or **Carrier below host**. The chooser explains the current
scope. **Start new board** creates an undoable replacement; **Place headers on
current board** adds only the mating pattern and does not replace your board.
A new carrier defaults to a 10 mm surrounding margin; add-on defaults to zero.
Margins and board boundaries are editable without scaling the contacts.

Six entries also appear directly in **Parts → Platforms**. The initial placement
face follows the chosen role, not the camera: add-on connectors are bottom-facing,
carrier sockets top-facing. Pads are plated-through and routable from either side.
The inspector always shows the actual face. Flip deliberately changes the mating
orientation; it does not simply turn the camera over.

New templates lock the interface to avoid moving an entire connector pattern by
accident. Unlock it in the inspector to translate, rotate or flip. The four optional
mounting holes are owned by the interface and follow its transform. Dragging a
mounting hole selects the interface; edit its reference options to include/exclude
all nominal mounts. Per-hole editing is not exposed in this release.

Contact numbers, signal aliases and coordinates are available in the inspector,
hover tooltip, searchable pin table and **Export pin map CSV**. CSV positions are
always in the PCB’s top-view coordinate system, not screen coordinates. Repeated
GND/power contacts and aliased pins are NOT silently net-merged. Internal host
circuitry is not simulated or treated as PCB copper continuity.

## What is real versus visual

Actual plated pads, user circuitry, selected mounting holes and board outline
control manufacturing. The translucent host/reference illustration and on-screen
pin captions are not silkscreen, copper, automatic keepouts or certified mechanical
models. For printable pin captions, use the existing silkscreen text tool and
inspect the fabrication view. The reference shows orientation, not guaranteed
component heights or a complete host-board component layout.

The reference footprint is one compound connector assembly in the BOM, not an
instruction to buy an entire Raspberry Pi or Arduino. Choose specific header/
socket SKUs, connector genders and quantities yourself. All stock contacts start
with 1.8 mm pads and 1.0 mm drills; these are application defaults, not universal
manufacturer-recommended land patterns. Review the selected connector datasheet.

## Coordinate convention and nominal data

Dimensions below are millimetres in the new board’s **top view**. X increases
rightward and Y downward. Arduino reference USB is at the left; Pi GPIO is at the
top. Templates with a margin add that margin to every coordinate. These tables
are also regression expectations, not a declaration of fabricated accuracy.

### Raspberry Pi 40-pin interface

The legacy-style add-on blank is 65 × 56 with 3 mm corner radius. Four optional
2.7 mm NPTH mounts have centers (3.5, 3.5), (61.5, 3.5), (3.5, 52.5),
(61.5, 52.5). The header has two rows of 20 contacts at 2.54 mm pitch.
Physical pin 1 is lower-left at (8.37, 4.77); pin 2 is at (8.37, 2.23).
Each following pair adds 2.54 mm in X; pins 39/40 are at X=56.63.

Physical numbers remain distinct from GPIO/BCM aliases. Pin 1 is 3V3; pins 2/4
are 5V. GPIO0/1 on physical pins 27/28 are identified as ID_SD/ID_SC reserved
contacts. This interface is for 40-pin Raspberry Pi SBC headers, not Pico,
Compute Modules, or the original 26-pin board.

The 65 × 56 reference represents the add-on envelope, NOT the full size of every
host Pi. Connector/cooling/PoE locations and required standoff/cable clearances
vary by host. The reference rendering is intentionally schematic.

A matching footprint does **not** make a board HAT/HAT+ compliant. Review the
current HAT+ ID EEPROM, power/standby, mechanical and marking requirements.
No EEPROM, identification contents, pull resistors, power switching or host
power connection is inserted automatically.

### Arduino Uno R3 interface

The classic-outline starter has a 68.58 × 53.34 envelope. All 32 perimeter
contacts are included; ICSP is NOT included. The banks use explicit application
IDs (`POWER.1`, `ANALOG.1`, `DIGITAL10.1`, etc.), not MCU package numbers.

| Bank | First contact | Last contact | Row Y | Contact order left → right |
|---|---:|---:|---:|---|
| Power, 8 | X=27.94 | X=45.72 | 50.8 | NC, IOREF, RESET, 3V3, 5V, GND, GND, VIN |
| Analog, 6 | X=50.8 | X=63.5 | 50.8 | A0…A5; A4/A5 include SDA/SCL aliases |
| Digital, 10 | X=18.796 | X=41.656 | 2.54 | SCL, SDA, AREF, GND, D13…D8 |
| Digital, 8 | X=45.72 | X=63.5 | 2.54 | D7…D0 |

Within each bank, pitch is 2.54. The D8–D7 gap is **4.064**, not 2.54.
Published legacy footprint coordinates sometimes round the offset row to two
fractional millimetre digits; this definition keeps the nominal 160 mil gap.

Optional nominal 3.2 mm mounts: (15.24, 2.54), (13.97, 50.8), (66.04, 17.78),
(66.04, 45.72). The classic polygon is a starting shield shape, not an imported
production outline from an Arduino EAGLE file. Check dimensions and holes on
the actual host or clone. The downloadable official CAD archive could not be
retrieved during this update; no claim of direct CAD extraction is made.

R3/ATmega328P is the electrical reference, with 5 V I/O. Review IOREF, supply
direction, USB-B and barrel-jack height, tail engagement and the separate ICSP
header where required. Uno R4, Uno Q, Mega and clones are not blanket-certified
by using this footprint. Duplicate SDA/SCL and analog aliases are not auto-routed.

### Arduino MKR 28-pin interface

Two 14-contact rows at 2.54 pitch, 20.32 apart. The representative envelope is
61.5 × 25, based on the MKR WiFi 1010 user-manual drawing. Nominal reference
coordinates use X=21.92 + 2.54×i for i=0…13; top row Y=2.44, bottom Y=22.76.
The X start is derived from the drawing’s 38.43 mm header center and the 33.02 mm
13-interval span. Board offsets and optional holes require actual-board review.

| Row | Left → right, USB at left |
|---|---|
| Bottom, contacts 1…14 | AREF, A0/DAC0, A1…A6, D0…D5 |
| Top, contacts 28…15 | 5V, VIN, 3V3, GND, RESET, D14/TX, D13/RX, D12/SCL, D11/SDA, D10/MISO, D9/SCK, D8/MOSI, D7, D6 |

Optional reference mounts use diameter 2.25 and centers (2.31, 2.31),
(59.19, 2.31), (2.31, 22.69), (59.19, 22.69). They are nominal, based on the
WiFi 1010 envelope, not universal MKR mechanical promises. Verify before enabling
mounts for another variant. To omit them, uncheck the mounting-hole option.

MKR I/O is referenced to 3.3 V; do not infer 5 V tolerance from a 5V-labeled
contact. Check the chosen model’s power tree: MKR Zero and WiFi 1010 references
must not be treated as identical power implementations. Antenna placement,
battery connector, reset/debug access and overall board lengths differ by model.
No automatic RF keepout or electrical power-direction solver is implemented.

## Sources and qualification

Reviewed 17 September 2026. All source geometry remains **nominal-review-required**;
no physical host measurement, fit test or fabricated shield is claimed. Published
mechanical drawings can themselves have rounded/reference-only dimensions.

| Reference | Used for |
|---|---|
| [Raspberry Pi 4 mechanical drawing](https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf) | Common 40-pin/header and mount reference positions; not the add-on outline itself. |
| [Raspberry Pi GPIO documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#gpio-and-the-40-pin-header) | Physical/BCM aliases, ID pins and GPIO voltage context. |
| [Raspberry Pi HAT+ specification](https://datasheets.raspberrypi.com/hat/hat-plus-specification.pdf) | Why a mating outline alone is not compliance; EEPROM, power and clearance review. |
| [Uno R3 pinout](https://docs.arduino.cc/resources/pinouts/A000066-full-pinout.pdf) | Contact order, analog/digital/bus aliases. |
| [Uno R3 user manual](https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf) | Nominal mechanical envelope and mounting reference. |
| [Legacy KiCad Uno R3 footprint](https://raw.githubusercontent.com/KiCad/kicad-footprints/master/Module.pretty/Arduino_UNO_R3.kicad_mod) | Cross-check of perimeter bank positions; old coordinates are rounded. Its text description is not relied on for pin function. |
| [MKR Zero pinout](https://docs.arduino.cc/resources/pinouts/ABX00012-full-pinout.pdf) | Shared 28-pin interface order and signal aliases. |
| [MKR WiFi 1010 user manual](https://docs.arduino.cc/resources/datasheets/ABX00023-datasheet.pdf) | Representative envelope, nominal header-center/edge and hole offsets, variant-specific power caution. |

The templates are independently authored parametric definitions. No downloaded
board imagery, trademarks/logos, complete third-party CAD libraries or binary
models are bundled. Product names identify intended interfaces, not endorsement.

## Project and export compatibility

Native **schema 2** retains all platform metadata, labels and linked holes.
v1.1 migrates schema-1 files; v1.0 rejects schema 2 rather than dropping unknown
NPTH geometry. Save a backup before upgrading, and keep using v1.1 for new saves.

Gerber and Excellon are actual two-layer PCB output. KiCad subset export keeps
pad and hole positions; linked holes become separate footprints, and aliases /
platform-reference metadata are not reconstructed on reimport. Retain native
JSON as the authoritative editable project. Six starter JSON files are included
in `examples/` and can be opened without depending on a remotely updated library.
