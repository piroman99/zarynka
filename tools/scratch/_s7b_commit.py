import os, subprocess

CMD = ['git', 'add', 'PROLOG_FIXES.md', '_prolog_finals.py', '_s7_plaque.py',
       '_prolog_s7b_a.py', 'assets/final/prolog/s7.png', 'vn2/img/prolog/s7.webp',
       'assets/gen/s7b_gpt_a_0.png', 'assets/refs/zg', 'assets/review/review_128_zg_refs.png',
       'assets/review/review_129_s7b_a.jpg', 'assets/review/review_130_s7b_plaque.png']
print(subprocess.run(CMD, capture_output=True, text=True).stdout)
msg = """S7: new frame from the reception porch, quiet wall plaque

- replace the floating "ТЫ НЕ ПРОЙДЁШЬ!" poster with a small enamel plaque
  mounted on the smooth wall at the left edge (geometry measured on the plate)
- plate: assets/gen/s7b_gpt_a_0.png (gpt-image-2, 2.70 RUB) - camera on the
  porch steps, spruce alley, ~50-70 people instead of a human river, no gates,
  Star City setting (forest, low buildings), no city skyline
- wall/place references: assets/refs/zg/ (Wikimedia Commons, 14 photos)
"""
r = subprocess.run(['git', 'commit', '-m', msg], capture_output=True, text=True)
print(r.stdout[-1500:], r.stderr[-800:])
