# -*- coding: utf-8 -*-
"""Собрать короткий аудио-тизер из готовой озвучки приёмной (vn2/audio/vo).

Только «чистые» реплики (целые фразы, не обрывки абзацев), без закадра —
голос закадра ещё выбирается, публиковать его рано.

Выход: out/reception_voices.mp3
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg', 'binaries',
                  'ffmpeg-linux-x86_64-v7.0.2')
VO = os.path.join(HERE, 'vn2', 'audio', 'vo')
OUT = os.path.join(HERE, 'out', 'reception_voices.mp3')
GAP = 0.45

# порядок = драматургия: знакомство -> вопрос -> отказ -> «я всё понимаю»
PICK = [
    ("rec_08.mp3", "Сергей: Добрый день. Добро пожаловать в Звёздный городок."),
    ("rec_10.mp3", "Сергей: Меня зовут Лихнецкий Сергей. Могу я увидеть ваши документы?"),
    ("rec_11.mp3", "Екатерина: Здравствуйте, Сергей, вот, пожалуйста."),
    ("rec_38.mp3", "Екатерина: Вы хотите сказать, что я слишком старая, чтобы лететь в космос?"),
    ("rec_48.mp3", "Сергей: Но ведь это не наш случай. Почти два года в космосе — это не шутка."),
    ("rec_55.mp3", "Екатерина: Не извиняйтесь. Я всё понимаю."),
]


def dur(path):
    r = subprocess.run([FF, '-i', path], capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if 'Duration:' in line:
            t = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = t.split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


def main():
    tmp = os.path.join(HERE, '.tmp_vo_pub')
    os.makedirs(tmp, exist_ok=True)
    sil = os.path.join(tmp, 'sil.mp3')
    subprocess.run([FF, '-y', '-f', 'lavfi', '-i',
                    'anullsrc=r=24000:cl=mono', '-t', str(GAP),
                    '-c:a', 'libmp3lame', '-b:a', '64k', sil],
                   capture_output=True, text=True)

    files, total = [], 0.0
    for name, text in PICK:
        p = os.path.join(VO, name)
        d = dur(p)
        total += d
        files.append((p, name, d))
        print("%-12s %5.2fs  %s" % (name, d, text))

    lst = os.path.join(tmp, 'list.txt')
    with open(lst, 'w', encoding='utf-8') as fh:
        for i, (p, _, _) in enumerate(files):
            if i:
                fh.write("file '%s'\n" % sil)
            fh.write("file '%s'\n" % p)
    total += GAP * (len(files) - 1)

    r = subprocess.run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                        '-ar', '24000', '-ac', '1', '-c:a', 'libmp3lame',
                        '-b:a', '80k', OUT], capture_output=True, text=True)
    if not os.path.exists(OUT):
        print(r.stderr[-1500:])
        return 1
    print("=" * 50)
    print("OUT      :", OUT, os.path.getsize(OUT) // 1024, "KB")
    print("duration : %.1f s (по расчёту %.1f s)" % (dur(OUT), total))
    return 0


if __name__ == '__main__':
    sys.exit(main())
