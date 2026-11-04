# -*- coding: utf-8 -*-
"""Озвучка сцен ГОЛОСАМИ КАСТА (постранично, по полю page.who).

Голоса зафиксированы Иваном:
  закадр/автор  -> gemini-3.8-flash-tts  Charon  «кинохроника без иронии»
  Старик        -> gemini-3.8-flash-tts  Fenrir
  Сергей        -> gemini-3.8-flash-tts  Charon
  Екатерина     -> elevenlabs-v4-tts     Charlotte   (вариант 9)
  Поэт (Лёша)   -> gemini-3.8-flash-tts  Umbriel     (Иван 2026-11-04: «2»
                   из теста `_voice_poet_test.py`, порядок 1 Achird … 2 Umbriel)

Обрабатывает ВСЕ узлы с текстом (приёмная, `steps`, `alley`), а не только приёмную.
Имена файлов берёт из плана `pg.vof` (его пишет сборка), а не из `pg.vo` — иначе
ещё не записанные страницы новых сцен не видны (404 в консоли и красный регресс).

Манифест vn2/audio/vo/_voices.json хранит, каким голосом сделан каждый файл:
повторный запуск переозвучивает ТОЛЬКО страницы, чей голос изменился.

  python3 _vn2_vo_cast.py --dry     # только смета
  python3 _vn2_vo_cast.py           # записать
  python3 _vn2_vo_cast.py --no-reuse  # ничего не переиспользовать (починка)

ВАЖНО (баг 2026-10-20): раньше переиспользование копировало файл из рабочего
дерева, а рабочее дерево в том же прогоне перезаписывается — получался каскад:
копия делалась с уже перезаписанного файла, и одна и та же озвучка расползалась
по десятку страниц. Теперь источник берётся из git-блоба (HEAD), он неизменен.
"""
import os, sys, json, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pv

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
FF = os.path.join(WS, '.probe', '.lib', 'imageio_ffmpeg',
                  'binaries', 'ffmpeg-linux-x86_64-v7.0.2')
OUTDIR = os.path.join(HERE, 'vn2', 'audio', 'vo')
MANIFEST = os.path.join(OUTDIR, '_voices.json')
CAP_RUB = 40.0
DRY = '--dry' in sys.argv
NO_REUSE = '--no-reuse' in sys.argv
# --force=rec_22,rec_23 — переозвучить указанные файлы, даже если текст/голос не менялись
FORCE = set()
for a in sys.argv:
    if a.startswith('--force='):
        FORCE = set(x.strip() for x in a.split('=', 1)[1].split(',') if x.strip())

NARR_STYLE = (
    "Спокойный, зрелый мужской закадровый голос. Документальная кинохроника: "
    "серьёзно, сдержанно, ровно, без иронии, без насмешки и без пафоса. "
    "Говори не спеша, чуть медленнее обычного, с небольшими паузами между фразами. "
    "Нейтральная чёткая дикция, доверительная интонация рассказчика."
)
STARIK_STYLE = (
    "Очень немолодой мужчина, начальник. Голос сухой, низкий, устало-"
    "начальственный. Говорит негромко, но веско, с раздражением, которое он "
    "не повышает. Без театральности и без пафоса."
)
SERGEY_STYLE = (
    "Мужчина около шестидесяти, инженер, много лет на службе. Голос спокойный, "
    "ровный, вежливо-официальный, немного усталый. Чёткая дикция, доброжелательно, "
    "но сдержанно, без иронии."
)
POET_STYLE = (
    "Молодой мужчина двадцати пяти лет, поэт. Голос мягкий, негромкий, с лёгкой "
    "хрипотцой и надломом. Говорит тихо и сбивчиво, как человек, который только что "
    "плакал: в интонации гордость за себя и отчаяние одновременно. Без театральности, "
    "без пафоса, без жалобы. Не диктор, не бас, не мальчик-подросток."
)

