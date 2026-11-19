#!/usr/bin/env python3
"""THE WORLD IN A DAY - Wednesday 18 November 2026.

A newspaper front page drawn entirely from code. A small rasterizer
paints into a framebuffer, an embedded 5 by 7 bitmap font supplies the
type, and a PNG encoder built on zlib writes the finished page.
Python standard library only. No network, no image assets.
The output is deterministic: the same bytes on every run.
"""

import hashlib
import os
import struct
import zlib

W = 1024
H = 1024
PAPER = (250, 244, 228)
INK = (26, 26, 26)
RED = (198, 32, 32)
WHITE = (255, 255, 255)
BLACK = (12, 12, 12)

FB = bytearray(W * H * 3)


def put_pixel(x, y, color):
    if x < 0:
        return
    if x >= W:
        return
    if y < 0:
        return
    if y >= H:
        return
    i = (y * W + x) * 3
    FB[i] = color[0]
    FB[i + 1] = color[1]
    FB[i + 2] = color[2]


def fill_rect(x, y, w, h, color):
    x0 = x
    if x0 < 0:
        x0 = 0
    y0 = y
    if y0 < 0:
        y0 = 0
    x1 = x + w
    if x1 > W:
        x1 = W
    y1 = y + h
    if y1 > H:
        y1 = H
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            FB[i] = color[0]
            FB[i + 1] = color[1]
            FB[i + 2] = color[2]


def draw_hline(x, y, length, color):
    fill_rect(x, y, length, 1, color)


def draw_vline(x, y, length, color):
    fill_rect(x, y, 1, length, color)


