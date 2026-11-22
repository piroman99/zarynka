# -*- coding: utf-8 -*-
"""Проверка новых файлов на секреты перед публикацией в публичный репозиторий."""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PATTERNS = [
    ('приватный IP', re.compile(r'\b192\.168\.\d+\.\d+\b')),
    ('ssh-ключ', re.compile(r'\.ssh/[\w.-]+')),
    ('Bearer-токен', re.compile(r'Bearer\s+[A-Za-z0-9._-]{16,}')),
    ('ключ sk-', re.compile(r'\bsk-[A-Za-z0-9]{16,}')),
    ('VK-токен', re.compile(r'vk1\.a\.\w{20,}')),
    ('TG-токен', re.compile(r'\b\d{8,10}:[A-Za-z0-9_-]{30,}')),
    ('pv_key', re.compile(r'pv_key')),
    ('api_key=', re.compile(r'api_key\s*=\s*[\'"][^\'"]{12,}')),
]

hits = {}
for base, dirs, files in os.walk(HERE):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if not f.endswith(('.py', '.md', '.json', '.txt', '.sh')):
            continue
        p = os.path.join(base, f)
        try:
            if os.path.getsize(p) > 2_000_000:
                continue
            with open(p, encoding='utf-8', errors='ignore') as fh:
                txt = fh.read()
        except OSError:
            continue
        for label, pat in PATTERNS:
            m = pat.search(txt)
            if m:
                hits.setdefault(label, []).append((os.path.relpath(p, ROOT), m.group(0)[:40]))

for label, rows in hits.items():
    print('%s: %d файлов' % (label, len(rows)))
    for path, sample in rows[:5]:
        print('   %-46s %s' % (path, sample))
if not hits:
    print('подозрительного не найдено')
