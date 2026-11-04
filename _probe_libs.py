# -*- coding: utf-8 -*-
"""Какие библиотеки для матирования доступны в песочнице."""
import importlib

for m in ('scipy', 'scipy.ndimage', 'cv2', 'numpy', 'PIL'):
    try:
        mod = importlib.import_module(m)
        print(m, 'OK', getattr(mod, '__version__', ''))
    except Exception as e:  # noqa: BLE001
        print(m, 'НЕТ', type(e).__name__)
