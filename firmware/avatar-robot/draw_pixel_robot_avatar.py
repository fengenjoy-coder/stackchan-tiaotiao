#!/usr/bin/env python3
"""Draw the pixel-robot-head avatar set (320x240 RGB) for StackChan firmware.

Replaces the Nezha avatar set. The robot head is designed on a 40x30 pixel
grid and upscaled x8 nearest-neighbour -> crisp 320x240 RGB PNGs with an
opaque light background (the converter drops alpha, transparent = black).

Outputs to ~/.stackchan/avatar/ the exact 14 files convert_avatars.py expects:
  Faces  : idle / happy / thinking / sad / surprised / embarrassed
  Eyes   : eyes_open / eyes_half / eyes_closed
  Mouths : mouth_closed / mouth_half / mouth_open / mouth_e / mouth_u

Run convert_avatars.py afterwards to regenerate avatar_images.local.{h,cc}.
"""
from PIL import Image
import os

W, H = 40, 30          # pixel grid
SCALE = 8              # 40*8=320, 30*8=240
OUT = os.path.expanduser("~/.stackchan/avatar")
os.makedirs(OUT, exist_ok=True)

BG = (10, 12, 16)    # near-black (converter drops alpha; black looks best on LCD)

# palette
PAL = {
    ".": BG,
    "G": (228, 231, 238),    # head light gray
    "g": (148, 154, 166),    # outline / shadow
    "N": (25, 28, 38),       # screen navy
    "L": (60, 66, 84),       # mouth fill (dark-lighter)
    "C": (86, 222, 255),     # cyan glow
    "W": (255, 255, 255),    # highlight
    "Y": (255, 199, 64),     # antenna ball
    "O": (235, 140, 40),     # ball shadow
    "P": (255, 140, 170),    # blush
    "T": (140, 200, 255),    # tear
}

def blank():
    return [["."] * W for _ in range(H)]

def px(g, x, y, ch):
    if 0 <= x < W and 0 <= y < H:
        g[y][x] = ch

def disc(g, cx, cy, rx, ry, ch):
    for y in range(H):
        for x in range(W):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                px(g, x, y, ch)

