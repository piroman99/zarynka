from PIL import Image
im = Image.open('assets/gen/s7b_gpt_a_0.png').convert('RGB')
W, H = im.size
# левая нижняя четверть — где по брифу парапет крыльца и колонна
c = im.crop((0, int(H*0.45), int(W*0.42), H))
c = c.resize((760, round(c.height * 760 / c.width)), Image.LANCZOS)
c.save('assets/review/_t_left.jpg', quality=92)
print(c.size)
