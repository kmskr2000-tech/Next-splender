"""object archetype: folk-tale props. draw(p, stage, spec) -> Sprite. spec={"archetype":"object","shape":...}"""
import math
from core import Sprite, hx, tone, ramp
from person import poly, blend

INK = (34, 26, 36)
WHITE = (255, 255, 255)
GOLD = (255, 226, 120)
WOOD = (150, 98, 58)
WATER = (122, 190, 222)
GREEN = (96, 170, 96)


def G_(s, x, y):
    return s.get(int(round(x)), int(round(y)))


def sparkle(s, x, y, r=2, col=WHITE):
    x, y = int(x), int(y)
    s.set(x, y, col)
    for i in range(1, r + 1):
        for dx, dy in ((i, 0), (-i, 0), (0, i), (0, -i)):
            s.set(x + dx, y + dy, col if i < r else tone(col, .9))


def dots_ring(s, cx, cy, r, n, col, col2=None):
    for i in range(n):
        a = i / n * math.tau
        s.set(cx + math.cos(a) * r, cy + math.sin(a) * r, col if (i % 3 or not col2) else col2)


def merge(s, t):
    for y in range(96):
        for x in range(96):
            if t.px[y][x]:
                s.px[y][x] = t.px[y][x]


def mound(s, cx, gy, w, col=(140, 190, 110)):
    s.ell(cx, gy + 1, w, 3.2, col)
    for dx in (-w * .6, w * .5):
        s.line(cx + dx, gy - 1, cx + dx - 1, gy - 3, tone(col, 1.2))
        s.line(cx + dx + 1, gy - 1, cx + dx + 2, gy - 3, tone(col, .8))


def blob(s, cx, cy, rx, ry, col, skew=.14, gloss=True):
    """egg: wider at the bottom."""
    r = ramp(col)
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        t = (y + .5 - cy) / ry
        if abs(t) >= 1:
            continue
        w = rx * math.sqrt(1 - t * t) * (1 + skew * t)
        for x in range(int(cx - w) - 1, int(cx + w) + 2):
            u = (x + .5 - cx) / max(w, 1e-6) * math.sqrt(1 - t * t)
            d = u * u + t * t
            if d > 1:
                continue
            nz = math.sqrt(1 - d)
            i = u * -.55 / .98 * .98 + t * -.65 + nz * .52
            k = 0 if i < .12 else 1 if i < .5 else 2 if i < .8 or not gloss else 3
            s.set(x, y, r[k])


# --------------------------------------------------------------------- egg
def egg(s, m, a, dt, st):
    cx = 48
    ry = [20, 24, 28][st]
    rx = [15, 18, 21][st]
    cy = 80 - ry - 1
    # glow rays behind
    nr = [8, 12, 16][st]
    for i in range(nr):
        ang = -math.pi / 2 + (i - (nr - 1) / 2) * (math.pi * 1.7 / nr) * 1.0
        L0, L1 = ry + 3, ry + (8 if i % 2 else 13) + st * 2
        for q in range(int(L0), int(L1)):
            if (q + i) % 2 == 0 or q > L1 - 4:
                s.set(cx + math.cos(ang) * q * (rx / ry * .6 + .4), cy + math.sin(ang) * q, tone(a, 1.25) if i % 2 else GOLD)
    mound(s, cx, 80, rx + 4)
    blob(s, cx, cy, rx, ry, m)
    # speckles / bands in accent
    spots = [(-.35, .25, 2), (.3, .5, 2), (.1, -.2, 1), (-.1, .65, 1), (.45, .05, 1), (-.45, .6, 1)]
    for sx, sy, r_ in spots[:2 + st * 2]:
        s.ell(cx + sx * rx, cy + sy * ry, r_ + .6, r_, a, flat=True)
    if st >= 1:  # accent band
        for x in range(cx - rx, cx + rx + 1):
            for y in (cy + int(ry * .25), cy + int(ry * .25) + 1):
                if G_(s,x, y) and G_(s,x, y - 2):
                    s.set(x, y, a if y == cy + int(ry * .25) else tone(a, .7))
    if st == 2:  # crack glow lines at top
        pts = [(cx - 1, cy - ry + 3), (cx + 1, cy - ry + 6), (cx - 1, cy - ry + 9), (cx + 1, cy - ry + 12)]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            s.line(x0, y0, x1, y1, GOLD)
    # gloss highlight
    s.ell(cx - rx * .45, cy - ry * .45, 2.2, 3.5, WHITE, rot=.5, flat=True)
    s.set(cx - rx * .45 + 3, cy - ry * .45 + 6, WHITE)
    sparkle(s, cx + rx + 5, cy - ry * .6, 2, GOLD)
    sparkle(s, cx - rx - 6, cy - ry * .1, 1, WHITE)
    if st >= 1:
        sparkle(s, cx + rx - 1, cy - ry - 4, 3, GOLD)
    if st == 2:
        sparkle(s, cx - rx - 2, cy - ry - 3, 2, WHITE)


# ------------------------------------------------------------------- lotus
def petal(s, bx, by, ang, ln, wd, col):
    """petal from base (bx,by) towards ang (0=up)."""
    cx = bx + math.sin(ang) * ln / 2
    cy = by - math.cos(ang) * ln / 2
    s.ell(cx, cy, wd, ln / 2, col, rot=-ang, gloss=False)


def lotus(s, m, a, dt, st):
    cx = 48
    k = [.8, .9, 1.0][st]
    # water
    s.ell(cx, 79, 36 * k + 2, 5.5, WATER)
    for dx in (-26, -10, 14, 28):
        s.line(cx + dx * k, 80, cx + dx * k + 5, 80, (214, 238, 248))
    # pad
    s.ell(cx, 74, 27 * k, 5.5, m)
    s.line(cx, 74, cx + 26 * k, 71, tone(m, .6))   # pad slit
    for dx in (-14, -4, 12, 18):
        s.set(cx + dx * k, 75, tone(m, 1.4))
    # petals: back row, mid row, front row
    base = 72
    n_back = [3, 4, 5][st]
    for i in range(n_back):
        ang = (i - (n_back - 1) / 2) * (1.9 / n_back) * 1.0
        petal(s, cx + math.sin(ang) * 3, base - 3, ang * 1.15, 26 * k, 6.2 * k, tone(a, .86))
    for sgn in (-1, 1):
        petal(s, cx + sgn * 5, base, sgn * 1.1, 19 * k, 6.5 * k, a)
    for sgn in (-1, 1):
        petal(s, cx + sgn * 3, base + 1, sgn * .55, 24 * k, 6.5 * k, tone(a, 1.12))
    petal(s, cx, base + 2, 0, 28 * k, 7 * k, tone(a, 1.2))
    # petal tips deeper pink
    for sgn in (-1, 1):
        pass
    # seed pod
    s.ell(cx, 52 - (1 - k) * 8, 4.5, 3, (250, 220, 90))
    for dx in (-2, 0, 2):
        s.set(cx + dx, 52 - (1 - k) * 8, tone((250, 220, 90), .55))
    # bud on side
    if st >= 1:
        bx = cx + 28 * k
        s.line(bx, 74, bx - 1, 60, tone(m, .8), 2)
        petal(s, bx - 1, 61, 0, 9, 3.4, tone(a, 1.0))
        petal(s, bx - 1, 61, .6, 7, 2.8, tone(a, .8))
    if st == 2:
        bx = cx - 29
        s.line(bx, 74, bx + 1, 63, tone(m, .8), 2)
        s.ell(bx + 1, 62, 3, 4, tone(a, 1.1))
    sparkle(s, cx + 22 * k, 40, 2, WHITE)
    sparkle(s, cx - 24 * k, 46, 1, GOLD)
    if st >= 1:
        sparkle(s, cx + 5, 34, 3, GOLD)


