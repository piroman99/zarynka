# -*- coding: utf-8 -*-
"""Какие локальные средства распознавания/просмотра картинок вообще есть.

    python3 _probe_ocr.py

Проверяет: tesseract в PATH, python-модули (pytesseract, easyocr, paddleocr, cv2,
rapidocr_onnxruntime, transformers), а также cf/провайдеры vision.
"""
import importlib.util
import shutil

print('tesseract:', shutil.which('tesseract') or 'НЕТ')
for m in ('pytesseract', 'easyocr', 'paddleocr', 'rapidocr_onnxruntime', 'cv2',
          'transformers', 'torch', 'onnxruntime'):
    print('%-22s %s' % (m, 'есть' if importlib.util.find_spec(m) else 'нет'))
