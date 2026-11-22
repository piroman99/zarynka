import os
for p in ('_vo_dup.txt', '.git_msg.txt', '.vo_dur_cache.json'):
    f = os.path.join('/home/ivan/.nanobot/workspace/novella/zaryanka', p)
    if os.path.exists(f):
        os.remove(f)
        print('удалён', p)
