# Everyday maker parts — COPPERBENCH v1.4.0

**v1.6.1 navigation:** catalog buttons are shortened; see the [current interface guide](QUIET_WORKBENCH.md). All workflows described here remain.

## What ships

The existing 36 entries remain available. v1.4 adds **134 mechanical/device variants in 17 families**, for **170 total library entries**. Variant count is not a count of independently qualified purchased components. Some entries identify a manufacturer and device; others are explicitly generic parametric templates. None has been physically fit-tested in this release.

| Family | New variants |
|---|---:|
| Single-row headers, sockets, right-angle headers | 30 |
| Dual-row headers, sockets and shrouded headers | 21 |
| Screw terminals, 3.5 and 5.08 mm pitch | 12 |
| JST PH, XH and SH | 14 |
| Qwiic / STEMMA QT interface preset | 1 |
| USB-C, generic switched barrel jack, battery wire pads | 3 |
| DIP, slide and momentary switches | 7 |
| Trimmer, rotary potentiometer, push-switch encoder | 3 |
| Axial resistor lead spacings | 4 |
| Polarized radial capacitor sizes/pitches | 5 |
| Axial diode and SMA protection-diode templates | 4 |
| Resettable fuse and cartridge-holder templates | 2 |
| NPN/PNP, MOSFET and relay entries | 4 |
| Fixed LM1117 and LM7805 regulator entries | 3 |
| Named IC/package combinations | 8 |
| Through-hole, SMD, RGB and addressable LED templates | 7 |
| Jumpers, wire-loop test points and clip pad | 6 |

The Uno ICSP option adds **six contacts to an existing platform part**, not six unrelated library components. Pico/Nano/ESP32/Feather/XIAO carriers and reviewed circuit blocks remain later roadmap work.

## Choose and place

Open **Parts → Everyday maker parts**. Select a family and a variant; search also matches manufacturer names, package identifiers and functional pin labels. The native list supports keyboard navigation. **Place selected part** arms the normal placement tool: click the board, R to rotate, Escape to finish. Drawer search offers directly draggable matches. With no search, families are grouped instead of flooding the drawer with duplicate-looking cards.

**Examples → Everyday maker sampler** is an unconnected layout of 14 representative parts. It demonstrates the library, not an electrically complete circuit. `examples/uno-r3-shield-icsp.json` demonstrates the optional Uno interface.

## Named pins and polarity

Select a part and use **Functional pin names**. The inspector and pin table identify terminals, and selected parts have editor-only functional captions. Editing a label does not change its physical number, location, polarity role or net. Names such as GND/VCC/VIN are not automatic net assignments. Existing plane-connection and via tools operate on these same real pads.

The named devices are TI NE555, LM358 and SN74HC595 in PDIP and SOIC; Microchip MCP23017-E/SP; TI ULN2803CDW; TI fixed LM1117 variants and LM7805; and onsemi 2N3904/2N3906. These are nominal land patterns with referenced pin maps, not a claim that every package variant is interchangeable. The ULN2803C DW entry has **20 terminals**, not the 18-terminal ULN2803A layout. MCP23017 uses the narrow 28-terminal SPDIP reference, not the SPI MCP23S17 map.

Diode/LED A/K and polarized-capacitor +/− remain actual silkscreen markings. **Functional captions are editor-only** and do not appear unexpectedly in Gerbers. Use silkscreen tools to print additional signal names. The v1.3.1 silkscreen compositing correction is retained.

## Device notes and review

**Part reference, notes & pin-map CSV** shows the selected identity, source links, variant-specific cautions and any documented internally common terminals. Source pages open only when explicitly clicked; the app otherwise runs without network access. JSON embeds all geometry and metadata, so library updates never silently replace a saved footprint.

**I checked the footprint** records the user's review. It is not a COPPERBENCH certification or proof of physical fit, electrical operation or manufacturer approval. Pin-name or footprint edits clear this acknowledgement. The separate manufacturer-specific notes remain available after acknowledgement.

### Internally common terminals

The fixed LM1117 output pin/tab, USB shell tabs, wire-loop endpoints and the explicitly assumed same-side button pairs carry `internalGroups` metadata. Assigning different nets within a group yields a blocking design finding. This does **not** create invisible PCB copper, automatically merge nets, or count two disconnected pads as routed. The library is not a switch-state simulator.

The selected generic switch pattern must be checked against the real switch. No permanent common group joins a switch's two switched contacts. Open jumpers remain open; no shunt/solder bridge is modeled as copper.

## Optional Uno R3 ICSP

