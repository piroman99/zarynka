import os, shutil
p = "assets/gen/kate_reception_0.bin"
with open(p, "rb") as f:
    head = f.read(16)
print("magic:", head)
sig = head[:8]
if head[:8] == b"\x89PNG\r\n\x1a\n":
    ext = ".png"
elif head[:2] == b"\xff\xd8":
    ext = ".jpg"
elif head[:4] == b"RIFF":
    ext = ".webp"
else:
    ext = ".dat"
dst = os.path.splitext(p)[0] + ext
os.rename(p, dst)
print("renamed ->", dst, os.path.getsize(dst), "bytes")
from PIL import Image
im = Image.open(dst)
print("image:", im.format, im.size, im.mode)
