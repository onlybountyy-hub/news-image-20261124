#!/usr/bin/env python3
"""news-image-20261124: draws the 24 November 2026 world-news poster.

Pure Python standard library only. Renders a 1024x1024 PNG using a small
hand-defined 5x7 bitmap font and a hand-written PNG encoder (zlib).
No network, no files read, no randomness, no wall-clock time: two runs
produce byte-identical output.

Run:  python3 -P -s main.py
Writes entry.png into $MAKEFUN_OUTPUT_DIR (or the current directory
when that variable is unset).
"""

import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

# Colours (R, G, B).
NAVY = (10, 30, 60)
HERO_NAVY = (18, 44, 82)
CREAM = (247, 241, 227)
GOLD = (212, 175, 55)
RED = (192, 57, 43)
WHITE = (255, 255, 255)
DARK = (20, 30, 45)
GREY = (96, 96, 90)

# ---------------------------------------------------------------------------
# 5x7 bitmap font, defined by hand. Each glyph is 7 rows of 5 cells;
# "#" is an inked cell, " " is blank. Uppercase letters, digits and the
# punctuation this poster needs.
# ---------------------------------------------------------------------------
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "    #", "    #", "    #", "    #", "#   #", " ### "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ";": ("     ", "     ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    "'": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
    "\u2022": ("     ", "     ", " ### ", " ### ", " ### ", "     ", "     "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "(": ("   # ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " #   "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "&": (" ### ", "#   #", "#   #", " #   ", "# # #", "#  # ", " ## #"),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "%": ("#   #", "#  # ", "   # ", "  #  ", " #   ", "#  # ", "#   #"),
}


def set_px(buf, x, y, color):
    """Set one RGB pixel, silently ignoring out-of-bounds coordinates."""
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        i = (y * WIDTH + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def fill_rect(buf, x, y, w, h, color):
    """Fill an axis-aligned rectangle (clipped to the canvas)."""
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    r, g, b = color
    for yy in range(y0, y1):
        base = (yy * WIDTH + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i], buf[i + 1], buf[i + 2] = r, g, b


def text_width(text, scale):
    """Pixel width of text at the given scale (5px glyph + 1px gap)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_glyph(buf, x, y, ch, scale, color):
    rows = FONT.get(ch)
    if rows is None:
        return
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            if cell == "#":
                for dy in range(scale):
                    for dx in range(scale):
                        set_px(buf, x + c * scale + dx, y + r * scale + dy, color)


def draw_text(buf, x, y, text, scale, color):
    """Draw one line of text, left-aligned at (x, y)."""
    cx = x
    for ch in text:
        draw_glyph(buf, cx, y, ch, scale, color)
        cx += 6 * scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(buf, x, y, text, scale, color, max_width, line_gap):
    """Draw wrapped text; returns the number of lines drawn."""
    lines = wrap_text(text, scale, max_width)
    for i, line in enumerate(lines):
        draw_text(buf, x, y + i * (7 * scale + line_gap), line, scale, color)
    return len(lines)


# ---------------------------------------------------------------------------
# PNG encoder (hand-written: signature + IHDR + IDAT via zlib + IEND,
# with a correct CRC32 on every chunk). Filter type 0 on every scanline.
# ---------------------------------------------------------------------------
def _chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png(buf):
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = WIDTH * 3
    for y in range(HEIGHT):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------------------
# Poster layout. All copy is uppercase so the one font covers everything.
# ---------------------------------------------------------------------------
MASTHEAD_TITLE = "THE WORLD TODAY"
DATE_LINE = "TUESDAY, 24 NOVEMBER 2026"

HERO_KICKER = "POLAND \u2022 NATO'S EASTERN FLANK"
HERO_HEADLINE = ["RUSSIAN DRONE", "STRAYS INTO POLAND"]
HERO_DECK = (
    "WARSAW HOLDS ITS FIRE AS THE DRONE TURNS BACK EAST OVERNIGHT, "
    "DAYS AFTER THREE RUSSIAN MISSILES LANDED IN POLAND. "
    "NATO JETS ARE ON WATCH."
)

# (kicker, headline, deck, accent colour) for the four tiles.
TILES = [
    (
        "SOUTH KOREA",
        "SEOUL SOUNDS THE ALARM",
        "ULLEUNG ISLAND TAKES SHELTER AS RUSSIAN AIRCRAFT NEAR; "
        "JETS SCRAMBLE, ALERT LIFTED IN MINUTES.",
        (192, 57, 43),
    ),
    (
        "CHESS \u2022 GENEVA",
        "CROWN ON THE LINE",
        "GUKESH DEFENDS HIS TITLE AGAINST SINDAROV, BOTH 20, IN THE "
        "YOUNGEST TITLE MATCH EVER. GAME 1 BEGINS TODAY.",
        (20, 143, 119),
    ),
    (
        "THE SKY TONIGHT",
        "BEAVER SUPERMOON PEAKS",
        "NOVEMBER'S FULL MOON, AT ITS CLOSEST TO EARTH, SHINES BESIDE "
        "THE PLEIADES STAR CLUSTER.",
        (125, 60, 152),
    ),
    (
        "UNITED STATES",
        "AMERICA HITS THE ROAD",
        "THE THANKSGIVING RUSH BEGINS: 81.5 MILLION TRAVEL THIS WEEK, "
        "5.96 MILLION BY AIR.",
        (202, 111, 30),
    ),
]

FOOTER_LINE_1 = (
    "EVERY STORY ABOVE HAPPENED, OR WAS FIRST REPORTED, "
    "ON TUESDAY 24 NOVEMBER 2026."
)
FOOTER_LINE_2 = "SOURCES: REUTERS \u2022 CHESS.COM \u2022 EARTHSKY \u2022 AAA"


def draw_poster(buf):
    # Backdrop.
    fill_rect(buf, 0, 0, WIDTH, HEIGHT, CREAM)

    # --- Masthead band (0..104) + gold rule (104..108). ---
    fill_rect(buf, 0, 0, WIDTH, 104, NAVY)
    draw_text(buf, 28, 34, MASTHEAD_TITLE, 5, CREAM)
    date_w = text_width(DATE_LINE, 2)
    draw_text(buf, WIDTH - 28 - date_w, 44, DATE_LINE, 2, GOLD)
    fill_rect(buf, 0, 104, WIDTH, 4, GOLD)

    # --- Hero panel (108..428). ---
    fill_rect(buf, 0, 108, WIDTH, 320, HERO_NAVY)
    draw_text(buf, 28, 132, HERO_KICKER, 2, GOLD)
    draw_text(buf, 28, 168, HERO_HEADLINE[0], 7, CREAM)
    draw_text(buf, 28, 224, HERO_HEADLINE[1], 7, CREAM)
    draw_wrapped(buf, 28, 300, HERO_DECK, 2, WHITE, WIDTH - 56, 6)

    # --- Red divider (428..434). ---
    fill_rect(buf, 0, 428, WIDTH, 6, RED)

    # --- 2x2 grid of tiles (434..928). ---
    margin = 24
    gap = 16
    tile_w = (WIDTH - 2 * margin - gap) // 2
    tile_h = 239
    top = 434
    for idx, (kicker, headline, deck, accent) in enumerate(TILES):
        tx = margin + (idx % 2) * (tile_w + gap)
        ty = top + (idx // 2) * (tile_h + gap)
        fill_rect(buf, tx, ty, tile_w, tile_h, CREAM)
        fill_rect(buf, tx, ty, tile_w, 6, accent)
        draw_text(buf, tx + 16, ty + 20, kicker, 2, accent)
        draw_wrapped(buf, tx + 16, ty + 50, headline, 4, DARK,
                     tile_w - 32, 4)
        draw_wrapped(buf, tx + 16, ty + 122, deck, 2, GREY,
                     tile_w - 32, 6)

    # --- Footer band (928..1024). ---
    fill_rect(buf, 0, 928, WIDTH, 96, NAVY)
    draw_text(buf, 28, 948, FOOTER_LINE_1, 2, WHITE)
    draw_text(buf, 28, 978, FOOTER_LINE_2, 2, GOLD)


def main():
    buf = bytearray(WIDTH * HEIGHT * 3)
    draw_poster(buf)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(encode_png(buf))
    return 0


if __name__ == "__main__":
    sys.exit(main())