Open **HATs, shields & carriers → Arduino Uno R3** and enable **Include Uno R3 ICSP 2×3 header**. Both new-board and current-board placement support it. Existing Uno parts also expose **Optional ICSP header** in the inspector. The original six platform entries and default 32-contact Uno template are unchanged until explicitly enabled.

The extra contacts are appended, so the original 32 pad indices, pin names, geometry and net assignments do not change. ICSP terminals start unassigned. They follow the same move/rotate/side transform as the host interface. Removing the option is blocked if an ICSP terminal has an assigned net or touches other copper. Removal and addition are undoable.

Nominal USB-left top-view coordinates, mm:

| Physical ICSP pin | Function | X | Y |
|---|---|---:|---:|
| 1 | MISO / D12 | 63.627 | 22.860 |
| 2 | 5V | 66.167 | 22.860 |
| 3 | SCK / D13 | 63.627 | 25.400 |
| 4 | MOSI / D11 | 66.167 | 25.400 |
| 5 | RESET | 63.627 | 27.940 |
| 6 | GND | 66.167 | 27.940 |

Source: Adafruit's `ARDUINOR3_ICSP` numerical footprint in [Adafruit Proto Shield.brd](https://github.com/adafruit/Adafruit-Proto-Shield-PCB/blob/master/Adafruit%20Proto%20Shield.brd), inspected blob `f2d43252b0178a6cafb2e69cdd01e2f61ac964d3`. Eagle Y-up coordinates are transformed by `y = 53.34 − y`; 1.0 mm drills and 1.8 mm pads are used. Cross-reference the [official Uno R3 pinout](https://docs.arduino.cc/resources/pinouts/A000066-full-pinout.pdf). This is the main MCU's header, not the USB-interface processor's programming connector. Check the actual host, header gender and spacer engagement before ordering. No implicit connection to perimeter SPI/power pins is created.

## Important variant limits

**USB-C:** The selected connector is GCT USB4085, with 16 through-hole signal contacts and four plated shell slots. It is only a connector. CC handling, power role, protection, decoupling and data routing remain the user's circuit. The land pattern is numerically adapted from the [KiCad USB4085 reference](https://github.com/KiCad/kicad-footprints/blob/master/Connector_USB.pretty/USB_C_Receptacle_GCT_USB4085.kicad_mod), inspected blob `7e16dba37f91e7797357a0f23e08fa95c5bf9a13`, recentered from datum (2.975, 4.025). Signal pads are **0.68 mm rather than the reference's 0.70 mm**; review this modification. The 0.4 mm contact drills and 0.6 mm-wide shell slots are retained. Slot travel is 1.5/0.8 mm (overall lengths 2.1/1.4 mm). Confirm the chosen fabricator's capability. The representative mating face is local +Y; suggested board edge is local y = 2.075 mm. No automatic cable keepout is enforced.

**JST:** PH uses 2.00 mm, XH 2.50 mm, and SH 1.00 mm pitch. Top-/side-entry and boss/retention variants are not interchangeable. The SH entries include two independently selectable mount tabs. The Qwiic/STEMMA QT entry labels contacts 1 GND, 2 VCC, 3 SDA, 4 SCL but inserts no pull-ups or level shifting. No generic battery polarity is assigned to other JST connectors.

**Generic controls and power:** The barrel jack, MOSFET, relay, switch, potentiometer, encoder, fuse-holder and addressable-LED reference entries are clearly marked nominal. They are not undocumented claims of universal PJ/EC11/Songle/WS2812 compatibility. Choose the actual device, validate its drawing, and edit or replace the footprint. No component rating, logic-level MOSFET suitability, power-supply stability, charging behavior, mains clearance or safety approval is implied.

**Passives:** Body size/pitch are selected separately from value. A given capacitance or resistance does not identify a unique physical package. Surface-mount LED cathode conventions and four-lead RGB orders must be checked against the purchased part.

## File compatibility and upgrade

Native JSON remains **schema 3**, with versioned catalog and optional ICSP metadata. v1.4 reads previous projects without rewriting their embedded parts. Save a backup before upgrading. Older editors do not implement the new catalog review/internal-group checks or ICSP management: use v1.4 for these projects, even when an older editor can display their geometry.

Gerber and Excellon use the same validated geometry engine. KiCad interchange preserves the supported pad/hole/net geometry but does not preserve this catalog metadata, functional labels, internal-group checking or compound ICSP workflow. Its export dialog warns explicitly. Keep native JSON as the lossless master. Rotated plated-slot support remains limited to the previously documented interchange subset.

See [the catalog](MAKER_CATALOG.md), [testing](TESTING.md), [compatibility](COMPATIBILITY.md) and the [polarity/silkscreen guide](POLARITY_AND_SILKSCREEN.md).
