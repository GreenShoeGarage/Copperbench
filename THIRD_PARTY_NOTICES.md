# Third-party notices

The only bundled runtime dependency is **JSZip 3.10.1** (`vendor/jszip.min.js`), used for local project and fabrication ZIPs. It is distributed under its MIT license option. The original full license is included at `vendor/JSZIP-LICENSE.md`; its attribution also appears in the minified source.

Original JSZip copyright: Stuart Knightley, David Duponchel, Franz Buchinger and António Afonso (2009–2016). See the retained license for its complete terms.

Playwright, Chromium and Shapely were used as development/test tools but are not redistributed in this app. No external fonts, KiCad footprint library, 3D component model collection or online service SDK is bundled. The original application license does not replace the dependency's retained license.

### v1.4 engineering references

Maker definitions are original parametric code and numerical pin/land-pattern transcriptions; no manufacturer PDFs, commercial 3D assets or complete third-party footprint files are bundled. Source attribution and reviewed blob identifiers for the KiCad USB4085 and Adafruit Uno ICSP numerical references are in `docs/MAKER_PARTS.md`; per-device reference URLs are in `docs/MAKER_CATALOG.md` and each embedded part. These references do not imply endorsement, physical qualification, or ownership of the named brands. Existing vendor-code license notices remain unchanged.

## Adafruit module interface reference data (v1.6)

Selected header/mounting-center data in `src/modules.js` are adapted from Adafruit
Industries' published CAD under **CC BY-SA 3.0**. The source paths, blob hashes,
coordinate changes, attribution and retained supplier text are in
[MODULE-NOTICES.txt](MODULE-NOTICES.txt) and
[the source ledger](docs/MODULES_AND_BLOCKS.md). No supplier images or logos are
bundled. The main application and original circuit examples remain MIT; this is
not an Adafruit endorsement or manufacturing qualification.
