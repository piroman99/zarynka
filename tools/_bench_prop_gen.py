# -*- coding: utf-8 -*-
"""Новый проп скамейки: целиком, все четыре ножки, акварель, изолированно на белом.

Зачем: у нынешнего пропа (`assets/sprites/prop_bench.png`) правый (дальний) конец
нарисован бледным эскизом — альфа 21…46 в среднем, плотных пикселей 2.8 %; правой
передней ножки фактически нет (замер `_bench_alpha_stat.py`). На фоне это читается
как «скамейка растворяется справа».

Ракурс должен совпасть с кадром: ближний торец СЛЕВА, длина уходит в глубину
вправо-вверх под ~26°, вид три четверти со стороны дороги.
Референс — сам нынешний проп (стиль и порода дерева) + кадр приёмной (акварель).

Запуск: python3 _bench_prop_gen.py [--dry]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import gen  # noqa: E402
import pv   # noqa: E402
from PIL import Image  # noqa: E402

REF_PROP = os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png')
REF_STYLE = os.path.join(ROOT, 'assets', 'pilot', 'pilot_reception_0.png')

PROMPT = """Изолированный предмет на чистом БЕЛОМ фоне: старая деревянная парковая
скамейка со спинкой, без людей.

Ракурс — как на приложенном рисунке: камера сбоку-спереди, ближний торец скамейки
СЛЕВА и крупнее, скамейка уходит в глубину ВПРАВО и ВВЕРХ (наклон её длины примерно
25° к горизонтали), дальний торец меньше по перспективе.

ГЛАВНОЕ, чего не хватало на референсе: скамейка прорисована ЦЕЛИКОМ и одинаково
плотно по всей длине, ничего не растворяется и не тает к правому краю. У скамейки
видны ВСЕ ЧЕТЫРЕ НОЖКИ: передняя левая (крупная, у ближнего торца), задняя левая,
передняя правая и задняя правая (последние две — у дальнего торца, меньше по размеру).
Каждая ножка стоит на земле, у каждой виден низ.

Материал: тёмное выветренное дерево, доски спинки и сиденья, чугунные или деревянные
опоры, потёртости и мелкие сколы.

Стиль — акварель: прозрачные заливки, зерно бумаги, мягкие растушёвки, палитра
серо-коричневая с пыльно-синими тенями, как на приложенном кадре интерьера.

БЕЗ тени на земле, БЕЗ фона, БЕЗ травы, БЕЗ надписей, БЕЗ рамки и БЕЗ обрезки по краям:
предмет целиком внутри кадра с полями белого."""


def flat_on_white(src, dst):
    """Проп лежит с прозрачностью: модели принимают RGB. Кладём на белый."""
    im = Image.open(src).convert('RGBA')
    canvas = Image.new('RGB', im.size, (255, 255, 255))
    canvas.paste(im, (0, 0), im)
    canvas.save(dst)
    return dst


def main():
    dry = '--dry' in sys.argv
    ref_prop = flat_on_white(REF_PROP, os.path.join(ROOT, '_sat', 'prop_ref_white.png'))
    refs = [gen.b64(ref_prop, max_w=1024)]
    print('референсов: 1 (проп на белом)', os.path.basename(ref_prop))
    opts = {"aspect_ratio": "16:9", "resolution": "1K", "input_base64": refs}
    q = pv.price('gpt-image-2', PROMPT, opts)
    print('[quote]', q.get('priceRub'), 'RUB  (2 референса = дороже)', flush=True)
    if dry:
        return
    files, st = pv.generate_to_files('gpt-image-2', PROMPT, opts, outdir='assets/gen',
                                     name='prop_bench_new', max_price_rub=12)
    print('[ok] priceRub=%s' % st.get('priceRub'))
    for f in files:
        from PIL import Image
        im = Image.open(f)
        print('  ', os.path.relpath(f, HERE), im.size, im.mode, os.path.getsize(f), 'B')


if __name__ == '__main__':
    main()
