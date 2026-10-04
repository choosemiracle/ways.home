#!/usr/bin/env python3
"""Download the explicitly curated, reusable image assets; never download videos."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
media = json.loads((ROOT / 'content/media.json').read_text(encoding='utf-8'))

def fetch(item):
    path = ROOT / item['file']
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        request = Request(item['download'], headers={'User-Agent':'WaysHome educational resource archive/4.0'})
        with urlopen(request, timeout=45) as response:
            if not response.headers.get('Content-Type','').startswith('image/'):
                raise ValueError('Not an image: ' + item['id'])
            data = response.read(8_000_001)
        if len(data) > 8_000_000 or not data.startswith(b'\xff\xd8'):
            raise ValueError('Unexpected image size/type: ' + item['id'])
        path.write_bytes(data)
    data = path.read_bytes()
    return {'id':item['id'],'file':item['file'],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'source':item['download'],'rights':item['rights'],'rights_url':item['rights_url']}

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=5) as pool:
        records = list(pool.map(fetch,media['images']))
    (ROOT / 'assets/media/manifest.json').write_text(json.dumps({'checked':media['checked'],'images':records},ensure_ascii=False,indent=2),encoding='utf-8')
    for record in records: print(record['id'], record['bytes'], 'bytes')
