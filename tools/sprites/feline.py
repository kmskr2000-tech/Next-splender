"""feline archetype: tiger / wildcat line. stage 0..2."""
import math

from core import Sprite, hx, tone


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    k = [0.62, 0.82, 1.0][stage]          # overall scale
    gx, gy = 48, 80                       # ground point
    belly = tone(m, 1.35)

    # tail (behind body)
    tail = [(gx + 16 * k, gy - 14 * k), (gx + 26 * k, gy - 18 * k), (gx + 30 * k, gy - 30 * k), (gx + 26 * k, gy - 40 * k)]
    s.tube(tail, [3.2 * k, 3 * k, 2.8 * k, 2.6 * k], m)
    if "stripes" in feats:
        for t in (1, 2):
            x, y = tail[t]
            s.line(x - 3 * k, y, x + 3 * k, y, dt, 1)
    if "gem" in feats or stage == 2:
        x, y = tail[2]
        s.ell(x, y, 3.4 * k, 1.6 * k, a, gloss=True)

    # back legs, body, front legs
    s.ell(gx + 12 * k, gy - 6 * k, 6 * k, 7 * k, tone(m, .9))
    s.ell(gx + 2 * k, gy - 14 * k, 18 * k, 11 * k, m)
    s.ell(gx - 2 * k, gy - 9 * k, 10 * k, 6 * k, belly)
    for lx in (-10, 4):
        s.ell(gx + lx * k, gy - 5 * k, 4 * k, 7 * k, m)
        s.ell(gx + lx * k, gy - 1 * k, 5 * k, 3 * k, belly)   # paws
    if "stripes" in feats:
        for i in range(4):
            x = gx - 2 * k + i * 6 * k
            s.line(x, gy - 24 * k, x + 2 * k, gy - 16 * k, dt, 1 + (stage > 0))

    # head
    hr = [12, 12.5, 13.5][stage] * k / [0.62, 0.82, 1.0][stage] * [0.62, 0.82, 1.0][stage]
    hr = [11.5, 11.5, 12.5][stage] * (k ** .55)
    hxc, hyc = gx - 16 * k, gy - 30 * k
    if "mane" in feats:
        for i in range(10):
            ang = math.pi * (0.62 + i / 9 * 1.76)
            s.ell(hxc + math.cos(ang) * hr * 1.05, hyc + math.sin(ang) * hr * 1.0, hr * .36, hr * .36, belly if stage < 2 else tone(m, 1.15))
    for ex in (-1, 1):  # ears
        s.tri([(hxc + ex * hr * .9, hyc - hr * .2), (hxc + ex * hr * .75, hyc - hr * 1.2), (hxc + ex * hr * .2, hyc - hr * .75)], m, "left")
        s.set(hxc + ex * hr * .62, hyc - hr * .8, tone(dt, 1.4))
    s.ell(hxc, hyc, hr, hr * .92, m)
    s.ell(hxc - hr * .05, hyc + hr * .42, hr * .55, hr * .38, belly)   # muzzle
    s.set(hxc - hr * .05, hyc + hr * .22, (70, 40, 50))                 # nose
    s.set(hxc - hr * .05 - 1, hyc + hr * .22, (70, 40, 50))
    ey = hyc - hr * .1
    es = 3 if stage == 0 else 2
    s.eye(hxc - hr * .55, ey, es, iris=(200, 130, 30) if stage else (50, 35, 40))
    s.eye(hxc + hr * .25, ey, es, iris=(200, 130, 30) if stage else (50, 35, 40))
    if "stripes" in feats:
        s.line(hxc - 1, hyc - hr * .85, hxc - 1, hyc - hr * .5, dt)
        s.line(hxc + 2, hyc - hr * .8, hxc + 2, hyc - hr * .55, dt)
        s.line(hxc - hr * .98, hyc + hr * .35, hxc - hr * .78, hyc + hr * .28, dt)
        s.line(hxc + hr * .78, hyc + hr * .28, hxc + hr * .98, hyc + hr * .35, dt)
    if "gem" in feats:
        s.ell(hxc - .5, hyc - hr * .62, 1.8, 1.6, a, gloss=True)
    if "aura" in feats:
        for i in range(16):
            ang = i / 16 * math.tau
            r = 40 + (i % 2) * 3
            s.set(48 + math.cos(ang) * r, 50 + math.sin(ang) * r * .9, tone(a, 1.3))
    return s
