#!/usr/bin/env python3
"""Check generated files, source syntax, local documentation links and vendor integrity."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote
from package import ROOT, generate


def main() -> int:
    failures: list[str] = []
    def check(ok: bool, message: str) -> None:
        if not ok:
            failures.append(message)
    required = ['index.html', 'README.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md',
                '.github/workflows/ci.yml', '.github/workflows/pages.yml', '.github/workflows/release.yml',
                'CONTRIBUTING.md', 'SECURITY.md', 'CHANGELOG.md', 'requirements-dev.txt', '.nojekyll',
                'docs/GITHUB.md', 'docs/DEPLOYMENT.md', 'docs/TESTING.md']
    for name in required:
        check((ROOT / name).is_file(), f'Missing required file: {name}')
    for name, data in generate().items():
        check((ROOT / name).is_file() and (ROOT / name).read_bytes() == data, f'Stale generated file: {name}; run tools/package.py')
    package = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))
    model = (ROOT / 'src/core.js').read_text(encoding='utf-8')
    check(f"C.VERSION='{package['version']}'" in model, 'package.json and model versions disagree')
    node = shutil.which('node')
    if not node:
        failures.append('Node.js is required for JavaScript syntax checks')
    else:
        for path in sorted((ROOT / 'src').glob('*.js')) + [ROOT / 'sw.js', ROOT / 'tests/core.test.js', ROOT / 'tests/platforms.test.js']:
            run = subprocess.run([node, '--check', str(path)], text=True, capture_output=True)
            check(run.returncode == 0, f'JavaScript syntax error: {path.relative_to(ROOT)}\n{run.stderr}')
    for path in list((ROOT / 'tools').glob('*.py')) + list((ROOT / 'tests').glob('*.py')):
        try:
            compile(path.read_text(encoding='utf-8'), str(path), 'exec')
        except SyntaxError as error:
            failures.append(f'Python syntax error: {error}')
    for name, sha in json.loads((ROOT/'tools/vendor-manifest.json').read_text())['files'].items():
        check(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, f'Vendor file changed without manifest review: {name}')
    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    check(f"v{package['version']}" in index, 'Visible header version disagrees with package.json')
    lock = json.loads((ROOT / 'package-lock.json').read_text())
    check(lock['version'] == package['version'] == lock['packages']['']['version'], 'Lockfile version disagrees with package.json')
    for ref in re.findall(r'(?:src|href)="([^"]+)"', index):
        if not ref.startswith(('#', 'data:', 'http:', 'https:')):
            check((ROOT / ref).is_file(), f'Broken runtime asset: {ref}')
    for path in list(ROOT.glob('*.md')) + list((ROOT / 'docs').rglob('*.md')) + list((ROOT / 'examples').glob('*.md')):
        text = path.read_text(encoding='utf-8')
        for ref in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text):
            ref = ref.split(' "', 1)[0].split('#', 1)[0]
            if not ref or '://' in ref or ref.startswith(('mailto:', '#')):
                continue
            check((path.parent / unquote(ref)).exists(), f'Broken local link in {path.relative_to(ROOT)}: {ref}')
    if failures:
        print('\n'.join('FAIL: ' + item for item in failures))
        return 1
    print('PASS: repository files, generated assets, source syntax, local links and bundled dependency hashes.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
