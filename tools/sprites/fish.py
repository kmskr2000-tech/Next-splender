"""fish archetype: carp -> great carp -> dragon-gate carp (koi-dragon). stage 0..2.
feats: fins scales whiskers beard horns antlers mane aura cloud gem crown flame stripes spots."""
import math

from core import Sprite, hx, tone

HORN = (246, 232, 196)
WHITE = (240, 236, 224)


def spline(c, n=8):
    pts = [c[0]] + list(c) + [c[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(.5 * (2 * p1[d] + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t * t
                                   + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t ** 3) for d in (0, 1)))
    out.append(tuple(c[-1]))
    return out


def curve(s, ctl, col, n=5):
    sp = spline(ctl, n)
    for (xa, ya), (xb, yb) in zip(sp, sp[1:]):
        s.line(xa, ya, xb, yb, col)


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    belly = tone(m, 1.35)
    fin = tone(a, 1.05) if stage else tone(m, 1.12)
    finb = tone(fin, .8)
    k = [.75, .95, 1.12][stage]
    th = [0, .08, .2][stage]
    ct, st = math.cos(th), math.sin(th)
    ox, oy = [50, 47, 38][stage], [60, 56, 52][stage]
    rx, ry = 18 * k, 13.5 * k

    def T(x, y):            # local (x right, y down) -> canvas
        return ox + x * ct - y * st, oy + x * st + y * ct

    def E(x, y, a_, b_, col, rot=0, **kw):
        X, Y = T(x, y)
        s.ell(X, Y, a_, b_, col, rot=rot + th, **kw)

    def TRI(pts, col, sh=None):
        s.tri([T(*q) for q in pts], col, sh)

    def LN(x0, y0, x1, y1, col):
        (X0, Y0), (X1, Y1) = T(x0, y0), T(x1, y1)
        s.line(X0, Y0, X1, Y1, col)

    def CV(ctl, col):
        curve(s, [T(*q) for q in ctl], col)

    if "aura" in feats and stage:
        for i in range(18):
            ang = i / 18 * math.tau
            s.set(48 + math.cos(ang) * 45, 50 + math.sin(ang) * 42, tone(a, 1.3))
    if "cloud" in feats and stage == 2:
        for qx, qy in ((16, 84), (72, 86), (84, 76)):
            s.ell(qx, qy, 7, 3, (236, 240, 248), flat=True)
            s.ell(qx + 5, qy + 1, 5, 2.5, (214, 222, 238), flat=True)

    # tail: peduncle + two flowing lobes + streamers
    s.tube([T(rx * .6, 0), T(rx + 5 * k, -1)], [ry * .55, ry * .28], m)
    tx = rx + 5 * k
    tl = [9, 12, 15][stage]
    for sg in (-1, 1):
        E(tx + tl * .6, sg * tl * .38, tl * .85, tl * .3 + stage * .5, tone(fin, 1.0 if sg < 0 else .88), rot=sg * .5)
    if stage == 2:
        for sg, ln in ((-1, 10), (1, 9)):
            CV([(tx + tl * 1.2, sg * 8), (tx + tl * 1.2 + ln * .3, sg * 13), (tx + tl * 1.2 + ln * .6, sg * 9), (tx + tl * 1.2 + ln * .8, sg * 14)], a)
    # dorsal fin
    dl = [6, 8, 11][stage]
    if stage >= 1 or "fins" in feats:
        TRI([(-rx * .25, -ry * .85), (rx * .15, -ry - dl), (rx * .7, -ry * .5)], fin, "left")
        if stage == 2:
            TRI([(-rx * .5, -ry * .75), (-rx * .3, -ry - dl * .8), (rx * .1, -ry * .8)], tone(a, 1.2), "left")
    # belly fins
    TRI([(rx * .15, ry * .75), (rx * .5, ry * .8), (rx * .45, ry + 4 + stage * 2)], finb)
    # body
    E(0, 0, rx, ry, m)
    E(-rx * .05, ry * .45, rx * .82, ry * .5, belly, flat=True)
    # scale pattern
    if "scales" in feats or stage >= 1:
        dark, lite = tone(m, .72), tone(m, 1.2)
        for row, v in enumerate((-.55, -.15, .25)):
            for j in range(5):
                lx = -rx * .1 + j * 4.2 * k + (row % 2) * 2
                if (lx / rx) ** 2 + v * v > .72:
                    continue
                X, Y = T(lx, v * ry)
                s.set(X, Y, dark)
                s.set(X + 1, Y + 1, dark)
    # spots / stripes (koi patches)
    if "spots" in feats or stage == 0:
        for (u, v, r_) in ((.0, -.45, 3.2), (.35, -.05, 2.4), (-.25, -.15, 2)):
            E(u * rx, v * ry, r_ * k + .5, r_ * k, a if stage else dt, flat=True)
    if "stripes" in feats:
        for u in (-.1, .2, .5):
            LN(u * rx, -ry * .8, u * rx + 1, -ry * .3, dt)
    # gill
    CV([(-rx * .4, -ry * .45), (-rx * .5, 0), (-rx * .42, ry * .45)], tone(m, .6))
    # pectoral fin
    TRI([(-rx * .15, ry * .3), (rx * .15 + stage * 1.5, ry * .4), (-rx * .05, ry * .65 + stage * 2)], tone(fin, .9), "left")
    # horns / mane (behind-eye region = top front of body)
    hxl = -rx * .55
    if stage >= 1 and ("mane" in feats or stage == 2):
        for i in range(3 if stage == 1 else 5):
            bx = hxl + 12 + i * 3.4
            TRI([(bx - 1.5, -ry * .88 + 1), (bx + 4 + stage, -ry * .88 - 3 - stage * 2 + i * .6), (bx + 2, -ry * .88 + 2)], a, "left")
    if stage == 2 or "horns" in feats or "antlers" in feats:
        hl = [0, 7, 12][stage]
        if hl:
            for ob in (0, 4):
                bx, by = hxl - 2 + ob, -ry * .8
                pts = [T(bx + hl * 1.3, by - hl * .35), T(bx + hl * .6, by - hl * .75), T(bx, by + 1)]
                s.tube(pts, [.8, 1.7, 2.8], HORN)
                if stage == 2 and ob == 0:
                    s.tube([T(bx + hl * .8, by - hl * .5), T(bx + hl * 1.0, by - hl * 1.0)], [.7, 1.3], HORN)
    # eye, mouth
    es = 3 if stage == 0 else 2
    iris = (50, 35, 60) if stage == 0 else (240, 190, 40) if stage == 2 else (200, 70, 40)
    X, Y = T(-rx * .68, -ry * .3)
    s.eye(X, Y, es, iris=iris)
    mx, my = T(-rx + .5, ry * .15)
    s.set(mx, my, tone(dt, .6))
    s.set(mx + 1, my + 1, tone(dt, .6))
    # whiskers
    if stage >= 1 and ("whiskers" in feats or stage == 2):
        wl = [0, 12, 16][stage]
        for sg, d in enumerate((5, 11)):
            CV([(-rx, ry * .2 + 1), (-rx - wl * .4, ry * .2 + d * .3), (-rx - wl * .75, ry * .2 + d), (-rx - wl, ry * .2 + d * .6 + sg * 4)],
               a if stage == 2 else WHITE)
    if "beard" in feats and stage == 2:
        TRI([(-rx * .85, ry * .5), (-rx * .55, ry * .6), (-rx * .75, ry * .5 + 9)], WHITE, "left")
    if "gem" in feats and stage >= 1:
        X, Y = T(-rx * .45, -ry * .75)
        s.ell(X, Y, 1.8, 1.6, a, gloss=True)
    if "crown" in feats and stage >= 1:
        for i in (-1, 0, 1):
            TRI([(hxl + 4 + i * 4 - 1.5, -ry * .85), (hxl + 4 + i * 4, -ry * .85 - 4), (hxl + 4 + i * 4 + 1.5, -ry * .85)], a)
    return s