def rrect(g, x0, y0, x1, y1, r, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = max(x0 + r - x, 0, x - (x1 - r))
            dy = max(y0 + r - y, 0, y - (y1 - r))
            if dx * dx + dy * dy <= r * r:
                px(g, x, y, ch)

def outlined_rrect(g, x0, y0, x1, y1, r, edge, fillch):
    rrect(g, x0, y0, x1, y1, r, edge)
    rrect(g, x0 + 1, y0 + 1, x1 - 1, y1 - 1, max(r - 1, 1), fillch)

def base():
    """antenna + ears + head + screen, shared by every frame"""
    g = blank()
    # ears (behind head)
    for ex in (4, 35):
        disc(g, ex, 17, 3.5, 3.5, "g")
        disc(g, ex, 17, 2.5, 2.5, "G")
        px(g, ex, 16, "g")
    # head
    outlined_rrect(g, 6, 6, 33, 29, 6, "g", "G")
    # face screen
    rrect(g, 9, 10, 30, 24, 4, "N")
    # antenna (stem + ball)
    px(g, 20, 4, "g"); px(g, 20, 5, "g"); px(g, 20, 6, "g")
    disc(g, 20, 2, 2.2, 2.2, "O")
    px(g, 20, 2, "Y"); px(g, 19, 2, "Y"); px(g, 21, 2, "Y")
    px(g, 20, 1, "Y"); px(g, 20, 3, "Y")
    px(g, 19, 1, "W")
    return g

EYE_Y = 13
MOUTH_Y = 19

# ---- eyes ----
def eyes_open(g, dx=0):
    for ex in (15, 25):
        for yy in range(EYE_Y, EYE_Y + 3):
            for xx in (ex + dx, ex + dx + 1):
                px(g, xx, yy, "C")
        px(g, ex + dx, EYE_Y, "W")

def eyes_half(g):
    for ex in (15, 25):
        px(g, ex, EYE_Y + 1, "C"); px(g, ex + 1, EYE_Y + 1, "C")

def eyes_closed(g):  # ^^ arcs (happy)
    px(g, 14, EYE_Y + 2, "C"); px(g, 15, EYE_Y + 1, "C"); px(g, 16, EYE_Y, "C")
    px(g, 26, EYE_Y + 2, "C"); px(g, 25, EYE_Y + 1, "C"); px(g, 24, EYE_Y, "C")

# ---- mouths ----
def mouth_closed(g):
    px(g, 18, MOUTH_Y, "C"); px(g, 22, MOUTH_Y, "C")
    px(g, 19, MOUTH_Y + 1, "C"); px(g, 20, MOUTH_Y + 1, "C"); px(g, 21, MOUTH_Y + 1, "C")

def mouth_half(g):
    for xx in range(19, 22):
        px(g, xx, MOUTH_Y + 1, "L")

def mouth_open(g):
    for yy in range(MOUTH_Y - 1, MOUTH_Y + 2):
        for xx in range(19, 22):
            px(g, xx, yy, "L")
    px(g, 20, MOUTH_Y + 1, "P")

def mouth_e(g):
    for xx in range(18, 23):
        px(g, xx, MOUTH_Y + 1, "L")

def mouth_u(g):  # o ring
    px(g, 20, MOUTH_Y - 1, "C")
    px(g, 19, MOUTH_Y, "C"); px(g, 21, MOUTH_Y, "C")
    px(g, 19, MOUTH_Y + 1, "C"); px(g, 21, MOUTH_Y + 1, "C")
    px(g, 20, MOUTH_Y + 2, "C")

def mouth_frown(g):
    px(g, 18, MOUTH_Y + 1, "C"); px(g, 22, MOUTH_Y + 1, "C")
    px(g, 19, MOUTH_Y, "C"); px(g, 20, MOUTH_Y, "C"); px(g, 21, MOUTH_Y, "C")

def mouth_wavy(g):
    px(g, 18, MOUTH_Y + 1, "C"); px(g, 19, MOUTH_Y, "C")
    px(g, 20, MOUTH_Y + 1, "C"); px(g, 21, MOUTH_Y, "C"); px(g, 22, MOUTH_Y + 1, "C")

def blush(g):
    for bx in (12, 26):
        px(g, bx, MOUTH_Y - 2, "P"); px(g, bx + 1, MOUTH_Y - 2, "P")

def save(g, name):
    im = Image.new("RGB", (W, H), BG)
    im.putdata([PAL[ch] for row in g for ch in row])
    im = im.resize((320, 240), Image.NEAREST)
    im.save(os.path.join(OUT, name + ".png"))
    print("saved", name)

def face(name, eyes, mouth_fn, brows=None, tear=False):
    g = base()
    eyes(g)
    mouth_fn(g)
    if brows == "raised":
        px(g, 14, EYE_Y - 1, "C"); px(g, 15, EYE_Y - 1, "C")
        px(g, 25, EYE_Y - 1, "C"); px(g, 26, EYE_Y - 1, "C")
    elif brows == "sad":
        px(g, 15, EYE_Y - 1, "C"); px(g, 16, EYE_Y, "C")
        px(g, 25, EYE_Y - 1, "C"); px(g, 24, EYE_Y, "C")
    if tear:
        px(g, 26, EYE_Y + 3, "T"); px(g, 26, EYE_Y + 4, "T")
    save(g, name)

# ---- the six faces ----
face("idle", eyes_open, mouth_closed)

# happy: ^^ eyes + open mouth + blush
g = base(); eyes_closed(g); mouth_open(g); blush(g); save(g, "happy")
g = base(); eyes_open(g, dx=1); mouth_u(g); save(g, "thinking")   # looking aside, small o
g = base(); eyes_open(g); mouth_frown(g); px(g, 15, EYE_Y - 1, "C"); px(g, 16, EYE_Y, "C")
px(g, 25, EYE_Y - 1, "C"); px(g, 24, EYE_Y, "C"); px(g, 26, EYE_Y + 3, "T"); px(g, 26, EYE_Y + 4, "T")
save(g, "sad")
g = base()
for ex in (15, 25):  # big square eyes
    for yy in range(EYE_Y, EYE_Y + 3):
        for xx in (ex - 1, ex, ex + 1):
            px(g, xx, yy, "C")
    px(g, ex - 1, EYE_Y, "W")
px(g, 14, EYE_Y - 1, "C"); px(g, 15, EYE_Y - 1, "C")
px(g, 25, EYE_Y - 1, "C"); px(g, 26, EYE_Y - 1, "C")
mouth_u(g); save(g, "surprised")
g = base(); eyes_open(g, dx=-1); mouth_wavy(g); blush(g); save(g, "embarrassed")

# ---- eye variants (mouth = smile) ----
face("eyes_open",  eyes_open,  mouth_closed)
face("eyes_half",  eyes_half,  mouth_closed)
face("eyes_closed", eyes_closed, mouth_closed)

# ---- mouth variants for lip-sync (eyes = open) ----
face("mouth_closed", eyes_open, mouth_closed)
face("mouth_half",   eyes_open, mouth_half)
face("mouth_open",   eyes_open, mouth_open)
face("mouth_e",      eyes_open, mouth_e)
face("mouth_u",      eyes_open, mouth_u)

print("all frames ->", OUT)