def draw_line(x0, y0, x1, y1, color):
    dx = x1 - x0
    if dx < 0:
        dx = -dx
    dy = y1 - y0
    if dy < 0:
        dy = -dy
    sx = 1
    if x1 < x0:
        sx = -1
    sy = 1
    if y1 < y0:
        sy = -1
    err = dx - dy
    x = x0
    y = y0
    while True:
        put_pixel(x, y, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err = err - dy
            x = x + sx
        if e2 < dx:
            err = err + dx
            y = y + sy


def draw_disc(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            ddx = xx - cx
            ddy = yy - cy
            if ddx * ddx + ddy * ddy <= r * r:
                put_pixel(xx, yy, color)


def draw_burst(cx, cy, r, color):
    draw_line(cx - r, cy, cx + r, cy, color)
    draw_line(cx, cy - r, cx, cy + r, color)
    diag = (r * 7) // 10
    draw_line(cx - diag, cy - diag, cx + diag, cy + diag, color)
    draw_line(cx - diag, cy + diag, cx + diag, cy - diag, color)
    draw_disc(cx, cy, r // 4, color)


def draw_box(x, y, w, h, color, thick):
    fill_rect(x, y, w, thick, color)
    fill_rect(x, y + h - thick, w, thick, color)
    fill_rect(x, y, thick, h, color)
    fill_rect(x + w - thick, y, thick, h, color)


def _chunk(kind, data):
    out = struct.pack(">I", len(data))
    out = out + kind
    out = out + data
    out = out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        start = y * W * 3
        raw = raw + FB[start:start + W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png = png + _chunk(b"IHDR", ihdr)
    png = png + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png = png + _chunk(b"IEND", b"")
    return png


# Embedded 5 by 7 bitmap font. Each glyph is seven rows; each row is
# a five-bit number, bit 4 the leftmost column, bit 0 the rightmost.
FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000),
    ".": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100),
    ",": (0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b00100, 0b01000),
    ";": (0b00000, 0b01100, 0b00000, 0b00000, 0b01100, 0b00100, 0b01000),
    ":": (0b00000, 0b01100, 0b00000, 0b00000, 0b01100, 0b00000, 0b00000),
    "'": (0b00100, 0b00100, 0b01000, 0b00000, 0b00000, 0b00000, 0b00000),
    "-": (0b00000, 0b00000, 0b00000, 0b01110, 0b00000, 0b00000, 0b00000),
    "$": (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100),
    "•": (0b00000, 0b00000, 0b00000, 0b01100, 0b01100, 0b00000, 0b00000),
}


def text_width(text, scale):
    total = 0
    for ch in text:
        if ch not in FONT:
            raise ValueError("no glyph for character: " + repr(ch))
        total = total + 6 * scale
    if total > 0:
        total = total - scale
    return total


def draw_glyph(ch, x, y, scale, color):
    rows = FONT[ch]
    for r in range(7):
        bits = rows[r]
        for c in range(5):
            if bits & (1 << (4 - c)):
                fill_rect(x + c * scale, y + r * scale, scale, scale, color)


def draw_text(text, x, y, scale, color):
    cx = x
    for ch in text:
        draw_glyph(ch, cx, y, scale, color)
        cx = cx + 6 * scale


def draw_text_centered(text, cx, y, scale, color):
    w = text_width(text, scale)
    draw_text(text, cx - w // 2, y, scale, color)


def wrap_text(text, scale, max_width):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        if text_width(word, scale) > max_width:
            raise ValueError("word too wide for box: " + word)
        if cur == "":
            trial = word
        else:
            trial = cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur != "":
        lines.append(cur)
    return lines


def draw_block(text, x, y, scale, max_width, color, leading):
    lines = wrap_text(text, scale, max_width)
    for i in range(len(lines)):
        draw_text(lines[i], x, y + i * leading, scale, color)
    return y + len(lines) * leading


MASTHEAD = "THE WORLD IN A DAY"
DATE_LINE = "WEDNESDAY 18 NOVEMBER 2026"

LEAD_HEAD = "GULF STRIKES"
LEAD_DECK = "U.S. JETS HIT IRAN MISSILE SITE ON QESHM ISLAND; IRAN FIRES AT KUWAIT AND BAHRAIN"
LEAD_BODY = "U.S. FIGHTER JETS STRUCK A REVOLUTIONARY GUARD MISSILE LAUNCH SITE ON QESHM ISLAND ON TUESDAY, AN AMERICAN OFFICIAL SAID, AFTER IRAN ATTACKED U.S. PERSONNEL AND ASSETS. IRAN SAID IT TARGETED U.S. DRONE AND MISSILE SITES IN KUWAIT AND FIRED AT BAHRAIN, ITS THIRD ATTACK THERE IN UNDER A WEEK. (REUTERS, AFP, BBC)"

PANELS = [
    (
        "SHENZHEN SUMMIT",
        "XI AND PUTIN MEET AHEAD OF FIRST THREE-WAY TALKS WITH TRUMP",
        "CHINA'S XI JINPING AND RUSSIA'S VLADIMIR PUTIN BEGAN TALKS IN SHENZHEN ON WEDNESDAY, A DAY BEFORE A FIRST-EVER TRILATERAL SUMMIT WITH PRESIDENT DONALD TRUMP AT APEC. (THE HINDU, BBC)",
    ),
    (
        "KERCH BRIDGE HIT AGAIN",
        "UKRAINE STRIKES FOR SECOND DAY; PART OF ROAD SPAN COLLAPSES",
        "UKRAINE HIT THE KERCH BRIDGE TO CRIMEA FOR A SECOND DAY, AND PART OF ITS ROAD SPAN FELL INTO THE STRAIT. (DAILY NEWS ROUNDUP)",
    ),
    (
        "ALASKA FLIPS THE SENATE",
        "PELTOLA WINS; DEMOCRATS TAKE 56-44 MAJORITY",
        "DEMOCRAT MARY PELTOLA DEFEATED REPUBLICAN SEN. DAN SULLIVAN IN ALASKA, THE LAST SENATE RACE OF THE MIDTERMS TO BE RESOLVED, GIVING DEMOCRATS THEIR NINTH FLIP AND A 56-44 MAJORITY. (AP)",
    ),
    (
        "MEASLES STATUS LOST",
        "U.S. LOSES ELIMINATION STATUS AFTER 26 YEARS",
        "THE PAN AMERICAN HEALTH ORGANIZATION SAID THE VIRUS HAS SPREAD CONTINUOUSLY FOR MORE THAN A YEAR. THE U.S. HAS RECORDED 5,412 CASES IN 2026, THE MOST SINCE 1991. (PAHO, CDC)",
    ),
]

STRIP_HEAD = "VOYAGER 1, ONE LIGHT-DAY OUT"
STRIP_BODY = "NASA SAYS VOYAGER 1 REACHED ONE LIGHT-DAY FROM EARTH ON WEDNESDAY, ABOUT 16 BILLION MILES, A DISTANCE NO HUMAN-MADE OBJECT HAS CROSSED BEFORE. (NASA JPL)"

TICKER = "ALSO WEDNESDAY: CYCLONE AKVAN STRENGTHENS IN BAY OF BENGAL, LANDFALL DUE FRIDAY ON INDIA'S ANDHRA COAST - EBOLA OUTBREAK IN DR CONGO PASSES 11,000 CASES - TRUMP ANNOUNCES PHILIPPINES TRADE DEAL IN MANILA - CYCLONE XAVIER, CATEGORY 5, HITS NORTHERN COOK ISLANDS - RUSSIAN MILITARY PLANE CRASHES IN SIBERIA, 19 KILLED - WORLD COURT TO RULE ON MYANMAR GENOCIDE CASE"


def draw_masthead():
    fill_rect(0, 0, W, 96, BLACK)
    draw_text_centered(MASTHEAD, W // 2, 19, 8, WHITE)
    fill_rect(0, 96, W, 4, RED)
    dw = text_width(DATE_LINE, 4)
    dx = (W - dw) // 2
    draw_text(DATE_LINE, dx, 106, 4, INK)
    fill_rect(dx - 40, 112, 16, 16, RED)
    fill_rect(dx + dw + 24, 112, 16, 16, RED)
    draw_hline(16, 142, W - 32, INK)


def draw_lead():
    x = 16
    y = 154
    w = 992
    h = 226
    draw_box(x, y, w, h, INK, 3)
    ix = x + 18
    iw = w - 36
    draw_text(LEAD_HEAD, ix, y + 14, 6, INK)
    draw_burst(ix + iw - 30, y + 36, 26, RED)
    fill_rect(ix, y + 64, iw, 3, RED)
    end = draw_block(LEAD_DECK, ix, y + 76, 2, iw, RED, 17)
    end = draw_block(LEAD_BODY, ix, end + 10, 2, iw, INK, 17)
    if end > y + h - 12:
        raise ValueError("lead body overflows its box")


def draw_panel(px, py, head, deck, body):
    w = 488
    h = 192
    draw_box(px, py, w, h, INK, 2)
    ix = px + 14
    iw = w - 28
    draw_text(head, ix, py + 12, 3, INK)
    fill_rect(ix, py + 40, iw, 2, INK)
    end = draw_block(deck, ix, py + 48, 2, iw, RED, 16)
    end = draw_block(body, ix, end + 6, 2, iw, INK, 15)
    if end > py + h - 12:
        raise ValueError("panel body overflows its box: " + head)


def draw_strip():
    x = 16
    y = 794
    w = 992
    h = 84
    fill_rect(x, y, w, 36, RED)
    draw_text_centered(STRIP_HEAD, W // 2, y + 7, 3, WHITE)
    end = draw_block(STRIP_BODY, x + 18, y + 44, 2, w - 36, INK, 17)
    if end > y + h - 6:
        raise ValueError("strip body overflows its box")


def draw_ticker():
    fill_rect(16, 888, W - 32, 3, RED)
    x = 16
    y = 900
    fill_rect(x, y + 2, 12, 12, RED)
    end = draw_block(TICKER, x + 24, y, 2, W - 32 - 24, INK, 17)
    if end > H - 6:
        raise ValueError("ticker overflows the page")


def compose():
    fill_rect(0, 0, W, H, PAPER)
    draw_masthead()
    draw_lead()
    draw_panel(16, 390, PANELS[0][0], PANELS[0][1], PANELS[0][2])
    draw_panel(520, 390, PANELS[1][0], PANELS[1][1], PANELS[1][2])
    draw_panel(16, 592, PANELS[2][0], PANELS[2][1], PANELS[2][2])
    draw_panel(520, 592, PANELS[3][0], PANELS[3][1], PANELS[3][2])
    draw_strip()
    draw_ticker()


def all_texts():
    texts = []
    texts.append(MASTHEAD)
    texts.append(DATE_LINE)
    texts.append(LEAD_HEAD)
    texts.append(LEAD_DECK)
    texts.append(LEAD_BODY)
    for head, deck, body in PANELS:
        texts.append(head)
        texts.append(deck)
        texts.append(body)
    texts.append(STRIP_HEAD)
    texts.append(STRIP_BODY)
    texts.append(TICKER)
    return texts


def check_glyphs():
    for text in all_texts():
        for ch in text:
            if ch not in FONT:
                raise ValueError("missing glyph for character: " + repr(ch))


def main():
    check_glyphs()
    compose()
    png = encode_png()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    digest = hashlib.sha256(png).hexdigest()
    print("wrote " + path)
    print("size " + str(len(png)) + " bytes")
    print("sha256 " + digest)


if __name__ == "__main__":
    main()