# -------------------------------------------------------------------- rope
def rope(s, m, a, dt, st):
    cx = 48
    t = Sprite()
    w = [2.8, 3.4, 4.0][st]
    pts = [(cx + 4 * math.sin(i / 10 * 5 + .5), 18 + i * 5.6) for i in range(11)]
    # coil on ground
    ring = [(cx + math.cos(q / 12 * math.tau + .6) * (20 + st * 3), 77 + math.sin(q / 12 * math.tau + .6) * 4.5) for q in range(13)]
    t.tube(ring, [w] * 13, m)
    ring2 = [(cx + math.cos(q / 12 * math.tau) * (11 + st * 2), 75 + math.sin(q / 12 * math.tau) * 3) for q in range(13)]
    t.tube(ring2, [w] * 13, tone(m, 1.1))
    t.tube(pts, [w] * 11, m)
    # twist pattern
    for y in range(96):
        for x in range(96):
            c = t.px[y][x]
            if c:
                q = (x + y * 2) % 6
                if q == 0:
                    t.px[y][x] = tone(c, .62)
                elif q == 1:
                    t.px[y][x] = tone(c, 1.25)
    merge(s, t)
    # cloud
    for dx, w_, dy in ((-14, 9, 1), (0, 12, -2), (14, 9, 1), (-6, 9, 3), (7, 9, 3)):
        s.ell(cx + dx, 9 + dy, w_, 5 + (dy < 0) * 1, (240, 246, 252))
    # tassel knot bottom of the rope
    s.ell(cx + 3, 33, 4, 3, a)
    s.set(cx + 2, 32, WHITE)
    s.tri([(cx, 35), (cx + 6, 35), (cx + 3, 42)], a)
    if st >= 1:
        s.ell(cx - 2, 55, 4, 3, a)
        s.tri([(cx - 5, 57), (cx + 1, 57), (cx - 2, 63)], a)
    # light sparkles
    for (x, y, r_, c) in ((cx - 16, 28, 2, GOLD), (cx + 17, 46, 2, WHITE), (cx - 14, 62, 1, GOLD)):
        sparkle(s, x, y, r_, c)
    if st == 2:
        sparkle(s, cx + 18, 24, 3, GOLD)
        sparkle(s, cx - 18, 48, 2, WHITE)


# ------------------------------------------------------------------ bridge
def magpie(s, x, y, face=1, k=1.0):
    body = (44, 48, 72)
    s.ell(x - face * 5 * k, y - 1, 5 * k, 1.9 * k, (60, 70, 120), rot=-face * .3, gloss=False)   # tail
    s.ell(x, y - 3 * k, 4.4 * k, 3.6 * k, body)
    s.ell(x + face * .5, y - 1.5 * k, 2.6 * k, 2.2 * k, (250, 250, 255), gloss=False)
    s.ell(x - face * 1.5, y - 3.5 * k, 2.6 * k, 1.7 * k, (70, 110, 170), gloss=False)  # wing blue
    s.ell(x + face * 3.4 * k, y - 6 * k, 2.6 * k, 2.4 * k, body)
    s.set(x + face * (3.4 * k + 2.7 * k), y - 6 * k, (240, 190, 60))
    s.set(x + face * (3.4 * k + 3.6 * k), y - 5.6 * k, (240, 190, 60))
    s.set(x + face * 4.3 * k, y - 6.6 * k, WHITE)
    s.set(x - 1, y + 1, (60, 50, 50)); s.set(x + 1, y + 1, (60, 50, 50))


def bridge(s, m, a, dt, st):
    cx = 48
    W = [32, 36, 41][st]
    H = [22, 27, 31][st]
    base = 80
    pts = [(cx + (i / 12 * 2 - 1) * W, base - H * (1 - ((i / 12 * 2 - 1) ** 2)) - 6) for i in range(13)]
    # underside arch stones + stars in the gap
    s.tube([(pts[0][0] + 2, pts[0][1] + 6), (pts[1][0], pts[1][1] + 5)], [2, 2], m)
    for p0 in range(len(pts) - 1):
        pass
    # deck
    t = Sprite()
    t.tube(pts, [6.0] * 13, m)
    merge(s, t)
    # accent plank lines on deck top (milky way glitter)
    for i, (x, y) in enumerate(pts):
        s.set(x - 1, y - 4, tone(a, 1.1))
        s.set(x + 1, y - 3, a)
        s.set(x, y + 1, tone(m, .6))
    for i in range(0, 12):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        s.line(x0, y0 - 5.5, x1, y1 - 5.5, a)
    # railing posts
    for i in (1, 4, 8, 11):
        x, y = pts[i]
        s.line(x, y - 6, x, y - 10, tone(m, 1.0))
        s.set(x, y - 11, a)
    # end legs
    for sgn in (-1, 1):
        x, y = pts[0 if sgn < 0 else 12]
        s.ell(x - sgn * 1, base - 4, 6, 4, tone(m, 1.1))
        s.ell(x - sgn * 1, base - 1.5, 7, 3, tone(m, .9))
    # birds on the bridge
    magpie(s, pts[2][0], pts[2][1] - 6, 1)
    if st >= 1:
        magpie(s, pts[10][0], pts[10][1] - 6, -1)
    if st == 2:
        magpie(s, pts[6][0], pts[6][1] - 6, 1, 1.15)
    # flying bird in the sky
    if st >= 1:
        fx, fy = cx + 18, 14
        s.line(fx - 4, fy, fx, fy + 2, (44, 48, 72)); s.line(fx, fy + 2, fx + 4, fy - 1, (44, 48, 72))
    # stars under bridge
    for (x, y, r_, c) in ((cx - 8, 62, 1, GOLD), (cx + 9, 68, 2, WHITE), (cx - 18, 20, 2, GOLD), (cx + 24, 36, 1, WHITE)):
        sparkle(s, x, y, r_, c)
    if st == 2:
        sparkle(s, cx - 30, 36, 2, WHITE)
        sparkle(s, cx + 4, 12, 3, GOLD)


# ---------------------------------------------------------------- wingrobe
def wingrobe(s, m, a, dt, st):
    cx = 48
    k = [.82, .92, 1.0][st]
    cy = 44
    t = 0
    # ribbons behind (accent / lighter)
    nrib = 2 + st
    for i in range(nrib):
        side = -1 if i % 2 else 1
        yy = 58 + i * 5
        pts = [(cx + side * (6 + q * 3.4), yy + 16 * math.sin(q / 5 * 3 + i) * (.6 + q / 10) + q * 1.2) for q in range(10)]
        s.tube(pts, [2.4 * k, 2.3, 2.1, 2, 1.9, 1.7, 1.5, 1.3, 1.1, .8], tone(a, 1.15) if i % 2 else tone(m, 1.25))
    # sleeves: long flowing
    for side in (-1, 1):
        pts = [(cx + side * (7 + q * 3.3 * k), cy - 5 + q * 1.3 + 4.6 * math.sin(q / 6 * 3.2 + (0 if side > 0 else 1.6)) - (q * .7)) for q in range(11)]
        rr = [3.2, 3.6, 4, 4.4, 4.7, 4.8, 4.7, 4.4, 3.9, 3.2, 2.6]
        s.tube(pts, [r_ * k for r_ in rr], m)
        ex, ey = pts[-1]
        s.ell(ex, ey, 3.4 * k, 3.0 * k, tone(m, 1.2))
        s.set(ex - 1, ey - 1, WHITE)
        # sleeve cuffs (accent)
        for q in (6, 7):
            x, y = pts[q]
            s.line(x, y - 4 * k, x, y + 4 * k, a)
    # body: flowing skirt-ish robe
    top = cy - 8
    poly(s, [(cx - 8 * k, top), (cx + 8 * k, top), (cx + 15 * k, top + 33 * k), (cx + 9 * k, top + 37 * k), (cx + 3 * k, top + 34 * k + 2),
             (cx - 4 * k, top + 38 * k), (cx - 10 * k, top + 34 * k), (cx - 15 * k, top + 33 * k)], m)
    for fx in (-6, -1, 5):
        s.line(cx + fx * k, top + 14 * k, cx + fx * 1.6 * k, top + 33 * k, tone(m, .75))
    # collar V + sash + ribbon
    for i in range(8):
        s.line(cx - 7 * k + i * .6, top + i, cx + i * .3, top + 9, a) if False else None
    s.line(cx - 7 * k, top, cx, top + 9, a, 2)
    s.line(cx + 7 * k, top, cx, top + 9, tone(a, 1.2), 2)
    s.line(cx - 8 * k, top + 12 * k, cx + 8 * k, top + 12 * k, a, 2)
    s.line(cx - 8 * k, top + 12 * k + 1, cx + 8 * k, top + 12 * k + 1, tone(a, .7))
    s.tri([(cx + 2, top + 13 * k), (cx + 8, top + 22 * k), (cx + 4, top + 22 * k)], tone(a, 1.1))
    s.tri([(cx - 2, top + 13 * k), (cx - 8, top + 21 * k), (cx - 4, top + 21 * k)], a)
    for (x, y, r_, c) in ((cx - 24, 22, 2, GOLD), (cx + 26, 24, 2, WHITE), (cx + 10, 15, 1, GOLD), (cx - 20, 70, 1, WHITE), (cx + 24, 68, 2, GOLD)):
        sparkle(s, x, y, r_, c)
    if st >= 1:
        sparkle(s, cx - 4, 14, 3, GOLD)
    # cloud at the bottom
    for dx, w_ in ((-10, 8), (0, 11), (10, 8)):
        s.ell(cx + dx, 80, w_, 3.5, (236, 244, 252))


