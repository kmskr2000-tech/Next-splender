"""bird archetype: magpie / crane -> phoenix (zhuque). stage 0..2. faces left."""
import math
from core import Sprite, hx, tone


def _nf(feats, key, d=0):
    for f in feats:
        if f.startswith(key + ":"):
            try:
                return int(f.split(":")[1])
            except ValueError:
                return d
    return d


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    k = [0.66, 0.86, 1.0][stage]
    gx, gy = [50, 49, 40][stage], 80
    belly = tone(m, 1.3)
    flame = "flame" in feats or stage == 2
    hov = 0 if stage < 2 else 0

    # tail feathers (behind): fan from rump, droop with stage
    n = max(_nf(feats, "multi_tail"), 0)
    nt = [3, 3, 5][stage] if not n else min(max(n, 3), 7 if stage == 2 else 4)
    L = [19, 27, 38][stage] * k
    bx, by = gx + 12 * k, gy - 26 * k
    cols = [dt, a, m, a, dt, a, m]
    order = sorted(range(nt), key=lambda i: -abs(i - (nt - 1) / 2))
    for i in order:
        t = i - (nt - 1) / 2
        ang = (.3 if stage == 2 else .2) + t * (.26 if stage == 2 else .3)
        ln = L * (1 - abs(t) * .08)
        x1, y1 = bx + math.cos(ang * .4) * ln * .55, by + math.sin(ang * .4) * ln * .55
        x2, y2 = bx + math.cos(ang) * ln, by + math.sin(ang) * ln
        c = cols[i % 7] if stage > 0 else (dt if i % 2 == 0 else a)
        s.tube([(bx, by), (x1, y1), (x2, y2)], [3.2 * k, 3.1 * k, 1.5], c)
        if flame and stage == 2:
            s.ell(x2 + 1, y2 + 1, 1.8, 3.2, tone(a, 1.25), gloss=True)
        elif stage == 2:
            s.ell(x2, y2, 1.8, 2.4, tone(a, 1.3), gloss=True)
    # legs
    for lx in (-3, 6):
        s.line(gx + lx * k, gy - 9 * k, gx + lx * k, gy - 1, a, 2 if stage else 1)
        s.line(gx + lx * k - 3, gy, gx + lx * k + 2, gy, a, 1)
        s.line(gx + lx * k - 3, gy - 1, gx + lx * k - 1, gy - 1, a, 1)
    # body
    cx, cy = gx + 2 * k, gy - 22 * k
    s.ell(cx, cy, 17 * k, 14.5 * k, m)
    s.ell(cx - 6 * k, cy + 4 * k, 9 * k, 8 * k, belly)
    # wing
    if "wings" in feats and stage > 0:
        s.ell(cx + 6 * k, cy - 13 * k, 5 * k, 11 * k, tone(dt, .9), rot=-.35)
        s.ell(cx + 11 * k, cy - 12 * k, 3.5 * k, 8 * k, a, rot=-.35)
    wc = dt if stage else m
    for i in range(3):   # feather tips
        s.tri([(cx + (6 + i * 3) * k, cy + (3 + i * 1.5) * k), (cx + (17 + i * 2.5) * k, cy + (7 + i * 2.5) * k), (cx + (11 + i * 3) * k, cy + (8 + i * 1.5) * k)], a if i % 2 == 0 else wc)
    s.ell(cx + 5 * k, cy - 1 * k, 10 * k, 7 * k, wc, rot=.35)
    s.ell(cx + 5 * k, cy - 3 * k, 6 * k, 2.4 * k, tone(wc, 1.35), rot=.35)
    if "spots" in feats or "stripes" in feats:
        for i in range(3):
            s.set(cx + (2 + i * 4) * k, cy - 3 * k + i * k, tone(m, 1.4))
            s.set(cx + (2 + i * 4) * k + 1, cy - 3 * k + i * k, tone(m, 1.4))
    # head
    hr = [10.5, 11, 11.5][stage]
    hxc, hyc = gx - 12 * k, gy - 40 * k
    if stage == 2:
        hyc -= 2
    # crest
    if "crest" in feats or stage == 2:
        nc = [2, 3, 5][stage]
        for i in range(nc):
            ang = -math.pi / 2 + (i - (nc - 1) / 2) * .38 + .35
            ln = (6 + 4 * (i % 2) + stage * 5) * (1 if k > .7 else .8)
            x0, y0 = hxc + math.cos(ang) * hr * .6, hyc + math.sin(ang) * hr * .6
            col = a if i % 2 == 0 else tone(a, 1.25)
            s.tube([(x0, y0), (x0 + math.cos(ang) * ln * .6 + 1, y0 + math.sin(ang) * ln * .6),
                    (x0 + math.cos(ang) * ln + 3, y0 + math.sin(ang) * ln + 1)], [2.2, 1.9, .9], col)
    s.ell(hxc, hyc, hr, hr * .94, m)
    s.ell(hxc - 2, hyc + hr * .45, hr * .62, hr * .38, belly)
    if "crown" in feats and not ("crest" in feats or stage == 2):
        for i in range(3):
            s.tri([(hxc - 5 + i * 4, hyc - hr + 1), (hxc - 3 + i * 4, hyc - hr - 4), (hxc - 1 + i * 4, hyc - hr + 1)], tone(a, 1.2))
    # beak
    bk = hr * .8
    s.tri([(hxc - hr * .7, hyc + 1), (hxc - hr * .7 - bk * .8, hyc + hr * .3 + 1), (hxc - hr * .55, hyc + hr * .62)], a)
    s.line(hxc - hr * .7 - 2, hyc + hr * .3 + 1, hxc - hr * .6, hyc + hr * .3 + 1, tone(a, .6))
    # eye
    es = 3 if stage == 0 else 2
    s.eye(hxc - hr * .38, hyc - hr * .3, es, iris=(60, 40, 40) if stage == 0 else (190, 60, 40))
    # cheek
    s.ell(hxc + 1, hyc + hr * .32, 2.2, 1.4, tone(a, 1.3), flat=True)
    if "gem" in feats:
        s.ell(hxc + 1, hyc - hr * .72, 1.8, 1.6, tone(dt, 1.4), gloss=True)
    if "aura" in feats and stage > 0:
        for i in range(18):
            ang = i / 18 * math.tau
            r = 40 + (i % 2) * 3
            s.set(48 + math.cos(ang) * r, 48 + math.sin(ang) * r * .92, tone(a, 1.3))
    if flame:
        for fx, fy in ((hxc - 4, hyc - hr - 9 - stage * 3), (cx - 8 * k, cy - 14 * k - 2)) if stage == 2 else ():
            s.ell(fx, fy, 2, 3, tone(a, 1.2), gloss=True)
    return s
