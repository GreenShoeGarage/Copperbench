#!/usr/bin/env python3
"""Run the documented checks in dependency order; stop on the first failing suite."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-browser', action='store_true', help='Explicitly omit the Chromium interaction suite')
    args = parser.parse_args()
    node = shutil.which('node')
    if node is None:
        parser.exit(1, 'Node.js 22 or newer is required for engine tests.\n')
    commands = [
        [sys.executable, 'tools/check_repo.py'],
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_packaging.py'],
        [node, 'tests/core.test.js'],
        [node, 'tests/platforms.test.js'],
        [node, 'tests/vias.test.js'],
        [node, 'tests/planes.test.js'],
        [node, 'tests/silkscreen.test.js'],
        [node, 'tests/maker.test.js'],
        [node, 'tests/carriers.test.js'],
        [node, 'tests/modules-blocks.test.js'],
        [node, 'tests/compact-polarity.test.js'],
        [node, 'tests/editing.test.js'],
        [node, 'tests/export-review.test.js'],
        [node, 'tests/casebench-export.test.js'],
        [sys.executable, 'tests/verify_manufacturing.py'],
        [sys.executable, 'tests/verify_platforms.py'],
        [sys.executable, 'tests/verify_vias.py'],
        [sys.executable, 'tests/verify_planes.py'],
        [sys.executable, 'tests/verify_silkscreen.py'],
        [sys.executable, 'tests/verify_maker.py'],
        [sys.executable, 'tests/verify_carriers.py'],
        [sys.executable, 'tests/verify_modules_blocks.py'],
        [sys.executable, 'tests/verify_compact_polarity.py'],
        [sys.executable, 'tests/verify_editing.py'],
    ]
    if not args.skip_browser:
        commands.append([sys.executable, 'tests/browser_test.py'])
        commands.append([sys.executable, 'tests/platform_browser_test.py'])
        commands.append([sys.executable, 'tests/via_browser_test.py'])
        commands.append([sys.executable, 'tests/plane_browser_test.py'])
        commands.append([sys.executable, 'tests/silkscreen_browser_test.py'])
        commands.append([sys.executable, 'tests/maker_browser_test.py'])
        commands.append([sys.executable, 'tests/carrier_browser_test.py'])
        commands.append([sys.executable, 'tests/modules_blocks_browser_test.py'])
        commands.append([sys.executable, 'tests/quiet_ui_browser_test.py'])
        commands.append([sys.executable, 'tests/compact_polarity_browser_test.py'])
        commands.append([sys.executable, 'tests/pan_browser_test.py'])
        commands.append([sys.executable, 'tests/editing_browser_test.py'])
        commands.append([sys.executable, 'tests/casebench_browser_test.py'])
    try:
        for command in commands:
            print('\n> ' + ' '.join(command), flush=True)
            subprocess.run(command, cwd=ROOT, check=True)
    except subprocess.CalledProcessError as error:
        return error.returncode
    print('\nAll requested suites passed.' + (' Browser suite was explicitly skipped.' if args.skip_browser else ''))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
