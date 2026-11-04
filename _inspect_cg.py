import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for p in ['assets/gen/cg_room_a__gpt-image-2_0.png',
          'assets/gen/cg_p4_refusal__gpt-image-2_0.png',
          'assets/gen/kate_smile_0.png',
          'assets/gen/sergey_eng_old__flux-2_0.jpg',
          'assets/gen/pilot_reception_0.png',
          'assets/gen/kate_reception_vn_0.png',
          'assets/gen/kate_sad_0.png',
          'vn2/img/bg/reception.webp',
          'vn2/img/cg/rec_48.webp']:
    f = os.path.join(HERE, p)
    try:
        im = Image.open(f)
        print('%-52s %s %s %d B' % (p, im.size, im.mode, os.path.getsize(f)))
    except Exception as e:
        print('%-52s ERR %s' % (p, e))
