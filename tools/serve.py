#!/usr/bin/env python3
"""Serve the repository on loopback only; not a production web server."""
from __future__ import annotations
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('--port must be between 1 and 65535')
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    try:
        with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
            print(f'COPPERBENCH: http://127.0.0.1:{args.port}/ (Ctrl+C to stop)', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    except OSError as error:
        parser.exit(1, f'Cannot start local server: {error}\nTry another --port.\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
