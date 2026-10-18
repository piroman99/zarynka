# -*- coding: utf-8 -*-
"""Варианты эмоций Сергея с жёстким локом возраста: flux-2 и gpt-image-2.
Результат: assets/gen/_sergey_v2/<emo>_<model>_0.jpg + лист лиц для сравнения.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen, pv

OUT = os.path.join(HERE, 'assets', 'gen', '_sergey_v2')
os.makedirs(OUT, exist_ok=True)
REF = os.path.join(HERE, 'assets', 'gen', 'sergey_eng_old__flux-2_0.jpg')

EMO = ['sergey_smile', 'sergey_concerned']
MODELS = sys.argv[1:] or ['flux-2', 'gpt-image-2']

for emo in EMO:
    spec = gen.SCENES[emo]
    prompt = spec['prompt'] + '\n\nСТИЛЬ: ' + gen.STYLE
    for model in MODELS:
        opts = {'aspect_ratio': spec.get('aspect', '3:4'),
                'resolution': spec.get('res', '1K'),
                'image_base64': gen.b64(REF)}
        try:
            q = pv.price(model, prompt, opts)
            print('%s / %s quote=%s' % (emo, model, q.get('priceRub')))
            files, st = pv.generate_to_files(model, prompt, opts, outdir=OUT,
                                             name='%s__%s' % (emo, model),
                                             max_price_rub=12)
            print('  ->', files, st.get('priceRub'), '₽')
        except Exception as e:
            print('  FAIL %s / %s: %s' % (emo, model, e))
