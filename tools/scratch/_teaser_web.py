import os, subprocess
H = "/home/ivan/.nanobot/workspace"
FF = H + "/.probe/.lib/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
src = H + "/novella/zaryanka/out/avm_v3_epic.mp4"
dst = H + "/ghio/teaser.mp4"
r = subprocess.run([FF, "-y", "-i", src,
                    "-vf", "scale=1280:-2:flags=lanczos",
                    "-c:v", "libx264", "-profile:v", "high", "-preset", "slow",
                    "-crf", "27", "-pix_fmt", "yuv420p", "-g", "60",
                    "-c:a", "aac", "-b:a", "64k", "-ac", "2",
                    "-movflags", "+faststart", dst], capture_output=True, text=True)
print("rc", r.returncode, "size", os.path.getsize(dst))
p = subprocess.run([FF, "-i", dst], capture_output=True, text=True)
for l in p.stderr.splitlines():
    if "Stream" in l or "Duration" in l:
        print(l.strip())
