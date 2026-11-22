from PIL import Image, ImageDraw, ImageFont
import art, os

keys = ["space", "city", "office", "alley", "pool", "yard", "winter", "dacha", "luna"]
th_w, th_h = 426, 240
sheet = Image.new("RGB", (th_w * 3, (th_h + 22) * 3), (18, 18, 20))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
for i, k in enumerate(keys):
    im = Image.open(os.path.join("assets", f"bg_{k}.png")).resize((th_w, th_h))
    x = (i % 3) * th_w
    y = (i // 3) * (th_h + 22)
    sheet.paste(im, (x, y + 22))
    d.text((x + 8, y + 3), k, font=f, fill=(240, 240, 240))
sheet.save("assets/_contact.png")
print("saved", sheet.size)