# --------------------------------------------------------------------- axe
def axe(s, m, a, dt, st):
    cx = 48
    k = [.9, 1.0, 1.1][st]
    # stump + ripples
    s.ell(cx, 79, 18, 4, WATER) if False else None
    mound_w = 20
    s.ell(cx + 2, 78, mound_w, 5, (122, 190, 222))
    for dx in (-14, 10, 16):
        s.line(cx + dx, 79, cx + dx + 4, 79, (214, 238, 248))
    s.ell(cx, 76, 13, 3.5, (214, 238, 248), flat=True)
    s.ell(cx, 77, 11, 2.5, WATER, flat=True)
    # handle: slight tilt
    x0, y0, x1, y1 = cx - 8, 78, cx + 6, 22
    n = 60
    tt = Sprite()
    for i in range(n + 1):
        u = i / n
        x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        tt.ell(x, y, 2.6, 2.6, WOOD)
    merge(s, tt)
    # grip wraps
    for q in range(5):
        u = .15 + q * .06
        x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        s.line(x - 2, y, x + 2, y - 1, tone(m, 1.3) if False else (214, 190, 140))
    # head
    hx_, hy_ = cx + 6, 28
    steel = tone(m, 1.9)
    if st == 1:
        steel = (214, 220, 232)
    if st == 2:
        steel = (255, 224, 110)
    ps = [(hx_ - 3, hy_ - 8), (hx_ + 4, hy_ - 9), (hx_ + 18 * k, hy_ - 16 * k), (hx_ + 22 * k, hy_ - 2), (hx_ + 18 * k, hy_ + 14 * k), (hx_ + 4, hy_ + 8), (hx_ - 3, hy_ + 7)]
    poly(s, ps, m)
    # edge highlight
    s.line(hx_ + 18 * k, hy_ - 14 * k, hx_ + 22 * k, hy_ - 2, steel, 2)
    s.line(hx_ + 22 * k, hy_ - 2, hx_ + 18 * k, hy_ + 12 * k, steel, 2)
    # bevel
    s.line(hx_ + 2, hy_ - 5, hx_ + 14 * k, hy_ - 11 * k, tone(m, 2.4))
    s.line(hx_ + 2, hy_ + 5, hx_ + 14 * k, hy_ + 9 * k, tone(m, 2.0))
    # collar
    s.ell(hx_ - 1, hy_ - 1, 4, 9, dt)
    s.line(hx_ - 4, hy_ - 4, hx_ + 2, hy_ - 4, a)
    s.line(hx_ - 4, hy_ + 3, hx_ + 2, hy_ + 3, a)
    # chip on old axe
    if st == 0:
        s.set(hx_ + 21, hy_ + 5, None); s.set(hx_ + 20, hy_ + 5, (255, 248, 236))
    # sparkle on edge
    sparkle(s, hx_ + 22 * k, hy_ - 2, 3 if st else 2, WHITE)
    sparkle(s, cx - 20, 44, 1, GOLD)
    sparkle(s, cx - 8, 20, 2, GOLD if st else WHITE)
    # gold glow ring dots
    if st == 2:
        dots_ring(s, hx_ + 10, hy_ - 1, 22, 40, GOLD, WHITE)
    # water drops
    s.set(cx + 24, 66, WATER); s.set(cx + 24, 67, WATER)
    s.set(cx - 22, 60, WATER); s.set(cx - 22, 61, WATER)


# --------------------------------------------------------------- persimmon
def persimmon(s, m, a, dt, st):
    cx = 48
    n = [3, 4, 5][st]
    rowh = [16, 14, 12][st]
    rx, ry = [15, 14, 13][st], [9.5, 8.5, 7.8][st]
    # skewer stick
    top = 80 - n * rowh - 8
    s.ell(cx, 80, 9, 2.5, (140, 190, 110))
    t = Sprite()
    for y in range(int(top), 80):
        t.ell(cx, y, 1.5, 1.5, (226, 190, 130))
    merge(s, t)
    s.tri([(cx - 1, top - 4), (cx + 2, top - 4), (cx + .5, top + 1)], (226, 190, 130))
    # persimmons bottom to top
    for i in range(n):
        y = 80 - 3 - ry - i * rowh
        jig = (-1, 1, -1, 1, -1)[i]
        x = cx + jig * 1
        s.ell(x, y, rx, ry, m)
        # frosty sugar bloom patches
        s.ell(x - rx * .5, y + ry * .35, 3.5, 2, tone(m, 1.45), flat=True)
        for dx, dy in ((.3, .2), (.55, -.1), (.1, .55)):
            s.set(x + dx * rx, y + dy * ry, (255, 244, 224))
        # calyx on top
        for d in (-6, -3, 0, 3, 6):
            s.line(x + d * .9, y - ry + 1, x + d * .6, y - ry - 1.5 + abs(d) * .15, (96, 150, 80))
        s.ell(x, y - ry + 1, 3.5, 1.8, (74, 140, 70), flat=True)
        s.set(x, y - ry - 1, dt)
        # face
        ey = y - 1
        for ex in (-5, 3):
            s.eye(x + ex, ey - 1, 2)
        s.ell(x - 8, ey + 3, 2.4, 1.5, (238, 120, 120), flat=True) if rx > 12 else None
        s.ell(x + 8, ey + 3, 2.4, 1.5, (238, 120, 120), flat=True) if rx > 12 else None
        s.line(x - 1, ey + 4, x + 1, ey + 4, dt)
        s.set(x - 2, ey + 3, dt); s.set(x + 2, ey + 3, dt)
    sparkle(s, cx + 22, 40, 2, a)
    sparkle(s, cx - 24, 54, 2, WHITE)
    if st >= 1:
        sparkle(s, cx + 20, 24, 3, GOLD)
    if st == 2:
        sparkle(s, cx - 22, 28, 2, GOLD)


