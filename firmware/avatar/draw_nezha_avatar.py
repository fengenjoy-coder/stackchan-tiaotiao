#!/usr/bin/env python3
"""Draw a chibi Nezha avatar set (6 faces + eye/mouth variants) for StackChan.

Outputs 320x240 RGB PNGs to ~/.stackchan/avatar/ for convert_avatars.py:
  idle / happy / thinking / sad / surprised / embarrassed   (full faces)
  eyes_open / eyes_half / eyes_closed                       (full-frame, mouth = closed smile)
  mouth_closed / mouth_half / mouth_open / mouth_e / mouth_u (full-frame, eyes = open)
"""
from PIL import Image, ImageDraw
import os

S = 3                      # supersample factor
W, H = 320 * S, 240 * S
OUT = os.path.expanduser("~/.stackchan/avatar")
os.makedirs(OUT, exist_ok=True)

# palette
CREAM  = (255, 246, 232)
SKIN   = (255, 224, 196)
HAIR   = (43, 43, 51)
RED    = (229, 57, 53)
DARK   = (45, 35, 40)
BLUSH  = (255, 158, 166)
TEAR   = (140, 200, 255)
WHITE  = (255, 255, 255)

CX, CY = 160, 132          # face center (in 320x240 space)
def sc(v): return v * S

def base_canvas():
    im = Image.new("RGB", (W, H), CREAM)
    return im, ImageDraw.Draw(im)

def draw_head(d):
    """hair buns + face + forehead ribbon, shared by every frame"""
    # hair buns
    for bx in (96, 224):
        d.ellipse([sc(bx-30), sc(28), sc(bx+30), sc(88)], fill=HAIR)
    # ribbon tails (two little red triangles on outer side of each bun)
    for bx, flip in ((96, -1), (224, 1)):
        d.polygon([(sc(bx+flip*24), sc(44)), (sc(bx+flip*46), sc(30)),
                   (sc(bx+flip*40), sc(58))], fill=RED)
    # face
    d.ellipse([sc(CX-80), sc(CY-74), sc(CX+80), sc(CY+86)], fill=SKIN)
    # forehead ribbon band (red band across the top of the face)
    d.chord([sc(CX-80), sc(CY-100), sc(CX+80), sc(CY+40)],
            start=195, end=345, fill=RED)
    # knot dot at center of band
    d.ellipse([sc(CX-8), sc(CY-84), sc(CX+8), sc(CY-68)], fill=RED)

def blush(d, strong=False):
    rx = 20 if strong else 14
    ry = 12 if strong else 9
    for bx in (106, 214):
        d.ellipse([sc(bx-rx), sc(156-ry), sc(bx+rx), sc(156+ry)], fill=BLUSH)

def eyes_open(d, look=0, scale=1.0):
    """round eyes; look: -1 left, 0 center, 1 right"""
    r = int(16 * scale)
    for ex in (126, 194):
        cx = ex + look * 6
        d.ellipse([sc(cx-r), sc(124-r), sc(cx+r), sc(124+r)], fill=DARK)
        d.ellipse([sc(cx-r+5), sc(124-r+4), sc(cx-r+13), sc(124-r+12)], fill=WHITE)

def eyes_half(d):
    for ex in (126, 194):
        d.pieslice([sc(ex-16), sc(108), sc(ex+16), sc(140)], start=0, end=180, fill=DARK)
        d.line([sc(ex-16), sc(124), sc(ex+16), sc(124)], fill=DARK, width=sc(3))

def eyes_closed(d):  # happy ^^ arcs
    for ex in (126, 194):
        d.arc([sc(ex-15), sc(112), sc(ex+15), sc(136)], start=200, end=340,
              fill=DARK, width=sc(4))

def eyes_sad(d):
    for ex in (126, 194):
        r = 14
        d.ellipse([sc(ex-r), sc(126-r), sc(ex+r), sc(126+r)], fill=DARK)
        d.ellipse([sc(ex-r+4), sc(126-r+3), sc(ex-r+11), sc(126-r+10)], fill=WHITE)
        # droopy inner brow
        side = -1 if ex < 160 else 1
        d.arc([sc(ex-14+side*2), sc(102), sc(ex+14+side*2), sc(120)],
              start=200 if side < 0 else 250, end=300 if side < 0 else 340,
              fill=DARK, width=sc(3))

