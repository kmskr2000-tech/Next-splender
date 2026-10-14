"""critter archetype: rabbit / mouse / squirrel (small). stage 0..2. Faces left."""
import math
from core import Sprite, hx, tone


def _flame(s, x, y, a, sz):
    s.tri([(x - sz, y + sz * .6), (x + sz, y + sz * .6), (x + sz * .2, y - sz * 2.2)], a)
    s.tri([(x - sz * .5, y + sz * .6), (x + sz * .5, y + sz * .6), (x, y - sz * .8)], tone(a, 1.5))


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    k = [0.68, 0.86, 1.0][stage]
    gx, gy = 50, 80
    belly = tone(m, 1.3)
    ink = (50, 36, 46)
    nt = 1
    for f in feats:
        if f.startswith("multi_tail"):
            nt = int(f.split(":")[1]) if ":" in f else 2
    nt = max(1, min(nt, 5))

    if "aura" in feats:
        for i in range(20):
            ang = i / 20 * math.tau
            s.set(48 + math.cos(ang) * 40, 52 + math.sin(ang) * 38, tone(a, 1.3))
            s.set(48 + math.cos(ang + .15) * 43, 52 + math.sin(ang + .15) * 41, tone(a, 1.1))
    if "cloud" in feats:
        for x, r in ((-14, 5), (-4, 6), (8, 6.5), (18, 5)):
            s.ell(gx + x, gy + 1, r, 2.6, (232, 238, 250))
    if "wings" in feats:
        s.tri([(gx + 2 * k, gy - 22 * k), (gx + 24 * k, gy - 44 * k), (gx + 20 * k, gy - 16 * k)], a, "left")

    # tail(s): big fluffy curl behind
    bx, by = gx + 12 * k, gy - 10 * k
    for i in range(nt):
        f = (i - (nt - 1) / 2) / ((nt - 1) / 2) if nt > 1 else 0
        c = m if i % 2 == 0 else tone(m, .9)
        ang = math.radians(-78 + f * 28)
        L = 22 * k
        c_, s_ = math.cos(ang), math.sin(ang)
        pts = [(bx, by), (bx + c_ * L * .4 + 3 * k, by + s_ * L * .4), (bx + c_ * L * .75 + 4 * k, by + s_ * L * .75), (bx + c_ * L * .95 - 1 * k, by + s_ * L)]
        if nt == 1 and "long_ears" in feats:   # rabbit: short pom tail
            pts = [(bx, by + 2 * k), (bx + 4 * k, by), (bx + 6 * k, by - 3 * k), (bx + 6 * k, by - 5 * k)]
            s.tube(pts, [3 * k, 4 * k, 4 * k, 3.4 * k], belly)
            if "flame" in feats:
                _flame(s, pts[-1][0], pts[-1][1] - 4 * k, a, 3.2 * k)
            continue
        s.tube(pts, [2.6 * k, 5 * k, 6 * k, 4.2 * k], c)
        ex, ey = pts[-1]
        if "flame" in feats:
            _flame(s, ex, ey - 3 * k, a, 3.4 * k)
        else:
            s.ell(ex, ey - 1, 3 * k, 3 * k, belly)
    # hind foot + body
    s.ell(gx + 6 * k, gy - 11 * k, 12 * k, 11 * k, m)
    s.ell(gx + 1 * k, gy - 9 * k, 7 * k, 7.5 * k, belly)
    s.ell(gx + 10 * k, gy - 3 * k, 7 * k, 3.4 * k, tone(m, .92))
    s.ell(gx + 7 * k, gy - 1.8 * k, 4 * k, 1.8 * k, dt)
    for sx in (-3, 3):
        s.ell(gx + (sx - 4) * k, gy - 2.4 * k, 3.4 * k, 2.6 * k, tone(m, 1.05))
    if "spots" in feats:
        for x, y in ((10, -15), (14, -9), (6, -17)):
            s.ell(gx + x * k, gy + y * k, 1.6 * k + .3, 1.6 * k + .3, dt, flat=True)
    if "stripes" in feats:
        sc = dt if abs(sum(dt) - sum(m)) > 150 else tone(m, 1.6)
        for i in range(3):
            s.line(gx + (6 + i * 3.5) * k, gy - 21 * k, gx + (8 + i * 3.5) * k, gy - 15 * k, sc, 1 + (stage > 0))

    # head
    hr = [12.5, 12.5, 13][stage] * (k ** .5)
    hxc, hyc = gx - 7 * k, gy - 24 * k - (0 if stage else -1)
    # ears (behind head)
    long = "long_ears" in feats
    ey_ = hr * (2.0 if long else .95)
    for dx, dark in ((.0, True), (.78, False)):
        ex_, eyc = hxc + dx * hr, hyc - hr * .5 - ey_ * .78
        rot = .22 if dx > .5 else .02
        if long:
            rot = .38 if dx > .5 else .08
        s.ell(ex_, eyc, hr * (.36 if long else .42), ey_ * (.75 if long else .55), tone(m, .9) if dark else m, rot=rot)
        s.ell(ex_ + .5, eyc + 1, hr * (.18 if long else .24), ey_ * (.55 if long else .38), tone(a, 1.2) if sum(a) < 700 else a, rot=rot, flat=True)
    s.ell(hxc, hyc, hr, hr * .9, m)
    s.ell(hxc - hr * .5, hyc + hr * .36, hr * .5, hr * .36, belly)       # muzzle
    s.ell(hxc - hr * .86, hyc + hr * .2, 1.7, 1.4, ink, flat=True)       # nose
    s.line(hxc - hr * .5, hyc + hr * .5, hxc - hr * .25, hyc + hr * .56, tone(dt, .8))
    if stage > 0:
        s.set(hxc - hr * .6, hyc + hr * .62, (255, 255, 255)); s.set(hxc - hr * .6 + 1, hyc + hr * .62, (255, 255, 255))  # buck teeth
    es = 3 if stage == 0 else 2
    iris = (50, 35, 40) if stage == 0 else (160, 60, 60)
    s.eye(hxc - hr * .4, hyc - hr * .22, es, iris=iris)
    s.eye(hxc + hr * .35, hyc - hr * .22, es, iris=iris)
    s.ell(hxc - hr * .02, hyc + hr * .4, 1.8, 1.2, tone(a, 1.2), flat=True) if "cheek" in feats else None
    if "whiskers" in feats:
        for d in (-1, 1):
            s.line(hxc - hr * .9, hyc + hr * .4 + d, hxc - hr * .9 - 5, hyc + hr * .4 + d * 2, tone(dt, 1.6))
    if "beak" in feats:
        s.tri([(hxc - hr * .9, hyc + hr * .1), (hxc - hr * .9, hyc + hr * .5), (hxc - hr * 1.3, hyc + hr * .3)], a)
    if "crest" in feats:
        for i in range(3):
            s.tri([(hxc - 2 + i * 3, hyc - hr * .85), (hxc + i * 3, hyc - hr * .85), (hxc - 1 + i * 3, hyc - hr * 1.3)], a)
    if "horns" in feats:
        s.tri([(hxc - 2, hyc - hr * .75), (hxc + 2, hyc - hr * .75), (hxc, hyc - hr * 1.5)], a, "left")
    if "gem" in feats:
        s.ell(hxc, hyc - hr * .55, 1.9, 1.7, a, gloss=True)
    if "crown" in feats:
        cx, cy = hxc, hyc - hr * .8
        cc = (240, 200, 70)
        s.ell(cx, cy + 1, 5.5, 2, cc)
        for dx in (-4, 0, 4):
            s.tri([(cx + dx - 2, cy), (cx + dx + 2, cy), (cx + dx, cy - 5)], cc)
            s.set(cx + dx, cy - 5, (230, 70, 70))
        s.set(cx, cy + 1, (230, 70, 70))
    if "mane" in feats:
        for i in range(7):
            ang = math.pi * (0.8 + i / 6 * 1.0)
            s.ell(hxc + math.cos(ang) * hr * 1.0, hyc + 2 + math.sin(ang) * hr * .5 * -1 + hr * .5, 3, 3, tone(m, 1.15) if stage < 2 else a)
    if "leaf" in feats:
        s.ell(hxc + hr * .6, hyc - hr * .85, 3.5, 2, (90, 170, 90), rot=-.5)
    return s
