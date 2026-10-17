# -*- coding: utf-8 -*-
"""Финализация значка: znak3d_rot_B.mp4 -> out/znak3d_rot.mp4 (финальный ассет VN).
Черновик znak3d_rot_draft.mp4 (1280x720) остаётся в репе как история."""
import os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, 'out', 'znak3d_rot_B.mp4')
dst = os.path.join(HERE, 'out', 'znak3d_rot.mp4')
shutil.copyfile(src, dst)
print('скопировано:', os.path.relpath(dst, HERE), os.path.getsize(dst), 'байт')

# сверим, что файлы идентичны
import hashlib
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
print('sha src', h(src), '| dst', h(dst))
