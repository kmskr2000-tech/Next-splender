"""canine archetype: fox / dog / haetae / wolf. stage 0..2. Faces left, 3/4 side."""
import math
from core import Sprite, hx, tone


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    k = [0.66, 0.85, 1.0][stage]
    gx, gy = 48, 80
    belly = tone(m, 1.3)
    nt = 1
    for f in feats:
        if f.startswith("multi_tail"):
            nt = int(f.split(":")[1]) if ":" in f else 3
    nt = max(1, min(nt, 9))
    ink = (50, 36, 46)

    # aura behind
    if "aura" in feats:
        for i in range(20):
            ang = i / 20 * math.tau
            s.set(48 + math.cos(ang) * 41, 50 + math.sin(ang) * 37, tone(a, 1.3))
            s.set(48 + math.cos(ang + .15) * 44, 50 + math.sin(ang + .15) * 40, tone(a, 1.1))

    # tails (behind body): fan of bushy tails
    bx, by = gx + 13 * k, gy - 17 * k
    for i in range(nt):
        f = (i - (nt - 1) / 2) / ((nt - 1) / 2) if nt > 1 else 0
        spread = 62 if nt > 3 else 40
        ang = math.radians(-62 + f * spread)
        L = (27 - abs(f) * 4) * k if nt > 1 else 24 * k
        c, sn = math.cos(ang), math.sin(ang)
        px_, py_ = -sn, c
        bend = (4 + 2 * f) * k if nt > 1 else 5 * k
        pts = [(bx, by), (bx + c * L * .35 + px_ * bend * .5, by + sn * L * .35 + py_ * bend * .5),
               (bx + c * L * .7 + px_ * bend, by + sn * L * .7 + py_ * bend),
               (bx + c * L + px_ * bend * .6, by + sn * L + py_ * bend * .6)]
        w = 1.0 if nt < 4 else .7
        col = m if (i % 2 == 0 or nt == 1) else tone(m, .9)
        s.tube(pts, [2.4 * k, 5.4 * k * w + .4, 5.0 * k * w + .4, 2.4 * k], col)
        ex, ey = pts[-1]
        if "flame" in feats:
            fw = 2.6 * k * (w + .2)
            s.ell(ex, ey, fw, fw, tone(a, .9))
            s.tri([(ex - fw, ey - fw * .3), (ex + fw, ey - fw * .3), (ex + fw * .2, ey - fw * 2.6)], a)
            s.tri([(ex - fw * .5, ey - fw * .3), (ex + fw * .5, ey - fw * .3), (ex, ey - fw * 1.5)], tone(a, 1.5))
        else:
            s.ell(ex, ey, 2.6 * k * (w + .3), 2.6 * k * (w + .3), belly)

    # back leg + body + front legs
    s.ell(gx + 10 * k, gy - 7 * k, 7 * k, 7.5 * k, tone(m, .92))
    s.ell(gx + 9 * k, gy - 1.5 * k, 5 * k, 2.4 * k, dt)
    s.ell(gx + 3 * k, gy - 15 * k, 15 * k, 10.5 * k, m)
    s.ell(gx - 1 * k, gy - 10 * k, 11 * k, 5.5 * k, belly)
    for lx in (-9, 2):
        s.ell(gx + lx * k, gy - 6 * k, 3.4 * k, 6.5 * k, m if lx > 0 else tone(m, 1.05))
        s.ell(gx + lx * k - .5, gy - 1.6 * k, 4.2 * k, 2.4 * k, dt)
    if "stripes" in feats:
        for i in range(3):
            x = gx + 2 * k + i * 6 * k
            s.line(x, gy - 24 * k, x + 1 * k, gy - 18 * k, dt, 1 + (stage > 0))
    if "spots" in feats:
        for x, y in ((6, -19), (12, -14), (0, -21)):
            s.ell(gx + x * k, gy + y * k, 1.5 * k + .5, 1.5 * k + .5, dt, flat=True)

    # mane / ruff on chest
    hr = [13, 12.5, 13][stage] * (k ** .5) * [1.0, 1.0, 1.0][stage]
    hx_, hy_ = gx - 15 * k, gy - 29 * k
    if "mane" in feats:
        for i in range(9):
            ang = math.pi * (0.55 + i / 8 * 1.3)
            s.ell(hx_ + 3 + math.cos(ang) * hr * 1.0, hy_ + 2 + math.sin(ang) * hr * .95,
                  hr * .34, hr * .34, a if stage == 2 else belly)

    # ears (tall, pointed)
    eh = hr * (1.45 if "long_ears" not in feats else 1.8)
    for ex, dx in ((-.45, 0), (.45, 1)):
        bxe = hx_ + ex * hr
        s.tri([(bxe - hr * .38, hy_ - hr * .55), (bxe + (ex * hr * .35), hy_ - eh), (bxe + hr * .42, hy_ - hr * .45)],
              m if dx else tone(m, .9), "left")
        s.tri([(bxe - hr * .12, hy_ - hr * .6), (bxe + ex * hr * .2, hy_ - eh * .86 + 1), (bxe + hr * .22, hy_ - hr * .55)], dt)

    # head + snout
    s.ell(hx_, hy_, hr, hr * .88, m)
    # cheek fluff
    s.tri([(hx_ + hr * .5, hy_ + hr * .3), (hx_ + hr * 1.05, hy_ + hr * .55), (hx_ + hr * .4, hy_ + hr * .85)], belly)
    sx, sy = hx_ - hr * .8, hy_ + hr * .3
    s.ell(sx, sy, hr * .62, hr * .38, belly)
    s.ell(sx - hr * .42, sy - hr * .05, 2, 1.7, ink, flat=True)       # nose
    s.set(sx - hr * .42 - .5, sy - hr * .35, (255, 255, 255))
    s.line(sx - hr * .25, sy + hr * .3, sx + hr * .3, sy + hr * .3, tone(dt, .8))   # mouth
    ey = hy_ - hr * .22
    es = 3 if stage == 0 else 2
    iris = (50, 35, 40) if stage == 0 else (210, 140, 30)
    s.eye(hx_ - hr * .4, ey, es, iris=iris)
    s.eye(hx_ + hr * .35, ey, es, iris=iris)
    if "beard" in feats:
        s.tri([(sx - 2, sy + hr * .3), (sx + 3, sy + hr * .3), (sx, sy + hr * .3 + 6 * k)], a)
    if "whiskers" in feats:
        for d in (-1, 1):
            s.line(sx + 2, sy + d * 2 + 1, sx + 9, sy + d * 4 + 1, tone(dt, 1.4))
    if "horns" in feats:
        s.tri([(hx_ - 2, hy_ - hr * .8), (hx_ + 2, hy_ - hr * .8), (hx_, hy_ - hr * 1.75)], a, "left")
    if "crest" in feats:
        for i in range(3):
            s.tri([(hx_ + 2 + i * 3, hy_ - hr * .9), (hx_ + 5 + i * 3, hy_ - hr * .8), (hx_ + 5 + i * 3, hy_ - hr * 1.3)], a)
    if "gem" in feats:
        s.ell(hx_ - 1, hy_ - hr * .55, 1.9, 1.7, a, gloss=True)
    if "wings" in feats:
        s.tri([(gx + 4 * k, gy - 22 * k), (gx + 20 * k, gy - 44 * k), (gx + 14 * k, gy - 20 * k)], a, "left")
    if "cloud" in feats:
        for x in (-14, 0, 14):
            s.ell(gx + x * k, gy + 1, 5, 2, (235, 238, 248), flat=True)
    return s
