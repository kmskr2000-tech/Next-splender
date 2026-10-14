"""hoofed archetype: deer / kirin / horse. stage 0..2. Faces left, side view."""
import math
from core import Sprite, hx, tone


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    k = [0.68, 0.86, 1.0][stage]
    gx, gy = 50, 80
    belly = tone(m, 1.3)
    ink = (50, 36, 46)
    hoof = dt

    if "aura" in feats:
        for i in range(20):
            ang = i / 20 * math.tau
            s.set(48 + math.cos(ang) * 41, 48 + math.sin(ang) * 38, tone(a, 1.3))
            s.set(48 + math.cos(ang + .15) * 44, 48 + math.sin(ang + .15) * 41, tone(a, 1.1))
    if "cloud" in feats:
        for x, r in ((-18, 5), (-8, 6.5), (4, 7), (16, 6), (26, 4.5)):
            s.ell(gx + x, gy + 1, r, 2.6, (232, 238, 250))

    # wings behind
    if "wings" in feats:
        s.tri([(gx - 2 * k, gy - 38 * k), (gx + 22 * k, gy - 62 * k), (gx + 20 * k, gy - 32 * k)], a, "left")

    # tail
    bcx, bcy = gx + 4 * k, gy - 28 * k
    s.tube([(bcx + 13 * k, bcy - 3 * k), (bcx + 19 * k, bcy + 1 * k), (bcx + 19 * k, bcy + 8 * k)],
           [2.2 * k, 3 * k, 2 * k], dt if "mane" in feats else tone(m, 1.1))

    # far legs (darker), body, near legs
    ll = 15 * k
    def leg(x, col, thick=2.4):
        s.tube([(x, bcy + 5 * k), (x + .5, gy - 6 * k), (x, gy - 3 * k)], [thick * k + .4, 1.9 * k + .3, 1.5 * k + .3], col)
        s.ell(x, gy - 1.4, 2.1 * k + .6, 1.9 * k + .3, hoof)
    leg(bcx + 7 * k, tone(m, .75), 2.4)
    leg(bcx - 6 * k, tone(m, .75), 2.4)
    s.ell(bcx, bcy, 16 * k, 9.5 * k, m)
    s.ell(bcx - 1 * k, bcy + 5 * k, 12 * k, 4.2 * k, belly)
    leg(bcx + 13 * k, m, 2.9)
    leg(bcx - 12 * k, m, 2.6)

    if "spots" in feats:
        for x, y in ((-6, -5), (0, -7), (6, -4), (10, -8), (-1, -1), (7, 1)):
            s.ell(bcx + x * k, bcy + y * k, 1.5 * k + .4, 1.4 * k + .4, tone(m, 1.55) if sum(m) < 600 else tone(a, 1.1), flat=True)

    # neck + head
    hr = [10.5, 9, 9.5][stage] * (k ** .4)
    nx0, ny0 = bcx - 11 * k, bcy - 3 * k
    hxc, hyc = gx - 17 * k, gy - 54 * k + (7 if stage == 0 else 0)
    s.tube([(nx0, ny0), ((nx0 + hxc) / 2 + 2, (ny0 + hyc) / 2 + 1), (hxc + 2, hyc + 3)], [5.6 * k, 4.2 * k + .5, 4.0 * k + .5], m)
    if "mane" in feats:
        for i in range(6):
            t = i / 5
            s.ell(nx0 + (hxc + 5 - nx0) * t + 4, ny0 + (hyc + 2 - ny0) * t - 1, 2.8 * k + .8, 2.8 * k + .8, a if stage == 2 else tone(dt, 1.3))
    # horns / antlers (behind head)
    ax, ay = hxc + hr * .3, hyc - hr * .7
    ac = tone(a, 1.0)
    if "antlers" in feats and stage > 0:
        n = 1 if stage == 1 else 2
        s.line(ax, ay, ax + 3, ay - 9 * k - 2, ac, 1)
        s.line(ax + 3, ay - 9 * k - 2, ax + 1, ay - 15 * k - 3, ac, 1)
        s.line(ax + 1.5, ay - 6 * k, ax + 7, ay - 9 * k - 2, ac, 1)
        if n == 2:
            s.line(ax + 3, ay - 12 * k, ax + 8, ay - 17 * k, ac, 1)
            s.line(ax + 2, ay - 10 * k, ax - 4, ay - 14 * k, ac, 1)
            s.line(ax + 7, ay - 9 * k - 2, ax + 11, ay - 10 * k, ac, 1)
    elif "antlers" in feats:
        s.line(ax, ay, ax + 1, ay - 4, ac); s.line(ax + 2, ay, ax + 3, ay - 4, ac)
    if "horns" in feats:
        s.tri([(hxc - 2, hyc - hr * .6), (hxc + 2, hyc - hr * .6), (hxc - 1, hyc - hr * 1.9)], a, "left")
    if "crest" in feats:
        for i in range(3):
            s.tri([(hxc + 2 + i * 3, hyc - hr * .8), (hxc + 5 + i * 3, hyc - hr * .7), (hxc + 5 + i * 3, hyc - hr * 1.2)], a)
    # ears
    ew = 1.5 if "long_ears" in feats else 1.0
    s.tri([(hxc + hr * .35, hyc - hr * .3), (hxc + hr * 1.5 * ew, hyc - hr * .9 * ew), (hxc + hr * .85, hyc + hr * .1)], tone(m, .9), "left")
    s.tri([(hxc + hr * .5, hyc - hr * .3), (hxc + hr * 1.25 * ew, hyc - hr * .7 * ew), (hxc + hr * .85, hyc)], tone(a, 1.1))
    s.ell(hxc, hyc, hr, hr * .9, m)
    # muzzle (long, toward left)
    mx, my = hxc - hr * .85, hyc + hr * .4
    s.ell(mx, my, hr * .72, hr * .5, belly)
    s.ell(mx - hr * .48, my - hr * .15, 1.8, 1.5, ink, flat=True)
    s.line(mx - hr * .2, my + hr * .38, mx + hr * .35, my + hr * .3, tone(dt, .8))
    es = 3 if stage == 0 else 2
    iris = (50, 35, 40) if stage == 0 else (200, 120, 40)
    s.eye(hxc - hr * .25, hyc - hr * .3, es, iris=iris)
    if "beard" in feats:
        s.tri([(mx - 2, my + hr * .45), (mx + 3, my + hr * .45), (mx, my + hr * .45 + 6)], a)
    if "whiskers" in feats:
        s.line(mx, my + 1, mx + 7, my + 3, tone(dt, 1.4))
    if "gem" in feats:
        s.ell(hxc - hr * .2, hyc - hr * .7, 1.8, 1.7, a, gloss=True)
    return s
