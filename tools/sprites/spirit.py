"""spirit archetype: dokkaebi / mountain spirit. stage 0..2. front view."""
import math
from core import Sprite, hx, tone


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    k = [0.66, 0.84, 1.0][stage]
    gx, gy = 44, 80
    belly = tone(m, 1.3)
    skin = m
    hair = dt
    fire = tone(a, 1.25)
    ink = (34, 26, 36)

    # club (behind) on the right, big end up
    cx0 = gx + 20 * k
    s.tube([(cx0 - 2 * k, gy - 6 * k), (cx0, gy - 28 * k), (cx0 + 1 * k, gy - 44 * k)], [2.2 * k, 3 * k, 6 * k], tone(a, .8) if stage < 2 else a)
    for i in range(5 if stage else 3):
        ang = i * 1.3
        s.set(cx0 + 1 * k + math.cos(ang) * 4.2 * k, gy - 43 * k + math.sin(ang) * 4.5 * k, tone(a, 1.5))
        if stage:
            s.set(cx0 + 1 * k + math.cos(ang) * 4.2 * k + 1, gy - 43 * k + math.sin(ang) * 4.5 * k, ink)
    if "flame" in feats or stage == 2:
        fx, fy = cx0 + 1 * k, gy - 44 * k - 8 * k - 1
        s.ell(fx, fy + 1, 2.8 * k + 1, 3.6 * k + 1, tone((90, 160, 230), 1.0))
        s.ell(fx, fy + 2, 1.4, 2.4, (200, 235, 255), flat=True)
        s.tri([(fx - 2, fy - 1), (fx, fy - 6), (fx + 2, fy - 1)], tone((90, 160, 230), 1.0))

    # legs & feet
    for lx in (-6, 6):
        s.ell(gx + lx * k, gy - 6 * k, 5 * k, 7 * k, tone(skin, .9))
        s.ell(gx + lx * k + (lx / 6), gy - 2, 5.5 * k, 3 * k, skin)
    # body
    s.ell(gx, gy - 20 * k, 15 * k, 14 * k, skin)
    s.ell(gx - 1 * k, gy - 18 * k, 8 * k, 9 * k, belly)
    # loincloth with tiger stripes
    s.ell(gx, gy - 12 * k, 14 * k, 5.5 * k, a)
    if "stripes" in feats or stage > 0:
        for i in range(-3, 4):
            s.line(gx + i * 4 * k, gy - 16 * k, gx + i * 4 * k + 1, gy - 9 * k, dt if stage else tone(a, .6))
    # arms
    s.tube([(gx - 14 * k, gy - 28 * k), (gx - 19 * k, gy - 20 * k), (gx - 17 * k, gy - 13 * k)], [3.6 * k, 3.2 * k, 3.4 * k], skin)
    s.tube([(gx + 14 * k, gy - 28 * k), (gx + 19 * k, gy - 24 * k), (cx0 - 1, gy - 20 * k)], [3.6 * k, 3.2 * k, 3.6 * k], skin)
    s.ell(cx0 - 1, gy - 19 * k, 3.6 * k, 3.4 * k, tone(skin, 1.1))
    # head
    hr = [13, 13.5, 14][stage]
    hxc, hyc = gx, gy - 38 * k - hr * .55
    # ears
    for e in (-1, 1):
        s.tri([(hxc + e * hr * .85, hyc - 1), (hxc + e * (hr + 6), hyc - hr * .35), (hxc + e * hr * .8, hyc + hr * .45)], skin, "left")
    # horns
    nh = 1 if stage == 0 else 2
    for i in range(nh):
        e = 0 if nh == 1 else (-1 if i == 0 else 1)
        hh = [5, 8, 13][stage]
        x0 = hxc + e * hr * .5
        y0 = hyc - hr * .85
        if "horns" in feats or stage < 2 or True:
            s.tube([(x0, y0 + 2), (x0 + e * hh * .35, y0 - hh * .6), (x0 + e * hh * .15 + e * (stage), y0 - hh)], [2.8 + stage * .6, 2 + stage * .4, .9], tone(a, 1.25) if stage else tone(a, 1.1))
    s.ell(hxc, hyc, hr, hr * .92, skin)
    # hair tuft (shaggy)
    for dx, ry in ((-.5, .3), (.5, .3), (0, .4)):
        s.ell(hxc + dx * hr * .8, hyc - hr * .72, hr * .38, hr * ry, hair)
    s.ell(hxc, hyc - hr * .66, hr * .6, hr * .26, hair)
    if "mane" in feats or stage == 2:
        for e in (-1, 1):
            s.ell(hxc + e * hr * .92, hyc + hr * .2, hr * .22, hr * .5, hair)
    if "leaf" in feats:
        lx, ly = hxc - 6, hyc - hr * .95
        s.ell(lx, ly, 3.5, 1.6, (96, 170, 80), rot=-.6)
    if "crown" in feats and stage > 1:
        for i in range(4):
            s.tri([(hxc - 8 + i * 4.5, hyc - hr * .8), (hxc - 6 + i * 4.5, hyc - hr * .8 - 5), (hxc - 4 + i * 4.5, hyc - hr * .8)], tone(a, 1.3))
    # face
    es = 3 if stage == 0 else 2
    s.eye(hxc - hr * .55 - 1, hyc - hr * .05, es, iris=(60, 35, 30) if stage < 2 else (190, 70, 40))
    s.eye(hxc + hr * .55 - es + 1, hyc - hr * .05, es, iris=(60, 35, 30) if stage < 2 else (190, 70, 40))
    s.ell(hxc - hr * .72, hyc + hr * .3, 2.2, 1.4, tone((230, 120, 120), 1.0), flat=True)
    s.ell(hxc + hr * .72, hyc + hr * .3, 2.2, 1.4, tone((230, 120, 120), 1.0), flat=True)
    # mouth + tusks
    my = hyc + hr * .5
    s.line(hxc - 3, my, hxc + 3, my, ink)
    s.set(hxc - 3, my - 1, ink); s.set(hxc + 3, my - 1, ink)
    if stage > 0 or "beak" in feats:
        s.tri([(hxc - 4, my), (hxc - 3, my + 4), (hxc - 2, my)], (250, 248, 235))
        s.tri([(hxc + 2, my), (hxc + 3, my + 4), (hxc + 4, my)], (250, 248, 235))
    if "beard" in feats or stage == 2:
        bc = (tone(dt, 1.7) if sum(m) > 650 else (240, 238, 232)) if stage == 2 else hair
        bh = [3, 5, 9][stage]
        for i, dx in enumerate((-.5, 0, .5)):
            s.ell(hxc + dx * hr * .8, my + 3 + bh * .5 + (i == 1) * 2, hr * .3, bh * .8, bc)
    if "gem" in feats and stage > 0:
        s.ell(hxc, hyc - hr * .45, 1.8, 1.8, (110, 200, 240), gloss=True)
    if "aura" in feats and stage > 0:
        for i in range(18):
            ang = i / 18 * math.tau
            r = 40 + (i % 2) * 3
            s.set(48 + math.cos(ang) * r, 46 + math.sin(ang) * r * .92, tone(a, 1.3))
    return s
