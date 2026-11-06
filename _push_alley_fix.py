# -*- coding: utf-8 -*-
"""Уборка одноразовых проб + коммит правки сцены «аллея» (Иван 2026-11-05).

Коммитим только то, что нужно демо и воспроизводимости: код движка/сборки, новые спрайты
и проп, кадры-исходники, выбранную музыку (alley_mix), статус и скрипты правки.
Зеркало `master` НЕ трогаем — только по слову Ивана.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
ENV = dict(os.environ, GIT_SSH_COMMAND=(
    'ssh -i %s/.ssh/github_ed25519 -o IdentitiesOnly=yes '
    '-o UserKnownHostsFile=%s/.ssh/known_hosts -o StrictHostKeyChecking=no' % (WS, WS)))

# одноразовые пробы (диагностика фона/файлов) — в репозитории не нужны
DROP = ['_dbg_geo.py', '_bg_probe.py', '_sit_files.py', '_prop_check.py', '_seat_sil.py']
for n in DROP:
    p = os.path.join(HERE, n)
    if os.path.exists(p):
        os.remove(p)
        print('удалён', n)

ADD = [
    'vn2/app.js', 'vn2/index.html', 'vn2/style.css', 'vn2/content.js',
    'vn2/img/char', 'vn2/img/prop', 'vn2/img/cg/al_muza.webp',
    'assets/sprites/poet_seat_neutral.png', 'assets/sprites/poet_seat_upset.png',
    'assets/sprites/poet_seat_interested.png', 'assets/sprites/poet_seat_shy.png',
    'assets/sprites/poet_seat_sullen.png', 'assets/sprites/poet_seat_smile.png',
    'assets/sprites/prop_bench.png',
    'assets/gen/bench_long_0.png', 'assets/gen/cg_muza2_0.png', 'assets/gen/_bench_ref.jpg',
    'assets/gen/sit2_neutral_0.png', 'assets/gen/sit_upset_0.png',
    'assets/gen/sit_interested_0.png', 'assets/gen/sit_shy_0.png',
    'assets/gen/sit_sullen_0.png', 'assets/gen/sit_smile_0.png',
    'assets/audio/sketch/alley_mix.mp3',
    'assets/review', '_sat/sheet_alley2.png',
    '_vn2_build.py', '_alley_fix2.py', '_alley_fix4.py', '_alley_fix2_matte.py',
    '_alley_fix_check.py', '_alley_audio.py', '_alley_ascii.py', '_bench_prop.py',
    '_poet_seat_norm.py', '_poet_seat_probe.py', '_shot_alley2.py', '_seat_sizes.py',
    '_prop_alpha.py', '_prop_frame.py', '_silhouette_ascii.py', '_img_glass_price.py',
    'STATUS.md',
]

MSG = """vn2: аллея — скамейка отдельным статичным слоем, 6 эмоций поэта, CG v2, своя тема

Правка по пяти замечаниям Ивана (2026-11-05).

1. Скамейка больше не часть спрайта поэта — это статичный предмет сцены:
   новый слой #props (z-index между фоном и персонажами), поле узла nd.prop и
   applyProp() в движке; проп снимается на странице CG и на финальном экране.
   Кадр-исходник assets/gen/bench_long_0.png (gpt-image-2 по референсу скамейки
   с нашего же фона) -> _bench_prop.py -> assets/sprites/prop_bench.png ->
   vn2/img/prop/bench.webp. Правый край растушёван: генератор обрезал скамейку
   краем кадра, иначе посреди дороги торчала вертикальная пила.
   На сцене скамейка 1025x447 px (~2.3 м при 450 px/м) — длинная, а не «стул».

2. Дрожания нет: у сидящих спрайтов класс .seated (chars.seated) и своё дыхание
   breatheSeated — только масштаб 1.004 от нижней кромки, без подскока на 4 px.
   Замер в живом браузере (_alley_fix_check.py): низ спрайта 780 -> 780,
   проп 802 -> 802, верх спрайта 211 -> 210.

3. Эмоций поэта на скамейке 6 (было 3): neutral, upset, interested, shy, sullen,
   smile. Нормировка сидящего набора — по ширине головы (head/canvas_h = 0.16),
   плечи в сидячих позах гуляют на +-28 %, голова нет; сходится с Екатериной
   (749 px на 1.70 м ~ 440 px/м). Линия сиденья = 30 % высоты холста.
   Раскладка: «уронил голову на ладони» -> upset, «дернул плечом» -> sullen,
   «покраснел и отвернулся» -> shy, «потрепала по голове» -> smile.

4. CG «Муза» v2: скамейка стоит ВДОЛЬ аллеи (длина параллельна краю дороги),
   углом к дороге больше не развёрнута. Старый кадр оставлен исходником.

5. Своя музыка сцены вместо темы приёмной: music 'alley' -> alley_mix.mp3
   (тема lyria-3-5 + петля весенней улицы elevenlabs-sound-effects-v2).
   Рядом варианты alley_bed.mp3 (только тема) и alley_amb.mp3 (только улица).

Стороны: поэт теперь СЛЕВА (он на скамейке у края аллеи, как в тексте), Екатерина
справа на дороге. Одиночного сидящего движок не центрует — иначе уезжает со скамейки.

Регрессы: emo_visible 57/57, restart 3/3 (246 кликов), cg_range 10/10,
ded_credits зелёный, _alley_fix_check OK.
"""

with open(os.path.join(HERE, '.git_msg_alley_fix.txt'), 'w', encoding='utf-8') as f:
    f.write(MSG)


def sh(cmd, t=900):
    p = subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True,
                       timeout=t, env=ENV)
    return p.returncode, (p.stdout or '').strip(), (p.stderr or '').strip()


for a in ADD:
    rc, out, err = sh('git add -A "%s"' % a)
    if rc:
        print('  add FAIL', a, err[-120:])
print('статус после add:', sh('git status --porcelain | wc -l')[1])
print('commit:', sh('git commit -q -F .git_msg_alley_fix.txt')[0])
print('HEAD:', sh('git log --oneline -1')[1][:120])
rc, out, err = sh('git push origin rebuild')
print('push rebuild rc=%d %s %s' % (rc, out[-200:], err[-200:]))
