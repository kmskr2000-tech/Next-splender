"""serpent archetype: snake -> imugi -> eastern dragon. stage 0..2.
feats: horns antlers mane whiskers beard scales aura crown flame cloud gem fins(tail fin) claws(auto stage2)."""
import math

from core import Sprite, hx, tone

HORN = (246, 232, 196)
CLAW = (250, 244, 224)


def spline(c, n=8):
    pts = [c[0]] + list(c) + [c[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * (2 * p1[d] + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2
                                   + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3) for d in (0, 1)))
    out.append(tuple(c[-1]))
    return out


def curve(s, ctl, col, n=5):
    sp = spline(ctl, n)
    for (xa, ya), (xb, yb) in zip(sp, sp[1:]):
        s.line(xa, ya, xb, yb, col)


def draw(p, stage, feats):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    belly = tone(m, 1.3)
    ink = (34, 26, 36)
    if stage == 0:
        ctrl = [(32, 46), (38, 56), (52, 61), (60, 68), (52, 76), (38, 75), (42, 69), (56, 77), (68, 77), (76, 71)]
        r0, r1, hr = 4.4, 1.2, 9.5
    elif stage == 1:
        ctrl = [(24, 34), (30, 47), (48, 52), (66, 58), (65, 70), (48, 76), (34, 74), (28, 80), (40, 86), (62, 85), (78, 79), (86, 68)]
        r0, r1, hr = 5.2, 1.2, 11
    else:
        ctrl = [(20, 28), (22, 44), (40, 50), (60, 47), (76, 54), (75, 66), (58, 70), (40, 69), (27, 76), (30, 86), (50, 89), (72, 87), (88, 79), (91, 66)]
        r0, r1, hr = 5.8, 1.4, 12.5
    path = spline(ctrl, 7)
    n = len(path)

    def rad(i):
        t = i / (n - 1)
        return r1 + (r0 - r1) * (1 - t) ** .75

    def side(i):
        """unit normal at i, pointing to the back/upper-right side of the body"""
        x, y = path[i]
        x2, y2 = path[min(i + 1, n - 1)]
        nx, ny = -(y2 - y), (x2 - x)
        l = math.hypot(nx, ny) or 1
        nx, ny = nx / l, ny / l
        return (nx, ny) if (nx - ny) > 0 else (-nx, -ny)

    if "aura" in feats and stage:
        for i in range(18):
            ang = i / 18 * math.tau
            s.set(48 + math.cos(ang) * 45, 52 + math.sin(ang) * 40, tone(a, 1.3))
    if "cloud" in feats and stage == 2:
        for cx, cy in ((10, 84), (86, 92), (12, 56)):
            s.ell(cx, cy, 6, 3, (236, 240, 248), flat=True)
            s.ell(cx + 4, cy + 1, 4, 2.5, (214, 222, 238), flat=True)

    # tail tip ornament
    tx, ty = path[-1]
    px, py = path[-4]
    dx, dy = tx - px, ty - py
    ln = math.hypot(dx, dy) or 1
    dx, dy = dx / ln, dy / ln
    if stage:
        if "flame" in feats:
            s.ell(tx + dx * 4, ty + dy * 4 - 2, 3, 4.5, a, gloss=True)
        else:
            for sg in (-1, 1):
                s.tri([(tx, ty), (tx + dx * (4 + 3 * stage) - dy * sg * (3 + 2 * stage), ty + dy * (4 + 3 * stage) + dx * sg * (3 + 2 * stage)),
                       (tx + dx * 2, ty + dy * 2)], a if stage > 1 else tone(m, 1.1))

    for i in range(n - 1, -1, -1):
        x, y = path[i]
        s.ell(x, y, rad(i), rad(i), m)
    # belly bands, scale dots
    for i in range(4, n - 4):
        x, y = path[i]
        nx, ny = side(i)
        r = rad(i)
        if i % 4 == 0:
            s.line(x - nx * r * .3, y - ny * r * .3, x - nx * r * .75, y - ny * r * .75, belly)
        if ("scales" in feats or stage == 2) and i % 6 == 2:
            s.set(x + nx * r * .4, y + ny * r * .4, tone(m, .72))

    # dorsal spikes / mane
    if stage >= 1 and ("mane" in feats or stage == 2):
        cnt = 5 if stage == 1 else 12
        for i in range(2, 2 + cnt * 2, 2):
            x, y = path[i]
            nx, ny = side(i)
            r = rad(i)
            ml = (4 if stage == 1 else 6) * (1 - i / (n * 1.2)) + 2
            s.tri([(x + nx * r * .5 - ny * 2, y + ny * r * .5 + nx * 2), (x + nx * (r + ml) + 1, y + ny * (r + ml) - 1),
                   (x + nx * r * .5 + ny * 2, y + ny * r * .5 - nx * 2)], a, "left")

    # legs (dragon)
    if stage == 2:
        for idx, fx in ((int(n * .2), 1), (int(n * .5), -1)):
            x, y = path[idx]
            r = rad(idx)
            for lx, sh in ((-2.5, .8), (2.5, 1.0)):
                bx, by = x + lx, y + r * .7
                s.tube([(bx, by), (bx + lx * .3, by + 5)], [2.2, 1.8], tone(m, sh))
                s.ell(bx + lx * .3, by + 6, 2.6, 1.7, belly)
                for c in (-1, 1):
                    s.tri([(bx + lx * .3 + c * 2 - 1, by + 7), (bx + lx * .3 + c * 2 + 1, by + 7), (bx + lx * .3 + c * 2, by + 10)], CLAW)

    # head
    hx0, hy0 = path[0]
    hx0 -= 1
    # horns behind head
    if stage == 0:
        for ox in (.15, .6):
            s.tri([(hx0 + hr * ox - 1.5, hy0 - hr * .7), (hx0 + hr * ox + 1.5, hy0 - hr * .7), (hx0 + hr * ox + 3, hy0 - hr * .7 - 4)], HORN, "left")
    elif "horns" in feats or "antlers" in feats or stage == 2:
        hl = [0, 7, 11][stage]
        for ox in (.1, .55):
            bx, by = hx0 + hr * ox, hy0 - hr * .6
            s.tube([(bx + hl * .95, by - hl * .55), (bx + hl * .45, by - hl * .75), (bx, by)], [.7, 1.4, 2.2], HORN)
            if stage == 2 or "antlers" in feats:
                s.tube([(bx + hl * .6, by - hl * .7), (bx + hl * .3, by - hl * 1.3)], [.6, 1.1], HORN)
    s.ell(hx0, hy0, hr * 1.02, hr * .86, m)
    s.ell(hx0 - hr * .62, hy0 + hr * .3, hr * .6, hr * .44, belly)
    s.set(hx0 - hr * 1.0, hy0 + hr * .2, ink)
    if "beard" in feats and stage >= 1:
        bl = 6 if stage == 1 else 9
        s.tri([(hx0 - hr * .7, hy0 + hr * .7), (hx0 - hr * .2, hy0 + hr * .7), (hx0 - hr * .45, hy0 + hr * .7 + bl)], (240, 236, 224), "left")
    s.line(hx0 - hr * 1.0, hy0 + hr * .55, hx0 - hr * .3, hy0 + hr * .62, tone(dt, .7))
    ey = hy0 - hr * .2
    es = 3 if stage == 0 else 2
    iris = (50, 35, 60) if stage == 0 else (210, 70, 40) if stage == 1 else (240, 190, 40)
    s.eye(hx0 - hr * .45, ey, es, iris=iris)
    s.eye(hx0 + hr * .3, ey, es, iris=iris)
    if "whiskers" in feats or stage == 2:
        wl = [0, 14, 22][stage]
        for oy, dy in ((.38, 4), (.5, 10)):
            x0, y0 = hx0 - hr * .95, hy0 + hr * oy
            curve(s, [(x0, y0), (x0 - wl * .4, y0 - 2 + dy * .2), (x0 - wl * .75, y0 + dy * .6), (x0 - wl, y0 + dy)],
                  a if stage == 2 else (240, 236, 224))
    if "gem" in feats and stage >= 1:
        s.ell(hx0 + .5, hy0 - hr * .6, 1.8, 1.6, a, gloss=True)
    if "crown" in feats and stage >= 1:
        for i in (-1, 0, 1):
            s.tri([(hx0 + i * 4 - 1.5, hy0 - hr * .85), (hx0 + i * 4, hy0 - hr * .85 - 4), (hx0 + i * 4 + 1.5, hy0 - hr * .85)], a)
    return s
