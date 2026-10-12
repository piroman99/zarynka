# -*- coding: utf-8 -*-
"""Эмоции/персонажи для vn2: quote (бесплатно) и gen.

  python3 _vn2_emo.py quote
  python3 _vn2_emo.py gen kate_smile sergey_smile sergey_concerned starik
"""
import os, sys
import gen

HERE = os.path.dirname(os.path.abspath(__file__))
REF = {
    'kate_smile':      'assets/gen/kate_overalls_0.png',
    'sergey_smile':    'assets/gen/sergey_eng_old__flux-2_0.jpg',
    'sergey_concerned':'assets/gen/sergey_eng_old__flux-2_0.jpg',
    'starik':          None,
    'starik_stern':    'assets/gen/starik_0.png',
    'starik_smile':    'assets/gen/starik_0.png',
}
ALL = ['kate_smile', 'sergey_smile', 'sergey_concerned', 'starik']


def do_quote(names):
    import pv
    print('balance:', pv.balance())
    total = 0.0
    for n in names:
        spec = gen.SCENES[n]
        prompt = spec['prompt'] + '\n\nСТИЛЬ: ' + gen.STYLE
        opts = {'aspect_ratio': spec.get('aspect', '3:4'), 'resolution': spec.get('res', '1K')}
        ref = REF.get(n)
        if ref:
            opts['image_base64'] = gen.b64(os.path.join(HERE, ref))
        q = pv.price('flux-2', prompt, opts)
        p = float(q.get('priceRub') or 0)
        total += p
        print(f'  {n:18s} = {p} ₽  ({q.get("model")})')
    print(f'  ИТОГО ~ {round(total,2)} ₽')


def do_gen(names):
    for n in names:
        ref = REF.get(n)
        ref = os.path.join(HERE, ref) if ref else None
        if ref and not os.path.exists(ref):
            print('SKIP (нет рефа):', n, ref); continue
        print('===', n, 'ref=', ref)
        gen.run(n, ref=ref, model='flux-2')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'quote'
    names = sys.argv[2:] or ALL
    if cmd == 'quote':
        do_quote(names)
    elif cmd == 'gen':
        do_gen(names)
    else:
        print('usage: _vn2_emo.py quote|gen [names]')
