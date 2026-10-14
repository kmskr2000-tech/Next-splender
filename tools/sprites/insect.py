"""insect archetype: butterfly / firefly. stage 0..2. hovering, front-ish view."""
import math
from core import Sprite, hx, tone


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    k = [0.62, 0.85, 1.0][stage]
    cx, cy = 48, 44 + (2 - stage) * 4
    ink = (34, 26, 36)
    glow = tone(a, 1.35)
    wm = tone(m, 1.05)

    def wing(sx, ox, oy, rx, ry, rot, c, spot):
        x, y = cx + sx * ox * k, cy + oy * k
        r = rot * sx
        s.ell(x, y, rx * k + 1.5, ry * k + 1.5, dt, rot=r, flat=True)      # rim
        s.ell(x, y, rx * k, ry * k, c, rot=r)
        if spot:
            s.ell(x - sx * 1 * k + sx * 2, y - 1 * k, rx * k * .38, ry * k * .34, a, rot=r, gloss=True)
            s.ell(x - sx * 1 * k + sx * 2, y - 1 * k, rx * k * .16, ry * k * .14, dt, rot=r, flat=True)

    # hindwings (behind)
    for sx in (-1, 1):
        if stage == 2 or "wings" in feats and stage:
            s.tube([(cx + sx * 12 * k, cy + 14 * k), (cx + sx * 17 * k, cy + 24 * k), (cx + sx * 14 * k, cy + 33 * k)],
                   [3.2 * k, 2.6 * k, 1.4], tone(m, .8))
            s.ell(cx + sx * 14 * k, cy + 33 * k, 1.8, 1.8, a, gloss=True)
        wing(sx, 14, 12, 10, 7.5, .65, tone(m, .92), stage > 0)
    # forewings
    for sx in (-1, 1):
        wing(sx, 16, -9, 16, 9.5, -.55, wm, stage > 1 or "spots" in feats)
    # abdomen (firefly glow)
    s.ell(cx, cy + 14 * k, 5.2 * k, 13 * k, tone(dt, 1.0) if stage else tone(m, .95))
    s.ell(cx, cy + 20 * k, 4.8 * k, 7 * k, glow if True else a, gloss=True)
    for i in range(2):
        s.line(cx - 4 * k, cy + (6 + i * 4) * k, cx + 4 * k, cy + (6 + i * 4) * k, tone(dt, .7))
    # legs
    for sx in (-1, 1):
        for i in range(2):
            s.line(cx + sx * 3 * k, cy + (3 + i * 3) * k, cx + sx * (9 + i * 2) * k, cy + (8 + i * 5) * k, ink)
    # thorax
    s.ell(cx, cy, 6.5 * k, 7 * k, tone(dt, 1.2) if stage else m)
    s.ell(cx, cy - 1 * k, 4 * k, 3.5 * k, tone(dt, 1.5), flat=False)
    # head
    hr = [8.5, 9, 9.5][stage]
    hy = cy - 11 * k - hr * .3
    # antennae
    la = [8, 12, 17][stage]
    for sx in (-1, 1):
        s.tube([(cx + sx * 3, hy - hr * .7), (cx + sx * (la * .55), hy - hr * .7 - la * .8), (cx + sx * la, hy - hr * .7 - la * .8 - 3 + 2)],
               [.8, .8, 1.5 if stage else .8], ink if stage == 0 else tone(dt, .6))
        if stage:
            s.ell(cx + sx * la, hy - hr * .7 - la * .8 - 1, 2, 2, a, gloss=True)
    s.ell(cx, hy, hr, hr * .92, m)
    s.ell(cx, hy + hr * .5, hr * .55, hr * .3, tone(m, 1.3))
    es = 3 if stage == 0 else 2
    s.eye(cx - hr * .62 - (0 if es == 2 else 1), hy - hr * .1, es, iris=(50, 40, 60) if stage < 2 else (200, 90, 40))
    s.eye(cx + hr * .62 - es + 1, hy - hr * .1, es, iris=(50, 40, 60) if stage < 2 else (200, 90, 40))
    s.ell(cx - hr * .8, hy + hr * .35, 2, 1.3, tone((230, 120, 120), 1.0), flat=True)
    s.ell(cx + hr * .8, hy + hr * .35, 2, 1.3, tone((230, 120, 120), 1.0), flat=True)
    s.line(cx - 1, hy + hr * .5, cx + 1, hy + hr * .5, ink)
    if "crown" in feats and stage > 1:
        for i in range(3):
            s.tri([(cx - 5 + i * 4, hy - hr + 1), (cx - 3 + i * 4, hy - hr - 4), (cx - 1 + i * 4, hy - hr + 1)], tone(a, 1.2))
    if "gem" in feats and stage > 0:
        s.ell(cx, hy - hr * .55, 1.8, 1.6, (110, 200, 240), gloss=True)
    # glow sparkles
    if "aura" in feats or "flame" in feats:
        n = [6, 10, 18][stage]
        for i in range(n):
            ang = i / n * math.tau + .4
            r = (22 + (i % 3) * 5) * (.7 + .3 * k) + 8
            x, y = cx + math.cos(ang) * r, cy + 6 + math.sin(ang) * r * .85
            s.set(x, y, tone(a, 1.4)); s.set(x + 1, y, tone(a, 1.4)); s.set(x, y + 1, tone(a, 1.4))
    return s
