#!/usr/bin/env python3
"""Check generated HTML, assets, local links and fragment targets without dependencies."""
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.tags = [], [], Counter()
        self.lang = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags[tag] += 1
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'html':
            self.lang = attrs.get('lang')
        for attr in ('href', 'src'):
            if attr in attrs:
                self.links.append(attrs[attr])


def main():
    manifest = json.loads((ROOT / 'assets/page-manifest.json').read_text())
    docs = {p: Document((ROOT / p).read_text(encoding='utf-8')) for p in manifest}
    errors, checked = [], 0
    for name, doc in docs.items():
        if doc.tags['h1'] != 1 or doc.tags['main'] != 1 or doc.lang != 'zh-CN':
            errors.append(f'{name}: invalid main/h1/language structure')
        duplicates = [key for key, count in Counter(doc.ids).items() if count > 1]
        if duplicates:
            errors.append(f'{name}: duplicate ids {duplicates}')
        for raw in doc.links:
            u = urlsplit(raw)
            if u.scheme or u.netloc:
                if u.scheme not in ('https', 'http', 'mailto'):
                    errors.append(f'{name}: unexpected URL scheme {raw}')
                continue
            if not raw or raw == '#':
                errors.append(f'{name}: empty navigation target')
                continue
            if u.path.startswith('/ways.home/'):
                target = ROOT / unquote(u.path[len('/ways.home/'):])
            elif u.path:
                target = (ROOT / name).parent / unquote(u.path)
            else:
                target = ROOT / name
            target = target.resolve()
            if not target.is_relative_to(ROOT):
                errors.append(f'{name}: link escapes website {raw}')
                continue
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file():
                errors.append(f'{name}: missing {raw}')
                continue
            key = target.relative_to(ROOT).as_posix()
            if u.fragment and key in docs and unquote(u.fragment) not in docs[key].ids:
                errors.append(f'{name}: missing fragment {raw}')
            checked += 1
    index = json.loads((ROOT / 'assets/search-index.json').read_text())
    for item in index:
        if item['url'] not in docs or not item['text']:
            errors.append('Invalid search record: ' + item['url'])
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(docs)} pages, {checked} local links/assets, {len(index)} search records; no missing files, fragments, or duplicate IDs.')


if __name__ == '__main__':
    main()
