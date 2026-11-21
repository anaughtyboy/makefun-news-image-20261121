#!/usr/bin/env python3
"""Saturday Globe — draws the 21 November 2026 front page (1024x1024 PNG).

Everything is drawn in code with PIL: the masthead, headlines and body text
are rendered from strings, and every picture is shapes on a canvas. No photo,
no downloaded asset, no text inside any illustration.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (20, 20, 20)
RED = (168, 30, 34)
GREY = (110, 105, 95)
RULE = (60, 55, 45)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Split text into lines that fit max_w, measured with fnt."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, fill=INK, leading=1.28):
    """Draw wrapped text; return the y just below the last line."""
    size = fnt.size
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += int(size * leading)
    return y


def hline(draw, x0, x1, y, fill=RULE, width=2):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def burst(draw, cx, cy, r, core, rays):
    """Explosion flash: short spokes plus a hot core."""
    for i in range(14):
        a = math.pi * 2 * i / 14
        x2 = cx + math.cos(a) * r
        y2 = cy + math.sin(a) * r
        draw.line([(cx, cy), (x2, y2)], fill=rays, width=3)
    draw.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=core)
    draw.ellipse([cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2], fill=(255, 244, 200))


def ill_barrage(d, x, y, w, h):
    """Night barrage: skyline, missile arcs, explosion flashes."""
    d.rectangle([x, y, x + w, y + h], fill=(13, 27, 46))
    for i in range(40):
        sx = x + (i * 37) % w
        sy = y + (i * 53) % (h // 2)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(220, 225, 240))
    # skyline, clamped to the panel
    base = y + h
    bx = x
    i = 0
    while bx < x + w:
        bw = 26 + (i * 13) % 30
        bw = min(bw, x + w - bx)
        bh = 40 + (i * 29) % 70
        d.rectangle([bx, base - bh, bx + bw, base], fill=(5, 8, 14))
        for wy in range(base - bh + 8, base - 6, 14):
            if (i + wy) % 3 == 0:
                d.rectangle([bx + 5, wy, bx + 9, wy + 6], fill=(255, 200, 90))
        bx += bw + 4
        i += 1
    # missile arcs
    for (ax, ay, bx2, by2, col) in [
        (x + 20, y + h - 30, x + 150, y + 40, (255, 255, 255)),
        (x + 90, y + h - 20, x + 260, y + 70, (255, 220, 150)),
        (x + 200, y + h - 40, x + 350, y + 30, (255, 255, 255)),
    ]:
        pts = []
        for t in range(21):
            tt = t / 20
            px = ax + (bx2 - ax) * tt
            py = ay + (by2 - ay) * tt - 46 * math.sin(math.pi * tt)
            pts.append((px, py))
        d.line(pts, fill=col, width=2)
        d.ellipse([bx2 - 3, by2 - 3, bx2 + 3, by2 + 3], fill=col)
    burst(d, x + 130, y + 62, 26, (255, 140, 40), (255, 180, 80))
    burst(d, x + 300, y + 88, 20, (255, 120, 30), (255, 160, 60))
    burst(d, x + 350, y + 40, 14, (255, 150, 50), (255, 190, 90))


def ill_rout(d, x, y, w, h):
    """Falling market: descending red line over a fading bar chart."""
    d.rectangle([x, y, x + w, y + h], fill=(253, 246, 236))
    for gy in range(y + 16, y + h - 8, 18):
        d.line([(x + 8, gy), (x + w - 8, gy)], fill=(225, 215, 200), width=1)
    bars = [0.82, 0.74, 0.66, 0.58, 0.44, 0.36, 0.26]
    bw = w / len(bars)
    for i, f in enumerate(bars):
        bx = x + i * bw + 6
        d.rectangle([bx, y + h - 10 - f * (h - 26), bx + bw - 12, y + h - 10],
                    fill=(232, 150, 140))
    pts = []
    for i, f in enumerate(bars):
        pts.append((x + i * bw + bw / 2, y + h - 12 - f * (h - 26)))
    d.line(pts, fill=(178, 24, 28), width=4)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 16, ey - 2), (ex - 6, ey + 12)], fill=(178, 24, 28))
    d.ellipse([pts[0][0] - 4, pts[0][1] - 4, pts[0][0] + 4, pts[0][1] + 4], fill=(178, 24, 28))


def ill_ukeu(d, x, y, w, h):
    """Two partners joined by a bridge: stars on blue, cross on white."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 242, 247))
    # gold arch joining the two blocks, kept inside the panel
    d.arc([x + w * 0.30, y + 4, x + w * 0.70, y + h * 0.62],
          start=180, end=360, fill=(212, 175, 55), width=5)
    sq = h * 0.78
    # left block: blue with gold stars
    d.rounded_rectangle([x + 14, y + (h - sq) / 2, x + 14 + sq, y + (h + sq) / 2],
                        radius=10, fill=(31, 58, 147))
    for k in range(5):
        a = -math.pi / 2 + k * (2 * math.pi / 5)
        sx = x + 14 + sq / 2 + math.cos(a) * sq * 0.26
        sy = y + h / 2 + math.sin(a) * sq * 0.26
        d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 210, 80))
    # right block: white with a red cross
    rx = x + w - 14 - sq
    d.rounded_rectangle([rx, y + (h - sq) / 2, rx + sq, y + (h + sq) / 2],
                        radius=10, fill=(255, 255, 255), outline=(150, 150, 150), width=2)
    d.rectangle([rx + sq / 2 - 7, y + (h - sq) / 2 + 6, rx + sq / 2 + 7, y + (h + sq) / 2 - 6],
                fill=(178, 24, 28))
    d.rectangle([rx + 6, y + h / 2 - 7, rx + sq - 6, y + h / 2 + 7], fill=(178, 24, 28))


