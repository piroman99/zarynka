# -*- coding: utf-8 -*-
"""Какие vo-файлы лежат в vn2/audio/vo, но ни одним СЕГМЕНТОМ не используются."""
import os

import _vo_util as U

content = U.load_content()
used = {os.path.basename(vo) for _, _, vo, _, _ in U.segments(content)}
allf = {f for f in os.listdir(U.VO) if f.endswith('.mp3')}
print('файлов: %d, используется: %d' % (len(allf), len(used)))
orph = sorted(allf - used)
print('сироты (%d): %s' % (len(orph), ', '.join(orph) or '-'))
man = U.load_manifest()
extra = [k for k in man if os.path.basename(k) not in used]
print('лишних записей в манифесте: %d' % len(extra))