def mouth(d, shape):
    if shape == "smile":
        d.arc([sc(146), sc(158), sc(174), sc(178)], start=20, end=160, fill=DARK, width=sc(4))
    elif shape == "big":   # happy open smile
        d.pieslice([sc(140), sc(156), sc(180), sc(186)], start=20, end=160, fill=DARK)
        d.pieslice([sc(148), sc(164), sc(172), sc(182)], start=20, end=160, fill=(240, 120, 120))
    elif shape == "frown":
        d.arc([sc(146), sc(168), sc(174), sc(188)], start=200, end=340, fill=DARK, width=sc(4))
    elif shape == "o":     # surprised / u
        d.ellipse([sc(152), sc(160), sc(168), sc(180)], fill=DARK)
    elif shape == "half":  # small open
        d.ellipse([sc(148), sc(160), sc(172), sc(176)], fill=DARK)
    elif shape == "open":  # wide open
        d.ellipse([sc(142), sc(156), sc(178), sc(188)], fill=DARK)
        d.ellipse([sc(150), sc(172), sc(170), sc(186)], fill=(240, 120, 120))
    elif shape == "e":     # wide thin "e"
        d.ellipse([sc(138), sc(162), sc(182), sc(176)], fill=DARK)
    elif shape == "wavy":  # embarrassed ~~~
        pts = []
        import math
        for i in range(41):
            x = 144 + i
            y = 170 + math.sin(i / 40 * math.pi * 2) * 3
            pts.append((sc(x), sc(y)))
        d.line(pts, fill=DARK, width=sc(3))

def save(im, name):
    im = im.resize((320, 240), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".png"))
    print("saved", name)

def face(name, eyes, mouth_shape, brows="none", blush_strong=False, extras=None):
    im, d = base_canvas()
    draw_head(d)
    if brows == "raised":
        for ex in (126, 194):
            d.arc([sc(ex-14), sc(96), sc(ex+14), sc(112)], start=200, end=340,
                  fill=DARK, width=sc(3))
    eyes(d)
    blush(d, blush_strong)
    mouth(d, mouth_shape)
    if extras:
        extras(d)
    save(im, name)

def finger_on_cheek(d):
    d.ellipse([sc(88), sc(146), sc(120), sc(178)], fill=SKIN, outline=DARK, width=sc(3))
    d.ellipse([sc(96), sc(152), sc(104), sc(160)], fill=(255, 214, 190))

def sweat_drop(d):
    d.polygon([(sc(120), sc(146)), (sc(130), sc(146)), (sc(125), sc(162))], fill=TEAR)

# ---- the six faces ----
face("idle",       lambda d: eyes_open(d), "smile")
face("happy",      eyes_closed, "big", blush_strong=True)
face("thinking",   lambda d: eyes_open(d, look=1), "o", extras=finger_on_cheek)
face("sad",        eyes_sad, "frown", extras=sweat_drop)
face("surprised",  lambda d: eyes_open(d, scale=1.15), "o", brows="raised")
face("embarrassed", lambda d: eyes_open(d, look=-1), "wavy", blush_strong=True)

# ---- eye variants (mouth = smile) ----
face("eyes_open",  lambda d: eyes_open(d), "smile")
face("eyes_half",  eyes_half, "smile")
face("eyes_closed", eyes_closed, "smile")

# ---- mouth variants for lip-sync (eyes = open) ----
face("mouth_closed", lambda d: eyes_open(d), "smile")
face("mouth_half",   lambda d: eyes_open(d), "half")
face("mouth_open",   lambda d: eyes_open(d), "open")
face("mouth_e",      lambda d: eyes_open(d), "e")
face("mouth_u",      lambda d: eyes_open(d), "o")

print("all frames ->", OUT)
