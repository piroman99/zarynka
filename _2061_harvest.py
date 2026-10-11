#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Харвестер иллюстраций конкурса «Зарянка» (2061.su): страница -> картинка -> чанк-дамп."""
import os, re, json, subprocess, sys, hashlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://2061.su'
CHUNK = 8192
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

def curl(url, extra=None, timeout=60):
    cmd = ['curl', '-sk', '-m', str(timeout), '-A', UA]
    if extra:
        cmd += extra
    cmd.append(url)
    return subprocess.run(cmd, capture_output=True)

def get_page(path):
    p = curl(BASE + path, timeout=45)
    return p.stdout.decode('utf-8', 'replace')

def img_url_from_page(html):
    m = re.search(r'align="middle"\s+src="(/media/cache/[^"]+\.(?:jpg|jpeg|png))"', html)
    if not m:
        m = re.search(r'<img[^>]+src="(/media/cache/[^"]+\.(?:jpg|jpeg|png))"', html)
    return m.group(1) if m else None

def author_from_page(html):
    a = re.search(r'class="author"[^>]*>(.*?)</div>', html, re.S)
    if not a:
        a = re.search(r'<title>(.*?)</title>', html, re.S)
    if not a:
        return ''
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', a.group(1))).strip()

def content_length(url):
    p = curl(url, extra=['-I'], timeout=45)
    for line in p.stdout.decode('utf-8', 'replace').splitlines():
        if line.lower().startswith('content-length:'):
            return int(line.split(':')[1].strip())
    return None

def ranged_download(url, dest, maxlen=8_000_000):
    total = content_length(url)
    if total is None:
        p = curl(url, timeout=90)
        open(dest, 'wb').write(p.stdout)
        return len(p.stdout)
    if total > maxlen:
        print('    ! слишком большой, пропуск', total); return 0
    buf = bytearray()
    start = 0
    tries = 0
    while start < total and tries < 40:
        end = min(start + CHUNK - 1, total - 1)
        p = curl(url, extra=['-H', f'Range: bytes={start}-{end}'], timeout=60)
        got = p.stdout
        if not got:
            tries += 1; time.sleep(0.5); continue
        buf += got
        start += len(got)
    open(dest, 'wb').write(buf)
    return len(buf)

def main():
    slugs_file = sys.argv[1]
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    items = json.load(open(slugs_file, encoding='utf-8'))
    manifest = []
    for idx, item in enumerate(items, 1):
        path = item['path'] if isinstance(item, dict) else item
        slug = path.strip('/').split('/')[-1]
        tag = path.strip('/').split('/')[-2]  # iwork | work
        fn = f'{idx:03d}_{tag}_{slug}.jpg'
        dest = os.path.join(outdir, fn)
        if os.path.exists(dest) and os.path.getsize(dest) > 30000 and open(dest, 'rb').read()[-2:] == b'\xff\xd9':
            print(f'  [{idx}] skip {slug} (есть)'); continue
        html = get_page(path)
        iu = img_url_from_page(html) if html and 'Wayback' not in html[:200] else None
        if not iu and '/iwork/' in path:
            alt = path.replace('/iwork/', '/work/')
            html = get_page(alt)
            iu = img_url_from_page(html) if html else None
            if iu:
                path = alt
                tag = 'work'
        if not iu:
            print(f'  [{idx}] нет картинки {slug}'); continue
        author = author_from_page(html)
        n = ranged_download(BASE + iu, dest)
        ok = n and open(dest, 'rb').read()[-2:] == b'\xff\xd9'
        print(f'  [{idx}] {slug}: {n}B EOI={ok} | {author}')
        manifest.append({'n': idx, 'slug': slug, 'tag': tag, 'file': fn,
                         'author': author, 'page': BASE + path, 'src': iu, 'bytes': n})
    mf = os.path.join(outdir, 'manifest.json')
    if os.path.exists(mf):
        old = json.load(open(mf, encoding='utf-8'))
        seen = {(x['slug'], x['tag']) for x in manifest}
        manifest = [x for x in old if (x['slug'], x['tag']) not in seen] + manifest
    json.dump(manifest, open(mf, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('итого в манифесте:', len(manifest))

if __name__ == '__main__':
    main()