VOICES = {
    'narr':     ('gemini-3.8-flash-tts', {'gemini_voice': 'Charon', 'engine': 'flash',
                                          'style_instructions': NARR_STYLE}, 1.70),
    'Старик':   ('gemini-3.8-flash-tts', {'gemini_voice': 'Fenrir', 'engine': 'flash',
                                          'style_instructions': STARIK_STYLE}, 1.70),
    'Сергей':   ('gemini-3.8-flash-tts', {'gemini_voice': 'Charon', 'engine': 'flash',
                                          'style_instructions': SERGEY_STYLE}, 1.70),
    'Екатерина': ('elevenlabs-v4-tts', {'voice': 'Charlotte'}, 10.84),
    'Поэт':     ('gemini-3.8-flash-tts', {'gemini_voice': 'Umbriel', 'engine': 'flash',
                                         'style_instructions': POET_STYLE}, 1.70),
}

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
# все узлы с текстом: приёмная, «аллея» (steps + alley) и всё, что появится дальше
nds = [n for n in D['nodes'] if n.get('pages')]

man = {}
if os.path.exists(MANIFEST):
    man = json.load(open(MANIFEST, encoding='utf-8'))


def norm(tx):
    """Текст сегмента в том виде, в каком он уходит в TTS (для сравнения и кэша)."""
    t = re.sub(r'^[\u2014\u2013-]+\s*', '', tx.strip())
    t = re.sub(r'[,;:]+$', '', t)          # «Спасибо,» → «Спасибо» (иначе TTS тянет паузу)
    return re.sub(r'\s+', ' ', t).strip()

def segs_of(pg, plan=False):
    """Страница -> [(файл, текст, кто)]. У склеенной страницы ДВА сегмента
    («Спасибо» — Екатерина, «от улыбки…» — закадр), у обычной — один.
    Берём `vo` (уже записано) или, при plan=True, `vof` (план записи) — новые сцены
    живут на `vof`. Для ПЕРЕИСПОЛЬЗОВАНИЯ читаем только `vo`: план файла ещё не значит,
    что файл существует (иначе тест пытается копировать несуществующее и шумит)."""
    vo = pg.get('vo') or (pg.get('vof') if plan else None)
    if not vo:
        return []
    vos = [vo] if isinstance(vo, str) else list(vo)
    vtx = pg.get('vtx') or [pg['tx']] * len(vos)
    vwho = pg.get('vwho') or [pg.get('who') or 'narr'] * len(vos)
    return [(vos[i], vtx[i], (vwho[i] or 'narr')) for i in range(len(vos))]


# --- переиспользование уже оплаченной озвучки -------------------------------
# Разбивка на страницы меняется (реплики/авторский текст разведены), поэтому номера
# файлов сдвигаются. Чтобы не платить за тот же текст дважды, ищем совпадение
# (голос + текст) в предыдущей сборке content.js из git HEAD и копируем готовый файл.
def git_blob(rel):
    """Байты файла из HEAD — источник переиспользования (рабочее дерево
    в этом прогоне перезаписывается, брать из него нельзя)."""
    r = subprocess.run(['git', 'show', 'HEAD:' + rel], cwd=HERE,
                       capture_output=True)
    return r.stdout if r.returncode == 0 and r.stdout else None


REUSE = {}
OLD_MAN = {}
try:
    old = subprocess.run(['git', 'show', 'HEAD:vn2/content.js'], cwd=HERE,
                         capture_output=True, text=True).stdout
    omraw = subprocess.run(['git', 'show', 'HEAD:vn2/audio/vo/_voices.json'], cwd=HERE,
                           capture_output=True, text=True).stdout
    if omraw:
        OLD_MAN = json.loads(omraw)
    if old:
        oD = json.loads(old[old.index('=') + 1:].strip().rstrip(';'))
        for ond in oD['nodes']:
            for opg in ond.get('pages', []):
                for ovo, otx, ok in segs_of(opg):
                    if ok not in VOICES:
                        ok = 'narr'
                    REUSE[(ok, norm(otx))] = ovo
except Exception as e:
    print('reuse: пропущено (%s)' % e)

# СТРАХОВКА (баг 2026-10-21): копировать файл можно только если манифест HEAD
# описывает у источника ТОТ ЖЕ текст и голос. Без проверки переиспользование
# копировало чужой файл (путь «правильный», содержимое — нет), и страница
# Екатерины звучала мужским голосом.
def reuse_ok(src_vo, key, tx):
    om = OLD_MAN.get(src_vo) or {}
    if norm(om.get('text') or '') != tx:
        return False, 'источник %s записан с другим текстом' % os.path.basename(src_vo)
    if (om.get('voice') or 'narr') != key:
        return False, 'источник %s — голос %s' % (os.path.basename(src_vo), om.get('voice'))
    return True, ''

