# -*- coding: utf-8 -*-
"""Опубликовать первый пост «Зарянки» на стене сообщества.

  python3 vk_publish.py            — текст (обложка уже стоит)
  python3 vk_publish.py --photos   — текст + 3 кадра (нужен ВК-пользовательский токен)
Текст берётся из assets/vk/post_a.txt. Итоговый post_id печатается.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vk

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
VK = os.path.join(HERE, "assets", "vk")

def main():
    text = open(os.path.join(VK, "post_a.txt"), encoding="utf-8").read().strip()
    atts = []
    if "--photos" in sys.argv:
        for n in ("ok_reception_fix2_0.jpg", "ok_kate_suit_0.jpg", "ok_x_kate_moon_0.jpg"):
            atts.append(vk.upload_wall_photo(os.path.join(GEN, n)))
            print("photo:", atts[-1])
    res = vk.post(text, atts or None)
    print("wall.post:", res)
    return res

if __name__ == "__main__":
    main()