# -------------------------------------------------------------------- star
def star(s, m, a, dt, st):
    cx, cy = 48, [44, 42, 40][st]
    R = [22, 26, 30][st]
    r = R * .46
    # falling streak
    for i in range(24):
        u = i / 24
        x = cx + 18 + u * 24
        y = cy - 18 - u * 22 + 0
    # glow ring dots
    dots_ring(s, cx, cy, R + 7, 46 + st * 10, tone(a, 1.2), GOLD)
    # tail: dotted streak up-right
    for i in range(14):
        sx, sy = cx + 14 + i * 2.3, cy - 14 - i * 2.2
        sw = max(0, 3 - i // 5)
        s.ell(sx, sy, sw + .5 if sw else .8, sw + .5 if sw else .8, tone(a, 1.25 - i * .01), flat=True) if sw else s.set(sx, sy, tone(a, 1.2))
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5 + .0
        rr = R if i % 2 == 0 else r
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    # faceted: each tip splits into light/dark halves
    col_l, col_d = tone(m, 1.1), tone(m, .78)
    for i in range(0, 10, 2):
        tip = pts[i]
        left, right = pts[(i - 1) % 10], pts[(i + 1) % 10]
        for tri_, c in (([tip, left, (cx, cy)], col_l if i in (0, 8, 6) else tone(m, 1.0)),
                        ([tip, right, (cx, cy)], col_d if i in (0, 2, 4) else tone(m, .9))):
            s.tri(tri_, c)
    s.ell(cx - 1, cy - 1, 4, 4, tone(m, 1.3), flat=True)
    # gold inner glint
    s.ell(cx - 3, cy - 4, 2, 2, WHITE, flat=True)
    # accent edge dots at tips
    for i in range(0, 10, 2):
        x, y = pts[i]
        s.set(x, y, a)
    # small crater/mound
    s.ell(cx, 80, 16, 3.5, (150, 198, 120))
    s.ell(cx, 80, 8, 1.6, tone(a, .85), flat=True)
    sparkle(s, cx - R - 6, cy - 6, 2, GOLD)
    sparkle(s, cx + R + 3, cy + 12, 2, WHITE)
    sparkle(s, cx - 6, cy + R + 6, 1, GOLD)
    if st >= 1:
        sparkle(s, cx + 26, cy - R - 4, 3, WHITE)


# ------------------------------------------------------------------ pillar
def pillar(s, m, a, dt, st):
    cx = 48
    pw = [11, 12, 13][st]
    top = [26, 20, 14][st]
    mound(s, cx, 80, 18)
    # cylinder body: 3 vertical bands
    r = ramp(m)
    for y in range(top, 80):
        for x in range(cx - pw, cx + pw + 1):
            u = (x - cx) / pw
            if y == top and abs(u) > .8:
                continue
            k = 3 if u < -.55 else 2 if u < -.1 else 1 if u < .5 else 0
            s.set(x, y, r[k])
    # top rounded + cap
    s.ell(cx, top, pw, 3.5, tone(m, 1.15))
    s.ell(cx, top - 1, pw - 3, 2, tone(m, 1.4), flat=True)
    for x in range(cx - pw - 1, cx + pw + 2):
        s.set(x, top + 12 + 0, G_(s,x, top + 12))
    # hat band
    s.ell(cx, top + 1, pw + 1, 3, dt)
    s.ell(cx, top - 2, pw - 3, 2.5, tone(dt, 1.25))
    # wood grain
    for gx_, y0, ln in ((-8, 44, 6), (7, 50, 7), (-3, 66, 6), (6, 70, 5), (-9, 58, 4)):
        s.line(cx + gx_, y0, cx + gx_, y0 + ln, tone(m, .7))
    # face
    fy = top + 14
    # brows
    s.line(cx - 9, fy - 4, cx - 3, fy - 2, dt, 2)
    s.line(cx + 9, fy - 4, cx + 3, fy - 2, dt, 2)
    # eyes
    for ex in (-6, 6):
        s.ell(cx + ex, fy + 2, 3.4, 3.2, (250, 246, 236), flat=True)
        s.ell(cx + ex + (1 if ex < 0 else -1), fy + 2.5, 1.7, 1.8, INK, flat=True)
        s.set(cx + ex + (0 if ex < 0 else -2), fy + 1, WHITE)
    # nose
    s.ell(cx, fy + 7, 2.6, 3, tone(m, .78))
    s.set(cx - 1, fy + 6, tone(m, 1.4))
    # mouth w/ fangs
    my = fy + 13
    s.line(cx - 6, my, cx + 6, my, dt, 2)
    for fx in (-5, 4):
        s.tri([(cx + fx, my + 1), (cx + fx + 3, my + 1), (cx + fx + 1.5, my + 5)], (250, 246, 236), None)
    # rope band (accent)
    ry_ = 80 - 6
    for x in range(cx - pw, cx + pw + 1):
        s.set(x, ry_, a if x % 3 else tone(a, .7))
        s.set(x, ry_ + 1, tone(a, .75))
    # side marks: vertical hanja-ish strokes
    for i in range(3 + st):
        s.set(cx + pw - 3, fy + 22 + i * 3 - 0, dt) if False else None
    # sparkles
    sparkle(s, cx + 20, top + 8, 2, GOLD)
    sparkle(s, cx - 21, top + 22, 1, WHITE)
    if st >= 1:
        sparkle(s, cx - 20, top - 3, 2, GOLD)
    if st == 2:
        sparkle(s, cx + 22, top + 30, 2, WHITE)


# --------------------------------------------------------------- clepsydra
def jar(s, x, y, w, h, m, a, dt, water=.6):
    # body
    s.ell(x, y, w, h, m)
    # neck + rim
    s.ell(x, y - h + 1, w * .55, 2.2, tone(m, 1.1))
    s.ell(x, y - h - 1, w * .62, 1.8, tone(m, 1.3))
    # band in accent
    for dx in range(-int(w * .9), int(w * .9) + 1):
        if G_(s,x + dx, y - h * .2) is not None and G_(s,x + dx, y - h * .2 - 1) is not None:
            s.set(x + dx, y - h * .2, a)
    # water window
    s.ell(x, y + h * .35, w * .5, h * .32, (150, 205, 235), flat=True)
    s.set(x - w * .3, y + h * .2, WHITE)


def clepsydra(s, m, a, dt, st):
    cx = 48
    k = [.78, .88, 1.0][st]
    wood = (120, 86, 66)
    # ground
    s.ell(cx, 80, 40 * k + 2, 4, (166, 150, 136))
    # stand (wooden tiers)
    def tier(x0, x1, y):
        s.ell((x0 + x1) / 2, y + 2, (x1 - x0) / 2, 2.6, wood)
    # three jars stepping down left to right
    jars = [(cx - 22 * k, 38 * k + 14, 11 * k, 13 * k), (cx - 4 * k, 54, 10 * k, 12 * k), (cx + 12 * k, 68, 9.5 * k, 10 * k)]
    n = 2 + (st >= 1)
    n = 3
    # shelves
    for (jx, jy, jw, jh) in jars:
        s.ell(jx, jy + jh + 2, jw + 4, 2.4, wood)
        s.line(jx - jw - 2, jy + jh + 4, jx - jw - 2, 80, tone(wood, .8), 2)
        s.line(jx + jw + 2, jy + jh + 4, jx + jw + 2, 80, tone(wood, .8), 2)
    for (jx, jy, jw, jh), c in zip(jars, (m, tone(m, .95), tone(m, .9))):
        jar(s, jx, jy, jw, jh, c, a, dt)
    # spouts connecting
    for (j0, j1) in zip(jars, jars[1:]):
        s.line(j0[0] + j0[2] - 1, j0[1] + 4, j1[0] - 3, j1[1] - j1[3] - 2, (150, 205, 235), 1)
        s.set(j1[0] - 3, j1[1] - j1[3] + 1, (190, 225, 245))
    # cabinet (pavilion) on the right
    bx0, bx1 = int(cx + 25 * k), int(cx + 25 * k + 17 * k)
    by0, by1 = 49 - int(8 * (st)), 80
    by0 = int(80 - 38 * k)
    poly(s, [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], tone(m, .95))
    s.line(bx0, by0 + 12, bx1, by0 + 12, a)
    # roof (eave)
    poly(s, [(bx0 - 4, by0 + 1), (bx0 + 3, by0 - 6), (bx1 - 3, by0 - 6), (bx1 + 4, by0 + 1)], dt)
    s.line(bx0 - 5, by0 + 2, bx0 - 3, by0, a)
    s.line(bx1 + 5, by0 + 2, bx1 + 3, by0, a)
    # windows with tiny figures
    for i, fy in enumerate((by0 + 4, by0 + 15, by0 + 26)):
        if fy + 7 > by1:
            break
        s.ell((bx0 + bx1) / 2, fy + 3, 4.5, 4.2, tone(dt, 1.05), flat=True)
        s.ell((bx0 + bx1) / 2, fy + 3, 2.2, 2.4, (255, 212, 130), flat=True)
    # bell on top
    if st >= 1:
        s.line((bx0 + bx1) / 2, by0 - 6, (bx0 + bx1) / 2, by0 - 9, dt)
        s.ell((bx0 + bx1) / 2, by0 - 11, 3.2, 3, (236, 190, 70))
        s.set((bx0 + bx1) / 2 - 1, by0 - 12, WHITE)
    # water drop sparkles
    s.set(cx - 12 * k, 52, (190, 225, 245)); s.set(cx - 12 * k, 53, (150, 205, 235))
    sparkle(s, cx - 30 * k, 40, 2, WHITE)
    sparkle(s, cx + 6, 24, 2, GOLD if st else WHITE)
    if st == 2:
        sparkle(s, cx + 30, by0 - 14, 2, GOLD)


# -------------------------------------------------------------------- ship
def ship(s, m, a, dt, st):
    cx = 52
    k = [.74, .86, 1.0][st]
    gy = 74
    hull = (126, 88, 66)
    # dragon head (left)
    hx_, hy_ = cx - 36 * k, gy - 18 * k
    # hull
    poly(s, [(cx - 34 * k, gy - 16 * k), (cx + 34 * k, gy - 16 * k), (cx + 30 * k, gy), (cx - 26 * k, gy), ], hull)
    for q in range(1, 4):
        s.line(cx - 32 * k + q * 2, gy - 16 * k + q * 4 * k, cx + 32 * k - q * 2, gy - 16 * k + q * 4 * k, tone(hull, .75))
    s.line(cx - 33 * k, gy - 15 * k, cx + 33 * k, gy - 15 * k, a, 2)
    # oars
    for q in range(4 if st else 3):
        ox = cx - 18 * k + q * 12 * k
        s.line(ox, gy - 8 * k, ox - 6, gy + 7, tone(hull, 1.3), 2)
        s.ell(ox - 7, gy + 8, 3, 1.6, tone(hull, 1.3))
    # shell dome
    s.ell(cx, gy - 16 * k, 30 * k, 22 * k, m)
    # lower mask
    for y in range(int(gy - 16 * k) + 1, int(gy - 12 * k)):
        for x in range(96):
            s.px[y][x] = None if s.px[y][x] and False else s.px[y][x]
    # re-cut lower half by redrawing hull strip over it
    poly(s, [(cx - 34 * k, gy - 16 * k + 1), (cx + 34 * k, gy - 16 * k + 1), (cx + 30 * k, gy), (cx - 26 * k, gy)], hull)
    for q in range(1, 4):
        s.line(cx - 32 * k + q * 2, gy - 16 * k + q * 4 * k, cx + 32 * k - q * 2, gy - 16 * k + q * 4 * k, tone(hull, .75))
    s.line(cx - 33 * k, gy - 15 * k, cx + 33 * k, gy - 15 * k, a, 2)
    # hex plate seams
    seam = tone(m, .62)
    rows = [(gy - 22 * k, 5), (gy - 29 * k, 4), (gy - 35 * k, 3)]
    for i, (yy, nn) in enumerate(rows):
        for j in range(nn):
            xx = cx + (j - (nn - 1) / 2) * 11 * k
            for dx in (-5 * k, 5 * k):
                s.line(xx + dx, yy - 3, xx + dx, yy + 3, seam)
        s.line(cx - 26 * k, yy + 3, cx + 26 * k, yy + 3, seam) if i == 0 else None
    # spikes
    nsp = [5, 6, 7][st]
    for j in range(nsp):
        u = (j + .5) / nsp * 2 - 1
        x = cx + u * 22 * k
        y = gy - 16 * k - 22 * k * math.sqrt(max(0, 1 - (u * 22 / 30) ** 2)) + 1
        hgt = (5 if st else 4) + (2 if abs(u) < .3 else 0)
        s.tri([(x - 2, y + 1), (x + 2, y + 1), (x + .3, y - hgt)], dt)
        s.set(x - .5, y - hgt + 2, tone(dt, 2.2))
    # dragon neck + head
    neck = [(cx - 27 * k, gy - 18 * k), (hx_ + 3, hy_ - 1), (hx_ - 4 * k, hy_ - 6 * k)]
    s.tube(neck, [3.6 * k, 3.4 * k, 3.6 * k], a)
    hx2, hy2 = hx_ - 8 * k, hy_ - 9 * k
    s.ell(hx2, hy2, 7 * k, 5.6 * k, a)
    s.ell(hx2 - 6 * k, hy2 + 2 * k, 5.2 * k, 3.0 * k, tone(a, 1.1))      # snout
    s.line(hx2 - 9 * k, hy2 + 4 * k, hx2 - 1, hy2 + 4 * k, INK)           # mouth
    s.set(hx2 - 9 * k, hy2 + 5 * k, WHITE); s.set(hx2 - 5 * k, hy2 + 5 * k, WHITE)  # fangs
    s.eye(hx2 - 1, hy2 - 3 * k, 2, shine=True)
    # horns
    s.tri([(hx2 + 1, hy2 - 4 * k), (hx2 + 5, hy2 - 4 * k), (hx2 + 6 * k, hy2 - 12 * k)], (250, 226, 150))
    s.tri([(hx2 - 3, hy2 - 5 * k), (hx2, hy2 - 5 * k), (hx2 - 3, hy2 - 11 * k)], (250, 226, 150))
    # mane
    for q in range(3):
        s.tri([(hx2 + 4 + q * 2, hy2 + 3 * k), (hx2 + 8 + q * 2, hy2 + 5 * k), (hx2 + 4 + q * 3, hy2 + 8 * k)], tone(a, .7))
    # smoke
    for q, (dx, dy, rr) in enumerate(((-11, -3, 2.4), (-16, -7, 3), (-21, -12, 3.6))):
        if st or q < 2:
            s.ell(hx2 + dx * k, hy2 + dy * k, rr, rr, (222, 222, 232))
    # flag at the stern
    fx = cx + 26 * k
    s.line(fx, gy - 34 * k, fx, gy - 52 * k - st * 3, hull, 2)
    fy = gy - 52 * k - st * 3
    poly(s, [(fx + 1, fy), (fx + 15 * k, fy + 2), (fx + 10 * k, fy + 5), (fx + 15 * k, fy + 8), (fx + 1, fy + 10)], a)
    s.set(fx + 4, fy + 4, WHITE)
    # waves
    for q, (wx, wy, ww) in enumerate(((cx - 36, gy + 3, 14), (cx - 12, gy + 5, 16), (cx + 14, gy + 3, 15), (cx + 36, gy + 5, 12), (cx - 24, gy + 9, 12), (cx + 4, gy + 10, 14), (cx + 28, gy + 9, 12))):
        s.ell(wx, wy, ww * k + 2, 3, WATER)
        s.line(wx - ww * .4, wy - 1, wx + ww * .2, wy - 1, (214, 238, 248))
    sparkle(s, cx - 38 * k - 8, hy_ - 22, 2, GOLD)
    sparkle(s, cx + 6, gy - 44 * k - 4, 2, WHITE)


# ======================= revision 2 (overrides above) =====================
def egg_rays(s, cx, cy, rx, ry, a, st):
    nr = [7, 9, 11][st]
    for i in range(nr):
        ang = -math.pi / 2 + (i - (nr - 1) / 2) * (math.pi * 1.55 / (nr - 1))
        L0 = 1.0
        long_ = i % 2 == 0
        r0 = 1.18 + (.0 if long_ else .06)
        r1 = r0 + (.3 if long_ else .17) + st * .03
        ex, ey = rx / ry, 1.0
        s.line(cx + math.cos(ang) * ry * r0 * ex * .8 - 0, cy + math.sin(ang) * ry * r0,
               cx + math.cos(ang) * ry * r1 * ex * .8, cy + math.sin(ang) * ry * r1,
               GOLD if long_ else tone(a, 1.3))


def egg(s, m, a, dt, st):
    cx = 48
    ry = [20, 24, 28][st]
    rx = [15, 18, 21][st]
    cy = 80 - ry - 1
    egg_rays(s, cx, cy, rx, ry, a, st)
    mound(s, cx, 80, rx + 4)
    blob(s, cx, cy, rx, ry, m)
    spots = [(-.35, .25, 2), (.3, .5, 2), (.1, -.2, 1), (-.1, .65, 1), (.45, .05, 1), (-.45, .6, 1)]
    for sx, sy, r_ in spots[:2 + st * 2]:
        s.ell(cx + sx * rx, cy + sy * ry, r_ + .6, r_, a, flat=True)
    if st >= 1:
        yb = cy + int(ry * .25)
        for x in range(cx - rx, cx + rx + 1):
            if G_(s, x, yb) and G_(s, x, yb - 2):
                s.set(x, yb, a); s.set(x, yb + 1, tone(a, .7))
    if st == 2:
        pts = [(cx - 1, cy - ry + 3), (cx + 1, cy - ry + 6), (cx - 1, cy - ry + 9), (cx + 1, cy - ry + 12)]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            s.line(x0, y0, x1, y1, GOLD)
    s.ell(cx - rx * .45, cy - ry * .45, 2.2, 3.5, WHITE, rot=.5, flat=True)
    s.set(cx - rx * .45 + 3, cy - ry * .45 + 6, WHITE)
    sparkle(s, cx + rx + 7, cy - ry * .5, 2, GOLD)
    sparkle(s, cx - rx - 8, cy - ry * .1, 1, WHITE)
    if st >= 1:
        sparkle(s, cx + rx - 2, cy - ry - 8, 3, GOLD)
    if st == 2:
        sparkle(s, cx - rx - 2, cy - ry - 6, 2, WHITE)


def petal(s, bx, by, ang, ln, wd, col):
    pts = [(bx + math.sin(ang) * ln * q / 6 * (1 + .0), by - math.cos(ang) * ln * q / 6) for q in range(7)]
    # slight outward bend
    pts = [(x + math.sin(ang) * (q / 6) ** 2 * 3, y) for q, (x, y) in enumerate(pts)]
    s.tube(pts, [wd * .45, wd * .85, wd, wd * .95, wd * .75, wd * .45, .7], col)


def lotus(s, m, a, dt, st):
    cx = 48
    k = [.82, .92, 1.0][st]
    s.ell(cx, 79, 38 * k + 2, 5.5, WATER)
    for dx in (-28, -12, 16, 30):
        s.line(cx + dx * k, 80, cx + dx * k + 5, 80, (214, 238, 248))
    s.ell(cx, 74, 28 * k, 5.5, m)
    s.line(cx, 74, cx + 27 * k, 71, tone(m, .6))
    for dx in (-16, -4, 13, 20):
        s.set(cx + dx * k, 75, tone(m, 1.4))
    base = 72
    L = 34 * k
    for sg in (-1, 1):
        petal(s, cx + sg * 3, base, sg * .95, L * .8, 5.2 * k, tone(a, .8))
    petal(s, cx - 1, base, -.5, L * .95, 5.6 * k, tone(a, .9))
    petal(s, cx + 1, base, .5, L * .95, 5.6 * k, tone(a, .9))
    petal(s, cx, base, 0, L, 5.8 * k, tone(a, 1.0))
    for sg in (-1, 1):
        petal(s, cx + sg * 2, base + 2, sg * 1.25, L * .6, 5.4 * k, a)
    for sg in (-1, 1):
        petal(s, cx + sg * 1.5, base + 2, sg * .3, L * .72, 5.8 * k, tone(a, 1.18))
    # base pod hidden; yellow stamens peek
    s.ell(cx, 56 + (1 - k) * 10, 3.5, 2.2, (250, 220, 90))
    if st >= 1:
        bx = cx + 30 * k
        s.line(bx, 74, bx - 1, 58, tone(m, .8), 2)
        petal(s, bx - 1, 60, 0, 11, 3.6, tone(a, 1.0))
        petal(s, bx - 1, 60, .7, 8, 3, tone(a, .8))
    if st == 2:
        bx = cx - 31
        s.line(bx, 74, bx + 1, 63, tone(m, .8), 2)
        s.ell(bx + 1, 62, 3, 4, tone(a, 1.1))
    sparkle(s, cx + 24 * k, 36, 2, WHITE)
    sparkle(s, cx - 26 * k, 42, 1, GOLD)
    if st >= 1:
        sparkle(s, cx + 6, 28, 3, GOLD)


def rope(s, m, a, dt, st):
    cx = 48
    t = Sprite()
    w = [3.4, 4.0, 4.6][st]
    ring = [(cx + math.cos(q / 12 * math.tau + .6) * (18 + st * 3), 77 + math.sin(q / 12 * math.tau + .6) * 4.5) for q in range(13)]
    t.tube(ring, [w * .9] * 13, tone(m, .92))
    pts = [(cx + 3 * math.sin(i / 10 * 4 + .5), 20 + i * 5.2) for i in range(11)]
    t.tube(pts, [w] * 11, m)
    for y in range(96):
        for x in range(96):
            c = t.px[y][x]
            if c:
                q = (x + y * 2) % 6
                if q == 0:
                    t.px[y][x] = tone(c, .6)
                elif q == 1:
                    t.px[y][x] = tone(c, 1.3)
    merge(s, t)
    # big knots
    for ky in ([34, 56] if st < 2 else [32, 46, 60]):
        kx = cx + 3 * math.sin((ky - 20) / 52 * 4 + .5)
        s.line(kx - w, ky - 1, kx + w, ky + 1, tone(a, 1.0), 2)
        s.line(kx - w, ky + 1, kx + w, ky + 3, tone(a, .7))
    # tassel at end
    ex = pts[-1][0]
    s.ell(ex, 70, w + 1, 3, a)
    # cloud
    for dx, w_, dy in ((-8, 8, 2), (0, 10, -1), (9, 8, 2), (-1, 8, 3)):
        s.ell(cx + dx, 11 + dy, w_, 4.5, (244, 248, 253))
    for (x, y, r_, c) in ((cx - 18, 36, 2, GOLD), (cx + 19, 50, 2, WHITE), (cx - 17, 62, 1, GOLD), (cx + 18, 26, 1, GOLD)):
        sparkle(s, x, y, r_, c)
    if st == 2:
        sparkle(s, cx + 20, 18, 3, GOLD)
        sparkle(s, cx - 20, 48, 2, WHITE)
    # light shafts from cloud
    for sg in (-1, 1):
        for q in range(3 + st * 2):
            s.set(cx + sg * (9 + q * 1.6), 20 + q * 5, tone(a, 1.3))


def magpie(s, x, y, face=1, k=1.0):
    body = (44, 48, 72)
    s.ell(x - face * 6.5 * k, y - 1.5 * k, 6 * k, 2.2 * k, (60, 78, 140), rot=-face * .35, gloss=False)
    s.ell(x, y - 4 * k, 5.4 * k, 4.4 * k, body)
    s.ell(x + face * 1.2 * k, y - 2.2 * k, 3.4 * k, 2.8 * k, (250, 250, 255), gloss=False)
    s.ell(x - face * 1.5 * k, y - 4.4 * k, 3.4 * k, 2.2 * k, (70, 120, 190), gloss=False)
    hx_, hy_ = x + face * 4.4 * k, y - 8 * k
    s.ell(hx_, hy_, 3.3 * k, 3 * k, body)
    for q in range(2):
        s.set(hx_ + face * (3.2 * k + q * 1.5), hy_ + .5 + q * .4, (244, 190, 60))
    s.set(hx_ + face * .6, hy_ - .8, WHITE)
    s.set(hx_ + face * 1.6, hy_ - .4, INK)
    s.set(x - 1, y + 1, (60, 50, 50)); s.set(x + 1, y + 1, (60, 50, 50))


def bridge(s, m, a, dt, st):
    cx = 48
    W = [32, 36, 40][st]
    H = [22, 26, 30][st]
    base = 80
    pts = [(cx + (i / 12 * 2 - 1) * W, base - H * (1 - ((i / 12 * 2 - 1) ** 2)) - 6) for i in range(13)]
    t = Sprite()
    t.tube(pts, [5.4] * 13, m)
    merge(s, t)
    # silvery deck top
    for i in range(12):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        s.line(x0, y0 - 4, x1, y1 - 4, a, 2)
        s.line(x0, y0 - 5, x1, y1 - 5, tone(a, 1.3))
    # plank seams
    for (x, y) in pts:
        s.line(x, y - 3, x, y + 3, tone(m, .6))
    # stars / milky-way glitter on arch face
    for (x, y) in pts[1:-1:2]:
        s.set(x + 1, y + 1, tone(a, 1.3))
    for sgn in (-1, 1):
        x, y = pts[0 if sgn < 0 else 12]
        s.ell(x, base - 3, 7, 5, tone(m, 1.15))
        s.ell(x, base - 1, 8, 3, tone(m, .9))
        s.set(x - 2, base - 5, tone(a, 1.3))
    kb = [1.2, 1.4, 1.5][st]
    magpie(s, pts[2][0], pts[2][1] - 6, 1, kb)
    if st >= 1:
        magpie(s, pts[10][0], pts[10][1] - 6, -1, kb)
    if st == 2:
        magpie(s, pts[6][0] - 1, pts[6][1] - 6, 1, kb + .1)
    if st >= 1:
        fx, fy = cx + 22, 12
        for (x0, y0, x1, y1) in ((fx - 5, fy, fx, fy + 2), (fx, fy + 2, fx + 5, fy - 1)):
            s.line(x0, y0, x1, y1, (44, 48, 72))
    for (x, y, r_, c) in ((cx - 4, 66, 1, GOLD), (cx + 6, 70, 2, WHITE), (cx - 24, 16, 2, GOLD), (cx + 30, 32, 1, WHITE)):
        sparkle(s, x, y, r_, c)
    if st == 2:
        sparkle(s, cx - 32, 34, 2, WHITE)
        sparkle(s, cx + 2, 10, 3, GOLD)


def wingrobe(s, m, a, dt, st):
    cx = 48
    k = [.84, .92, 1.0][st]
    cy = 44
    top = cy - 8
    sky, pink = (176, 222, 244), (252, 190, 212)
    # scarves drooping both sides
    for i in range(1 + (st >= 1) + (st == 2)):
        for side in (-1, 1):
            col = sky if (i + (side > 0)) % 2 == 0 else pink
            pts = [(cx + side * (10 + 3 * i + 4 * math.sin(q / 8 * 5 + i + (side > 0))), top + 8 + q * (30 / 8) * k) for q in range(9)]
            s.tube(pts, [2.2, 2.2, 2.0, 2.0, 1.8, 1.6, 1.4, 1.1, .8], col)
    for side in (-1, 1):
        pts = [(cx + side * (7 + q * 3.5 * k), cy - 5 + q * 1.0 + 4.6 * math.sin(q / 6 * 3.2 + (0 if side > 0 else 1.6)) - (q * .8)) for q in range(11)]
        rr = [3.2, 3.6, 4, 4.4, 4.7, 4.8, 4.7, 4.4, 3.9, 3.2, 2.6]
        s.tube(pts, [r_ * k for r_ in rr], m)
        ex, ey = pts[-1]
        s.ell(ex, ey, 3.4 * k, 3.0 * k, tone(m, 1.25))
        s.set(ex - 1, ey - 1, WHITE)
        for q in (6, 7):
            x, y = pts[q]
            s.line(x, y - 4 * k, x, y + 4 * k, tone(a, 1.15))
    poly(s, [(cx - 8 * k, top), (cx + 8 * k, top), (cx + 15 * k, top + 33 * k), (cx + 9 * k, top + 37 * k), (cx + 3 * k, top + 34 * k + 2),
             (cx - 4 * k, top + 38 * k), (cx - 10 * k, top + 34 * k), (cx - 15 * k, top + 33 * k)], m)
    for fx in (-6, -1, 5):
        s.line(cx + fx * k, top + 14 * k, cx + fx * 1.6 * k, top + 33 * k, tone(m, .78))
    s.line(cx - 7 * k, top, cx, top + 9, tone(a, 1.1), 2)
    s.line(cx + 7 * k, top, cx, top + 9, tone(a, 1.3), 2)
    s.line(cx - 8 * k, top + 12 * k, cx + 8 * k, top + 12 * k, tone(a, 1.15), 2)
    s.tri([(cx + 2, top + 13 * k), (cx + 8, top + 23 * k), (cx + 4, top + 23 * k)], pink)
    s.tri([(cx - 2, top + 13 * k), (cx - 8, top + 22 * k), (cx - 4, top + 22 * k)], sky)
    for (x, y, r_, c) in ((cx - 26, 20, 2, GOLD), (cx + 27, 22, 2, WHITE), (cx + 10, 14, 1, GOLD), (cx - 24, 66, 1, WHITE), (cx + 26, 62, 2, GOLD)):
        sparkle(s, x, y, r_, c)
    if st >= 1:
        sparkle(s, cx - 4, 12, 3, GOLD)
    for dx, w_ in ((-10, 8), (0, 11), (10, 8)):
        s.ell(cx + dx, 80, w_, 3.5, (236, 244, 252))


def star(s, m, a, dt, st):
    cx, cy = 46, [48, 46, 44][st]
    R = [22, 26, 29][st]
    r = R * .47
    m = blend(m, (255, 244, 196), .35)
    dots_ring(s, cx, cy, R + 7, 40 + st * 10, tone(a, 1.2), GOLD)
    d = (.707, -.707)
    nx, ny = .707, .707
    for j, (off, ln) in enumerate(((0, 40), (-6, 30), (6, 30), (-11, 18), (11, 18))):
        for q in range(int(R * .8), int(R * .8) + ln):
            x = cx + d[0] * q + nx * off
            y = cy + d[1] * q + ny * off
            u = (q - R * .8) / ln
            if (q + j) % 3 == 0 or u < .3:
                s.set(x, y, GOLD if u < .55 else WHITE)
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = R if i % 2 == 0 else r
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    for i in range(0, 10, 2):
        tip = pts[i]
        left, right = pts[(i - 1) % 10], pts[(i + 1) % 10]
        s.tri([tip, left, (cx, cy)], tone(m, 1.12) if i in (0, 8, 6) else tone(m, 1.0))
        s.tri([tip, right, (cx, cy)], tone(m, .8) if i in (0, 2, 4) else tone(m, .9))
    s.ell(cx - 1, cy - 1, 4, 4, tone(m, 1.3), flat=True)
    s.ell(cx - 3, cy - 4, 2, 2, WHITE, flat=True)
    for i in range(0, 10, 2):
        x, y = pts[i]
        s.set(x, y, a)
    s.ell(cx, 80, 16, 3.5, (150, 198, 120))
    s.ell(cx, 80, 8, 1.6, tone(a, .85), flat=True)
    sparkle(s, cx - R - 6, cy - 6, 2, GOLD)
    sparkle(s, cx + R + 4, cy + 14, 2, WHITE)
    sparkle(s, cx - 6, cy + R + 6, 1, GOLD)
    if st >= 1:
        sparkle(s, cx - R, cy - R - 2, 3, WHITE)


def clepsydra(s, m, a, dt, st):
    cx = 26
    k = [.86, .94, 1.0][st]
    wood = (120, 86, 66)
    s.ell(cx + 30 * k, 80, 40 * k + 2, 4, (166, 150, 136))
    jars = [(cx, 36, 13 * k, 14.5 * k), (cx + 17 * k, 52, 12 * k, 13 * k), (cx + 33 * k, 66, 11 * k, 11 * k)]
    for (jx, jy, jw, jh) in jars:
        s.ell(jx, jy + jh + 2, jw + 4, 2.4, wood)
        s.line(jx - jw - 2, jy + jh + 4, jx - jw - 2, 80, tone(wood, .8), 2)
        s.line(jx + jw + 2, jy + jh + 4, jx + jw + 2, 80, tone(wood, .8), 2)
    for (jx, jy, jw, jh), c in zip(jars, (m, tone(m, .95), tone(m, .9))):
        jar(s, jx, jy, jw, jh, c, a, dt)
    for (j0, j1) in zip(jars, jars[1:]):
        s.line(j0[0] + j0[2] - 1, j0[1] + 5, j1[0] - 3, j1[1] - j1[3] - 2, (110, 180, 220), 2)
        s.set(j1[0] - 3, j1[1] - j1[3] + 1, (190, 225, 245))
    bx0 = int(cx + 49 * k)
    bx1 = bx0 + int(18 * k)
    by0 = int(80 - 50 * k)
    by1 = 80
    poly(s, [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], tone(m, .95))
    s.line(bx0, by0 + 12, bx1, by0 + 12, a)
    poly(s, [(bx0 - 5, by0 + 1), (bx0 + 3, by0 - 7), (bx1 - 3, by0 - 7), (bx1 + 5, by0 + 1)], dt)
    s.line(bx0 - 6, by0 + 2, bx0 - 4, by0, tone(a, 1.1))
    s.line(bx1 + 6, by0 + 2, bx1 + 4, by0, tone(a, 1.1))
    mx = (bx0 + bx1) / 2
    for fy in (by0 + 5, by0 + 17, by0 + 29):
        if fy + 8 > by1:
            break
        s.ell(mx, fy + 4, 5, 4.6, tone(dt, 1.05), flat=True)
        s.ell(mx, fy + 4, 2.6, 2.8, (255, 212, 130), flat=True)
    s.line(mx, by0 - 7, mx, by0 - 10, dt)
    s.ell(mx, by0 - 12, 3.4, 3.2, (236, 190, 70))
    s.set(mx - 1, by0 - 13, WHITE)
    s.set(cx - 14 * k, 54, (190, 225, 245)); s.set(cx - 14 * k, 55, (150, 205, 235))
    sparkle(s, cx - 34 * k, 40, 2, WHITE)
    sparkle(s, cx + 4, 20, 2, GOLD if st else WHITE)
    if st == 2:
        sparkle(s, bx1 + 2, by0 - 16, 2, GOLD)


def ship(s, m, a, dt, st):
    cx = 54
    k = [.74, .86, 1.0][st]
    gy = 74
    hull = (126, 88, 66)

    def hullpoly():
        poly(s, [(cx - 34 * k, gy - 16 * k + 1), (cx + 34 * k, gy - 16 * k + 1), (cx + 30 * k, gy), (cx - 26 * k, gy)], hull)
        for q in range(1, 4):
            s.line(cx - 32 * k + q * 2, gy - 16 * k + q * 4 * k, cx + 32 * k - q * 2, gy - 16 * k + q * 4 * k, tone(hull, .75))
        s.line(cx - 33 * k, gy - 15 * k, cx + 33 * k, gy - 15 * k, a, 2)
    # shell dome with plate pattern
    t = Sprite()
    t.ell(cx, gy - 16 * k, 30 * k, 22 * k, m)
    for y in range(96):
        for x in range(96):
            c = t.px[y][x]
            if c:
                row = int((gy - y) // 6)
                off = 4 if row % 2 else 0
                if (y % 6 == 0) or ((x + off) % 8 == 0):
                    t.px[y][x] = tone(c, .66)
    merge(s, t)
    hullpoly()
    nsp = [5, 6, 7][st]
    for j in range(nsp):
        u = (j + .5) / nsp * 2 - 1
        x = cx + u * 22 * k
        y = gy - 16 * k - 22 * k * math.sqrt(max(0, 1 - (u * 22 / 30) ** 2)) + 1
        hgt = (6 if st else 5) + (2 if abs(u) < .3 else 0)
        s.tri([(x - 2.5, y + 1), (x + 2.5, y + 1), (x + .3, y - hgt)], dt)
        s.set(x - .5, y - hgt + 2, tone(dt, 2.4))
    for q in range(4 if st else 3):
        ox = cx - 18 * k + q * 12 * k
        s.line(ox, gy - 8 * k, ox - 6, gy + 7, tone(hull, 1.3), 2)
    # dragon
    hx2, hy2 = cx - 38 * k, gy - 33 * k
    neck = [(cx - 27 * k, gy - 17 * k), (cx - 33 * k, gy - 24 * k), (hx2 + 4 * k, hy2 + 4 * k)]
    s.tube(neck, [4 * k, 4 * k, 4 * k], a)
    for q in range(3):
        s.tri([(hx2 + 4 + q * 3, hy2 - 1 + q * 3), (hx2 + 11 + q * 3, hy2 + 3 + q * 3), (hx2 + 5 + q * 3, hy2 + 6 + q * 3)], tone(a, .65))
    s.ell(hx2 - 6 * k, hy2 + 5.5 * k, 6.2 * k, 2.6 * k, tone(a, .8))          # lower jaw
    s.ell(hx2, hy2, 8 * k, 6.4 * k, a)
    s.ell(hx2 - 7 * k, hy2 + 1.5 * k, 6.2 * k, 3.4 * k, tone(a, 1.12))          # snout
    s.line(hx2 - 12 * k, hy2 + 4 * k, hx2 - 2 * k, hy2 + 4 * k, INK)
    s.set(hx2 - 11 * k, hy2 + 5 * k, WHITE); s.set(hx2 - 7 * k, hy2 + 5 * k, WHITE)
    s.set(hx2 - 11 * k, hy2, INK)
    s.eye(hx2 - 1, hy2 - 3.5 * k, 2)
    s.tri([(hx2 + 1, hy2 - 5 * k), (hx2 + 5, hy2 - 5 * k), (hx2 + 7 * k, hy2 - 14 * k)], (250, 226, 150))
    s.tri([(hx2 - 4, hy2 - 5 * k), (hx2, hy2 - 5 * k), (hx2 - 4, hy2 - 12 * k)], (250, 226, 150))
    for q, (dx, dy, rr) in enumerate(((-15, -1, 2), (-19, -5, 2.6), (-23, -10, 3.2))):
        if st or q < 2:
            s.ell(hx2 + dx * k, hy2 + dy * k + 3, rr, rr, (226, 226, 236))
    fx = cx + 26 * k
    fy = gy - 54 * k - st * 2
    s.line(fx, gy - 34 * k, fx, fy, hull, 2)
    poly(s, [(fx + 1, fy), (fx + 15 * k, fy + 2), (fx + 10 * k, fy + 5), (fx + 15 * k, fy + 8), (fx + 1, fy + 10)], a)
    s.set(fx + 4, fy + 4, WHITE)
    # waves band
    for x in range(0, 96):
        y0 = gy + 4 + 1.6 * math.sin(x / 3.2) + (x % 11 == 0)
        for y in range(int(y0), gy + 13):
            c = (214, 238, 248) if y < y0 + 1 else WATER if y < y0 + 4 else tone(WATER, .86)
            s.set(x, y, c)
    sparkle(s, cx - 38 * k - 10, hy2 - 8, 2, GOLD)
    sparkle(s, cx + 6, gy - 44 * k - 6, 2, WHITE)
    for dx in (-30, 8, 30):
        s.line(cx + dx, gy + 8, cx + dx + 4, gy + 8, (214, 238, 248))



SHAPES = dict(egg=egg, lotus=lotus, rope=rope, bridge=bridge, wingrobe=wingrobe, axe=axe,
              persimmon=persimmon, star=star, pillar=pillar, clepsydra=clepsydra, ship=ship)


def draw(p, stage, spec):
    s = Sprite()
    SHAPES[spec["shape"]](s, hx(p["main"]), hx(p["accent"]), hx(p["detail"]), stage)
    return s
