"""Generate home-screen icons for each of the 4 Book PWA instances.

Draws a simple dark/brass "seal" icon matching the app's theme, with a small
teal number badge per player so the 4 home-screen icons are visually distinct.
Run with: python3 generate_icons.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join(os.path.dirname(__file__), "build", "icons")
os.makedirs(OUT_DIR, exist_ok=True)

INK = (18, 21, 26, 255)
INK_2 = (25, 29, 36, 255)
BRASS = (198, 161, 91, 255)
BRASS_BRIGHT = (221, 185, 110, 255)
CREAM = (242, 237, 225, 255)
TEAL = (91, 156, 143, 255)
TEAL_BRIGHT = (116, 183, 169, 255)

SIZES = [180, 192, 512]


def find_font(size, bold=True):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def draw_icon(size, player_num):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    pad = int(size * 0.06)
    d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=int(size * 0.18), fill=INK)

    # subtle inner panel
    inset = int(size * 0.14)
    d.rounded_rectangle([inset, inset, size - inset, size - inset], radius=int(size * 0.14),
                         outline=BRASS, width=max(2, int(size * 0.012)))

    # "B" seal, centered
    font = find_font(int(size * 0.44))
    text = "B"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((size / 2 - tw / 2 - bbox[0], size / 2 - th / 2 - bbox[1] - size * 0.03), text,
           font=font, fill=BRASS_BRIGHT)

    # player number badge, bottom-right
    badge_r = int(size * 0.19)
    cx, cy = size - int(size * 0.24), size - int(size * 0.24)
    d.ellipse([cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r], fill=TEAL,
              outline=INK_2, width=max(2, int(size * 0.02)))
    nfont = find_font(int(badge_r * 1.25))
    ntext = str(player_num)
    nbbox = d.textbbox((0, 0), ntext, font=nfont)
    ntw, nth = nbbox[2] - nbbox[0], nbbox[3] - nbbox[1]
    d.text((cx - ntw / 2 - nbbox[0], cy - nth / 2 - nbbox[1]), ntext, font=nfont, fill=CREAM)

    return img


for player_num in [1, 2, 3, 4]:
    for size in SIZES:
        icon = draw_icon(size, player_num)
        path = os.path.join(OUT_DIR, f"icon-{size}-p{player_num}.png")
        icon.save(path)
        print("wrote", path)
