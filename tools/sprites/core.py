"""Pixel sprite core: 96x96 canvas at 1px scale, sphere-shaded parts quantized to
3 tones, selective outline. Matches the reference sprite size/feel without copying.
"""
import colorsys
import math

from PIL import Image

G = 96
LIGHT = (-0.55, -0.65, 0.52)
_ln = math.sqrt(sum(v * v for v in LIGHT))
LIGHT = tuple(v / _ln for v in LIGHT)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def tone(c, f):
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in c])
    if f < 1 and l > .78:
        # light fur/feathers: shade toward cool lilac grey instead of khaki
        t = 1 - f
        target = (122, 118, 150)
        return tuple(round(cv + (tv - cv) * t * 1.15) for cv, tv in zip(c, target))
    if f < 1:
        l, s = l * f, min(1, s * 1.1)
    else:
        l = l + (1 - l) * (f - 1)
    return tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, max(0, min(1, l)), s))


def ramp(c):
    """dark, mid, light, highlight"""
    return [tone(c, .62), c, tone(c, 1.22), tone(c, 1.5)]


class Sprite:
    def __init__(self):
        self.px = [[None] * G for _ in range(G)]

    def set(self, x, y, col):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < G and 0 <= y < G and col is not None:
            self.px[y][x] = col

    def get(self, x, y):
        if 0 <= x < G and 0 <= y < G:
            return self.px[y][x]
        return None

    # ---- shaded primitives -------------------------------------------------
    def ell(self, cx, cy, rx, ry, col, rot=0.0, flat=False, gloss=False):
        r = ramp(col)
        ca, sa = math.cos(rot), math.sin(rot)
        R = int(max(rx, ry)) + 2
        for y in range(int(cy - R), int(cy + R) + 1):
            for x in range(int(cx - R), int(cx + R) + 1):
                dx, dy = x + .5 - cx, y + .5 - cy
                u = (dx * ca + dy * sa) / rx
                v = (-dx * sa + dy * ca) / ry
                d = u * u + v * v
                if d > 1:
                    continue
                if flat:
                    self.set(x, y, col)
                    continue
                nz = math.sqrt(1 - d)
                nx, ny = u * ca - v * sa, u * sa + v * ca
                i = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
                k = 0 if i < .25 else 1 if i < .62 else 2 if i < .9 or not gloss else 3
                self.set(x, y, r[k])

    def tri(self, pts, col, shade_dir=None):
        r = ramp(col)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        (x1, y1), (x2, y2), (x3, y3) = pts
        den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if den == 0:
            return
        for y in range(int(min(ys)), int(max(ys)) + 1):
            for x in range(int(min(xs)), int(max(xs)) + 1):
                px, py = x + .5, y + .5
                a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / den
                b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / den
                c = 1 - a - b
                if min(a, b, c) < 0:
                    continue
                k = 1
                if shade_dir == "left":
                    k = 2 if a > .5 else 1 if b + a > .4 else 0
                self.set(x, y, r[k])

    def line(self, x0, y0, x1, y1, col, w=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            t = i / max(n, 1)
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for ox in range(w):
                for oy in range(w):
                    self.set(x + ox - w // 2, y + oy - w // 2, col)

    def tube(self, pts, radii, col):
        """Chain of shaded circles along a polyline (tails, serpents, necks)."""
        seg = []
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            n = max(2, int(math.hypot(x1 - x0, y1 - y0)))
            for j in range(n):
                t = j / n
                seg.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, radii[i] + (radii[i + 1] - radii[i]) * t))
        seg.append((*pts[-1], radii[-1]))
        for x, y, rr in reversed(seg):
            self.ell(x, y, max(rr, .7), max(rr, .7), col)

    def eye(self, x, y, size=2, iris=(42, 30, 40), shine=True):
        x, y = int(round(x)), int(round(y))
        ink = (34, 26, 36)
        for dy in range(-1, size + 2):          # dark rim
            for dx in range(-1, size + 1):
                self.set(x + dx, y + dy, ink)
        for dy in range(size + 1):
            for dx in range(size):
                self.set(x + dx, y + dy, iris)
        self.set(x + size - 1, y + size, ink)   # pupil
        if shine:
            self.set(x, y, (255, 255, 255))

    # ---- finish ------------------------------------------------------------
    def render(self, scale=1):
        out = Image.new("RGBA", (G, G), (0, 0, 0, 0))
        o = out.load()
        for y in range(G):
            for x in range(G):
                c = self.px[y][x]
                if c:
                    o[x, y] = c + (255,)
        # selective outline: darkest tone of neighbour, or ink for light parts
        src = [row[:] for row in self.px]
        for y in range(G):
            for x in range(G):
                if src[y][x] is None:
                    nb = [src[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                          if 0 <= x + dx < G and 0 <= y + dy < G and src[y + dy][x + dx]]
                    if nb:
                        c = nb[0]
                        o[x, y] = (tone(c, .32) if sum(c) < 600 else (64, 58, 70)) + (255,)
        return out.resize((G * scale, G * scale), Image.NEAREST) if scale > 1 else out
