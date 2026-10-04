#!/usr/bin/env python3
"""Loopback-only preview with the same /ways.home/ prefix as GitHub Pages."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path):
        clean = urlsplit(path).path
        if clean.startswith('/ways.home/'):
            clean = clean[len('/ways.home/'):]
        clean = unquote(clean).lstrip('/') or 'index.html'
        target = (ROOT / clean).resolve()
        if not target.is_relative_to(ROOT) or any(x.startswith('.') for x in Path(clean).parts):
            return str(ROOT / '__not_found__')
        return str(target)

    def list_directory(self, path):
        self.send_error(403, 'Directory listings are disabled')
        return None

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, format, *args):
        if len(args) > 1 and str(args[1]) not in ('200', '304'):
            super().log_message(format, *args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8785)
    args = parser.parse_args()
    with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
        print(f'Preview: http://127.0.0.1:{args.port}/ways.home/', flush=True)
        server.serve_forever()
