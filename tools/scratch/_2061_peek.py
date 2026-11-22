#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.tmp2061')
h = open(os.path.join(OUT, 'page_1.html'), encoding='utf-8', errors='replace').read()
# montrer un extrait autour de la 1re apparition d'un bloc 'iwork'
i = h.find('iwork/')
print(h[i-1500:i+500])
