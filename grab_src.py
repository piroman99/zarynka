import os, shutil
from PIL import Image

src_dir = "/home/ivan/.nanobot/media/websocket"
files = ["3029d614b3a2.png", "9f57530bfc6e.png", "caccf3b4ebc5.png", "c66f332fa5c9.png"]
os.makedirs("assets/src", exist_ok=True)
for f in files:
    s = os.path.join(src_dir, f)
    im = Image.open(s)
    print(f, im.size, im.mode)
    dst = os.path.join("assets/src", f)
    shutil.copy2(s, dst)
print("copied ->", os.listdir("assets/src"))
