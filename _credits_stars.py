# -*- coding: utf-8 -*-
"""Мерцающие звёзды в титрах — чистый CSS, без картинок (0 ₽, 0 КБ трафика).

Генерит блок .cr-stars (три слоя точек через radial-gradient + своя частота
мерцания) и вставляет его в vn2/style.css между маркерами STARS:BEGIN/END.
Повторный запуск перегенерирует блок на месте.
"""
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = os.path.join(HERE, 'vn2', 'style.css')

# слой: (точек, радиус px, яркость, длительность мерцания с, задержка с)
LAYERS = [(84, 1.1, 0.55, 9.5, 0.0),
          (46, 1.5, 0.72, 6.4, 1.7),
          (20, 2.1, 0.9, 4.6, 0.8)]

random.seed(20610)          # фиксируем — картинка звёзд одна и та же при пересборке

blocks = []
for i, (n, r, a, dur, delay) in enumerate(LAYERS):
    dots = []
    for _ in range(n):
        x = round(random.uniform(1, 99), 2)
        y = round(random.uniform(1, 99), 2)
        # звёзды чуть голубоватые и тёплые вперемешку — «грустное» небо
        tint = random.choice(['255,255,255', '214,226,255', '255,240,214'])
        dots.append('radial-gradient(%.1fpx %.1fpx at %s%% %s%%, rgba(%s,%.2f) 0 55%%, '
                    'rgba(%s,0) 56%%)' % (r, r, x, y, tint, a, tint))
    blocks.append('.cr-stars .l%d{background-image:%s;\n'
                  '  animation:crTwinkle %ss ease-in-out %ss infinite alternate}'
                  % (i, ', '.join(dots), dur, delay))

STARS = """/* STARS:BEGIN — сгенерировано _credits_stars.py, руками не править */
.cr-stars{position:absolute; inset:0; pointer-events:none; z-index:0; opacity:.9}
.cr-stars i{position:absolute; inset:0; display:block; will-change:opacity}
%s
@keyframes crTwinkle{
  from{opacity:.35}
  to{opacity:1}
}
@media (prefers-reduced-motion: reduce){
  .cr-stars i{animation:none!important}
}
/* STARS:END */
""" % '\n'.join(blocks)

src = open(CSS, encoding='utf-8').read()
if '/* STARS:BEGIN' in src:
    a = src.index('/* STARS:BEGIN')
    b = src.index('/* STARS:END */') + len('/* STARS:END */')
    src = src[:a] + STARS.rstrip('\n') + src[b:]
    print('блок звёзд заменён')
else:
    anchor = '#credits{z-index:25;'
    i = src.index(anchor)
    j = src.index('}', i) + 1
    src = src[:j] + '\n' + STARS + src[j:]
    print('блок звёзд добавлен после #credits')
open(CSS, 'w', encoding='utf-8').write(src)
print('style.css', os.path.getsize(CSS), 'байт')
