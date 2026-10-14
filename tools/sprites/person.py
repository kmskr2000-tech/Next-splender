"""person archetype: Korean folk/history humans. draw(p, stage, spec) -> Sprite.
spec: body child|youth|adult|elder, sex m|f, headwear, outfit, props[<=2], beard
"""
import math
from core import Sprite, hx, tone, ramp

SKIN = (246, 203, 166)
BLUSH = (238, 128, 122)
INK = (34, 26, 36)
HAIR = (40, 32, 46)
WHITEHAIR = (230, 228, 234)
CREAM = (248, 240, 222)
STEEL = (200, 208, 220)
WOOD = (150, 98, 58)
GOLD = (236, 190, 70)

BODY = {  # hr, leg, torso, sw
    "child": (13.0, 11, 12, 7.2),
    "youth": (12.2, 15, 16, 8.6),
    "adult": (11.8, 17, 18, 9.6),
    "elder": (11.8, 14, 17, 9.2),
}
SKIRT = ("hanbok_f", "celestial", "shaman")
ROBE = ("royal", "official", "scholar", "monk")


def blend(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def poly(s, pts, col, flat=False):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = min(xs), max(xs)
    r = ramp(col)
    n = len(pts)
    for y in range(int(min(ys)), int(max(ys)) + 1):
        yy = y + .5
        cr = []
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            if (ay <= yy < by) or (by <= yy < ay):
                cr.append(ax + (yy - ay) * (bx - ax) / (by - ay))
        cr.sort()
        for j in range(0, len(cr) - 1, 2):
            for x in range(int(round(cr[j])), int(round(cr[j + 1]))):
                t = (x + .5 - x0) / max(1e-6, x1 - x0)
                k = 1 if flat else (2 if t < .2 else 0 if t > .8 else 1)
                s.set(x, y, r[k])


def overlay_clip(s, fn, ymax=None, ymin=None):
    t = Sprite()
    fn(t)
    for y in range(96):
        if ymax is not None and y >= ymax:
            continue
        if ymin is not None and y < ymin:
            continue
        for x in range(96):
            if t.px[y][x]:
                s.px[y][x] = t.px[y][x]


def scales(s, x0, x1, y0, y1, col):
    for r, y in enumerate(range(int(y0), int(y1), 3)):
        off = 2 if r % 2 else 0
        for x in range(int(x0) + off, int(x1), 4):
            if s.get(x, y) is not None:
                s.set(x, y, tone(col, 1.35))
            for dx in (0, 1, 2):
                if s.get(x + dx, y + 2) is not None:
                    s.set(x + dx, y + 2, tone(col, .55))
            if s.get(x + 3, y + 1) is not None:
                s.set(x + 3, y + 1, tone(col, .62))


def draw(p, stage, spec):
    s = Sprite()
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    body = spec.get("body", "adult")
    sex = spec.get("sex", "m")
    hw = spec.get("headwear", "none")
    of = spec.get("outfit", "hanbok")
    props = list(spec.get("props", []))[:2]
    beard = spec.get("beard", False)
    elder = body == "elder"
    k = [0.86, 0.93, 1.0][stage]
    hr0, leg0, tor0, sw0 = BODY[body]
    hr = hr0 * k ** .5
    leg, tor, sw = leg0 * k, tor0 * k, sw0 * k * (0.93 if sex == "f" else 1.04)
    u = hr / 12.0
    cx = 48
    lift = 5 if of == "celestial" else 0
    gy = 82 - lift
    hip = gy - leg
    sh = hip - tor
    cy = sh - hr * 0.80
    hair = WHITEHAIR if elder else HAIR
    kind = "hanbok_f" if (of == "hanbok" and sex == "f") else of
    skirt = kind in SKIRT
    robe = of in ROBE
    ytop = cy - hr

    # ---------------- back layer ----------------
    if stage == 2:   # halo: soft ring + sparkles
        for i in range(120):
            ang = i / 120 * math.tau
            hc = (255, 238, 170) if i % 3 else tone(a, 1.3)
            s.set(cx + math.cos(ang) * (hr + 10), cy - 2 + math.sin(ang) * (hr + 10), hc)
    if of == "armor" and stage >= 1:   # cape
        poly(s, [(cx - sw, sh + 2), (cx + sw, sh + 2), (cx + sw + 9 + stage * 3, gy - 8), (cx - sw - 9 - stage * 3, gy - 8)], tone(dt, 1.0) if sum(dt) > 150 else dt)
    if of == "celestial":
        for side in (-1, 1):
            for n_, (ph, col) in enumerate(((0, tone(a, 1.15)), (1, tone(m, 1.2)))):
                if n_ and stage == 0:
                    continue
                pts = []
                for q in range(9):
                    tt = q / 8
                    pts.append((cx + side * (sw + 1 + tt * (20 + 3 * stage)), sh + 5 + 5 * n_ + math.sin(tt * 4.5 + ph * 1.5) * 4 - tt * 2))
                s.tube(pts, [3.2, 3.0, 2.8, 2.5, 2.2, 2.0, 1.6, 1.2, .9], col)
        # cloud
        for dx, w in ((-10, 7), (0, 10), (10, 7), (-4, 8), (6, 8)):
            s.ell(cx + dx, gy + 1.5, w, 3.2, (236, 244, 252), gloss=False)

    # ---------------- lower garment & feet ----------------
    shoe = {"hanbok": CREAM, "shaman": CREAM, "celestial": CREAM, "monk": (200, 196, 190),
            "peasant": (206, 172, 104), "armor": (70, 60, 74)}.get(of, (44, 36, 52))
    cuff = a
    if skirt:
        hy0 = sh + tor * (0.36 if kind == "hanbok_f" else 0.40)
        hw_b = sw * (1.7 if of != "celestial" else 1.8)
        hem = gy - 3
        skc = m if kind != "shaman" else m
        pts = [(cx - sw * .7, hy0), (cx + sw * .7, hy0), (cx + hw_b, hem), (cx + hw_b * .5, hem + 1.3), (cx, hem + 1.7), (cx - hw_b * .5, hem + 1.3), (cx - hw_b, hem)]
        poly(s, pts, skc)
        for fx in (-.45, 0, .45):
            s.line(cx + fx * hw_b * .55, hy0 + 4, cx + fx * hw_b * .95, hem - 1, tone(skc, .78))
        if stage >= 1:
            s.line(cx - hw_b + 1, hem - 1, cx + hw_b - 1, hem - 1, a)
    elif robe:
        hem = gy - 3
        hw_b = sw * (1.35 if of != "monk" else 1.3)
        pts = [(cx - sw * .92, sh + 3), (cx + sw * .92, sh + 3), (cx + hw_b, hem), (cx + hw_b * .5, hem + 1.2), (cx, hem + 1.5), (cx - hw_b * .5, hem + 1.2), (cx - hw_b, hem)]
        base = {"royal": m, "official": m, "scholar": m, "monk": m}[of]
        poly(s, pts, base)
        if stage >= 1 and of != "monk":
            s.line(cx - hw_b + 1, hem - 1, cx + hw_b - 1, hem - 1, a)
        if of == "scholar":
            s.line(cx + 2, sh + 12, cx + hw_b - 3, hem - 1, tone(m, .8))   # overlapping panel
        else:
            s.line(cx, sh + 14, cx, hem - 1, tone(m, .8))
    else:  # pants
        pc = blend(m, CREAM, .5) if of == "hanbok" else (tone(blend(m, (190, 170, 130), .5), 1.05) if of == "peasant" else dt)
        if of == "armor":
            pc = tone(dt, 1.1)
        plen = 1.0 if of != "peasant" else .72
        for lx in (-1, 1):
            xx = cx + lx * sw * .48
            y0 = hip - 2
            y1 = gy - 3 if of != "peasant" else hip + leg * .62
            s.ell(xx, (y0 + y1) / 2, sw * .52, (y1 - y0) / 2 + 1, pc)
            if of == "peasant":
                s.ell(xx, gy - 4, sw * .26, 3.4, SKIN)
            else:
                s.ell(xx, y1 - 1, sw * .36, 1.5, dt, flat=True)  # daenim band
        if of == "armor":   # tasset
            poly(s, [(cx - sw * .9, hip - 5), (cx + sw * .9, hip - 5), (cx + sw * 1.2, hip + leg * .5), (cx - sw * 1.2, hip + leg * .5)], m)
            scales(s, cx - sw * 1.2, cx + sw * 1.2, hip - 5, hip + leg * .5, m)
            s.line(cx - sw * 1.2, hip + leg * .5, cx + sw * 1.2, hip + leg * .5, a)
    for lx in (-1, 1):
        fx = cx + lx * (sw * .5 if not skirt else sw * .55)
        sh_h = 2.0 if of in ("royal", "official", "scholar", "armor") else 1.7
        s.ell(fx + lx * .5, gy - 1.6, 3.6 * k ** .5, sh_h + .4, shoe)
        if of in ("hanbok", "shaman", "celestial", "monk"):
            s.tri([(fx + lx * 2.5, gy - 2), (fx + lx * 5.2, gy - 4.5), (fx + lx * 4, gy - 1)], shoe)
        if of == "armor":
            s.set(fx, gy - 4, a)

    # ---------------- torso garment ----------------
    # base torso shape
    shoulder = lambda col: s.ell(cx, sh + 3.5, sw + .5, 4.6, col)
    torc = m
    if kind == "hanbok_f" or kind == "shaman":
        torc = a if kind == "hanbok_f" else CREAM
    elif of == "hanbok":
        torc = m
    elif of == "peasant":
        torc = tone(blend(m, (210, 190, 150), .45), 1.0)
    elif of == "celestial":
        torc = blend(a, CREAM, .35)
    elif of == "armor":
        torc = tone(m, 1.0)
    lo = sh + tor * (0.50 if skirt else 1.0)
    if skirt:
        lo = sh + tor * .44
    elif of == "hanbok":
        lo = hip + 2
    elif of == "armor":
        lo = hip - 3
    elif of == "peasant":
        lo = hip - 1
    else:
        lo = hip - 1
    if not robe:
        shoulder(torc)
        poly(s, [(cx - sw, sh + 4), (cx + sw, sh + 4), (cx + sw * .88, lo), (cx - sw * .88, lo)], torc)
        if kind == "hanbok_f" or kind == "shaman" or of == "celestial":
            pass
    else:
        shoulder(m)

    cyl = sh + tor * .45   # chest line
    # collar & details
    if kind in ("hanbok_f", "shaman", "celestial") or of == "hanbok":
        # white dongjeong V
        for dx in (-1, 1):
            s.line(cx + dx * 4.2, sh + 1, cx + dx * -.5 + (1 if dx > 0 else 0), sh + 9, CREAM, 1)
        s.line(cx - 4, sh + 1, cx + 1, sh + 9, CREAM)
        if of == "hanbok" and sex == "m" or of == "peasant":
            s.line(cx - sw * .88, lo - 3, cx + sw * .88, lo - 3, dt, 2)   # sash
        else:
            # goreum ribbons
            gyy = sh + 8
            s.line(cx + 1, gyy, cx + 3, gyy + 8, dt if kind != "shaman" else (210, 60, 60), 2)
            s.line(cx + 1, gyy, cx - 1, gyy + 6, dt if kind != "shaman" else (210, 60, 60), 2)
            s.ell(cx + 1, gyy, 2.2, 1.6, dt if kind != "shaman" else (210, 60, 60), flat=True)
            if stage >= 1 and kind != "shaman":   # norigae
                s.ell(cx - 2, gyy + 8, 1.9, 2.1, tone(a, 1.2), gloss=True)
                s.line(cx - 2, gyy + 9, cx - 2, gyy + 13, dt)
    if of == "peasant":
        s.line(cx - 4, sh + 1, cx + 1, sh + 8, CREAM)
        s.line(cx + 4, sh + 1, cx - 1, sh + 8, CREAM)
        # patches
        s.ell(cx - 4, sh + 11, 2.2, 2.0, a, flat=True)
        s.set(cx - 4, sh + 11, tone(a, .6)); s.set(cx - 3, sh + 12, tone(a, .6))
        if stage >= 1:
            s.ell(cx + 5, hip - 6, 2.2, 2.0, blend(a, dt, .5), flat=True)
        s.line(cx - sw * .88, hip - 3, cx + sw * .88, hip - 3, (150, 112, 60), 2)   # rope belt
        s.line(cx + 4, hip - 3, cx + 6, hip + 3, (150, 112, 60))
    if of == "armor":
        shoulder(m)
        poly(s, [(cx - sw, sh + 4), (cx + sw, sh + 4), (cx + sw * .85, hip - 2), (cx - sw * .85, hip - 2)], m)
        scales(s, cx - sw, cx + sw, sh + 4, hip - 2, m)
        s.line(cx - sw * .88, hip - 3, cx + sw * .88, hip - 3, a, 2)     # belt
        s.ell(cx, hip - 3, 2.6, 2.2, tone(a, 1.3), gloss=True)
        # collar guard
        s.ell(cx, sh + 1.5, 4.6, 2.2, tone(a, 1.0))
        for side in (-1, 1):   # pauldrons
            s.ell(cx + side * (sw + .5), sh + 5, 4.4 if stage else 3.6, 3.8, tone(m, 1.1))
            s.line(cx + side * (sw - 3), sh + 8, cx + side * (sw + 3), sh + 8, a)
            if stage >= 2:
                s.tri([(cx + side * (sw + 3), sh + 2), (cx + side * (sw + 5.5), sh - 4), (cx + side * (sw + 1), sh + 2)], tone(a, 1.2))
    if robe:
        by = sh + tor * (0.62 if of in ("royal", "official") else 0.55)
        if of == "royal":
            poly(s, [(cx - sw * .92, sh + 3), (cx + sw * .92, sh + 3), (cx + hw_b * .86, hem), (cx - hw_b * .86, hem)], m, flat=False) if False else None
            # round collar
            s.ell(cx, sh + 1.5, 5.2, 3.2, dt)
            s.ell(cx, sh + 2.4, 3.4, 2.0, SKIN)
            # dragon medallion (bo)
            my_ = sh + 8.5 * (1 if body != "child" else .9)
            r_ = 4.4 if body != "child" else 3.6
            s.ell(cx, my_, r_, r_, tone(a, 1.0), flat=True)
            s.ell(cx, my_, r_ - 1.4, r_ - 1.4, tone(a, .72), flat=True)
            s.line(cx - 2, my_ + 1, cx + 2, my_ - 1, tone(a, 1.4))
            s.set(cx - 2, my_ - 1, tone(a, 1.5)); s.set(cx + 2, my_ + 1, tone(a, 1.5))
            if stage >= 1:
                for side in (-1, 1):
                    s.ell(cx + side * (sw - 1), sh + 6, 2.0, 2.0, a, flat=True)
            # belt
            s.line(cx - sw * 1.0, by + 4, cx + sw * 1.0, by + 4, dt, 3)
            for i in range(-3, 4):
                s.set(cx + i * 2.3, by + 4, tone(a, 1.3))
        elif of == "official":
            s.ell(cx, sh + 1.8, 5.0, 3.0, dt)
            s.ell(cx, sh + 2.6, 3.2, 1.9, SKIN)
            # hyungbae (square badge)
            bw, bh = 4.6, 4.2
            x0_, y0_ = cx - bw, sh + 6
            for yy in range(int(y0_), int(y0_ + bh * 2)):
                for xx in range(int(x0_), int(x0_ + bw * 2)):
                    edge = xx in (int(x0_), int(x0_ + bw * 2) - 1) or yy in (int(y0_), int(y0_ + bh * 2) - 1)
                    s.set(xx, yy, tone(a, .7) if edge else a)
            # crane/tiger motif
            s.ell(cx, y0_ + bh, 1.8, 1.6, tone(a, .62), flat=True)
            s.set(cx - 2, y0_ + bh + 2, tone(a, 1.5)); s.set(cx + 2, y0_ + 2, tone(a, 1.5))
            s.line(cx - sw * 1.0, by + 4, cx + sw * 1.0, by + 4, (50, 40, 56), 3)
            for i in range(-3, 4):
                s.set(cx + i * 2.3, by + 4, tone(a, 1.3))
            if stage >= 1:
                s.line(cx - sw + 1, sh + 12, cx - sw + 1, sh + 15, a)
        elif of == "scholar":
            # V collar black trim + knotted belt
            s.line(cx - 4.5, sh + 1, cx + 1, sh + 13, dt, 2)
            s.line(cx + 4.5, sh + 1, cx - 1, sh + 13, dt, 2)
            s.line(cx - sw, by + 2, cx + sw, by + 2, dt, 2)
            s.ell(cx + 1, by + 2, 2.2, 2.2, dt, flat=True)
            s.line(cx + 1, by + 3, cx + 4, by + 12, dt, 2)
            s.line(cx + 1, by + 3, cx - 2, by + 11, dt, 2)
            if stage >= 1:
                s.line(cx - sw * 1.3, hem - 3, cx + sw * 1.3, hem - 3, tone(dt, 1.2))
        elif of == "monk":
            # kasaya diagonal patchwork
            pts = [(cx - sw * .9, sh + 1), (cx - sw * .1, sh + 1), (cx + sw * 1.1, hip + 4), (cx + sw * .9, hem - 4), (cx + sw * .0, hem - 4), (cx - sw * .9, hip + 6)]
            poly(s, pts, a)
            for t in range(1, 5):
                yy = sh + 1 + t * (hem - 4 - sh) / 5
                s.line(cx - sw * 1.0, yy, cx + sw * 1.1, yy, tone(a, .66))
            s.line(cx - 1, sh + 1, cx + 4, hip + 6, tone(a, .66))
            s.line(cx - 4, sh + 2, cx + 1, sh + 7, tone(m, 1.2))   # robe collar
            s.ell(cx, sh + 2.4, 3.4, 1.9, SKIN)
            for i in range(11):   # beads
                ang = i / 10 * math.pi
                s.set(cx + math.cos(ang) * 5.2, sh + 3 + math.sin(ang) * 6.5, (110, 72, 44))
            s.line(cx - sw, hip - 1, cx + sw, hip - 1, tone(m, .7), 2)
    if kind == "celestial":
        s.line(cx - sw * .88, sh + tor * .44, cx + sw * .88, sh + tor * .44, tone(a, 1.2), 2)
    if kind == "shaman":
        # bells hanging from belt
        for i, bx in enumerate((-5, -2, 1, 4)):
            if i % 2 == 0 or stage >= 1:
                s.line(cx + bx, sh + tor * .46, cx + bx, sh + tor * .46 + 5, tone(a, .8))
                s.ell(cx + bx, sh + tor * .46 + 6.2, 1.6, 1.6, tone(a, 1.25), gloss=True)
        s.line(cx - sw * .88, sh + tor * .44, cx + sw * .88, sh + tor * .44, (60, 100, 190), 2)

    # ---------------- arms / hands / props ----------------
    modes = {"book": "front", "scroll": "front", "brush": "front", "fan": "front", "flute": "front"}
    slots = [(1, props[0])] if props else []
    if len(props) > 1:
        slots.append((-1, props[1]))
    used = {sd: nm for sd, nm in slots}
    sleevec = {"hanbok_f": a, "hanbok": m, "royal": m, "official": m, "scholar": m, "monk": m,
               "armor": tone(m, .95), "peasant": torc, "celestial": blend(a, CREAM, .35), "shaman": CREAM}[kind if kind in ("hanbok_f",) else of if of != "hanbok" else "hanbok"] if True else m
    if kind == "shaman":
        sleevec = CREAM
    wide = of in ("royal", "official", "scholar", "monk", "celestial", "shaman") or kind == "hanbok_f"
    r1 = (5.2 if of in ("scholar", "monk", "official", "royal") else 4.3 if wide else 2.9) * (k ** .5) * (0.85 if body == "child" else 1)
    r0 = 3.1 * k ** .5
    hands = {}
    for sd in (-1, 1):
        nm = used.get(sd)
        mode = modes.get(nm, "pole")
        if nm and mode == "front":
            hxp, hyp = cx + sd * (sw * .45), sh + tor * .68
        else:
            hxp, hyp = cx + sd * (sw + 4.5), hip - 1 + (1 if nm else 2)
        hands[sd] = (hxp, hyp, nm)
        shp = (cx + sd * (sw - .6), sh + 4.2)
        ex, ey = hxp, hyp - (2.5 if wide else 1)
        ctr = (cx + sd * (sw + 1.5), sh + 4.2 + (ey - shp[1]) * .5)
        if kind == "shaman":
            cols = [(220, 70, 70), (244, 200, 70), (70, 120, 210), (240, 240, 240), (80, 170, 100)]
            for i in range(5):
                t0, t1 = i / 5, (i + 1) / 5
                pa = (shp[0] + (ex - shp[0]) * t0, shp[1] + (ey - shp[1]) * t0)
                pb = (shp[0] + (ex - shp[0]) * (t1 + .05), shp[1] + (ey - shp[1]) * (t1 + .05))
                s.tube([pb, pa][::-1] if False else [pa, pb], [r0 + (r1 - r0) * t0, r0 + (r1 - r0) * t1], cols[i])
        else:
            s.tube([shp, ctr, (ex, ey)], [r0, (r0 + r1) / 2, r1], sleevec)
        if stage >= 1 or of in ("royal", "official", "monk"):
            if of in ("royal", "official", "armor", "hanbok", "celestial") or kind == "hanbok_f":
                s.ell(ex, ey - .5, r1 * .95, r1 * .5, a if of != "hanbok" or sex == "f" else tone(a, 1.0), flat=True)
        if of == "armor":
            s.ell(ex, ey - .5, r1 * 1.0, r1 * .6, a, flat=True)

    def prop(nm, sd, hxp, hyp):
        kk = k ** .8
        d = (sd * .14, -.99)
        P = lambda t: (hxp + d[0] * t * kk, hyp + d[1] * t * kk)
        if nm == "sword":
            x0, y0 = P(2); x1, y1 = P(28)
            s.line(x0, y0, x1, y1, (214, 222, 234), 2)
            s.line(x0 - sd * 0 + 1, y0, x1 + 1, y1, (150, 160, 180), 1)
            s.tri([(x1 - 1, y1), (x1 + 2, y1), (x1 + .5, y1 - 4)], (220, 228, 240))
            gx_, gy_ = P(1)
            s.line(gx_ - 3, gy_, gx_ + 3, gy_, tone(GOLD, 1.0), 2)
            hx2, hy2 = P(-5)
            s.line(gx_, gy_, hx2, hy2, (120, 40, 40), 2)
        elif nm == "spear":
            x0, y0 = P(-14); x1, y1 = P(50)
            s.line(x0, y0, x1, y1, WOOD, 2)
            s.tri([(x1 - 2, y1 + 1), (x1 + 2.5, y1 + 1), (x1 + .5, y1 - 11)], (222, 230, 242))
            s.line(x1 + .5, y1 + 1, x1 + .5, y1 - 7, (150, 160, 180))
            s.ell(x1 + .5, y1 + 3, 2.8, 2.6, (210, 60, 60))
            s.ell(x1 + .5, y1 + 5, 1.6, 2.2, (170, 40, 50))
        elif nm == "axe":
            x0, y0 = P(-12); x1, y1 = P(36)
            s.line(x0, y0, x1, y1, WOOD, 2)
            s.ell(x1 + sd * 3.5, y1 + 1.5, 4.8, 6, (200, 208, 220))
            s.ell(x1 + sd * 1.2, y1 + 1.5, 1.8, 2, WOOD, flat=True)
        elif nm == "hoe":
            x0, y0 = P(-12); x1, y1 = P(38)
            s.line(x0, y0, x1, y1, WOOD, 2)
            s.tri([(x1 - 1, y1 - 1), (x1 + sd * 8, y1 + 1), (x1 + sd * 7, y1 + 7)], (170, 176, 190))
            s.line(x1, y1, x1 + sd * 3, y1 - 1, (110, 80, 60), 2)
        elif nm == "bow":
            for i in range(-20, 21):
                t = i / 20
                bx = hxp - sd * 3 + sd * 7.5 * (1 - t * t)
                s.set(bx, hyp - 1 + t * 22 * kk, WOOD); s.set(bx + sd * .0 + 1, hyp - 1 + t * 22 * kk, tone(WOOD, .7))
            s.line(hxp - sd * 3, hyp - 23 * kk, hxp - sd * 3, hyp + 21 * kk, (240, 232, 210))
            s.line(hxp + sd * 4, hyp - 3, hxp + sd * 4, hyp + 2, (200, 60, 60), 2)
        elif nm == "brush":
            x0, y0 = hxp, hyp
            x1, y1 = hxp - sd * 4 * kk, hyp - 15 * kk
            s.line(x0 + sd * 2, y0 + 4, x1, y1, (210, 170, 90), 2)
            s.line(x1, y1, x1 - sd * 1.5, y1 - 5, (30, 26, 34), 2)
            s.set(x1 - sd * 2, y1 - 7, (30, 26, 34))
        elif nm == "book":
            bw, bh = 5, 7
            for yy in range(int(hyp - bh - 2), int(hyp + bh - 2)):
                for xx in range(int(hxp - bw), int(hxp + bw)):
                    edge = xx in (int(hxp - bw), int(hxp + bw) - 1) or yy in (int(hyp - bh - 2), int(hyp + bh - 3))
                    s.set(xx, yy, (130, 100, 70) if edge else (232, 208, 150))
            for yy in range(int(hyp - bh), int(hyp + bh - 3), 3):
                s.set(hxp - bw + 2, yy, (200, 50, 50))
            s.ell(hxp + 1, hyp - bh + 1, 2.4, 1.2, (250, 250, 244), flat=True)
        elif nm == "scroll":
            s.line(hxp - 9, hyp - 4, hxp + 8, hyp - 6, WOOD, 3)
            s.line(hxp - 7, hyp - 4, hxp + 6, hyp - 6, (250, 244, 226), 3)
            s.line(hxp - 9, hyp - 4, hxp - 9, hyp - 4, WOOD)
            s.line(hxp - 1, hyp - 5, hxp - 1, hyp - 5, (200, 50, 50), 3)
        elif nm == "fan":
            fcx, fcy = hxp, hyp - 11
            s.line(hxp, hyp - 3, hxp, hyp + 1, WOOD, 2)
            s.ell(fcx, fcy, 7, 7, (250, 242, 218), flat=True)
            for ang in range(0, 360, 45):
                s.line(fcx, fcy, fcx + math.cos(math.radians(ang)) * 6, fcy + math.sin(math.radians(ang)) * 6, (222, 204, 168))
            for i in range(24):
                aa = i / 24 * math.tau
                s.set(fcx + math.cos(aa) * 6.6, fcy + math.sin(aa) * 6.6, WOOD)
            s.ell(fcx, fcy, 2.4, 2.4, (214, 60, 60), flat=True)
            for xx in range(-2, 3):
                for yy in range(0, 3):
                    if xx * xx + yy * yy < 6:
                        s.set(fcx + xx, fcy + yy, (60, 100, 200))
        elif nm == "gourd":
            gx_, gy_ = hxp, hyp + 8 * kk
            s.line(hxp, hyp, hxp, hyp + 4, (80, 140, 80), 1)
            s.ell(gx_, gy_ + 3, 5.4, 5.2, (232, 200, 110))
            s.ell(gx_, gy_ - 2.2, 3.4, 3.2, (238, 210, 126))
            s.set(gx_, gy_ - 5.5, (90, 140, 70))
            s.line(gx_ - 3, gy_, gx_ + 3, gy_, (90, 150, 80))
        elif nm == "flute":
            x0, y0 = hxp, hyp
            x1, y1 = hxp - sd * 14, hyp - 8
            s.line(x0 + sd * 5, y0 + 3, x1, y1, (190, 160, 80), 2)
            for t in (.3, .5, .7):
                s.set(x0 + sd * 5 + (x1 - x0 - sd * 5) * t, y0 + 3 + (y1 - y0 - 3) * t - 1, (90, 60, 30))
            s.set(x1 + sd * 1, y1, (90, 60, 30))
        elif nm == "lotus":
            fx_, fy_ = hxp + sd * 1, hyp - 14 * kk
            s.line(hxp, hyp, fx_, fy_ + 3, (70, 150, 80), 1)
            s.ell(fx_ + sd * 6, hyp - 5, 5, 2.2, (80, 170, 96), rot=-sd * .5)
            for ang, ln in ((-1.9, 4), (-1.2, 4), (-1.57, 5), (-2.6, 3.6), (-.55, 3.6)):
                ex2, ey2 = fx_ + math.cos(ang) * ln, fy_ + math.sin(ang) * ln
                s.ell((fx_ + ex2) / 2, (fy_ + ey2) / 2 + .5, 2.2, 3.0, (250, 170, 196) if ang in (-1.57, -2.6, -.55) else (255, 196, 214), rot=ang + math.pi / 2)
            s.ell(fx_, fy_ + 1, 1.6, 1.2, (250, 220, 90), flat=True)
        elif nm == "moon":
            mcx, mcy = hxp + sd * 2, hyp - 14
            for yy in range(-8, 9):
                for xx in range(-8, 9):
                    if xx * xx + yy * yy <= 36 and (xx - 3) ** 2 + (yy + 1) ** 2 > 30:
                        l = (xx + yy) < 0
                        s.set(mcx + xx, mcy + yy, (255, 246, 190) if l else (240, 214, 120))
            s.set(mcx + 6, mcy - 6, (255, 255, 255)); s.set(mcx + 7, mcy - 5, (255, 255, 255))
        elif nm == "sun":
            mcx, mcy = hxp + sd * 2, hyp - 14
            for i in range(8):
                ang = i / 8 * math.tau
                s.line(mcx + math.cos(ang) * 6, mcy + math.sin(ang) * 6, mcx + math.cos(ang) * 8.3, mcy + math.sin(ang) * 8.3, (255, 200, 80))
            s.ell(mcx, mcy, 5.2, 5.2, (255, 160, 60), gloss=True)

    for sd in (-1, 1):
        hxp, hyp, nm = hands[sd]
        if nm:
            prop(nm, sd, hxp, hyp)
        s.ell(hxp, hyp + .5, 2.5 if body != "child" else 2.3, 2.5, tone(SKIN, 1.04) if not nm else SKIN)

    # ---------------- head ----------------
    long_back = hw in ("braid",) or (sex == "f" and hw in ("none", "jokduri", "crown", "binyeo", "horns"))
    # hair back mass
    if hw not in ("monk", "helmet", "gat"):
        s.ell(cx, cy, hr + (.2 if body == 'child' else .6), hr * .99, hair)
    if hw == "helmet":
        for side in (-1, 1):
            s.ell(cx + side * (hr - .5), cy + hr * .3, 3.4, hr * .72, (150, 158, 172))
        s.ell(cx, cy + hr * .88, hr * .7, 2.6, (150, 158, 172))
    # ears
    for side in (-1, 1):
        s.ell(cx + side * (hr - .3), cy + hr * .22, 2.0, 2.6, SKIN)
    # face
    if hw == "monk":
        s.ell(cx, cy, hr, hr * .98, SKIN)
    else:
        s.ell(cx, cy + hr * .13, hr - .6, hr * .86, SKIN)
    # fringe
    if hw in ("none", "braid", "binyeo", "jokduri", "horns", "crown") and not (hw == "crown" and sex == "m"):
        fy = cy - hr * .66
        s.ell(cx, fy, hr * .94, hr * (.34 if body == 'child' else .42), hair)
        if body == "child" or sex == "f":
            for dx in (-.6, 0, .6):
                s.ell(cx + dx * hr, fy + hr * .2, hr * .28, hr * .2, hair)
            # center part
            s.set(cx, cy - hr * .66, tone(hair, 1.4))
    elif hw in ("topknot", "crown", "gat"):
        s.ell(cx, cy - hr * .72, hr * .88, hr * .34, hair)
    # face features
    es = 3 if body == "child" else 2
    eyec = (60, 38, 40)
    ey = cy + hr * (.18 if body == "child" else .1)
    ex_ = hr * (.5 if body == "child" else .46)
    s.eye(cx - ex_ - es / 2 + .5, ey, es, iris=eyec)
    s.eye(cx + ex_ - es / 2 + .5, ey, es, iris=eyec)
    bc = hair if not elder else (200, 200, 208)
    if body != "child":
        for side in (-1, 1):
            xb = cx + side * ex_ - 1
            s.line(xb - 1, ey - 3, xb + 2, ey - (3 if sex == "f" else 4) + (0 if side < 0 else 0), bc)
    for side in (-1, 1):
        s.ell(cx + side * hr * .62, ey + es + 2.2, 2.2, 1.3, BLUSH, flat=True)
    my = cy + hr * .62
    s.line(cx - 1, my, cx + 1, my, (150, 60, 60))
    s.set(cx - 2, my - 1, (150, 60, 60)); s.set(cx + 2, my - 1, (150, 60, 60))
    if body == "elder":
        s.set(cx - ex_ - 2, ey + 4, tone(SKIN, .8)); s.set(cx + ex_ + 2, ey + 4, tone(SKIN, .8))
    if sex == "f" and body != "child":
        s.set(cx - ex_ - 1, ey - 1, INK); s.set(cx + ex_ + 1, ey - 1, INK)

    # headwear
    top = cy - hr
    if hw == "topknot":
        s.ell(cx, top - 1.6, 3.4 * u, 3.2 * u, hair)
        s.ell(cx - .5, top - 2.2, 1.6, 1.2, tone(hair, 1.8), flat=True)
        s.line(cx - hr * .9, cy - hr * .46, cx + hr * .9, cy - hr * .46, dt, 2)   # manggeon band
        s.line(cx - hr * .55, top + 1.2, cx + hr * .55, top + 1.2, dt, 1)
    elif hw == "braid":
        for side in ((-1, 1) if body == "child" else (-1,)):
            pts = [(cx + side * (hr * (1.0 if body == 'child' else .8)), cy + hr * (.3 if body == 'child' else .45)), (cx + side * (sw * .95 + 2), sh + 2 + tor * .3), (cx + side * (sw * .85 + 1), sh + tor * (.75 if body != "child" else .9))]
            s.tube(pts, [2.4, 2.4, 2.0], hair)
            (x0_, y0_), (x1_, y1_) = pts[1], pts[2]
            for i in range(int(y1_ - y0_)):
                if i % 3 == 1:
                    s.set(x0_ + (x1_ - x0_) * i / max(1, int(y1_ - y0_)) - 1, y0_ + i, tone(hair, 1.9))
                    s.set(x0_ + (x1_ - x0_) * i / max(1, int(y1_ - y0_)) + 1, y0_ + i, tone(hair, 1.9))
            # daenggi ribbon
            s.ell(x1_, y1_ + 1.4, 2.4, 1.8, (226, 60, 70), flat=True)
            s.line(x1_ - 1, y1_ + 2, x1_ - 1, y1_ + 6, (226, 60, 70)); s.line(x1_ + 1, y1_ + 2, x1_ + 1, y1_ + 5, tone(a, 1.1))
        s.ell(cx, top + 1, 2.0, 1.4, (226, 60, 70), flat=True)
    elif hw == "binyeo":
        s.ell(cx, top - 1.8, 4.6 * u, 3.6 * u, hair)
        s.ell(cx - 1, top - 2.6, 2.2, 1.4, tone(hair, 1.9), flat=True)
        s.line(cx - 7 * u, top - 1.5, cx + 8 * u, top - 1.5, tone(a, 1.15), 2)
        s.ell(cx + 8 * u, top - 1.5, 1.8, 1.8, (220, 50, 70), gloss=True)
        s.set(cx - 7 * u, top - 1.5, tone(a, 1.5))
    elif hw == "gat":
        by = cy - hr * .56
        # crown
        poly(s, [(cx - 6 * u, by), (cx + 6 * u, by), (cx + 5.3 * u, by - 12 * u), (cx - 5.3 * u, by - 12 * u)], (52, 44, 58))
        s.ell(cx, by - 12 * u, 5.3 * u, 2.0 * u, (74, 64, 82))
        s.line(cx - 5.5 * u, by - 2, cx + 5.5 * u, by - 2, tone(dt, 1.0) if False else (74, 64, 82))
        # brim
        s.ell(cx, by, hr + 8 * u, 4.4 * u, (46, 38, 52))
        s.line(cx - hr - 5 * u, by - 1, cx - hr * .5, by - 3, (86, 76, 96))
        # cords
        cord = tone(a, 1.0)
        for side in (-1, 1):
            pts = [(cx + side * (hr + 4 * u), by + 2), (cx + side * hr * .78, cy + hr * .55), (cx + side * 2.5, cy + hr * 1.02)]
            for i in range(3):
                pass
            s.line(*pts[0], *pts[1], cord); s.line(*pts[1], *pts[2], cord)
    elif hw == "crown":
        if sex == "m":
            if stage == 2:   # myeollyugwan
                s.ell(cx, top + 1, hr * .72, hr * .48, (36, 30, 44))
                s.line(cx - hr * .5, top - 1, cx + hr * .5, top - 1, tone(a, 1.0))
                bx0, bx1 = cx - hr * 1.0, cx + hr * 1.0
                for yy in (top - 2, top - 1, top):
                    s.line(bx0, yy, bx1, yy, (30, 26, 36))
                s.line(bx0 + 1, top - 3, bx1 - 1, top - 3, tone(dt, 1.0) if sum(dt) > 160 else (90, 80, 100))
                for i in range(-2, 3):
                    x_ = cx + i * hr * .42
                    for j in range(4):
                        s.set(x_, top + 1 + j * 2, (250, 250, 240) if j % 2 == 0 else (210, 60, 70))
                for side in (-1, 1):
                    s.set(cx + side * hr * .98, top + 2, tone(a, 1.2)); s.set(cx + side * hr * .98, top + 3, tone(a, 1.2))
            else:   # ikseongwan
                s.ell(cx, top + 1.5, hr * .78, hr * .72, (36, 30, 44))
                s.line(cx - hr * .78, cy - hr * .5, cx + hr * .78, cy - hr * .5, tone(a, 1.0), 1)
                for side in (-1, 1):
                    s.line(cx + side * hr * .4, top - 1, cx + side * hr * .4, top + 4, (88, 78, 100))
                    s.ell(cx + side * (hr * .82), top + 1 - 2, 1.8 * u, 4.0 * u, (36, 30, 44), rot=side * .5)
                    s.set(cx + side * hr * .82, top - 3, tone(a, 1.2))
                s.ell(cx, top + 2, hr * .2, hr * .3, tone(a, 1.1), flat=True)
        else:   # gold diadem
            by = cy - hr * .72
            s.line(cx - hr * .85, by, cx + hr * .85, by, tone(a, 1.0), 3)
            for i in range(-2, 3):
                hgt = 6 - abs(i) * 1.2
                s.tri([(cx + i * hr * .38 - 2, by - 1), (cx + i * hr * .38, by - hgt - 1), (cx + i * hr * .38 + 2, by - 1)], tone(a, 1.15))
                s.set(cx + i * hr * .38, by - hgt - 1, (255, 250, 214))
            s.ell(cx, by, 1.8, 1.8, (220, 50, 70), gloss=True)
            for side in (-1, 1):
                s.line(cx + side * hr * .86, by + 1, cx + side * hr * .86, by + 8, tone(a, 1.1))
                s.ell(cx + side * hr * .86, by + 9, 1.3, 1.3, (220, 50, 70), flat=True)
    elif hw == "helmet":
        sc = (178, 186, 200)
        dome = lambda t: t.ell(cx, cy - hr * .3, hr + 1.6, hr * .88, sc)
        dome(s)
        # re-draw face lower part (open face)
        t = Sprite(); t.ell(cx, cy + hr * .13, hr - 1.6, hr * .8, SKIN)
        for y in range(int(cy - hr * .22), 96):
            for x in range(96):
                if t.px[y][x]:
                    s.px[y][x] = t.px[y][x]
        # brow band
        s.line(cx - hr - 1, cy - hr * .28, cx + hr + 1, cy - hr * .28, tone(a, 1.0), 2)
        s.line(cx, top - 1, cx, cy - hr * .3, tone(a, 1.0), 1)
        s.tri([(cx - 2, top + 1), (cx, top - 5 * u), (cx + 2, top + 1)], tone(a, 1.2))
        s.ell(cx, top - 5 * u - 2, 1.6, 4.0, (214, 50, 56))
        s.line(cx, top - 6 * u, cx + 3, top - 1, (214, 50, 56), 1)
        s.set(cx - 3, cy - hr * .6, (240, 244, 250)); s.set(cx - 4, cy - hr * .6 + 1, (240, 244, 250))
        # re-draw eyes
        s.eye(cx - ex_ - es / 2 + .5, ey, es, iris=eyec); s.eye(cx + ex_ - es / 2 + .5, ey, es, iris=eyec)
        for side in (-1, 1):
            s.ell(cx + side * hr * .62, ey + es + 2.2, 2.2, 1.3, BLUSH, flat=True)
        s.line(cx - 1, my, cx + 1, my, (150, 60, 60))
    elif hw == "jokduri":
        by = cy - hr * .88
        pts = [(cx - 8 * u, by), (cx + 8 * u, by), (cx + 6 * u, by - 9 * u), (cx - 6 * u, by - 9 * u)]
        poly(s, pts, (66, 42, 84))
        s.ell(cx, by - 9 * u, 6 * u, 1.8, (92, 62, 112))
        s.line(cx - 8 * u, by - 1, cx + 8 * u, by - 1, tone(a, 1.1))
        for i in range(-2, 3):
            s.set(cx + i * 3 * u, by - 5, tone(a, 1.4)); s.set(cx + i * 3 * u, by - 4, tone(a, .9))
        s.ell(cx, by - 5, 1.5, 1.5, (230, 60, 80), gloss=True)
        for side in (-1, 1):
            s.line(cx + side * 8 * u, by, cx + side * 9 * u, by + 4, tone(a, 1.0))
            s.set(cx + side * 9 * u, by + 5, (230, 60, 80))
    elif hw == "monk":
        for dx in (-3, 0, 3):
            s.ell(cx + dx, top + 3, .9, .9, (170, 108, 96), flat=True)
        s.line(cx - hr * .8, cy - hr * .55, cx - hr * .4, cy - hr * .85, tone(SKIN, 1.18))
    elif hw == "horns":
        for side in (-1, 1):
            s.tube([(cx + side * hr * .5, top + 3), (cx + side * hr * .62, top - 2), (cx + side * hr * .55 + side * 1.5, top - 8 * u - stage)], [2.8, 2.0, .8], (250, 238, 196))
            s.set(cx + side * hr * .62, top - 1, tone(a, 1.0))
        for dx in (-3, 0, 3):
            s.tri([(cx + dx - 2, top + 3), (cx + dx, top - 2), (cx + dx + 2, top + 3)], hair)

    # beard
    if beard:
        bcol = WHITEHAIR if elder else hair
        s.ell(cx - 2.6, my - 1.6, 2.8, 1.2, bcol)
        s.ell(cx + 2.6, my - 1.6, 2.8, 1.2, bcol)
        L = 3 + tor * .3 * (1 + stage * .3)
        s.tube([(cx, my + 2.2), (cx, my + 2.2 + L * .5), (cx + .3, my + 2.2 + L)], [2.6, 2.3, .9], bcol)
        s.line(cx - 1, my + .5, cx + 1, my + .5, (150, 60, 60))
    return s
