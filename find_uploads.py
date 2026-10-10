import os, glob, time
roots = ["/home/ivan/.nanobot/media", "/home/ivan/.nanobot/workspace", os.path.expanduser("~/.nanobot")]
now = time.time()
hits = []
for r in roots:
    for ext in ("png", "jpg", "jpeg", "webp"):
        for p in glob.glob(f"{r}/**/*.{ext}", recursive=True):
            try:
                st = os.stat(p)
            except OSError:
                continue
            age = now - st.st_mtime
            if age < 3 * 3600 and st.st_size > 20000:
                hits.append((st.st_mtime, st.st_size, p))
hits.sort(reverse=True)
print("recent image files (last 3h):", len(hits))
for mt, sz, p in hits[:40]:
    print(f"  {time.strftime('%H:%M:%S', time.localtime(mt))}  {sz//1024:6d}KB  {p}")
