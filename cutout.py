# -*- coding: utf-8 -*-
"""Вырезает спрайт с однотонного фона (flood-fill от краёв) → PNG с альфой."""
import os, sys
from collections import deque
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))


def cutout(src, dst, tol=26):
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = im.load()
    # фон = средний цвет по рамке
    border = []
    for x in range(w):
        border.append(px[x, 0]); border.append(px[x, h - 1])
    for y in range(h):
        border.append(px[0, y]); border.append(px[w - 1, y])
    br = tuple(sum(c[i] for c in border) // len(border) for i in range(3))

    def close(p):
        return abs(p[0]-br[0]) <= tol and abs(p[1]-br[1]) <= tol and abs(p[2]-br[2]) <= tol

    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if close(px[x, y]) and not seen[y*w+x]:
                seen[y*w+x] = 1; q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if close(px[x, y]) and not seen[y*w+x]:
                seen[y*w+x] = 1; q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny*w+nx] and close(px[nx, ny]):
                seen[ny*w+nx] = 1; q.append((nx, ny))
    alpha = Image.new("L", (w, h), 255)
    ap = alpha.load()
    for i in range(w*h):
        if seen[i]:
            ap[i % w, i // w] = 0
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))
    out = im.copy(); out.putalpha(alpha)
    # обрезать по содержимому
    bb = alpha.getbbox()
    if bb:
        out = out.crop(bb)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    out.save(dst, "PNG")
    print(f"cutout {os.path.basename(src)} -> {os.path.basename(dst)} {out.size} (bg={br})")
    return dst


if __name__ == "__main__":
    jobs = [
        ("assets/gen/kate_overalls_0.png", "assets/sprites/kate_overalls.png", 26),
        ("assets/gen/kate_sad_0.png", "assets/sprites/kate_sad.png", 26),
        ("assets/gen/sergey_grok_0.jpg", "assets/sprites/sergey.png", 30),
    ]
    for src, dst, tol in jobs:
        sp = os.path.join(HERE, src)
        if os.path.exists(sp):
            cutout(sp, os.path.join(HERE, dst), tol=tol)
        else:
            print("skip (нет файла):", src)
