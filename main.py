#!/usr/bin/env python3
"""THE WORLD TODAY - Tuesday 24 November 2026.

A single-image newspaper front page summing up 24 November 2026 world
news: six equal illustrated panels in a 3x2 grid under a masthead.

Pure Python standard library only. No third-party imports, no network,
no external assets. The image is drawn pixel by pixel into an RGB buffer
and encoded as PNG by hand (zlib + struct). Output is fully deterministic:
no timestamps, no unseeded randomness, fixed compression level.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
NAVY = (11, 31, 58)        # masthead / page background
PANEL = (19, 42, 69)       # panel background
PANEL_DARK = (15, 34, 56)  # pictogram field inside a panel
WHITE = (245, 247, 250)
GOLD = (212, 175, 55)
MUTED = (176, 190, 205)    # fact-line text
SEA = (16, 52, 84)
SKY = (24, 68, 110)

ACCENTS = [
    (56, 189, 248),    # 1 warship - sky blue
    (245, 158, 11),    # 2 tanker  - amber
    (34, 197, 94),     # 3 nvidia - green
    (239, 68, 68),     # 4 factory fire - red
    (167, 139, 250),   # 5 gaza   - violet
    (250, 204, 21),    # 6 quake  - yellow
]

# ------------------------------------------------------------------ canvas
buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def fill_rect(x0, y0, x1, y1, c):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            buf[i] = c[0]
            buf[i + 1] = c[1]
            buf[i + 2] = c[2]


def hline(x0, x1, y, c, th=1):
    for t in range(th):
        for x in range(x0, x1):
            px(x, y + t, c)


def vline(x, y0, y1, c, th=1):
    for t in range(th):
        for y in range(y0, y1):
            px(x + t, y, c)


def line(x0, y0, x1, y1, c, th=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        for a in range(th):
            for b in range(th):
                px(x + a - th // 2, y + b - th // 2, c)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def fill_circle(cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        dy = y - cy
        span = int(math.sqrt(max(0, r * r - dy * dy)))
        for x in range(cx - span, cx + span + 1):
            px(x, y, c)


def circle(cx, cy, r, c, th=3):
    for a in range(360):
        rad = math.radians(a)
        for t in range(th):
            px(int(cx + (r + t - th // 2) * math.cos(rad)),
               int(cy + (r + t - th // 2) * math.sin(rad)), c)


def fill_poly(points, c):
    # Scanline polygon fill. points: list of (x, y).
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y0, y1 = min(ys), max(ys)
    n = len(points)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x0, yy0 = points[i]
            x1, yy1 = points[(i + 1) % n]
            if yy0 == yy1:
                continue
            if (yy0 <= y < yy1) or (yy1 <= y < yy0):
                t = (y - yy0) / (yy1 - yy0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for x in range(int(math.ceil(xs[k])), int(math.floor(xs[k + 1])) + 1):
                px(x, y, c)


def fill_triangle(x0, y0, x1, y1, x2, y2, c):
    fill_poly([(x0, y0), (x1, y1), (x2, y2)], c)


# ------------------------------------------------------------- bitmap font
# 5x7 glyphs, one row per integer, bit 4 = leftmost column.
FONT = {
    'A': [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    'B': [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    'C': [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    'D': [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    'E': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    'F': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    'G': [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    'H': [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    'I': [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    'J': [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    'K': [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    'L': [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    'M': [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    'N': [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    'O': [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    'P': [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    'Q': [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    'R': [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    'S': [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    'T': [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    'U': [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    'V': [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    'W': [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    'X': [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    'Y': [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    'Z': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    '0': [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    '1': [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    '2': [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F],
    '3': [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    '4': [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    '5': [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    '6': [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    '7': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    '8': [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    '9': [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    ' ': [0, 0, 0, 0, 0, 0, 0],
    '.': [0, 0, 0, 0, 0, 0x0C, 0x0C],
    ',': [0, 0, 0, 0, 0x0C, 0x04, 0x08],
    "'": [0x04, 0x04, 0x08, 0, 0, 0, 0],
    '-': [0, 0, 0, 0x1F, 0, 0, 0],
    ':': [0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0],
    '!': [0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04],
    '?': [0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04],
    '%': [0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13],
    '+': [0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0],
    '/': [0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10],
    '(': [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ')': [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    '=': [0, 0, 0x1F, 0, 0x1F, 0, 0],
    '&': [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    '*': [0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0],
    '\u00b7': [0, 0, 0, 0x0C, 0x0C, 0, 0],  # middle dot
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(s, x, y, scale, color, align="left"):
    """Draw text; x is left edge (or centre when align='center')."""
    if align == "center":
        x = x - text_width(s, scale) // 2
    cx = x
    for ch in s:
        glyph = FONT.get(ch.upper(), FONT['?'])
        for r in range(7):
            row = glyph[r]
            for cbit in range(5):
                if row & (1 << (4 - cbit)):
                    fill_rect(cx + cbit * scale, y + r * scale,
                              cx + (cbit + 1) * scale, y + (r + 1) * scale,
                              color)
        cx += 6 * scale
    return x


# -------------------------------------------------------------- PNG writer
def chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return c


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# -------------------------------------------------------------- pictograms
# Each takes the pictogram field box (x0, y0, x1, y1) and its accent colour.

def pic_warship(x0, y0, x1, y1, acc):
    """Warship on a dark sea, two naval drones above it."""
    mid = (x0 + x1) // 2
    sea_y = y0 + int((y1 - y0) * 0.66)
    fill_rect(x0, sea_y, x1, y1, SEA)
    # waves
    for k in range(3):
        wy = sea_y + 14 + k * 20
        for x in range(x0 + 8, x1 - 8, 26):
            line(x, wy, x + 13, wy - 5, (120, 180, 220), 3)
    # hull (grey warship)
    hull = (148, 163, 184)
    fill_poly([(mid - 118, sea_y - 6), (mid + 118, sea_y - 6),
               (mid + 96, sea_y + 26), (mid - 96, sea_y + 26)], hull)
    # deck + superstructure
    fill_rect(mid - 78, sea_y - 34, mid + 40, sea_y - 6, (176, 190, 205))
    fill_rect(mid - 46, sea_y - 58, mid + 8, sea_y - 34, (148, 163, 184))
    # mast + radar
    vline(mid - 18, sea_y - 96, sea_y - 58, WHITE, 5)
    fill_circle(mid - 18, sea_y - 100, 7, WHITE)
    # gun turret + barrel
    fill_rect(mid + 52, sea_y - 22, mid + 96, sea_y - 6, (120, 135, 155))
    line(mid + 92, sea_y - 18, mid + 122, sea_y - 30, (120, 135, 155), 5)
    # flag
    line(mid - 18, sea_y - 96, mid - 18, sea_y - 122, WHITE, 4)
    fill_poly([(mid - 18, sea_y - 122), (mid + 8, sea_y - 114),
               (mid - 18, sea_y - 106)], acc)
    # two drones in the sky
    for dx, dy in ((mid - 96, y0 + 34), (mid + 92, y0 + 58)):
        fill_rect(dx - 16, dy - 4, dx + 16, dy + 4, WHITE)
        fill_circle(dx - 20, dy - 6, 5, acc)
        fill_circle(dx + 20, dy - 6, 5, acc)
        fill_circle(dx - 20, dy + 8, 5, acc)
        fill_circle(dx + 20, dy + 8, 5, acc)
        fill_circle(dx, dy, 4, (239, 68, 68))


def pic_tanker(x0, y0, x1, y1, acc):
    """Oil tanker in the strait, a spiked mine beside it, small flames."""
    mid = (x0 + x1) // 2
    sea_y = y0 + int((y1 - y0) * 0.70)
    fill_rect(x0, sea_y, x1, y1, SEA)
    for k in range(2):
        wy = sea_y + 16 + k * 20
        for x in range(x0 + 8, x1 - 8, 26):
            line(x, wy, x + 13, wy - 5, (120, 180, 220), 3)
    # tanker hull
    fill_poly([(mid - 122, sea_y - 34), (mid + 122, sea_y - 34),
               (mid + 104, sea_y + 8), (mid - 104, sea_y + 8)],
              (90, 60, 48))
    fill_rect(mid - 122, sea_y - 42, mid + 122, sea_y - 34, (150, 80, 50))
    # deck containers
    fill_rect(mid - 100, sea_y - 76, mid - 58, sea_y - 42, (220, 120, 60))
    fill_rect(mid - 52, sea_y - 76, mid - 10, sea_y - 42, (60, 140, 180))
    fill_rect(mid - 4, sea_y - 76, mid + 38, sea_y - 42, (200, 200, 90))
    # bridge tower
    fill_rect(mid + 66, sea_y - 96, mid + 108, sea_y - 42, WHITE)
    for wy in range(sea_y - 88, sea_y - 48, 12):
        fill_rect(mid + 72, wy, mid + 102, wy + 6, NAVY)
    # flames on deck (tanker caught fire)
    flame = (245, 158, 11)
    for fx in (mid - 88, mid + 14):
        fill_triangle(fx - 12, sea_y - 76, fx, sea_y - 112, fx + 12,
                      sea_y - 76, flame)
        fill_triangle(fx - 6, sea_y - 76, fx, sea_y - 98, fx + 6,
                      sea_y - 76, (250, 220, 80))
    # spiked mine floating in the water, right of the tanker
    mx, my = mid + 122, sea_y + 34
    for a in range(0, 360, 30):
        rad = math.radians(a)
        line(int(mx + 12 * math.cos(rad)), int(my + 12 * math.sin(rad)),
             int(mx + 26 * math.cos(rad)), int(my + 26 * math.sin(rad)),
             (200, 210, 220), 4)
    fill_circle(mx, my, 15, (60, 70, 80))
    fill_circle(mx - 5, my - 5, 4, (200, 210, 220))


def pic_chip(x0, y0, x1, y1, acc):
    """Microchip, bottom left, with a steep rising chart arrow."""
    # chip, bottom left
    chx, chy = x0 + 78, y1 - 74
    for k in range(-2, 3):
        vline(chx - 46 + k * 21, chy - 50, chy - 36, acc, 4)
        vline(chx - 46 + k * 21, chy + 36, chy + 50, acc, 4)
        hline(chx - 50, chx - 36, chy - 46 + k * 21, acc, 4)
        hline(chx + 36, chx + 50, chy - 46 + k * 21, acc, 4)
    fill_rect(chx - 36, chy - 36, chx + 36, chy + 36, (30, 60, 40))
    fill_rect(chx - 36, chy - 36, chx + 36, chy - 29, acc)
    fill_rect(chx - 18, chy - 18, chx + 18, chy + 18, acc)
    fill_rect(chx - 10, chy - 10, chx + 10, chy + 10, WHITE)
    # chart axes
    line(x0 + 14, y0 + 18, x0 + 14, y1 - 16, (90, 110, 130), 4)
    line(x0 + 14, y1 - 16, x1 - 14, y1 - 16, (90, 110, 130), 4)
    # rising arrow line (steep), across the upper right
    pts = [(x0 + 128, y1 - 34), (x0 + 168, y1 - 62), (x0 + 198, y1 - 58),
           (x0 + 238, y1 - 108), (x0 + 272, y1 - 138)]
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], acc, 7)
    hx, hy = pts[-1]
    fill_triangle(hx, hy - 22, hx + 26, hy - 2, hx - 2, hy + 6, acc)


def pic_factory(x0, y0, x1, y1, acc):
    """Factory with sawtooth roof, chimney, big flames."""
    mid = (x0 + x1) // 2
    gy = y1 - 26
    fill_rect(x0, gy, x1, y1, (24, 40, 58))
    # chimney with smoke
    fill_rect(mid + 82, y0 + 46, mid + 108, gy, (120, 130, 145))
    fill_rect(mid + 76, y0 + 38, mid + 114, y0 + 48, (150, 160, 175))
    fill_circle(mid + 95, y0 + 22, 12, (140, 150, 165))
    fill_circle(mid + 112, y0 + 8, 9, (140, 150, 165))
    # factory body, sawtooth roof
    fill_rect(mid - 118, y0 + 96, mid + 70, gy, (176, 190, 205))
    fill_poly([(mid - 118, y0 + 96), (mid - 72, y0 + 62),
               (mid - 72, y0 + 96), (mid - 26, y0 + 62),
               (mid - 26, y0 + 96), (mid + 20, y0 + 62),
               (mid + 20, y0 + 96), (mid + 70, y0 + 62),
               (mid + 70, y0 + 96)], (140, 155, 175))
    # windows
    for wx in range(mid - 104, mid + 60, 36):
        fill_rect(wx, y0 + 128, wx + 20, y0 + 158, NAVY)
        fill_rect(wx, y0 + 168, wx + 20, y0 + 198, NAVY)
    # flames over the roof
    for fx, fh in ((mid - 88, 66), (mid - 40, 84), (mid + 8, 62)):
        fill_triangle(fx - 22, y0 + 96, fx, y0 + 96 - fh, fx + 22, y0 + 96,
                      (245, 158, 11))
        fill_triangle(fx - 11, y0 + 96, fx, y0 + 96 - fh + 26, fx + 11,
                      y0 + 96, (250, 220, 80))


def pic_gaza(x0, y0, x1, y1, acc):
    """City skyline with smoke columns rising."""
    mid = (x0 + x1) // 2
    gy = y1 - 22
    fill_rect(x0, gy, x1, y1, (24, 40, 58))
    # skyline
    buildings = [(-128, 96, 44), (-78, 150, 58), (-12, 120, 48),
                 (44, 168, 62), (112, 108, 40)]
    for bx, bh, bw in buildings:
        fill_rect(mid + bx, gy - bh, mid + bx + bw, gy, (150, 160, 175))
        for wy in range(gy - bh + 12, gy - 10, 22):
            for wx in range(mid + bx + 8, mid + bx + bw - 8, 16):
                fill_rect(wx, wy, wx + 7, wy + 9, GOLD)
    # smoke columns
    for sx, sy in ((mid - 100, y0 + 40), (mid + 20, y0 + 26),
                   (mid + 96, y0 + 52)):
        fill_circle(sx, sy, 16, (150, 155, 165))
        fill_circle(sx + 10, sy - 18, 12, (165, 170, 180))
        fill_circle(sx - 6, sy - 34, 10, (180, 185, 195))
    # small warning star above the skyline
    sx, sy = mid + 66, y0 + 96
    fill_triangle(sx, sy - 14, sx + 5, sy + 2, sx - 5, sy + 2, acc)
    fill_triangle(sx, sy + 14, sx + 5, sy - 2, sx - 5, sy - 2, acc)


def pic_quake(x0, y0, x1, y1, acc):
    """Cracked ground with seismic waves radiating from the epicentre."""
    mid = (x0 + x1) // 2
    gy = y0 + int((y1 - y0) * 0.62)
    # seismic rings from the epicentre
    ex, ey = mid, gy - 8
    for r in (26, 52, 78, 104):
        circle(ex, ey, r, acc, 5)
    fill_circle(ex, ey, 12, (239, 68, 68))
    fill_circle(ex, ey, 5, WHITE)
    # ground
    fill_rect(x0, gy, x1, y1, (60, 48, 36))
    fill_rect(x0, gy, x1, gy + 8, (96, 76, 52))
    # zigzag crack across the ground
    crack = [(x0 + 10, gy + 10), (x0 + 60, gy + 44), (x0 + 96, gy + 22),
             (x0 + 150, gy + 58), (x0 + 190, gy + 30), (x0 + 240, gy + 62),
             (x0 + 290, gy + 34), (x1 - 10, gy + 56)]
    for i in range(len(crack) - 1):
        line(crack[i][0], crack[i][1], crack[i + 1][0], crack[i + 1][1],
             (20, 16, 10), 6)
    # two small tilted houses on the ground
    for hx, tilt in ((mid - 116, -6), (mid + 62, 5)):
        fill_poly([(hx, gy + 70), (hx + 52, gy + 70 + tilt),
                   (hx + 52, gy + 34 + tilt), (hx, gy + 34)], (176, 190, 205))
        fill_poly([(hx - 6, gy + 36), (hx + 26, gy + 14),
                   (hx + 58, gy + 36 + tilt)], (150, 60, 50))
        fill_rect(hx + 20, gy + 52, hx + 32, gy + 70, NAVY)


# ------------------------------------------------------------------ layout
STORIES = [
    # (label, [fact lines], pictogram, accent index)
    ("WARSHIP SUNK",
     ["UKRAINE DRONES SANK", "RUSSIAN CORVETTE",
      "MERKURY OFF LIBYA"],
     pic_warship, 0),
    ("TANKERS HIT",
     ["THREE TANKERS HIT MINES", "CAUGHT FIRE IN HORMUZ"],
     pic_tanker, 1),
    ("NVIDIA SOARS 31%",
     ["HUANG BACK AS CEO", "S&P UP 4.73%"],
     pic_chip, 2),
    ("FACTORY FIRE",
     ["26 KILLED, DOZENS MISSING", "IN BANTEN, INDONESIA"],
     pic_factory, 3),
    ("GAZA AIRSTRIKES",
     ["AT LEAST SIX KILLED", "TWO POLICE OFFICERS"],
     pic_gaza, 4),
    ("NEPAL QUAKE",
     ["MAGNITUDE 5.6", "KOSHI PROVINCE"],
     pic_quake, 5),
]


def draw_masthead():
    fill_rect(0, 0, W, 118, NAVY)
    draw_text("THE WORLD TODAY", W // 2, 12, 7, WHITE, align="center")
    draw_text("TUESDAY 24 NOVEMBER 2026", W // 2, 70, 4, GOLD,
              align="center")
    fill_rect(0, 112, W, 116, GOLD)


def draw_panel(px0, py0, pw, ph, story):
    label, facts, pic, ai = story
    acc = ACCENTS[ai]
    fill_rect(px0, py0, px0 + pw, py0 + ph, PANEL)
    fill_rect(px0, py0, px0 + pw, py0 + 7, acc)
    # pictogram field
    fx0, fy0 = px0 + 10, py0 + 16
    fx1, fy1 = px0 + pw - 10, py0 + 252
    fill_rect(fx0, fy0, fx1, fy1, PANEL_DARK)
    pic(fx0, fy0, fx1, fy1, acc)
    # label + accent underline (label scale 3 fits the 326 px panel)
    draw_text(label, px0 + pw // 2, py0 + 266, 3, WHITE, align="center")
    lw = text_width(label, 3)
    fill_rect(px0 + pw // 2 - lw // 2, py0 + 296,
              px0 + pw // 2 + lw // 2, py0 + 299, acc)
    # fact lines, scale 2
    for i, fact in enumerate(facts):
        draw_text(fact, px0 + pw // 2, py0 + 312 + i * 24, 2, MUTED,
                  align="center")


def draw_footer():
    fill_rect(0, 962, W, H, NAVY)
    fill_rect(0, 962, W, 965, GOLD)
    draw_text("24 NOVEMBER 2026 \u00b7 THE WORLD IN ONE IMAGE",
              W // 2, 978, 3, MUTED, align="center")


def build():
    fill_rect(0, 0, W, H, NAVY)
    draw_masthead()
    # 3 x 2 grid of equal panels
    gx, gy = 12, 128
    pw, ph = 326, 412
    gap = 10
    for i, story in enumerate(STORIES):
        col, row = i % 3, i // 3
        draw_panel(gx + col * (pw + gap), gy + row * (ph + gap),
                   pw, ph, story)
    draw_footer()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    build()
    write_png(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
