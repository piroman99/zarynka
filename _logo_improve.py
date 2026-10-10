# -*- coding: utf-8 -*-
"""Улучшение логотипа-зарянки: 3 варианта от оригинала (nano-banana-2.1 как i2i)."""
import os, gen, pv

HERE = os.path.dirname(os.path.abspath(gen.__file__))
REF = os.path.join(HERE, "assets", "orig", "icon_large.png")
MODEL = "nano-banana-2.1"

COMMON = (
    "Профессиональный минималистичный ВЕКТОРНЫЙ логотип-иконка: птица зарянка (малиновка) "
    "в профиль, смотрит влево, круглое компактное тело, маленький аккуратный клюв, "
    "короткий хвост. Тёплый насыщенный красно-малиновый корпус, чуть более светлое красное "
    "крыло, аккуратный золотисто-кремовый контур по силуэту, один круглый золотой глаз с точкой. "
    "Чистые ровные линии одинаковой толщины, плоский дизайн с лёгкой cel-тенью для объёма, "
    "без лишних деталей. Хорошо читается в мелком размере. Ровный однотонный белый фон. "
    "Сохрани узнаваемый силуэт птицы с прикреплённого образца, но сделай линии чище, "
    "пропорции точнее, а контур — профессиональнее."
)

VARIANTS = {
    "logo_a": COMMON + " Вариант: чистый плоский знак без рамки, крупная птица по центру.",
    "logo_b": COMMON + (" Вариант: птица внутри аккуратного круга-медальона с тонкой золотой "
                        "окантовкой по краю (как эмблема-значок)."),
    "logo_c": COMMON + (" Вариант: чуть более детальный и живой — мягкая cel-раскраска, "
                        "выразительный глаз с бликом, лёгкая тень под птицей."),
}


def render(name, prompt):
    opts = {"aspect_ratio": "1:1", "resolution": "1K", "image_base64": gen.b64(REF)}
    try:
        q = pv.price(MODEL, prompt, opts)
        print(f"[quote] {name} {q.get('priceRub')} ₽", flush=True)
        files, st = pv.generate_to_files(MODEL, prompt, opts, outdir="assets/gen",
                                         name=name, max_price_rub=12)
        print(f"[OK] {name} {st.get('priceRub')} ₽ -> {os.path.relpath(files[0], HERE)}", flush=True)
    except Exception as e:
        print(f"[FAIL] {name} {str(e)[:180]}", flush=True)


for n, p in VARIANTS.items():
    render(n, p)
print("LOGO DONE", flush=True)
