"""Standard-library regression checks for the GitHub/static distribution."""
from pathlib import Path
import json
import re
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import package as builder
import release


class PackagingTests(unittest.TestCase):
    def test_generated_files_match_sources(self):
        for name, content in builder.generate().items():
            self.assertEqual((ROOT / name).read_bytes(), content, name)

    def test_generation_is_deterministic(self):
        self.assertEqual(builder.generate(), builder.generate())

    def test_portable_has_no_external_runtime_tags(self):
        text = builder.generate()['COPPERBENCH-portable.html'].decode()
        self.assertNotRegex(text, r'<script\s+src=')
        self.assertNotIn('<link rel="stylesheet"', text)
        self.assertNotIn('<link rel="manifest"', text)
        self.assertIn('window.CB_PORTABLE=true', text)
        self.assertIn('MIT License', text)
        self.assertIn('JSZip', text)

    def test_embedded_worker_is_current(self):
        text = builder.generate()['src/worker-source.js'].decode()
        worker = json.loads(text.split('window.CB_WORKER_SOURCE=', 1)[1].strip().rstrip(';'))
        for name in ['core.js', 'geometry.js', 'font.js', 'platforms.js', 'router.js', 'planes.js', 'worker-entry.js']:
            self.assertIn((ROOT/'src'/name).read_text(encoding='utf-8'), worker)

    def test_cache_revision_tracks_contents(self):
        before = builder.generate()['sw.js']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release.stage_site(root)
            shutil.copy2(ROOT/'package.json', root/'package.json')
            with (root/'styles.css').open('a', encoding='utf-8') as target:
                target.write('\n/* packaging regression */\n')
            after = builder.generate(root)['sw.js']
        self.assertNotEqual(before, after)

    def test_cache_is_owned_by_deployment_scope(self):
        worker = builder.generate()['sw.js'].decode()
        self.assertIn("self.registration.scope", worker)
        self.assertIn('key.startsWith(PREFIX)', worker)
        self.assertIn('caches.open(CACHE).then(cache => cache.match', worker)
        self.assertNotIn('caches.match(event.request)', worker)

    def test_source_archive_includes_hidden_config_not_outputs(self):
        paths = {p.relative_to(ROOT).as_posix() for p in release.repository_files()}
        self.assertIn('.github/workflows/ci.yml', paths)
        self.assertIn('.github/workflows/pages.yml', paths)
        self.assertIn('.gitignore', paths)
        self.assertIn('docs/images/routed-bench.png', paths)
        for path in paths:
            self.assertFalse(path.startswith(('tests/output/', 'dist/', '.git/', '.venv/', 'node_modules/', 'local-projects/')))

    def test_site_is_runnable_and_does_not_publish_developer_files(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            release.stage_site(destination)
            self.assertTrue((destination/'index.html').is_file())
            self.assertTrue((destination/'src/app.js').is_file())
            self.assertTrue((destination/'vendor/JSZIP-LICENSE.md').is_file())
            for ref in re.findall(r'(?:src|href)="([^"]+)"', (destination/'index.html').read_text(encoding='utf-8')):
                if not ref.startswith(('#', 'data:', 'http:', 'https:')):
                    self.assertTrue((destination/ref).is_file(), ref)
            for name in ['tests', '.github', 'tools', 'package.json']:
                self.assertFalse((destination/name).exists())

    def test_archive_is_reproducible_and_paths_are_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a.zip', Path(directory)/'b.zip'
            files = [ROOT/'README.md', ROOT/'.github/workflows/ci.yml']
            release.create_zip(a, files, ROOT, 'copperbench')
            release.create_zip(b, list(reversed(files)), ROOT, 'copperbench')
            self.assertEqual(a.read_bytes(), b.read_bytes())
            with zipfile.ZipFile(a) as archive:
                self.assertIsNone(archive.testzip())
                for name in archive.namelist():
                    self.assertTrue(name.startswith('copperbench/'))
                    self.assertNotIn('..', Path(name).parts)
                    self.assertFalse(name.startswith('/'))


if __name__ == '__main__':
    unittest.main()
