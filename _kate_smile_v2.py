# -*- coding: utf-8 -*-
"""kate_smile через gpt-image-2 (в эмоциях Кати не было улыбки — стоял откат на neutral).
Кладём во временную папку, ставим только если лицо не омолодилось."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen, pv

OUT = os.path.join(HERE, 'assets', 'gen', '_kate_v2')
os.makedirs(OUT, exist_ok=True)
REF = os.path.join(HERE, 'assets', 'gen', 'kate_overalls_0.png')
spec = gen.SCENES['kate_smile']
prompt = spec['prompt'] + '\n\nСТИЛЬ: ' + gen.STYLE
opts = {'aspect_ratio': spec.get('aspect', '3:4'), 'resolution': spec.get('res', '1K'),
        'image_base64': gen.b64(REF)}
for model in sys.argv[1:] or ['gpt-image-2']:
    q = pv.price(model, prompt, opts)
    print(model, 'quote', q.get('priceRub'))
    files, st = pv.generate_to_files(model, prompt, opts, outdir=OUT,
                                     name='kate_smile__%s' % model, max_price_rub=12)
    print('->', files, st.get('priceRub'), '₽')
