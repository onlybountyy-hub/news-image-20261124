#!/usr/bin/env python3
"""THE WORLD TODAY - Tuesday 24 November 2026.

A newspaper-style poster of the day's world news, drawn entirely with the
Python standard library. No third-party packages, no external assets, no
network access. Writes entry.png (1024x1024) into $MAKEFUN_OUTPUT_DIR.

Run: MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
"""

import os
import math
import struct
import zlib
import random

W, H = 1024, 1024

# ---------------------------------------------------------------------------
# 5x7 bitmap font (own letterforms, 7 rows of 5 bits each, MSB = left pixel)
# ---------------------------------------------------------------------------
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '-': (0, 0, 0, 0x0E, 0, 0, 0),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    '%': (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '+': (0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
}

# ---------------------------------------------------------------------------
# Canvas + drawing primitives
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x0, y0, x1, y1, c):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w, x1); y1 = min(self.h, y1)
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1):
                i = base + (x - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x0, x1, y, c):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            self.set(x, y, c)

    def vline(self, x, y0, y1, c):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            self.set(x, y, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0); dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def circle(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                    self.set(x, y, c)

    def ring(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if (r - 1) * (r - 1) <= d <= r * r:
                    self.set(x, y, c)

    def tri(self, ax, ay, bx, by, cx, cy, c):
        # filled triangle via scanline
        pts = sorted([(ax, ay), (bx, by), (cx, cy)], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        def interp(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) // (yb - ya)
        for y in range(y0, y2 + 1):
            if y < y1:
                xa = interp(x0, y0, x1, y1, y)
                xb = interp(x0, y0, x2, y2, y)
            else:
                xa = interp(x1, y1, x2, y2, y)
                xb = interp(x0, y0, x2, y2, y)
            self.hline(min(xa, xb), max(xa, xb), y, c)


def text_width(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def draw_text(cv, x, y, s, scale, color, align='left'):
    if align == 'center':
        x -= text_width(s, scale) // 2
    elif align == 'right':
        x -= text_width(s, scale)
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.rect(x + col * scale, y + row * scale,
                            x + (col + 1) * scale, y + (row + 1) * scale, color)
        x += 6 * scale


def wrap_text(s, max_w, scale):
    words = s.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# PNG encoding (hand-written, deterministic)
# ---------------------------------------------------------------------------
def chunk(typ, data):
    out = struct.pack('>I', len(data)) + typ + data
    out += struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
NAVY      = (10, 26, 46)
NAVY_DK   = (6, 16, 30)
PANEL     = (17, 40, 66)
PANEL_BD  = (64, 104, 146)
WHITE     = (242, 246, 250)
SOFT      = (196, 210, 226)
GOLD      = (255, 196, 66)
RED       = (224, 62, 52)
ORANGE    = (255, 140, 40)
TEAL      = (46, 205, 180)
GREEN     = (84, 204, 96)
PURPLE    = (168, 128, 224)
SKY_TOP   = (8, 20, 40)
SKY_HOR   = (18, 46, 80)
SEA       = (12, 44, 76)
SEA_LT    = (30, 80, 120)
SHIP      = (18, 24, 34)
FLAME_Y   = (255, 214, 64)
FLAME_O   = (255, 122, 26)
SMOKE     = (120, 128, 138)

M = 24            # page margin
CW = W - 2 * M    # content width = 976

# ---------------------------------------------------------------------------
# Masthead
# ---------------------------------------------------------------------------
def draw_masthead(cv):
    draw_text(cv, W // 2, 14, "THE WORLD TODAY", 7, WHITE, 'center')
    draw_text(cv, W // 2, 76, "TUESDAY 24 NOVEMBER 2026", 3, GOLD, 'center')
    cv.rect(M, 106, W - M, 109, PANEL_BD)
    cv.rect(M, 112, W - M, 114, PANEL_BD)

# ---------------------------------------------------------------------------
# Hero: night sea, warship, drones, explosion off Benghazi
# ---------------------------------------------------------------------------
def draw_hero(cv):
    x0, y0, x1, y1 = M, 128, W - M, 560
    # sky gradient bands
    for y in range(y0, 384):
        t = (y - y0) / (384 - y0)
        r = int(SKY_TOP[0] + (SKY_HOR[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_HOR[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_HOR[2] - SKY_TOP[2]) * t)
        cv.hline(x0, x1 - 1, y, (r, g, b))
    # stars (seeded, deterministic)
    rng = random.Random(20261124)
    for _ in range(70):
        sx = rng.randint(x0 + 8, x1 - 8)
        sy = rng.randint(y0 + 8, 340)
        cv.set(sx, sy, (200, 214, 232))
        if rng.random() < 0.3:
            cv.set(sx + 1, sy, (160, 176, 200))
    # moon
    cv.circle(884, 192, 34, (238, 232, 204))
    cv.circle(872, 184, 7, (214, 206, 176))
    cv.circle(896, 202, 5, (214, 206, 176))
    cv.circle(880, 208, 4, (222, 214, 186))
    # sea
    cv.rect(x0, 384, x1, y1, SEA)
    for _ in range(26):
        wx = rng.randint(x0 + 10, x1 - 90)
        wy = rng.randint(392, 436)
        wl = rng.randint(30, 80)
        cv.hline(wx, wx + wl, wy, SEA_LT)
    # explosion glow, right side (distant blast at Benghazi port)
    cv.circle(748, 402, 96, (120, 52, 16))
    cv.circle(748, 402, 72, (196, 84, 20))
    cv.circle(748, 402, 50, FLAME_O)
    cv.circle(748, 402, 32, FLAME_Y)
    cv.circle(748, 402, 16, (255, 246, 200))
    # smoke above the blast
    cv.circle(726, 330, 22, SMOKE)
    cv.circle(758, 312, 28, (96, 104, 114))
    cv.circle(790, 332, 20, SMOKE)
    # warship silhouette, centre-left
    cv.rect(300, 404, 560, 438, SHIP)                 # hull
    cv.tri(560, 404, 596, 404, 560, 438, SHIP)        # bow
    cv.rect(340, 380, 420, 404, SHIP)                 # bridge block
    cv.rect(440, 388, 500, 404, SHIP)                 # aft block
    cv.vline(380, 340, 380, SHIP)                     # mast
    cv.hline(368, 392, 352, SHIP)
    cv.vline(470, 360, 388, SHIP)                     # funnel mast
    cv.rect(456, 366, 484, 388, SHIP)                 # funnel
    cv.rect(320, 372, 336, 380, (255, 196, 66))      # lit bridge window
    # seven naval drones: small specks with trails, above the ship
    drones = [(330, 330), (392, 306), (452, 322), (512, 300),
              (566, 326), (618, 306), (664, 330)]
    for dx, dy in drones:
        cv.line(dx - 16, dy + 8, dx, dy, (150, 190, 220))
        cv.circle(dx, dy, 3, WHITE)
    # headline band
    cv.rect(x0, 448, x1, y1, NAVY_DK)
    cv.rect(x0, 448, x1, 451, GOLD)
    draw_text(cv, W // 2, 462, "UKRAINE SINKS RUSSIAN", 5, WHITE, 'center')
    draw_text(cv, W // 2, 502, "WARSHIP OFF LIBYA", 5, WHITE, 'center')
    draw_text(cv, W // 2, 540,
              "ZELENSKY: SEVEN NAVAL DRONES SANK THE CORVETTE MERKURY AT BENGHAZI",
              2, SOFT, 'center')
    # TOP STORY tag
    cv.rect(x0 + 12, y0 + 12, x0 + 138, y0 + 42, RED)
    draw_text(cv, x0 + 75, y0 + 19, "TOP STORY", 2, WHITE, 'center')
    # panel border
    cv.rect(x0, y0, x1, y0 + 2, PANEL_BD)
    cv.rect(x0, y1 - 2, x1, y1, PANEL_BD)
    cv.rect(x0, y0, x0 + 2, y1, PANEL_BD)
    cv.rect(x1 - 2, y0, x1, y1, PANEL_BD)

# ---------------------------------------------------------------------------
# Pictograms for the five grid stories
# ---------------------------------------------------------------------------
def pic_tanker(cv, cx, cy, accent):
    # hull + bow
    cv.rect(cx - 58, cy - 4, cx + 44, cy + 16, accent)
    cv.tri(cx + 44, cy - 4, cx + 66, cy - 4, cx + 44, cy + 16, accent)
    cv.rect(cx - 44, cy - 22, cx - 18, cy - 4, accent)   # bridge
    cv.rect(cx + 8, cy - 26, cx + 26, cy - 4, accent)    # funnel
    cv.rect(cx - 58, cy + 16, cx + 66, cy + 19, SEA_LT)  # waterline
    # spiky mine
    cv.circle(cx + 34, cy - 44, 10, (220, 226, 232))
    for dx, dy in [(-10, 0), (10, 0), (0, -10), (0, 10), (-7, -7), (7, -7)]:
        cv.line(cx + 34, cy - 44, cx + 34 + dx, cy - 44 + dy, (220, 226, 232))
    # small flame on the tanker
    cv.tri(cx - 6, cy - 34, cx + 6, cy - 34, cx, cy - 52, FLAME_O)
    cv.tri(cx - 3, cy - 34, cx + 3, cy - 34, cx, cy - 44, FLAME_Y)

def pic_chart(cv, cx, cy, accent):
    # axes
    cv.vline(cx - 58, cy - 52, cy + 18, SOFT)
    cv.hline(cx - 58, cx + 62, cy + 18, SOFT)
    # rising line + arrowhead
    pts = [(cx - 52, cy + 8), (cx - 26, cy - 6), (cx - 2, cy + 2),
           (cx + 24, cy - 24), (cx + 52, cy - 48)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], accent)
        cv.line(a[0], a[1] + 1, b[0], b[1] + 1, accent)
    cv.line(cx + 52, cy - 48, cx + 38, cy - 48, accent)
    cv.line(cx + 52, cy - 48, cx + 52, cy - 34, accent)
    # chip square
    cv.rect(cx + 30, cy - 6, cx + 58, cy + 16, (24, 60, 92))
    cv.rect(cx + 30, cy - 6, cx + 58, cy - 3, accent)
    cv.rect(cx + 38, cy + 2, cx + 50, cy + 10, accent)

def pic_factory(cv, cx, cy, accent):
    # sawtooth factory
    cv.rect(cx - 58, cy - 6, cx + 58, cy + 18, accent)
    cv.tri(cx - 58, cy - 6, cx - 30, cy - 34, cx - 2, cy - 6, accent)
    cv.tri(cx - 2, cy - 6, cx + 26, cy - 34, cx + 54, cy - 6, accent)
    cv.rect(cx + 34, cy - 52, cx + 48, cy - 6, accent)   # chimney
    # flame on the roof
    cv.tri(cx - 26, cy - 34, cx - 6, cy - 34, cx - 16, cy - 56, FLAME_O)
    cv.tri(cx - 21, cy - 34, cx - 11, cy - 34, cx - 16, cy - 46, FLAME_Y)
    # windows
    for wx in (-44, -18, 8):
        cv.rect(cx + wx, cy + 2, cx + wx + 12, cy + 12, NAVY_DK)

def pic_skyline(cv, cx, cy, accent):
    heights = [44, 62, 38, 70, 52]
    bx = cx - 60
    for i, hh in enumerate(heights):
        bw = 22
        cv.rect(bx, cy + 18 - hh, bx + bw, cy + 18, accent)
        for wy in range(cy + 14 - hh, cy + 12, 12):
            cv.rect(bx + 5, wy, bx + 9, wy + 5, NAVY_DK)
            cv.rect(bx + 13, wy, bx + 17, wy + 5, NAVY_DK)
        bx += bw + 3
    # impact flash above the skyline
    cv.circle(cx + 40, cy - 56, 9, FLAME_Y)
    cv.circle(cx + 40, cy - 56, 5, WHITE)

def pic_quake(cv, cx, cy, accent):
    # ground line with a crack
    cv.hline(cx - 62, cx + 62, cy + 14, SOFT)
    cv.line(cx - 6, cy + 14, cx + 2, cy + 26, SOFT)
    cv.line(cx + 2, cy + 26, cx - 2, cy + 38, SOFT)
    # concentric seismic arcs above the ground line
    for r in (16, 30, 44, 58):
        for ang in range(0, 181, 3):
            x = cx + int(r * math.cos(math.radians(ang)))
            y = cy - 6 - int(r * math.sin(math.radians(ang)))
            cv.set(x, y, accent)
    cv.circle(cx, cy - 6, 6, accent)

# ---------------------------------------------------------------------------
# Grid panels
# ---------------------------------------------------------------------------
PANELS = [
    ("TANKERS BURN IN HORMUZ",
     "THREE OIL TANKERS HIT MINES AND CAUGHT FIRE",
     RED, pic_tanker),
    ("NVIDIA UP 31% IN A DAY",
     "HUANG BACK AS CEO; S&P 500 UP 4.73%",
     GREEN, pic_chart),
    ("FACTORY FIRE KILLS 26",
     "BLAZE IN BANTEN; DOZENS STILL MISSING",
     ORANGE, pic_factory),
    ("AIRSTRIKES KILL SIX IN GAZA",
     "VICTIMS INCLUDE TWO POLICE OFFICERS",
     PURPLE, pic_skyline),
    ("QUAKE SHAKES NEPAL",
     "5.6 MAGNITUDE IN KOSHI, NEAR CHINA BORDER",
     TEAL, pic_quake),
]

def draw_panel(cv, x0, y0, x1, y1, label, fact, accent, pic):
    cv.rect(x0, y0, x1, y1, PANEL)
    cv.rect(x0, y0, x1, y0 + 6, accent)
    cv.rect(x0, y0, x1, y0 + 2, PANEL_BD)
    cv.rect(x0, y1 - 2, x1, y1, PANEL_BD)
    cv.rect(x0, y0, x0 + 2, y1, PANEL_BD)
    cv.rect(x1 - 2, y0, x1, y1, PANEL_BD)
    cx = (x0 + x1) // 2
    pic(cv, cx, y0 + 88, accent)
    draw_text(cv, cx, y0 + 122, label, 2, WHITE, 'center')
    lines = wrap_text(fact, (x1 - x0) - 28, 2)
    ly = y0 + 146
    for ln in lines:
        draw_text(cv, cx, ly, ln, 2, SOFT, 'center')
        ly += 18

def draw_grid(cv):
    # row 1: three panels
    y0, y1 = 576, 760
    xs = [(M, 344), (352, 672), (680, W - M)]
    for (x0, x1), (label, fact, accent, pic) in zip(xs, PANELS[:3]):
        draw_panel(cv, x0, y0, x1, y1, label, fact, accent, pic)
    # row 2: two panels
    y0, y1 = 768, 952
    xs = [(M, 504), (520, W - M)]
    for (x0, x1), (label, fact, accent, pic) in zip(xs, PANELS[3:]):
        draw_panel(cv, x0, y0, x1, y1, label, fact, accent, pic)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def draw_footer(cv):
    draw_text(cv, W // 2, 970,
              "24 NOVEMBER 2026 - THE WORLD IN ONE IMAGE", 2, SOFT, 'center')

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    cv = Canvas(W, H)
    cv.rect(0, 0, W, H, NAVY)
    draw_masthead(cv)
    draw_hero(cv)
    draw_grid(cv)
    draw_footer(cv)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, size))

if __name__ == "__main__":
    main()
