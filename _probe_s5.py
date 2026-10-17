from PIL import Image, ImageChops

def small(p, n=64):
    return Image.open(p).convert('RGB').resize((n, n))

def diff(a, b):
    d = ImageChops.difference(a, b)
    px = list(d.getdata())
    return sum(sum(p) for p in px) / (len(px) * 3)

cands = {
    'final/s4': 'assets/final/prolog/s4.png',
    'final/s5': 'assets/final/prolog/s5.png',
    'vn2/s4': 'vn2/img/prolog/s4.png',
    'vn2/s5': 'vn2/img/prolog/s5.png',
    'gen s4': 'assets/gen/prologfin4_s4_d_0.jpg',
    'gen s5(triumph)': 'assets/gen/prologfin6_s5_a_0.jpg',
    'gen s5 old': 'assets/gen/prologfin_s5_0.jpg',
}
S = {k: small(v) for k, v in cands.items()}
keys = list(S)
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        print(keys[i], '<->', keys[j], round(diff(S[keys[i]], S[keys[j]]), 1))