def ill_iran(d, x, y, w, h):
    """Desert dusk with a jet silhouette."""
    for i in range(h):
        t = i / h
        r = int(250 + (120 - 250) * t)
        g = int(170 + (70 - 170) * t)
        b = int(90 + (40 - 90) * t)
        d.line([(x, y + i), (x + w, y + i)], fill=(r, g, b))
    d.ellipse([x + w * 0.68, y + 8, x + w * 0.68 + 34, y + 42], fill=(255, 236, 180))
    # dunes
    d.polygon([(x, y + h), (x, y + h * 0.72), (x + w * 0.4, y + h * 0.6),
               (x + w * 0.75, y + h * 0.78), (x + w, y + h * 0.66), (x + w, y + h)],
              fill=(96, 58, 32))
    d.polygon([(x, y + h), (x, y + h * 0.86), (x + w * 0.5, y + h * 0.78),
               (x + w, y + h * 0.88), (x + w, y + h)], fill=(70, 42, 24))
    # jet silhouette
    jx, jy = x + w * 0.30, y + h * 0.30
    d.polygon([(jx, jy), (jx + 52, jy + 7), (jx + 66, jy + 11), (jx + 52, jy + 15),
               (jx, jy + 22), (jx + 8, jy + 11)], fill=(25, 20, 20))
    d.polygon([(jx + 22, jy + 2), (jx + 34, jy + 10), (jx + 22, jy + 12)], fill=(25, 20, 20))
    d.polygon([(jx + 26, jy + 20), (jx + 38, jy + 12), (jx + 26, jy + 10)], fill=(25, 20, 20))


def ill_cop(d, x, y, w, h):
    """A globe, a clock running late, and blank placards."""
    d.rectangle([x, y, x + w, y + h], fill=(220, 239, 230))
    cx, cy, r = x + w * 0.30, y + h * 0.52, h * 0.40
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(58, 130, 200))
    for (gx, gy, gr) in [(-0.4, -0.3, 0.22), (0.25, 0.1, 0.26), (-0.1, 0.45, 0.18),
                          (0.45, -0.35, 0.14)]:
        d.ellipse([cx + gx * r - gr * r, cy + gy * r - gr * r,
                   cx + gx * r + gr * r, cy + gy * r + gr * r], fill=(76, 168, 96))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(30, 80, 60), width=2)
    # clock
    kx, ky, kr = x + w * 0.74, y + h * 0.46, h * 0.32
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(255, 255, 255),
              outline=(40, 40, 40), width=2)
    for hh in range(12):
        a = hh * math.pi / 6
        d.line([(kx + math.sin(a) * kr * 0.82, ky - math.cos(a) * kr * 0.82),
                (kx + math.sin(a) * kr * 0.92, ky - math.cos(a) * kr * 0.92)],
               fill=(40, 40, 40), width=2)
    d.line([(kx, ky), (kx + math.sin(-0.15) * kr * 0.62, ky - math.cos(-0.15) * kr * 0.62)],
           fill=(40, 40, 40), width=3)
    d.line([(kx, ky), (kx + math.sin(1.75) * kr * 0.85, ky - math.cos(1.75) * kr * 0.85)],
           fill=(178, 24, 28), width=3)
    d.ellipse([kx - 3, ky - 3, kx + 3, ky + 3], fill=(40, 40, 40))
    # blank placards
    for px in (x + w * 0.12, x + w * 0.42, x + w * 0.68):
        d.line([(px, y + h - 22), (px, y + h - 4)], fill=(90, 70, 50), width=3)
        d.rectangle([px - 13, y + h - 44, px + 13, y + h - 22], fill=(255, 255, 255),
                    outline=(120, 120, 120), width=1)


