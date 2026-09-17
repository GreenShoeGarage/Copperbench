# Publish the repository on GitHub

**Suggested repository name: `copperbench`.** This package is a source tree, not
an already-published remote repository. It contains no Git history, remote URL,
credentials, account binding or custom-domain configuration.

## Create and upload

Create an empty GitHub repository named `copperbench` under the account or
organization you choose. Choose its visibility deliberately. Do not initialize
a second README or license if you will push this complete tree.

Extract the source ZIP and open its `copperbench` folder. The **contents** of that
folder belong at the repository root: `index.html` and `README.md` should not end
up inside another release-named subfolder. Include hidden files, especially
`.github/`, `.gitignore`, `.gitattributes` and `.nojekyll`.

GitHub Desktop can publish an existing local repository. From a terminal,
replace `YOUR-ACCOUNT` with your chosen account or organization:

```sh
cd copperbench
git init -b main
git add .
git commit -m "Add COPPERBENCH v1.1.0"
git remote add origin https://github.com/YOUR-ACCOUNT/copperbench.git
git push -u origin main
```

Use GitHub's normal authentication; do not put tokens in files or remote URLs.
Upload extracted files, not just the release ZIP. If using the web upload UI,
confirm the hidden `.github` directory was included.

## What runs after upload

The **CI** workflow checks source/asset consistency, repository packaging,
JavaScript geometry/routing/interchange, independent manufacturing geometry and
the Chromium interaction harness. It saves new results and screenshots as an
Actions artifact. The browser suite deliberately uses simulated origin storage
and intercepted downloads; see [testing](TESTING.md).

GitHub Pages is **off by default in the workflow**, so an ordinary source push
does not try to publish a site before you configure Pages. To publish the app,
follow [deployment](DEPLOYMENT.md). No secret is needed for the standard Pages
workflow; the jobs use the repository's provided GitHub token with limited
permissions.

The **Draft release** workflow runs when you deliberately push a version tag.
It checks that the tag matches `package.json`, runs CI, and prepares a draft
GitHub Release containing the source ZIP, static ZIP, portable HTML and SHA-256
checksums. It does not publish the draft for you. For the current app:

```sh
git tag -a v1.1.0 -m "COPPERBENCH v1.1.0"
git push origin v1.1.0
```

Review the resulting draft's files and notes before publishing. A rerun will
fail if a release for that tag already exists rather than silently overwrite it.
Do not reuse an existing published tag for changed application code.

## Repository settings to review

Use `main` as the default branch to match the provided Pages workflow. Enable
private vulnerability reporting before inviting public use. Consider branch
protection requiring the CI checks. Decide which contributors may trigger
releases or approve deployments. Set a description such as:

> A local-first, tactile two-layer PCB workbench with representative 3D parts,
> assisted routing, JSON backups, and Gerber/Excellon export.

Suggested topics: `pcb`, `eda`, `gerber`, `excellon`, `electronics`, `offline`,
`local-first`, `javascript`, `field-instrument`.

## References

GitHub's documented custom Pages workflow and permissions:
https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

GitHub Pages source configuration:
https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

GitHub CLI draft-release command:
https://cli.github.com/manual/gh_release_create

These instructions configure future user-controlled repository actions. No
remote repository, deployment or GitHub Actions execution was created during
local packaging.
