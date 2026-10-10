import os
p = ".pv_key"
os.chmod(p, 0o600)
print("perms", oct(os.stat(p).st_mode & 0o777))