def ill_pill(d, x, y, w, h):
    """A capsule and tumours shrinking, step by step."""
    d.rectangle([x, y, x + w, y + h], fill=(242, 247, 251))
    # capsule, tilted
    cx, cy = x + w * 0.26, y + h * 0.5
    d.rounded_rectangle([cx - 52, cy - 20, cx + 52, cy + 20], radius=20,
                        fill=(240, 120, 40), outline=(120, 60, 20), width=2)
    d.rounded_rectangle([cx - 52, cy - 20, cx, cy + 20], radius=20, fill=(255, 255, 255),
                        outline=(120, 60, 20), width=2)
    d.rectangle([cx - 2, cy - 20, cx + 2, cy + 20], fill=(120, 60, 20))
    # shrinking circles with down arrows
    for i, rr in enumerate((17, 12, 7)):
        ccx = x + w * (0.58 + i * 0.15)
        ccy = y + h * 0.42
        d.ellipse([ccx - rr, ccy - rr, ccx + rr, ccy + rr], fill=(178, 24, 28))
        d.line([(ccx, ccy + rr + 4), (ccx, ccy + rr + 16)], fill=(60, 60, 60), width=2)
        d.polygon([(ccx, ccy + rr + 20), (ccx - 4, ccy + rr + 13), (ccx + 4, ccy + rr + 13)],
                  fill=(60, 60, 60))
    d.ellipse([x + w * 0.88 - 5, y + h * 0.42 - 5, x + w * 0.88 + 5, y + h * 0.42 + 5],
              fill=(76, 168, 96))


STORIES = [
    # (kicker, headline, body, illustration)
    ("UKRAINE • POLAND",
     "RUSSIA'S BIGGEST BARRAGE HITS UKRAINE — AND REACHES POLAND",
     "More than 400 drones and 110 missiles rain down overnight; at least 8 civilians "
     "killed. Two missiles and a suspected drone come down in Poland — PM Tusk calls it "
     "a deliberate provocation; NATO calls it a grave violation.",
     ill_barrage),
    ("MARKETS",
     "AI STOCK ROUT AS MARKETS SLIDE INTO CORRECTION",
     "US shares fall sharply as AI and chip stocks sell off. The S&P 500 and the Dow "
     "both slip into correction territory.",
     ill_rout),
    ("BRITAIN • EUROPE",
     "UK AND EU SIGN BIGGEST POST-BREXIT DEALS YET",
     "Agri-food trade eased, carbon markets linked, and youth mobility to live, work "
     "or study on either side.",
     ill_ukeu),
    ("WASHINGTON • TEHRAN",
     "TRUMP WEIGHS NEW STRIKES ON IRAN",
     "The president considers more extensive strikes under pressure from "
     "Israel, while talks stall over enriched uranium.",
     ill_iran),
    ("CLIMATE • ANTALYA",
     "COP31 RUNS PAST DEADLINE WITH NO DEAL",
     "The summit closes with no agreed text; fossil-fuel language and a $120bn "
     "package are cut. Protesters halt the closing session.",
     ill_cop),
    ("MEDICINE",
     "PANCREATIC CANCER PILL SHOWS EARLY PROMISE",
     "Daraxonrasib with chemotherapy made tumours undetectable in 1 in 12 of 61 "
     "patients in an early trial; researchers stress it is not a cure.",
     ill_pill),
]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 36
    # masthead
    name_f = font(SERIF_B, 62)
    d.text((W / 2, 30), "THE SATURDAY GLOBE", font=name_f, fill=INK, anchor="ma")
    hline(d, M, W - M, 104, width=3)
    date_f = font(SANS_B, 28)
    d.text((W / 2, 116), "SATURDAY 21 NOVEMBER 2026", font=date_f, fill=RED, anchor="ma")
    hline(d, M, W - M, 156, width=2)

    # lead story
    kicker_f = font(SANS_B, 16)
    d.text((M, 172), STORIES[0][0], font=kicker_f, fill=RED)
    head_f = font(SERIF_B, 33)
    y = para(d, M, 196, STORIES[0][1], head_f, W - 2 * M, leading=1.12)
    body_f = font(SANS, 17)
    STORIES[0][3](d, 606, 292, 382, 208)
    para(d, M, 292, STORIES[0][2], body_f, 554, leading=1.35)
    hline(d, M, W - M, 522, width=2)

    # middle row: two stories
    col_w = (W - 2 * M - 12) // 2
    for i, st in enumerate(STORIES[1:3]):
        x = M + i * (col_w + 12)
        d.text((x, 538), st[0], font=font(SANS_B, 15), fill=RED)
        y = para(d, x, 560, st[1], font(SERIF_B, 23), col_w, leading=1.12)
        st[3](d, x, 622, col_w, 104)
        para(d, x, 736, st[2], font(SANS, 15), col_w, leading=1.3)
    hline(d, M, W - M, 812, width=2)

    # bottom row: three stories, compact: kicker, 2-line headline,
    # short illustration, 3-line body
    col3 = (W - 2 * M - 24) // 3
    for i, st in enumerate(STORIES[3:6]):
        x = M + i * (col3 + 12)
        d.text((x, 824), st[0], font=font(SANS_B, 13), fill=RED)
        para(d, x, 842, st[1], font(SERIF_B, 18), col3, leading=1.12)
        st[3](d, x, 888, col3, 64)
        para(d, x, 958, st[2], font(SANS, 13), col3, leading=1.25)
    return img


def main():
    img = build()
    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
