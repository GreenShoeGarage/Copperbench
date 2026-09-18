#!/usr/bin/env python3
"""Create a clean source ZIP, static-site ZIP, portable HTML and SHA-256 checksums.

Only allowlisted repository content enters the archives. No .git directory,
virtual environment, customer projects or transient test outputs are included.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
from package import ROOT

SOURCE_FILES = (
    '.gitignore', '.gitattributes', '.editorconfig', '.nvmrc', '.python-version', '.nojekyll',
    'index.html', 'styles.css', 'icon.svg', 'manifest.webmanifest', 'sw.js',
    'COPPERBENCH-portable.html', 'package.json', 'package-lock.json', 'requirements-dev.txt',
    'README.md', 'LICENSE', 'MODULE-NOTICES.txt', 'THIRD_PARTY_NOTICES.md', 'CONTRIBUTING.md', 'SECURITY.md', 'CHANGELOG.md'
)
SOURCE_DIRS = ('.github', 'src', 'vendor', 'docs', 'examples', 'tests', 'tools')
SITE_FILES = ('index.html', 'styles.css', 'icon.svg', 'manifest.webmanifest', 'sw.js', '.nojekyll',
              'COPPERBENCH-portable.html', 'LICENSE', 'MODULE-NOTICES.txt', 'THIRD_PARTY_NOTICES.md')
SITE_DIRS = ('src', 'vendor', 'examples')


def repository_files(root: Path = ROOT) -> list[Path]:
    files = {root / name for name in SOURCE_FILES}
    for name in SOURCE_DIRS:
        for path in (root / name).rglob('*'):
            rel = path.relative_to(root)
            if '__pycache__' in rel.parts or (len(rel.parts) > 1 and rel.parts[:2] == ('tests', 'output')):
                continue
            if path.suffix in ('.pyc', '.pyo') or path.is_dir():
                continue
            if path.is_symlink():
                raise ValueError(f'Refusing symlink in source package: {rel}')
            files.add(path)
    for path in files:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f'Missing or unsafe release input: {path.relative_to(root)}')
    return sorted(files)


def create_zip(target: Path, files: list[Path], root: Path, prefix: str = '') -> None:
    """Stable archive paths, order and timestamps make a fixed tree reproducible."""
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            name = (Path(prefix) / path.relative_to(root)).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def stage_site(destination: Path, root: Path = ROOT) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for name in SITE_FILES:
        shutil.copy2(root / name, destination / name)
    for name in SITE_DIRS:
        shutil.copytree(root / name, destination / name, dirs_exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-only', action='store_true', help='Stage dist/site for static hosting only')
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT / 'tools/check_repo.py')], check=True, cwd=ROOT)
    version = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))['version']
    dist = ROOT / 'dist'
    site = dist / 'site'
    if site.exists():
        if site.is_symlink():
            raise ValueError('Refusing symlink at dist/site')
        shutil.rmtree(site)
    stage_site(site)
    if args.site_only:
        print('Static app staged at dist/site/')
        return 0
    source = dist / f'COPPERBENCH-v{version}-github.zip'
    static = dist / f'COPPERBENCH-v{version}-static.zip'
    portable = dist / f'COPPERBENCH-v{version}.html'
    create_zip(source, repository_files(), ROOT, 'copperbench')
    create_zip(static, [p for p in site.rglob('*') if p.is_file()], site)
    shutil.copyfile(ROOT / 'COPPERBENCH-portable.html', portable)
    checksums = '\n'.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name for p in (source, static, portable)) + '\n'
    (dist / 'SHA256SUMS.txt').write_text(checksums, encoding='utf-8')
    print('Release artifacts:')
    for path in (source, static, portable, dist / 'SHA256SUMS.txt'):
        print(f'  {path.name} ({path.stat().st_size:,} bytes)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
