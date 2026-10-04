#!/usr/bin/env python3
"""Inventory every rendered heading for editorial line-break review."""
import argparse
import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Headings(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.current = None
    def handle_starttag(self, tag, attrs):
        if re.fullmatch(r'h[1-3]', tag):
            self.current = {'level': tag, 'text': '', 'breaks': []}
        elif self.current and tag == 'br':
            self.current['breaks'].append(len(self.current['text']))
    def handle_data(self, data):
        if self.current is not None:
            self.current['text'] += data
    def handle_endtag(self, tag):
        if self.current and tag == self.current['level']:
            if self.current['text'].strip():
                self.items.append(self.current)
            self.current = None

def inventory():
    paths = json.loads((ROOT/'assets/page-manifest.json').read_text())
    items = defaultdict(lambda: {'levels': set(), 'pages': [], 'breaks': []})
    total = 0
    for path in paths:
        parser = Headings()
        parser.feed((ROOT/path).read_text())
        for row in parser.items:
            text = row['text'].strip()
            item = items[text]
            item['levels'].add(row['level'])
            if path not in item['pages']:
                item['pages'].append(path)
            item['breaks'] = row['breaks']
            total += 1
    return paths, total, items

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--minimum', type=int, default=16)
    args.add_argument('--check', action='store_true', help='Fail for unreviewed long titles, for the build pipeline')
    opts = args.parse_args()
    paths, total, items = inventory()
    print(f'{len(paths)} pages / {total} headings / {len(items)} unique titles')
    if opts.check:
        from typography import TitleTypography
        composer = TitleTypography(ROOT)
        missing = [text for text in items if len(composer.core(text)[0]) >= 10 and composer.core(text)[0] not in composer.plans]
        if missing:
            raise SystemExit('Add editorial title plans before publishing:\n'+'\n'.join(missing))
        print('PASS: every current title of ten or more characters has an editorial phrase plan.')
        raise SystemExit(0)
    for text, info in sorted(items.items(), key=lambda x: (-len(x[0]), x[0])):
        if len(text) >= opts.minimum:
            print(json.dumps({'n':len(text), 'heading':text, 'levels':sorted(info['levels']), 'page':info['pages'][0], 'breaks':info['breaks']}, ensure_ascii=False))
