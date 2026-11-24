#!/usr/bin/env python3
"""THE WORLD TODAY - Tuesday, 24 November 2026.

A deterministic 1024x1024 newspaper poster summing up the world's news
of Tuesday 24 November 2026. Every story on the poster happened, or was
first reported, on 24 November 2026 (verified against Reuters, Chess.com,
EarthSky and AAA). Drawn from scratch with PIL; no network, no randomness,
no timestamps in the output, so two runs produce byte-identical PNGs.

Usage:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes entry.png (1024x1024, under 1 MiB) to the output directory.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette: newsprint cream, ink navy, signal red, amber accent ---
CREAM = (247, 242, 232)
PAPER = (252, 250, 244)
INK = (18, 24, 38)
NAVY = (15, 36, 64)
NAVY2 = (22, 52, 88)
SKY = (38, 74, 116)
RED = (178, 34, 34)
AMBER = (232, 164, 42)
GREY = (88, 94, 106)
LIGHT = (226, 232, 240)
WHITE = (255, 255, 255)
TEAL = (18, 110, 105)
GOLD = (176, 132, 24)

# --- the day's verified stories (see SOURCES.md for one source each) ---
HERO = {
    "kicker": "POLAND  •  NATO'S EASTERN FLANK",
    "headline": "RUSSIAN DRONE STRAYS INTO POLAND",
    "deck": (
        "Warsaw holds its fire as the drone turns back east overnight, "
        "days after three Russian missiles landed in Poland. "
        "NATO jets are on watch."
    ),
}

TILES = [
    {
        "kicker": "SOUTH KOREA",
        "color": RED,
        "headline": "SEOUL SOUNDS THE ALARM",
        "deck": (
            "Ulleung island takes shelter as Russian aircraft "
            "near; jets scramble, alert lifted in minutes."
        ),
        "icon": "siren",
    },
    {
        "kicker": "CHESS  •  GENEVA",
        "color": INK,
        "headline": "CROWN ON THE LINE",
        "deck": (
            "Gukesh defends his title against Sindarov, "
            "both 20, in the youngest title match ever. "
            "Game 1 begins today."
        ),
        "icon": "chess",
    },
    {
        "kicker": "THE SKY TONIGHT",
        "color": TEAL,
        "headline": "BEAVER SUPERMOON PEAKS",
        "deck": (
            "November's full Moon, at its closest to Earth, "
            "shines beside the Pleiades star cluster."
        ),
        "icon": "moon",
    },
    {
        "kicker": "UNITED STATES",
        "color": GOLD,
        "headline": "AMERICA HITS THE ROAD",
        "deck": (
            "The Thanksgiving rush begins: 81.5 million "
            "travel this week, 5.96 million by air."
        ),
        "icon": "plane",
    },
]

FOOTER_NOTE = (
    "Every story above happened, or was first reported, "
    "on Tuesday 24 November 2026."
)
FOOTER_SOURCES = "Sources: Reuters  •  Chess.com  •  EarthSky  •  AAA"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
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


def text_block(draw, xy, lines, fnt, fill, leading):
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_siren(d, cx, cy, s, color):
    """Warning triangle with an exclamation mark."""
    pts = [(cx, cy - s), (cx + s, cy + s * 0.8), (cx - s, cy + s * 0.8)]
    d.polygon(pts, outline=color, width=4)
    d.rectangle([cx - 3, cy - s * 0.45, cx + 3, cy + s * 0.25], fill=color)
    d.ellipse([cx - 4, cy + s * 0.45, cx + 4, cy + s * 0.62], fill=color)


def draw_chess(d, cx, cy, s, color):
    """A chessboard square with a crown on top."""
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=color)
    for i in range(4):
        for j in range(4):
            if (i + j) % 2 == 0:
                d.rectangle(
                    [cx - s + i * s / 2, cy - s + j * s / 2,
                     cx - s + (i + 1) * s / 2, cy - s + (j + 1) * s / 2],
                    fill=CREAM)
    # crown
    top = cy - s * 1.05
    d.polygon([(cx - s * 0.7, cy - s * 0.7), (cx - s * 0.7, top + s * 0.25),
               (cx - s * 0.35, top + s * 0.55), (cx, top),
               (cx + s * 0.35, top + s * 0.55), (cx + s * 0.7, top + s * 0.25),
               (cx + s * 0.7, cy - s * 0.7)], fill=AMBER, outline=INK)


def draw_moon(d, cx, cy, s, color):
    """Full moon with a cluster of small stars (the Pleiades)."""
    d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=AMBER, outline=color, width=3)
    d.ellipse([cx - s * 0.55, cy - s * 0.3, cx - s * 0.25, cy],
              fill=(214, 138, 20))
    d.ellipse([cx + s * 0.1, cy + s * 0.35, cx + s * 0.4, cy + s * 0.65],
              fill=(214, 138, 20))
    for dx, dy, r in [(0.95, -0.6, 4), (1.05, -0.3, 3), (0.85, -0.25, 3),
                      (1.0, 0.05, 3), (0.9, 0.3, 2), (1.1, -0.55, 2)]:
        d.ellipse([cx + dx * s - r, cy + dy * s - r,
                   cx + dx * s + r, cy + dy * s + r], fill=TEAL)


def draw_plane(d, cx, cy, s, color):
    """Simple jet in flight, nose to the right, with a dotted trail."""
    # fuselage
    d.ellipse([cx - s * 1.1, cy - s * 0.22, cx + s * 1.1, cy + s * 0.22],
              fill=color)
    # nose
    d.polygon([(cx + s * 0.9, cy - s * 0.22), (cx + s * 1.5, cy),
               (cx + s * 0.9, cy + s * 0.22)], fill=color)
    # tail fin
    d.polygon([(cx - s * 1.0, cy - s * 0.18), (cx - s * 0.75, cy - s * 0.85),
               (cx - s * 0.45, cy - s * 0.18)], fill=color)
    # swept wing below
    d.polygon([(cx - s * 0.1, cy + s * 0.1), (cx + s * 0.35, cy + s * 0.95),
               (cx + s * 0.6, cy + s * 0.1)], fill=color)
    for i in range(2):
        x = cx - s * (1.35 + i * 0.22)
        d.ellipse([x - 3, cy - 3, x + 3, cy + 3], fill=GREY)


def draw_drone_scene(d, x0, y0, x1, y1):
    """Night sky over Poland: radar arcs, a small drone, red alert band."""
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    # radar sweep arcs, bottom-left origin
    ox, oy = x0 + 130, y1 - 10
    for r in (90, 170, 250, 330):
        d.arc([ox - r, oy - r, ox + r, oy + r], start=270, end=360,
              fill=(64, 110, 160), width=2)
    d.line([ox, oy - 330, ox, oy], fill=(64, 110, 160), width=2)
    d.line([ox, oy, x1, oy], fill=(64, 110, 160), width=2)
    # stars
    for sx, sy, r in [(640, 30, 2), (720, 70, 3), (820, 40, 2), (900, 90, 3),
                      (600, 110, 2), (960, 30, 2), (760, 130, 2)]:
        d.ellipse([x0 + sx - r, y0 + sy - r, x0 + sx + r, y0 + sy + r],
                  fill=WHITE)
    # drone silhouette: body + four rotors
    cx, cy = x0 + 800, y0 + 150
    d.ellipse([cx - 70, cy - 12, cx + 70, cy + 12], fill=(10, 18, 32))
    d.ellipse([cx - 18, cy - 8, cx + 18, cy + 8], fill=RED)
    for dx in (-78, 78):
        d.ellipse([cx + dx - 26, cy - 34, cx + dx + 26, cy - 22],
                  outline=LIGHT, width=3)
        d.line([cx + dx, cy - 12, cx + dx, cy - 22], fill=LIGHT, width=3)
    # dashed flight path curving away east, clear of the deck text
    for i in range(8):
        t = i / 7.0
        fx = cx - 100 + t * 220
        fy = cy + 70 + t * t * 55
        d.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=AMBER)
    # Polish white-red band along the bottom of the scene
    d.rectangle([x0, y1 - 26, x1, y1 - 13], fill=WHITE)
    d.rectangle([x0, y1 - 13, x1, y1], fill=RED)


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---------- masthead ----------
    d.rectangle([0, 0, W, 104], fill=NAVY)
    d.rectangle([0, 104, W, 110], fill=AMBER)
    f_title = font(SERIF_B, 46)
    d.text((32, 24), "THE WORLD TODAY", font=f_title, fill=CREAM)
    f_date = font(SANS_B, 22)
    date_txt = "TUESDAY, 24 NOVEMBER 2026"
    dw = d.textlength(date_txt, font=f_date)
    d.text((W - 32 - dw, 34), date_txt, font=f_date, fill=AMBER)

    # ---------- hero ----------
    hx0, hy0, hx1, hy1 = 28, 128, W - 28, 500
    draw_drone_scene(d, hx0, hy0, hx1, hy1)
    f_kick = font(SANS_B, 22)
    d.text((hx0 + 28, hy0 + 24), HERO["kicker"], font=f_kick, fill=AMBER)
    f_head = font(SERIF_B, 58)
    head_lines = wrap(d, HERO["headline"], f_head, hx1 - hx0 - 56)
    y = text_block(d, (hx0 + 28, hy0 + 58), head_lines, f_head, CREAM, 66)
    f_deck = font(SANS, 23)
    deck_lines = wrap(d, HERO["deck"], f_deck, 560)
    text_block(d, (hx0 + 28, y + 14), deck_lines, f_deck, LIGHT, 31)

    # ---------- grid: 2 x 2 tiles ----------
    tiles_top, tile_h, gap = 512, 204, 10
    tile_w = (W - 56 - gap) // 2
    f_tkick = font(SANS_B, 19)
    f_thead = font(SERIF_B, 29)
    f_tdeck = font(SANS, 19)
    icons = {"siren": draw_siren, "chess": draw_chess,
             "moon": draw_moon, "plane": draw_plane}
    for i, t in enumerate(TILES):
        col, row = i % 2, i // 2
        x0 = 28 + col * (tile_w + gap)
        y0 = tiles_top + row * (tile_h + gap)
        x1, y1 = x0 + tile_w, y0 + tile_h
        d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=PAPER,
                            outline=(210, 203, 188), width=2)
        d.rectangle([x0 + 10, y0, x1 - 10, y0 + 6], fill=t["color"])
        icons[t["icon"]](d, x0 + 58, y0 + 92, 36, t["color"])
        tx = x0 + 112
        d.text((tx, y0 + 16), t["kicker"], font=f_tkick, fill=t["color"])
        head = wrap(d, t["headline"], f_thead, tile_w - 126)
        y = text_block(d, (tx, y0 + 44), head, f_thead, INK, 32)
        deck = wrap(d, t["deck"], f_tdeck, tile_w - 126)
        text_block(d, (tx, y + 6), deck, f_tdeck, GREY, 24)

    # ---------- footer ----------
    fy0 = 944
    d.rectangle([0, fy0, W, H], fill=NAVY)
    f_foot = font(SANS_B, 19)
    d.text((32, fy0 + 10), FOOTER_NOTE, font=f_foot, fill=CREAM)
    f_src = font(SANS, 18)
    d.text((32, fy0 + 38), FOOTER_SOURCES, font=f_src, fill=LIGHT)
    return img


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not outdir:
        outdir = "/output" if os.path.isdir("/output") else "."
    os.makedirs(outdir, exist_ok=True)
    img = build()
    path = os.path.join(outdir, "entry.png")
    img.save(path, format="PNG", compress_level=9)
    print("wrote", path, img.size)


if __name__ == "__main__":
    main()
