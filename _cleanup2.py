# -*- coding: utf-8 -*-
import os
for f in ['_cleanup_s4.py','_review86.py','_review88.py','_review89.py',
          '_s1_rebuild.py','_s2_rebuild.py','_prolog_s3_sheet.py','_prolog_s3_sheet2.py',
          '_prolog_s4_sheet.py','_prolog_s4_sheet2.py']:
    if os.path.exists(f):
        os.remove(f); print('removed', f)
