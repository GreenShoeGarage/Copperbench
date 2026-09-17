# Run or host COPPERBENCH

## Portable HTML

Open `COPPERBENCH-portable.html` in a desktop browser. The application, ZIP
library and worker source are embedded. No Node, Python, internet connection or
build step is required to use this edition. File-origin storage behavior varies;
keep independent **Save JSON** backups rather than relying on browser autosave.

## Local static server

From the repository root:

```sh
python3 tools/serve.py
```

Open `http://127.0.0.1:8000/`. To use a different port:

```sh
python3 tools/serve.py --port 8080
```

On Windows, `py -3` can replace `python3`. The server binds only to loopback,
serves this checkout, and is for development—not public production hosting.

## GitHub Pages

After pushing the complete repository, open **Settings → Pages**. Under
**Build and deployment**, set **Source** to **GitHub Actions**. Then open
**Actions → Deploy GitHub Pages → Run workflow** and select `main`.

The workflow runs the checks, stages only public application files, uploads the
Pages artifact and deploys it through the `github-pages` environment. The
successful deployment reports the real URL; the repository does not assume an
account name or invent a live address. For project Pages sites, relative asset
paths support a repository subdirectory.

To deploy future pushes to `main` automatically, add the repository Actions
**variable** `ENABLE_PAGES` with the value `true` under
**Settings → Secrets and variables → Actions → Variables**. It is not a secret.
Without that variable, deployment is manual. CI still runs for ordinary pushes
and pull requests. Pages is optional and subject to your account/repository
settings; uploading this ZIP alone does not enable it.

Source: GitHub's [custom workflow guide](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
and [publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Any static host, including an existing website

Generate a clean deployment folder:

```sh
python3 tools/release.py --site-only
```

Upload the **contents of `dist/site/`** to the desired directory, such as
`mbparks.com/copperbench/`. This is an example target, not a claim of an existing
deployment. The generated static ZIP contains the same public files at its root.
Keep `src/`, `vendor/` and the other folders intact. No server routes, build
command, database, CDN or environment variables are required.

The deployment folder contains `index.html`, `styles.css`, `src/`, `vendor/`,
`icon.svg`, `manifest.webmanifest`, `sw.js`, the portable HTML, examples and
license notices. Tests, workflows, development tools and test output are not
published. No `CNAME` is included, so uploading the repo does not point a domain
somewhere unexpected.

## Offline behavior and updates

The hosted service worker is designed to cache the application shell. Installation
requires an appropriate secure browser context, normally HTTPS or localhost.
Examples in the `examples/` directory are not pre-cached; the app's built-in
examples are part of the bundled source.

After changing source, run `python3 tools/package.py` and commit all generated
changes. The cache revision derives from the runtime files, so it changes when
the app changes even without a manually edited cache counter. Cache ownership
is scoped to the deployment URL, avoiding cross-deletion between new-format
COPPERBENCH deployments. Old pre-repackaging cache names are not deleted
indiscriminately and may remain until removed through browser site-data tools.

If an update seems stale, save a JSON backup first, close older tabs and reload.
Clearing browser site data can remove both caches and saved projects. Do not
clear it casually. The provided browser harness does not validate the actual
hosted install/update/offline lifecycle; verify that on the final deployment.

A strict Content Security Policy must accommodate the app's blob workers and
portable inline source. This package does not claim compatibility with arbitrary
host policies. See [verification limits](TESTING.md).
