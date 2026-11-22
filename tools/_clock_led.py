# -*- coding: utf-8 -*-
"""Табло-часы «как железо»: цифры вписываются в панель, есть кронштейн и контактная тень.
Геометрия будки замерена по градиентам (_s6_booth_edges.py):
   вертикальные стойки  x ≈ 1839..1842 (левая), 2033, 2086, 2121, 2175..2178 (правая)
   горизонтальные связи y ≈ 397 (средняя), 597..600 (низ)
"""
import os
from PIL import Image, ImageDraw, ImageFilter

# сегменты: a верх, b верх-право, c низ-право, d низ, e низ-лево, f верх-лево, g середина
SEG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc',
       '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcfgd'}


def seg_poly(x, y, w, h, seg, t):
    g = t * 0.42
    m = t / 2.0
    if seg == 'a':
        return [(x + m, y + m), (x + w - m, y + m), (x + w - m - t, y + t), (x + m + t, y + t)]
    if seg == 'd':
        return [(x + m + t, y + h - t), (x + w - m - t, y + h - t), (x + w - m, y + h - m), (x + m, y + h - m)]
    if seg == 'g':
        return [(x + m + t, y + h / 2 - g), (x + w - m - t, y + h / 2 - g),
                (x + w - m - t, y + h / 2 + g), (x + m + t, y + h / 2 + g)]
    if seg == 'f':
        return [(x + m, y + m), (x + t, y + t), (x + t, y + h / 2 - g), (x + m, y + h / 2 - g * 0.6)]
    if seg == 'b':
        return [(x + w - m, y + m), (x + w - t, y + t), (x + w - t, y + h / 2 - g),
                (x + w - m, y + h / 2 - g * 0.6)]
    if seg == 'e':
        return [(x + m, y + h / 2 + g * 0.6), (x + t, y + h / 2 + g), (x + t, y + h - t), (x + m, y + h - m)]
    if seg == 'c':
        return [(x + w - m, y + h / 2 + g * 0.6), (x + w - t, y + h / 2 + g),
                (x + w - t, y + h - t), (x + w - m, y + h - m)]
    return []


def led_width(h, text, t_ratio=0.16):
    t = max(2, h * t_ratio)
    w = h * 0.56
    gap = h * 0.20
    total = 0
    for ch in text:
        total += (gap + t * 1.2) if ch == ':' else (w + gap)
    return total - gap


def draw_led(d, x, y, h, text, color, t_ratio=0.16):
    t = max(1.5, h * t_ratio)
    w = h * 0.56
    gap = h * 0.20
    cx = x
    for ch in text:
        if ch == ':':
            r = t * 0.72
            d.ellipse([cx + gap * 0.2, y + h * 0.30 - r, cx + gap * 0.2 + 2 * r, y + h * 0.30 + r], fill=color)
            d.ellipse([cx + gap * 0.2, y + h * 0.70 - r, cx + gap * 0.2 + 2 * r, y + h * 0.70 + r], fill=color)
            cx += gap + t * 1.2
            continue
        for s in SEG.get(ch, ''):
            d.polygon(seg_poly(cx, y, w, h, s, t), fill=color)
        cx += w + gap
    return cx - x - gap


def clock(base, box, text='06:07', color=(255, 96, 60), bracket=True):
    """Табло в box: панель + LED-цифры (вписываются по ширине) + свечение + кронштейн."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    pad_x = max(6, w * 0.08)
    avail = w - 2 * pad_x
    # подобрать высоту цифр так, чтобы влезли по ширине
    th = h * 0.56
    while th > 4 and led_width(th, text) > avail:
        th *= 0.94
    # свечение позади панели
    glow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([x0 - h * 0.25, y0 - h * 0.25, x1 + h * 0.25, y1 + h * 0.25],
                                           radius=h * 0.3, fill=color + (55,))
    glow = glow.filter(ImageFilter.GaussianBlur(max(3, h * 0.35)))
    base = Image.alpha_composite(base.convert('RGBA'), glow).convert('RGB')

    # контактная тень под панелью (панель не «висит»)
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x0 + h * 0.05, y1 - h * 0.05, x1 + h * 0.10, y1 + h * 0.22],
                                         radius=h * 0.2, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(max(2, h * 0.12)))
    base = Image.alpha_composite(base.convert('RGBA'), sh).convert('RGB')

    d = ImageDraw.Draw(base)
    # кронштейн: короткая стойка от панели в поверхность
    if bracket:
        bw = max(3, w * 0.035)
        d.rectangle([x0 + w * 0.12, y0 - h * 0.16, x0 + w * 0.12 + bw, y0 + 2], fill=(30, 31, 35))
        d.rectangle([x1 - w * 0.12 - bw, y0 - h * 0.16, x1 - w * 0.12, y0 + 2], fill=(30, 31, 35))
    d.rounded_rectangle([x0, y0, x1, y1], radius=h * 0.14, fill=(15, 16, 19))
    d.rounded_rectangle([x0, y0, x1, y1], radius=h * 0.14, outline=(62, 64, 70), width=max(1, int(h * 0.045)))
    draw_led(d, x0 + (w - led_width(th, text)) / 2, y0 + (h - th) / 2, th, text, color)
    return base
