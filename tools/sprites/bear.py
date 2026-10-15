"""bear archetype: bear / panda / badger. stage 0..2. Front 3/4 view, chubby."""
import math
from core import Sprite, hx, tone


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    k = [0.66, 0.84, 1.0][stage]
    gx, gy = 48, 81
    belly = tone(m, 1.3)
    ink = (50, 36, 46)
    pad = dt

    if "aura" in feats:
        for i in range(20):
            ang = i / 20 * math.tau
            s.set(48 + math.cos(ang) * 42, 50 + math.sin(ang) * 40, tone(a, 1.3))
            s.set(48 + math.cos(ang + .15) * 45, 50 + math.sin(ang + .15) * 43, tone(a, 1.1))
    if "cloud" in feats:
        for x, r in ((-20, 5), (-9, 6.5), (3, 7), (15, 6.5), (25, 4.5)):
            s.ell(gx + x, gy + 1, r, 2.6, (232, 238, 250))
    if "wings" in feats:
        s.tri([(gx - 6 * k, gy - 30 * k), (gx - 34 * k, gy - 52 * k), (gx - 20 * k, gy - 22 * k)], a, "left")
        s.tri([(gx + 6 * k, gy - 30 * k), (gx + 34 * k, gy - 52 * k), (gx + 20 * k, gy - 22 * k)], a)

    # stub tail + feet behind
    s.ell(gx + 14 * k, gy - 12 * k, 3.5 * k, 3.5 * k, belly)
    # body
    bcy = gy - 17 * k
    s.ell(gx, bcy, 20 * k, 17 * k, m)
    s.ell(gx, bcy + 3 * k, 12 * k, 12 * k, belly)
    if "shell" in feats:
        for i, (x, y) in enumerate(((-12, -6), (12, -6), (-14, 5), (14, 5))):
            s.ell(gx + x * k, bcy + y * k, 3.5 * k + .5, 3 * k + .5, a)
    sc = dt if abs(sum(dt) - sum(m)) > 150 else tone(m, 1.6)
    if "stripes" in feats:
        for x in (-13, 13):
            for j in range(3):
                yy = bcy + (-6 + j * 5) * k
                s.line(gx + x * k - 3 * k, yy, gx + x * k + 3 * k, yy + 2 * k, sc, 1 + (stage > 0))
    if "spots" in feats:
        for x, y in ((-9, 4), (9, 6), (0, 9), (-4, -2)):
            s.ell(gx + x * k, bcy + y * k, 1.6 * k + .4, 1.5 * k + .4, dt, flat=True)
    # legs / feet
    for sx in (-1, 1):
        s.ell(gx + sx * 12 * k, gy - 4.5 * k, 7 * k, 5.2 * k, m)
        s.ell(gx + sx * 12 * k, gy - 2 * k, 4.2 * k + .5, 2.4 * k + .5, pad)
        s.set(gx + sx * 12 * k - 2, gy - 2 * k - 2, tone(pad, 1.8))
    # arms
    for sx in (-1, 1):
        s.ell(gx + sx * 19 * k, bcy + 3 * k, 5 * k, 9 * k, tone(m, .95), rot=sx * .25)
        s.ell(gx + sx * 20 * k, bcy + 10 * k, 4.3 * k, 3.2 * k, pad)
    # mane / shoulder fur
    hr = [14, 14, 14.5][stage] * (k ** .55)
    hxc, hyc = gx, gy - 38 * k + (3 if stage == 0 else 0)
    if "mane" in feats:
        for i in range(16):
            ang = i / 16 * math.tau
            s.ell(hxc + math.cos(ang) * hr * 1.0, hyc + math.sin(ang) * hr * .9 + 1,
                  hr * .3 + 1, hr * .3 + 1, tone(m, 1.15) if stage < 2 else a)
    # horns
    if "horns" in feats:
        for sx in (-1, 1):
            s.tri([(hxc + sx * hr * .45, hyc - hr * .7), (hxc + sx * hr * .8, hyc - hr * .55), (hxc + sx * hr * .8, hyc - hr * 1.5)], a, "left" if sx < 0 else None)
    # ears
    for sx in (-1, 1):
        s.ell(hxc + sx * hr * .78, hyc - hr * .68, hr * .3, hr * .3, tone(m, .95))
        s.ell(hxc + sx * hr * .78, hyc - hr * .66, hr * .16 + .3, hr * .16 + .3, dt if sum(m) > 400 else a, flat=True)
    # head
    s.ell(hxc, hyc + hr * .35, hr * .9, hr * .7, tone(m, .6))
    s.ell(hxc, hyc, hr, hr * .84, m)
    s.ell(hxc, hyc + hr * .34, hr * .52, hr * .36, belly)     # muzzle
    s.ell(hxc, hyc + hr * .2, 2, 1.5, ink, flat=True)          # nose
    s.line(hxc, hyc + hr * .3, hxc, hyc + hr * .5, tone(dt, .8))
    s.line(hxc - 3, hyc + hr * .52, hxc + 3, hyc + hr * .52, tone(dt, .8))
    ey = hyc - hr * .22
    es = 3 if stage == 0 else 2
    iris = (50, 35, 40) if stage == 0 else (160, 90, 40)
    s.eye(hxc - hr * .6, ey, es, iris=iris)
    s.eye(hxc + hr * .35, ey, es, iris=iris)
    if "crest" in feats:
        s.ell(hxc, hyc - hr * .72, 2.2, 3, a, flat=False)
        s.tri([(hxc - 3, hyc - hr * .6), (hxc + 3, hyc - hr * .6), (hxc, hyc - hr * 1.1 - 3)], a)
    if "gem" in feats:
        s.ell(hxc - .5, hyc - hr * .5, 1.9, 1.7, a, gloss=True)
    if "beard" in feats:
        s.tri([(hxc - 4, hyc + hr * .6), (hxc + 4, hyc + hr * .6), (hxc, hyc + hr * .6 + 6)], a)
    if "whiskers" in feats:
        for sx in (-1, 1):
            s.line(hxc + sx * hr * .55, hyc + hr * .35, hxc + sx * (hr * .55 + 6), hyc + hr * .3, tone(dt, 1.4))
    if "flame" in feats:
        fx, fy = gx - 24 * k, bcy - 4 * k
        s.tri([(fx - 3, fy + 4), (fx + 3, fy + 4), (fx, fy - 10)], a)
        s.tri([(fx - 1.5, fy + 4), (fx + 1.5, fy + 4), (fx, fy - 4)], tone(a, 1.5))
    if "leaf" in feats:
        s.ell(hxc + hr * .5, hyc - hr * .95, 3.5, 2, (90, 170, 90), rot=-.5)
    return s
