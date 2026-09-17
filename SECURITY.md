# Security and privacy

COPPERBENCH processes projects in the browser. Browser-local storage is not an
encrypted vault. Save independent JSON backups, and avoid opening untrusted
projects on a device containing sensitive work. Image, SVG, native JSON, ZIP and
EDA imports are untrusted inputs even when a project looks harmless.

The repository does not contain credentials, a server API or a telemetry SDK.
Static hosting providers still control their own request logging. GitHub Actions
runs development tests and is separate from the offline application.

## Reporting

Do not post exploit payloads, credentials, or private board designs in a public
issue. Use the repository's **Security → Report a vulnerability** option when
the maintainer has enabled private vulnerability reporting. Otherwise contact
the maintainer privately using a contact they have published. No private contact
address or response-time promise is invented here.

Maintainers should enable private vulnerability reporting before opening the
repository to broad public use. Ordinary non-security bugs belong in Issues.
Include app/browser versions and a minimal non-sensitive reproduction.

## Fabrication is a separate risk

Passing software checks is not manufacturer approval, a circuit-function
certificate, or a safety assessment. Inspect exported files independently,
check purchased-component drawings and the manufacturer's preview, and validate
a small physical coupon before relying on fabrication output.
