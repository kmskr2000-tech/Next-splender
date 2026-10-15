"""turtle archetype: turtle -> great turtle -> Xuanwu (turtle entwined by a serpent). stage 0..2.
feats: shell leaf horns crest gem aura cloud flame spots stripes multi_tail:N (extra snake tails, stage 2) whiskers fins(ignored)."""
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


def snake(s, ctl, r0, r1, col, belly, a, dt, flame=False, eye_col=(240, 190, 40), n=6):
    """serpent tail from root (ctl[0]) to head (ctl[-1], faces left/toward ctl dir)."""
    path = spline(ctl, n)
    N = len(path)
    for i in range(N):               # root first, head last (head on top)
        x, y = path[i]
        r = r0 + (r1 - r0) * i / (N - 1)
        s.ell(x, y, r, r, col)
        if i % 4 == 2:
            s.set(x - 1, y + 1, belly)
            s.set(x, y + 2, belly)
    hxx, hyy = path[-1]
    hr = r1 + 3.2
    s.ell(hxx - 1, hyy, hr * 1.2, hr, col)
    s.ell(hxx - hr * 1.0, hyy + hr * .3, hr * .7, hr * .5, belly)
    s.eye(hxx - 1, hyy - hr * .55, 1, iris=eye_col)
    s.set(hxx - hr * 1.7, hyy + hr * .35, (210, 60, 70))   # tongue tip
    s.set(hxx - hr * 1.7 - 1, hyy + hr * .35, (210, 60, 70))
    # head crest
    s.tri([(hxx, hyy - hr * .8), (hxx + hr * .9, hyy - hr * 1.7), (hxx + hr * 1.1, hyy - hr * .6)], a, "left")
    return path


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    k = [.62, .82, 1.0][stage]
    gx, gy = 46, 80
    belly = tone(m, 1.35)
    skin = tone(dt, 1.5) if sum(dt) < 330 else tone(m, 1.05)   # skin tone from detail/main
    skin = tone(m, 1.1)
    shell_c = tone(dt, 1.0)
    # shell colour: detail tone if mid-dark, otherwise main darkened
    shell_c = dt if sum(dt) > 260 else tone(m, .8)

    snakes = 0
    if stage == 2:
        snakes = 1
        for f in feats:
            if f.startswith("multi_tail"):
                try:
                    snakes = max(1, min(3, int(f.split(":")[1])))
                except Exception:
                    pass

    if "aura" in feats and stage:
        for i in range(18):
            ang = i / 18 * math.tau
            s.set(48 + math.cos(ang) * 45, 50 + math.sin(ang) * 42, tone(a, 1.3))

    # snake behind shell
    snake_front = []
    if snakes:
        sc = tone(a, .9) if sum(a) < 600 else tone(a, .8)
        sc = tone(dt, 1.3) if False else tone(m, .95)
        for q in range(snakes):
            dy = q * 6
            ctl = [(gx + 22 * k, gy - 9 * k), (gx + 33 * k + q * 2, gy - 10 * k - dy * .3), (gx + 40 * k + q * 3, gy - 24 * k - dy),
                   (gx + 36 * k, gy - 40 * k - dy), (gx + 24 * k, gy - 48 * k - dy), (gx + 12 * k, gy - 46 * k - dy)]
            snake(s, ctl, 3.6, 2.9, tone(m, .95 - q * .06), belly, a, dt, flame="flame" in feats)

    # legs behind
    s.ell(gx + 15 * k, gy - 4 * k, 6 * k, 4.5 * k, tone(skin, .8))
    s.ell(gx - 12 * k, gy - 4 * k, 6 * k, 4.5 * k, tone(skin, .8))
    # tail stub
    if stage < 2:
        s.tri([(gx + 22 * k, gy - 10 * k), (gx + 30 * k + stage * 2, gy - 6 * k), (gx + 21 * k, gy - 6 * k)], skin, "left")
    # plastron/rim
    s.ell(gx + 1 * k, gy - 9 * k, 24 * k, 8 * k, tone(belly, 1.0))
    # front legs
    s.ell(gx + 8 * k, gy - 4 * k, 6.5 * k, 5 * k, skin)
    s.ell(gx - 18 * k, gy - 4 * k, 6.5 * k, 5 * k, skin)
    for lx in (gx + 8 * k, gx - 18 * k):
        for c in (-1, 1):
            s.set(lx + c * 2.5 * k, gy - .5, WHITE)

    # neck + head (left)
    hr = [8.5, 8.5, 9.5][stage] * (k ** .4)
    hx0, hy0 = gx - 29 * k - 3, gy - 20 * k - stage * 2
    s.tube([(gx - 20 * k, gy - 14 * k), (hx0 + 3, hy0 + 3)], [5.5 * k + 1, 4.5 * k + 1], skin)
    if "horns" in feats or stage == 2:
        hl = [0, 4, 7][stage]
        if hl:
            for ob in (1, 5):
                s.tube([(hx0 + ob + hl, hy0 - hr * .7 - hl * .8), (hx0 + ob + hl * .4, hy0 - hr * .8 - hl * .5), (hx0 + ob, hy0 - hr * .5)], [.7, 1.3, 2], HORN)
    s.ell(hx0, hy0, hr, hr * .9, skin)
    s.ell(hx0 - hr * .45, hy0 + hr * .35, hr * .55, hr * .4, tone(skin, 1.3))
    s.set(hx0 - hr * .85, hy0 + hr * .2, (60, 40, 50))
    s.line(hx0 - hr * .9, hy0 + hr * .55, hx0 - hr * .25, hy0 + hr * .62, tone(dt, .6))
    es = 3 if stage == 0 else 2
    iris = (50, 35, 60) if stage == 0 else (240, 190, 40) if stage == 2 else (200, 70, 40)
    s.eye(hx0 - hr * .3, hy0 - hr * .35, es, iris=iris)
    if "crest" in feats or stage == 2:
        for i in range(2 + stage):
            s.tri([(hx0 + hr * .2 + i * 3, hy0 - hr * .75), (hx0 + hr * .9 + i * 3 + 1, hy0 - hr * 1.5 - i * .5), (hx0 + hr * .6 + i * 3 + 3, hy0 - hr * .5)], a, "left")
    # shell
    cx, cy = gx + 1 * k, gy - 22 * k
    rx, ry = 25 * k, 19 * k
    if stage == 2:                      # spiky rim
        for i in range(7):
            ang = math.pi * (1.05 + i / 6 * .9)
            X, Y = cx + math.cos(ang) * rx * .98, cy + math.sin(ang) * ry * .98
            s.tri([(X - 2.5, Y + 2), (X + math.cos(ang) * 4 + 0, Y + math.sin(ang) * 6), (X + 2.5, Y + 2)], tone(a, .95))
    s.ell(cx, cy, rx, ry, shell_c)
    # hex pattern
    line_c = tone(shell_c, 1.5) if sum(shell_c) < 300 else tone(shell_c, .6)
    def inside(x, y, f=.93):
        return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < f
    hexr = 7 * k + 1
    pts = [(cx + math.cos(math.pi / 3 * i + math.pi / 6) * hexr * 1.15, cy - 2 * k + math.sin(math.pi / 3 * i + math.pi / 6) * hexr * .9) for i in range(6)]
    for i in range(6):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 6]
        s.line(x0, y0, x1, y1, line_c)
        ex_, ey_ = x0 + (x0 - cx) * 1.1, y0 + (y0 - cy + 2 * k) * 1.1
        # radial line stops at the rim
        for t in range(1, 30):
            X, Y = x0 + (x0 - cx) * t / 18, y0 + (y0 - cy + 2 * k) * t / 18
            if not inside(X, Y, .8):
                break
            s.set(X, Y, line_c)
    if "spots" in feats or "gem" in feats and stage:
        s.ell(cx, cy - 2 * k, 3 * k + .5, 2.5 * k + .5, a, gloss=True)
    # rim highlight
    # sprout
    if "leaf" in feats:
        lc = (90, 190, 90)
        s.line(cx, cy - ry + 2, cx, cy - ry - 3, tone(lc, .7))
        s.tri([(cx, cy - ry - 2), (cx - 7, cy - ry - 5), (cx - 2, cy - ry + 1)], lc, "left")
        s.tri([(cx, cy - ry - 2), (cx + 7, cy - ry - 6), (cx + 2, cy - ry + 1)], tone(lc, 1.1), "left")
    # snake wrapping across the shell front
    if snakes:
        sc = tone(m, .95)
        wp = spline([(gx + 30 * k, gy - 36 * k), (gx + 16 * k, gy - 30 * k), (gx + 6 * k, gy - 18 * k), (gx - 2 * k, gy - 8 * k)], 6)
        for i, (X, Y) in enumerate(wp):
            r_ = 3.4 - 1.0 * i / len(wp)
            s.ell(X, Y, r_, r_, sc)
            if i % 5 == 2:
                s.set(X, Y + 2, belly)

    if "cloud" in feats and stage == 2:
        for qx in (22, 58, 82):
            s.ell(qx, 86, 7, 3, (236, 240, 248), flat=True)
            s.ell(qx + 5, 87, 5, 2.5, (214, 222, 238), flat=True)
    return s
