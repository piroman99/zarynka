import subprocess, sys, time, os
os.chdir("/home/ivan/.nanobot/workspace/novella/zaryanka")
for i in range(6):
    r = subprocess.run(["python3", "tg.py", "info"], capture_output=True, text=True, timeout=300)
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 0:
        print("OK try", i)
        print(out[-2000:])
        break
    print("fail", i, out.strip().splitlines()[-1][:200])
    time.sleep(3)
