"""Korean treasure resource icons (D14). Standalone, Pillow only.
Same drawing defined in 30-unit space, rasterized at 30px and 60px (finer detail, not a resize).
Run: /tmp/claude-0/bl/bin/python -I tools/sprites/treasures.py [--sheet PATH]
"""
import math, os, sys
from PIL import Image

U = 30.0
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "items")


def hx(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


# ---- shape builders: return f(x,y)->bool in 30-space ----
def ell(cx, cy, rx, ry):
    return lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1
def ring(cx, cy, rx, ry, th):
    o = ell(cx, cy, rx, ry); i = ell(cx, cy, rx - th, ry - th)
    return lambda x, y: o(x, y) and not i(x, y)
def rect(x0, y0, x1, y1):
    return lambda x, y: x0 <= x <= x1 and y0 <= y <= y1
def poly(pts):
    def f(x, y):
        c = False; n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
        return c
    return f
def cap(x1, y1, x2, y2, r):
    def f(x, y):
        dx, dy = x2 - x1, y2 - y1; L = dx * dx + dy * dy
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / L)) if L else 0
        return (x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2 <= r * r
    return f
def union(*fs): return lambda x, y: any(f(x, y) for f in fs)
def sub(a, b): return lambda x, y: a(x, y) and not b(x, y)
def inter(a, b): return lambda x, y: a(x, y) and b(x, y)
def profile(pts, cx=15):
    ys = [p[0] for p in pts]
    def f(x, y):
        if y < ys[0] or y > ys[-1]: return False
        for (ya, wa), (yb, wb) in zip(pts, pts[1:]):
            if ya <= y <= yb:
                t = (y - ya) / (yb - ya) if yb > ya else 0
                return abs(x - cx) <= wa + (wb - wa) * t
        return False
    return f


class Canvas:
    def __init__(self, n):
        self.n = n; self.px = [[None] * n for _ in range(n)]
        self.sh = []
    def pts(self):
        n = self.n
        for j in range(n):
            for i in range(n):
                yield i, j, (i + .5) * U / n, (j + .5) * U / n
    def layer(self, fn, col, shade=None, tones=None):
        """shade: None flat; 'd' diagonal 3-tone; 'h' horizontal 3-tone. tones=(hi,lo) override."""
        cells = [(i, j, x, y) for i, j, x, y in self.pts() if fn(x, y)]
        if not cells: return
        xs = [c[2] for c in cells]; ys = [c[3] for c in cells]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        w = max(x1 - x0, .01); h = max(y1 - y0, .01)
        c = hx(col) if isinstance(col, str) else col
        hi, lo = tones if tones else (mix(c, (255, 255, 255), .38), mix(c, (20, 10, 40), .32))
        hi = hx(hi) if isinstance(hi, str) else hi; lo = hx(lo) if isinstance(lo, str) else lo
        for i, j, x, y in cells:
            col2 = c
            if shade:
                t = (x - x0) / w * (.75 if shade == 'd' else 1) + ((y - y0) / h * .25 if shade == 'd' else 0)
                col2 = hi if t < .27 else lo if t > .74 else c
            self.px[j][i] = col2
    def dot(self, cx, cy, col, r=.62):
        self.layer(ell(cx, cy, r, r), col)
    def outline(self, col):
        n = self.n; c = hx(col) if isinstance(col, str) else col
        new = []
        for j in range(n):
            for i in range(n):
                if self.px[j][i] is None:
                    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        a, b = i + di, j + dj
                        if 0 <= a < n and 0 <= b < n and self.px[b][a] is not None:
                            new.append((i, j)); break
        for i, j in new: self.px[j][i] = c
    def halo(self, col, rad, alpha):
        n = self.n; c = hx(col); out = {}
        for j in range(n):
            for i in range(n):
                if self.px[j][i] is None:
                    best = 99
                    for dj in range(-rad, rad + 1):
                        for di in range(-rad, rad + 1):
                            a, b = i + di, j + dj
                            if 0 <= a < n and 0 <= b < n and self.px[b][a] is not None:
                                best = min(best, math.hypot(di, dj))
                    if best <= rad + .2: out[(i, j)] = alpha * (1 - (best - 1) / (rad + 1))
        for (i, j), a in out.items(): self.px[j][i] = c + (int(a),)
    def image(self):
        im = Image.new("RGBA", (self.n, self.n), (0, 0, 0, 0))
        for j in range(self.n):
            for i in range(self.n):
                p = self.px[j][i]
                if p: im.putpixel((i, j), p + (255,) if len(p) == 3 else p)
        return im


# ---------------- items ----------------
def monster(c):  # norigae, crimson
    R, RD = "#D6322E", "#8E1B1E"
    G, GD = "#F0C040", "#B8861C"
    c.layer(ring(15, 3.6, 3.4, 2.9, 1.4), G, 'd')
    c.layer(rect(14.2, 6, 15.8, 8), RD)
    c.layer(union(ell(10.6, 10, 4.3, 2.8), ell(19.4, 10, 4.3, 2.8)), R, 'd')
    c.layer(ell(15, 10, 2, 2.3), "#B02228", 'd')
    c.dot(15, 10, "#F08070", .7)
    c.layer(ell(15, 15.6, 3.9, 3.9), G, 'd', (hx(G), hx(GD)))
    c.layer(ell(15, 15.6, 2.7, 2.7), "#2FA88A", 'd', ("#7FE0C0", "#157560"))
    c.layer(rect(14.2, 19, 15.8, 21), RD)
    c.layer(ell(15, 21.2, 2.4, 1.5), R, 'd')
    tas = poly([(12.4, 22), (17.6, 22), (21.2, 29.4), (8.8, 29.4)])
    c.layer(tas, R, 'd')
    # strands
    c.layer(lambda x, y: tas(x, y) and int((x - 15) * 2.2 + 50) % 2 == 0 and y > 24.5, "#EE5A48")
    c.layer(rect(12.4, 22.6, 17.6, 24.2), G, 'd', (hx(G), hx(GD)))


def super_(c):  # najeon box
    K, KH = "#2A2A38", "#55556E"
    G, GD = "#F0C040", "#B8861C"
    c.layer(poly([(6, 10), (9, 5.5), (21, 5.5), (24, 10)]), "#3C3C4E", 'd', (KH, "#2A2A38"))
    c.layer(rect(3.5, 10, 26.5, 15), K, 'd', ("#4A4A62", "#1E1E2A"))
    c.layer(rect(4.5, 15, 25.5, 25.2), K, 'd', ("#3E3E54", "#1E1E2A"))
    c.layer(rect(4, 25, 7.5, 27.4), "#1A1A24"); c.layer(rect(22.5, 25, 26, 27.4), "#1A1A24")
    c.layer(rect(3.5, 14.4, 26.5, 15.4), G, 'd', (hx(G), hx(GD)))
    c.layer(rect(13.2, 13.4, 16.8, 17.6), G, 'd', (hx(G), hx(GD)))
    c.dot(15, 16.4, "#6A4A10", .5)
    # mother-of-pearl flowers
    P = ["#FFD6EC", "#BFF3F0", "#E0D0FF", "#FFF4C8", "#C8E8FF"]
    def flower(cx, cy, r, k=0):
        for a in range(5):
            t = a * 2 * math.pi / 5 - math.pi / 2
            c.dot(cx + math.cos(t) * r, cy + math.sin(t) * r, P[(a + k) % 5], r * .62 + .05)
        c.dot(cx, cy, "#F0C040", r * .5)
    flower(9.5, 20.6, 1.5, 1); flower(20.5, 20.6, 1.5, 3); flower(15, 21.2, 2.0, 0)
    c.dot(6.8, 22.8, P[0], .55); c.dot(23.2, 22.8, P[1], .55)
    for x in (9, 12, 18, 21): c.dot(x, 12.3, P[(x // 3) % 5], .55)
    c.layer(rect(9.5, 6.8, 20.5, 7.5), "#6A6A88")


def hyper(c):  # bokjumeoni
    Y, YH, YD = "#F2B632", "#FFE07A", "#C07A12"
    body = ell(15, 18.8, 10.6, 8.6)
    neck = poly([(11.2, 9.5), (18.8, 9.5), (20, 13), (10, 13)])
    frill = union(ell(11.8, 7, 3.4, 3.2), ell(18.2, 7, 3.4, 3.2))
    c.layer(union(body, neck, frill), Y, 'd', (YH, YD))
    c.layer(cap(15, 4.2, 15, 9, .5), YD)
    c.layer(rect(10.6, 10.6, 19.4, 12.4), "#D6322E", 'd')
    c.layer(ell(15, 11.5, 2.1, 2.1), "#2F6FC0", 'd', ("#6FA8F0", "#1B3F80"))
    c.layer(cap(13.5, 12.8, 12.2, 16.6, .55), "#D6322E"); c.layer(cap(16.5, 12.8, 17.8, 16.6, .55), "#2F6FC0")
    c.layer(ring(15, 19.6, 5.6, 4.7, .9), "#D98A1F")
    for dx, dy in ((0, 0), (-2.6, 0), (2.6, 0), (0, -2.3), (0, 2.3)):
        c.dot(15 + dx, 19.6 + dy, "#D6322E", .7)
    for x, y in ((6.2, 19), (23.8, 19), (8, 24.4), (22, 24.4), (15, 26.6)): c.dot(x, y, "#D6322E", .6)


def heal(c):  # cheongja maebyeong
    B, BH, BD = "#6FA89A", "#A4D6C6", "#3F7E70"
    pts = [(2, 2.4), (3.4, 2.7), (3.9, 1.9), (6, 2.0), (7.5, 3.6), (9, 6.5), (11, 9), (13, 10.4),
           (16, 10.4), (19, 9.2), (22.5, 7.3), (25.5, 6.0), (27.6, 5.6), (28.6, 6.2)]
    pts = [(y, w) for y, w in pts]
    body = profile([(2, 2.3), (3.2, 2.5), (3.7, 1.7), (6, 1.9), (7.5, 3.6), (9, 6.4), (10.5, 8.8), (12.5, 10.1),
                    (16, 10.5), (19, 9.4), (22.5, 7.4), (25.5, 6.2), (27.6, 5.6), (28.6, 6.0)])
    c.layer(body, B, 'h', (BH, BD))
    c.layer(rect(10, 27.6, 20, 28.6), BD)
    W, K = "#FFFFFF", "#1E2A2E"
    # crane: swept wings, neck, black head dot
    c.layer(poly([(8.5, 18.8), (12, 13.2), (15, 15.6), (18.5, 13), (21, 18.6), (15, 19.6)]), W)
    c.layer(cap(18.8, 14.5, 20.6, 11.4, .6), W); c.dot(21, 10.8, K, .6)
    c.layer(cap(14, 19, 12, 22.6, .4), K); c.layer(cap(15.5, 19, 15.2, 22.8, .4), K)
    # clouds / dots
    for x, y in ((7.2, 14, ), (23.5, 15.5), (9.5, 22.5), (21, 22.5), (15, 7.8), (10.5, 10.5)): c.dot(x, y, W, .6)
    for x, y in ((6.6, 18.5), (23.8, 20), (13, 10.2), (17.5, 9.6), (15, 24.2)): c.dot(x, y, K, .45)
    c.layer(rect(10.2, 25.4, 19.8, 25.9), W)


def quick(c):  # baekja moon jar
    W, WH, WD = "#F4F1E6", "#FFFFFF", "#CFCBBC"
    jar = union(ell(15, 17.4, 11.8, 10.2), profile([(5.4, 5.6), (8.5, 6.3), (9, 8)]), profile([(24.5, 4.6), (27.8, 5.8)]))
    c.layer(jar, W, 'd', (WH, WD))
    c.layer(sub(ell(15, 5.6, 5.8, 1.5), ell(15, 5.9, 4.0, .75)), "#FFFFFF")
    c.layer(ell(15, 5.9, 4.0, .75), "#C8C4B4")
    c.layer(rect(10, 27.0, 20, 27.8), WD)
    c.layer(ell(9.6, 13, 1.4, 3), "#FFFFFF")  # highlight
    c.layer(inter(jar, lambda x, y: (x - 15) * .6 + (y - 17.4) * .8 > 7.2), "#D8D4C4")
    c.layer(inter(jar, lambda x, y: (x - 15) * .6 + (y - 17.4) * .8 > 9.4), "#BDB9A8")


def master(c):  # mapae
    Cu, CuH, CuD = "#B87333", "#E6A868", "#7A4A22"
    R = "#D02A2A"
    c.layer(ell(15, 17.6, 10.7, 10.7), Cu, 'd', (CuH, CuD))
    c.layer(ring(15, 17.6, 9.0, 9.0, .8), CuD)
    c.layer(ell(15, 17.6, 8.2, 8.2), "#C98445", 'd', ("#EDB67C", "#8A5528"))
    c.layer(ring(15, 3.9, 2.9, 2.5, 1.3), Cu, 'd', (CuH, CuD))
    c.layer(rect(13.6, 5.2, 16.4, 8.2), R, 'd', ("#F06060", "#8E1B1E"))
    c.layer(cap(14.4, 8, 12.8, 12.6, .5), R); c.layer(cap(15.6, 8, 17.2, 12.6, .5), R)
    H = "#4A2810"
    # horse: 3 body dots + legs
    c.layer(ell(14.2, 18.4, 3.7, 2.1), H); c.layer(ell(19.4, 15.2, 1.7, 2.5), H)
    c.layer(ell(20.8, 13.3, 1.5, 1.1), H); c.layer(cap(11.8, 19.5, 11.2, 23.5, .55), H)
    c.layer(cap(16.6, 19.8, 17.2, 23.5, .55), H); c.layer(cap(10.6, 17.5, 9.5, 20.5, .5), H)
    c.layer(cap(13.5, 20, 13.2, 23.2, .5), H); c.layer(cap(15.5, 20, 15.2, 23.3, .5), H)
    c.dot(20.6, 12.4, "#E0B070", .4)


ITEMS = [("monster", monster, "#2A0A0C"), ("super", super_, "#0C0C14"), ("hyper", hyper, "#6A3A0A"),
         ("heal", heal, "#1E4A42"), ("quick", quick, "#8C8A80"), ("master", master, "#3A1E08")]


def build(key, fn, oc, n):
    c = Canvas(n); fn(c); c.outline(oc)
    if key == "master": c.halo("#FFD84A", 1 if n == 30 else 3, 120)
    return c.image()


def main():
    os.makedirs(os.path.join(ROOT, "2x"), exist_ok=True)
    ims = {}
    for k, fn, oc in ITEMS:
        a, b = build(k, fn, oc, 30), build(k, fn, oc, 60)
        a.save(os.path.join(ROOT, k + ".png")); b.save(os.path.join(ROOT, "2x", k + ".png"))
        ims[k] = (a, b)
    if "--sheet" in sys.argv:
        out = sys.argv[sys.argv.index("--sheet") + 1]
        sheet(ims, out)


def sheet(ims, out):
    S = 4; cw = 125
    rows = [("30 cream", 30, "#FFF8EC", 1), ("60 cream", 60, "#FFF8EC", 1), ("30 white", 30, "#FFFFFF", 1),
            ("60 white", 60, "#FFFFFF", 1), ("16 cream", 16, "#FFF8EC", 1), ("16 white", 16, "#FFFFFF", 1),
            ("30 x3 view", 30, "#FFF8EC", 3), ("60 x2 view", 60, "#FFF8EC", 2)]
    hh = lambda sz, z: 130 if (sz == 60 and z == 2) else (100 if z == 3 else (70 if sz == 60 else 50))
    H = sum(hh(r[1], r[3]) for r in rows)
    im = Image.new("RGB", (cw * 6 + 10, H), (255, 255, 255)); y = 0
    for name, sz, bg, z in rows:
        h = hh(sz, z)
        im.paste(hx(bg), (0, y, im.width, y + h))
        for i, (k, _, _) in enumerate(ITEMS):
            a, b = ims[k]
            src = b if sz == 60 else a
            if sz == 16: src = a.resize((16, 16), Image.LANCZOS)
            if z >= 2: src = src.resize((sz * z if sz == 60 else 90,) * 2, Image.NEAREST)
            bgi = Image.new("RGBA", src.size, hx(bg) + (255,)); bgi.alpha_composite(src)
            im.paste(bgi.convert("RGB"), (i * cw + 5, y + 5))
        y += h
    im.save(out)


if __name__ == "__main__":
    main()
