import os, shutil

REJ = 'assets/rejected/s7'
os.makedirs(REJ, exist_ok=True)

MOVES = [
    ('assets/gen/prologfin_s7_0.jpg', 'prologfin_s7_0.jpg',
     '2026-10-18 · старая проходная (КПП, вахтёр, туман, мальчик с ракетой на плечах): '
     'место не то, ворот в кадре второй раз, очередь-река.'),
    ('assets/gen/s7_gpt_a_0.png', 's7_gpt_a_0.png',
     '2026-10-18 · верхний ракурс, очередь-река по аллее: «слишком много народа, хоть вдвое меньше».'),
    ('assets/gen/s7_gpt_b_0.png', 's7_gpt_b_0.png',
     '2026-10-18 · вид от ворот вниз по аллее: «слишком много народа», «лишние ворота», '
     '«это не та местность» (городской силуэт, река с мостом, купол-павильон).'),
]

for src, dst, why in MOVES:
    if os.path.exists(src):
        shutil.move(src, os.path.join(REJ, dst))
        print('archived', src, '->', dst)
    else:
        print('нет файла', src)

md = os.path.join(REJ, 'REJECTED.md')
head = ('# S7 — отклонённые кадры\n\n'
        'Ничего не удаляем: каждый забракованный вариант лежит здесь с причиной '
        '(решение Ивана, правило проекта).\n\n')
lines = []
if os.path.exists(md):
    lines = open(md, encoding='utf-8').read().splitlines()
new = []
for src, dst, why in MOVES:
    new.append('- **%s** — %s' % (dst, why))
body = '\n'.join(lines) if lines else ''
if not body.startswith('# S7'):
    body = head + '\n'.join(new) + '\n'
else:
    body = body.rstrip() + '\n' + '\n'.join(new) + '\n'
open(md, 'w', encoding='utf-8').write(body)
print(open(md, encoding='utf-8').read())