todo, done, reused = [], [], 0
skipped = []
for nd in nds:
    for pg in nd['pages']:
        for vo, stx, skey in segs_of(pg, plan=True):
            key = skey if skey in VOICES else 'narr'
            name = os.path.basename(vo)[:-4]
            dst = os.path.join(OUTDIR, name + '.mp3')
            tx = norm(stx)
            rec = man.get(vo, {})
            if name in FORCE:
                todo.append((vo, name, key, stx.strip(), tx))
                continue
            if (rec.get('voice') == key and rec.get('text') == tx
                    and not rec.get('stale_reason')
                    and os.path.exists(dst) and os.path.getsize(dst) > 2000):
                done.append(name)
                continue
            # тот же голос + тот же текст уже озвучен в предыдущей сборке → копируем файл
            # (из git-блоба HEAD, а НЕ из рабочего дерева — иначе каскад копий)
            src_vo = None if NO_REUSE else REUSE.get((key, tx))
            if src_vo:
                ok, why = reuse_ok(src_vo, key, tx)
                if not ok:
                    skipped.append('%s: %s' % (name, why))
                    src_vo = None
            if src_vo:
                rel = 'vn2/audio/vo/' + os.path.basename(src_vo)[:-4] + '.mp3'
                blob = git_blob(rel)
                if blob and len(blob) > 2000:
                    with open(dst, 'wb') as fo:
                        fo.write(blob)
                    man[vo] = {'voice': key, 'text': tx, 'chars': len(tx), 'price': 0,
                               'reused_from': os.path.basename(src_vo)}
                    reused += 1
                    continue
            todo.append((vo, name, key, stx.strip(), tx))

chars = {}
for _, _, key, _, tx in todo:
    chars[key] = chars.get(key, 0) + len(tx)
cost = sum(len(tx) * VOICES[key][2] / 1000 for _, _, key, _, tx in todo)
npages = sum(len(n['pages']) for n in nds)
print('страниц: %d, к переозвучке: %d, уже в нужном голосе: %d, переиспользовано: %d'
      % (npages, len(todo), len(done), reused))
for s in skipped:
    print('  переиспользование отклонено — ' + s)
for k, n in sorted(chars.items(), key=lambda x: -x[1]):
    print('  %-10s %5d зн.  ~%.2f ₽  (%s)'
          % (k, n, n * VOICES[k][2] / 1000, VOICES[k][0]))
print('смета: ~%.2f ₽' % cost)
if DRY or not todo:
    json.dump(man, open(MANIFEST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.exit(0)

spent = 0.0
for vo, name, key, tx, ntx in todo:
    if spent >= CAP_RUB:
        print('STOP: cap %.0f ₽' % CAP_RUB); break
    model, opts, _ = VOICES[key]
    say = ntx
    try:
        files, st = pv.generate_to_files(model, say, opts, outdir=OUTDIR,
                                         name=name, max_price_rub=8)
        got = files[0]
        dst = os.path.join(OUTDIR, name + '.mp3')
        tmp = dst + '.tmp.mp3'
        r = subprocess.run([FF, '-y', '-i', got, '-ar', '44100', '-ac', '1',
                            '-b:a', '96k', tmp], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError('ffmpeg: ' + r.stderr[-200:])
        os.replace(tmp, dst)
        if os.path.abspath(got) != os.path.abspath(dst) and os.path.exists(got):
            os.remove(got)
        price = float(st.get('priceRub') or 0)
        spent += price
        man[vo] = {'voice': key, 'model': model, 'chars': len(say),
                   'price': price, 'text': ntx}
        json.dump(man, open(MANIFEST, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('  OK %-8s %-10s %4d зн.  %.2f ₽' % (name, key, len(say), price))
    except Exception as e:
        print('  FAIL %s (%s): %s' % (name, key, e))

print('итого %.2f ₽' % spent)
