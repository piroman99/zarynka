import re
s = open('vn2/style.css', encoding='utf-8').read()
for m in re.finditer(r'[^{}]*\{[^{}]*animation[^{}]*\}', s):
    t = m.group(0)
    if 'crTwinkle' in t or 'none' in t or 'cr-' in t:
        print(t[:220].replace('\n', ' '))
        print('---')
