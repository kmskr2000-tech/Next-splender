"""person archetype: Korean folk/history humans. draw(p, stage, spec) -> Sprite.
spec: body child|youth|adult|elder, sex m|f, headwear, outfit, props[<=2], beard
"""
import math
from core import Sprite, hx, tone, ramp

SKIN = (246, 203, 166)
SKINS = {"red": (212, 86, 74), "pale": (252, 222, 194), "fair": (246, 203, 166), "tan": (220, 178, 148), "dark": (176, 136, 112),
         0: (252, 222, 194), 1: (246, 203, 166), 2: (220, 178, 148), 3: (176, 136, 112)}
STRAW = (214, 184, 112)
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
ROBE = ("royal", "official", "scholar", "monk", "cheolik")
NEWHATS_COVER = ("tanggeon", "paeraengi", "jeonrip", "satgat", "samo", "yugeon")   # hide hair mass
NEWHATS_FRINGE = ("tanggeon", "paeraengi", "jeonrip", "satgat", "samo", "yugeon", "hwarang", "geumgwan")
NEWHATS_HAIR = ("hwagwan", "headband", "gache")   # keep long hair + fringe
EXTRA_PROPS = ("quiver", "flower_shoes")
ROYAL_COL = {"red": (196, 42, 50), "yellow": (232, 184, 56), "gold": (226, 176, 60), "iron": (120, 128, 146),
             "navy": (52, 66, 104), "black": (40, 38, 48), "green": (58, 110, 84), "brown": (122, 84, 56), "silver": (176, 184, 198)}


def col_of(v):
    if v is None:
        return None
    if isinstance(v, str):
        return hx(v)
    return tuple(v)


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


def studs(s, x0, x1, y0, y1, col):
    """dujeong-gap: cloth armour with rows of brass rivets."""
    for r, y in enumerate(range(int(y0) + 1, int(y1), 3)):
        for x in range(int(x0) + 1 + (2 if r % 2 else 0), int(x1) - 1, 4):
            if s.get(x, y) is not None:
                s.set(x, y, (240, 212, 120)); s.set(x, y + 1, (150, 110, 50))
        if r % 2 == 0:
            for x in range(int(x0) + 1, int(x1) - 1):
                if s.get(x, y + 2) is not None:
                    s.set(x, y + 2, tone(col, .62))


def draw(p, stage, spec):
    global SKIN
    s = Sprite()
    if spec.get("pal"):
        p = {**p, **spec["pal"]}
    _sk = spec.get("skin", "fair")
    SKIN = SKINS.get(_sk) or col_of(_sk) or SKINS["fair"]
    m, a, dt = hx(p["main"]), hx(p["accent"]), hx(p["detail"])
    body = spec.get("body", "adult")
    sex = spec.get("sex", "m")
    hw = spec.get("headwear", "none")
    of = spec.get("outfit", "hanbok")
    saek = of == "saekdong"
    if saek:
        of = "hanbok"
    props_all = list(spec.get("props", []))
    props = [q for q in props_all if q not in EXTRA_PROPS][:2]
    beard = spec.get("beard", False)
    mustache = spec.get("mustache", "none")
    brows_st = spec.get("brows")
    expr = spec.get("expression")
    blush_on = spec.get("blush", True)
    hatc = col_of(spec.get("hat_color"))
    sashc = col_of(spec.get("sash")) or dt
    cloak = spec.get("cloak")
    armor_style = spec.get("armor_style", "scale")
    if of == "royal" and spec.get("royal_color") in ROYAL_COL:
        m = ROYAL_COL[spec["royal_color"]]
    if of == "armor" and spec.get("armor_color"):
        m = col_of(ROYAL_COL.get(spec["armor_color"], spec["armor_color"]))
    elder = body == "elder"
    k = [0.86, 0.93, 1.0][stage]
    hr0, leg0, tor0, sw0 = BODY[body]
    bshape = spec.get("body_shape", "normal")
    leg0 *= {"tall": 1.14, "stout": .92}.get(bshape, 1.0)
    tor0 *= {"tall": 1.12, "stout": .95}.get(bshape, 1.0)
    sw0 *= {"slim": .84, "stout": 1.24}.get(bshape, 1.0)
    hr = hr0 * k ** .5
    leg, tor, sw = leg0 * k, tor0 * k, sw0 * k * (0.93 if sex == "f" else 1.04)
    u = hr / 12.0
    cx = 48
    lift = 5 if of == "celestial" else 0
    gy = 82 - lift
    hip = gy - leg
    sh = hip - tor
    cy = sh - hr * 0.80
    hair = col_of(spec.get("hair_color")) or (WHITEHAIR if elder else HAIR)
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
    if "quiver" in props_all:
        s.tube([(cx - sw * .1, hip - 2), (cx - sw - 2, sh + 1)], [3.4, 3.0], (120, 78, 48))
        for i_, dx_ in enumerate((-1.8, 0, 1.8)):
            bx_, by0_ = cx - sw - 2 + dx_, sh + 1
            s.line(bx_, by0_, bx_ - 1, by0_ - 8 - i_, (232, 222, 190))
            s.tri([(bx_ - 3, by0_ - 6 - i_), (bx_, by0_ - 6 - i_), (bx_ - 1.5, by0_ - 11 - i_)], (214, 56, 60))
        s.line(cx - sw * .1 - 2, hip - 4, cx - sw - 4, sh + 3, (210, 170, 80))
    if cloak == "jangot":
        jc = col_of(spec.get("cloak_color")) or (74, 150, 98)
        poly(s, [(cx - hr * 1.05, cy - hr * .2), (cx + hr * 1.05, cy - hr * .2), (cx + sw + 5, hip + 2), (cx - sw - 5, hip + 2)], jc)
        s.ell(cx, cy - 1, hr + 3.2, hr + 2.4, jc)
        s.line(cx - sw - 4, hip + 1, cx + sw + 4, hip + 1, tone(jc, .62))
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
    flowershoe = "flower_shoes" in props_all or spec.get("shoes") == "flower"
    if flowershoe:
        shoe = (234, 82, 112)
    cuff = a
    if skirt:
        hy0 = sh + tor * (0.36 if kind == "hanbok_f" else 0.40)
        hw_b = sw * (1.7 if of != "celestial" else 1.8) * (1.12 if bshape == "stout" else 1.0)
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
        hw_b = sw * (1.55 if of == "cheolik" else 1.35 if of != "monk" else 1.3)
        pts = [(cx - sw * .92, sh + 3), (cx + sw * .92, sh + 3), (cx + hw_b, hem), (cx + hw_b * .5, hem + 1.2), (cx, hem + 1.5), (cx - hw_b * .5, hem + 1.2), (cx - hw_b, hem)]
        base = m
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
            (studs if armor_style == "dujeong" else scales)(s, cx - sw * 1.2, cx + sw * 1.2, hip - 5, hip + leg * .5, m)
            s.line(cx - sw * 1.2, hip + leg * .5, cx + sw * 1.2, hip + leg * .5, a)
    for lx in (-1, 1):
        fx = cx + lx * (sw * .5 if not skirt else sw * .55)
        sh_h = 2.0 if of in ("royal", "official", "scholar", "armor") else 1.7
        s.ell(fx + lx * .5, gy - 1.6, 3.6 * k ** .5, sh_h + .4, shoe)
        if of in ("hanbok", "shaman", "celestial", "monk") or flowershoe:
            s.tri([(fx + lx * 2.5, gy - 2), (fx + lx * 5.2, gy - 4.5), (fx + lx * 4, gy - 1)], shoe)
        if flowershoe:
            s.ell(fx + lx * 1.2, gy - 2.6, 1.3, 1.3, (255, 224, 96), flat=True)
            s.set(fx + lx * 4.6, gy - 3.6, (255, 255, 255))
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
        (studs if armor_style == "dujeong" else scales)(s, cx - sw, cx + sw, sh + 4, hip - 2, m)
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
            s.line(cx - sw, by + 2, cx + sw, by + 2, sashc, 2)
            s.ell(cx + 1, by + 2, 2.2, 2.2, sashc, flat=True)
            s.line(cx + 1, by + 3, cx + 4, by + 12, sashc, 2)
            s.line(cx + 1, by + 3, cx - 2, by + 11, sashc, 2)
            if stage >= 1:
                s.line(cx - sw * 1.3, hem - 3, cx + sw * 1.3, hem - 3, tone(dt, 1.2))
        elif of == "cheolik":
            s.ell(cx, sh + 1.8, 4.6, 2.8, tone(a, 1.1))
            s.ell(cx, sh + 2.6, 3.0, 1.7, SKIN)
            s.line(cx - 4, sh + 1, cx + 2, sh + 11, tone(m, .7), 2)
            for i in range(-4, 5):   # waist pleats
                s.line(cx + i * hw_b * .2, by + 6, cx + i * hw_b * .27, hem - 2, tone(m, .72))
            s.line(cx - sw, by + 3, cx + sw, by + 3, a, 3)
            s.ell(cx, by + 3, 2.6, 2.4, tone(GOLD, 1.0), gloss=True)
            if stage >= 1:
                s.line(cx - sw * .9, sh + 3, cx + sw * .8, by + 3, tone(a, 1.25))
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
    modes = {"mapae": "front", "cloud_scroll": "front", "book": "front", "scroll": "front", "brush": "front", "fan": "front", "flute": "front",
             "brush_scroll": "front", "geomungo": "front"}
    slots = [(1, props[0])] if props else []
    if len(props) > 1:
        slots.append((-1, props[1]))
    used = {sd: nm for sd, nm in slots}
    sleevec = {"hanbok_f": a, "hanbok": m, "royal": m, "official": m, "scholar": m, "monk": m,
               "armor": tone(m, .95), "peasant": torc, "cheolik": tone(a, .9), "celestial": blend(a, CREAM, .35), "shaman": CREAM}[kind if kind in ("hanbok_f",) else of if of != "hanbok" else "hanbok"] if True else m
    if kind == "shaman":
        sleevec = CREAM
    wide = of in ("royal", "official", "scholar", "monk", "celestial", "shaman") or kind == "hanbok_f"
    r1 = (5.2 if of in ("scholar", "monk", "official", "royal") else 3.3 if of == "cheolik" else 4.3 if wide else 2.9) * (k ** .5) * (0.85 if body == "child" else 1)
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
        if kind == "shaman" or saek:
            cols = [(220, 70, 70), (244, 200, 70), (70, 120, 210), (240, 240, 240), (80, 170, 100)]
            for i in range(5):
                t0, t1 = i / 5, (i + 1) / 5
                pa = (shp[0] + (ex - shp[0]) * t0, shp[1] + (ey - shp[1]) * t0)
                pb = (shp[0] + (ex - shp[0]) * (t1 + .05), shp[1] + (ey - shp[1]) * (t1 + .05))
                s.tube([pb, pa][::-1] if False else [pa, pb], [r0 + (r1 - r0) * t0, r0 + (r1 - r0) * t1], cols[i])
        else:
            s.tube([shp, ctr, (ex, ey)], [r0, (r0 + r1) / 2, r1], sleevec)
        if stage >= 1 or of in ("royal", "official", "monk"):
            if of in ("royal", "official", "armor", "hanbok", "celestial", "cheolik") or kind == "hanbok_f":
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
        elif nm == "hwando":
            pts_ = [(P(t)[0] + sd * ((t - 3) ** 2) * .013, P(t)[1]) for t in range(3, 28)]
            for i_ in range(len(pts_) - 1):
                s.line(*pts_[i_], *pts_[i_ + 1], (214, 222, 234), 2)
                s.set(pts_[i_][0] - sd, pts_[i_][1], (150, 160, 180))
            gx_, gy_ = P(2)
            s.ell(gx_, gy_, 3.4, 1.5, (210, 170, 70))
            hx2, hy2 = P(-5)
            s.line(gx_, gy_, hx2, hy2, (74, 44, 40), 2)
            s.ell(hx2, hy2 + 1, 1.8, 1.8, (210, 170, 70), flat=True)
        elif nm == "sword_long":
            x0, y0 = P(2); x1, y1 = P(40)
            s.line(x0, y0, x1, y1, (222, 230, 242), 3)
            s.line(x0 + 1, y0, x1 + 1, y1, (150, 160, 180), 1)
            s.tri([(x1 - 1.5, y1), (x1 + 2.5, y1), (x1 + .5, y1 - 5)], (230, 236, 246))
            gx_, gy_ = P(1)
            s.line(gx_ - 4, gy_, gx_ + 4, gy_, (60, 70, 110), 2)
            hx2, hy2 = P(-7)
            s.line(gx_, gy_, hx2, hy2, (60, 70, 110), 2)
            s.ell(hx2, hy2 + 1, 1.8, 1.8, (210, 170, 70), flat=True)
        elif nm == "staff":
            x0, y0 = P(-10); x1, y1 = P(42)
            s.line(x0, y0, x1, y1, tone(WOOD, .9), 2)
            s.line(x1, y1, x1 + sd * 3, y1 - 2, tone(WOOD, .9), 2)
            s.line(x1 + sd * 3, y1 - 2, x1 + sd * 4.5, y1 + 2, tone(WOOD, .9), 2)
            s.line(x1 + sd * 4.5, y1 + 2, x1 + sd * 2, y1 + 4, tone(WOOD, .9), 2)
            s.line(x1, y1 + 9, x1 - sd * 3, y1 + 15, a)
            s.ell(x1 - sd * 3, y1 + 16, 1.3, 1.3, a, flat=True)
        elif nm == "banner":
            x0, y0 = P(-14); x1, y1 = P(54)
            s.line(x0, y0, x1, y1, WOOD, 2)
            s.ell(x1, y1 - 2, 1.8, 1.8, GOLD, gloss=True)
            fw, fh = 16, 19
            poly(s, [(x1 + sd * 1, y1), (x1 + sd * fw, y1 + 1.5), (x1 + sd * (fw - 4), y1 + fh * .5), (x1 + sd * fw, y1 + fh - 1.5), (x1 + sd * 1, y1 + fh)], m)
            s.ell(x1 + sd * 7, y1 + fh * .5, 3.8, 3.8, a, flat=True)
            s.ell(x1 + sd * 7, y1 + fh * .5, 1.9, 1.9, dt, flat=True)
            s.line(x1 + sd * 1, y1 + 2, x1 + sd * (fw - 1), y1 + 3, a)
        elif nm == "kite":
            kx_, ky_ = hxp + sd * 8, hyp - 38 * kk
            s.line(hxp, hyp - 2, kx_, ky_ + 9, (240, 240, 228))
            poly(s, [(kx_, ky_ - 9), (kx_ + 6.5, ky_), (kx_, ky_ + 9), (kx_ - 6.5, ky_)], m)
            poly(s, [(kx_, ky_ - 9), (kx_, ky_ + 9), (kx_ - 6.5, ky_)], a, flat=True)
            s.line(kx_ - 6, ky_, kx_ + 6, ky_, dt); s.line(kx_, ky_ - 8, kx_, ky_ + 8, dt)
            for i_ in range(1, 8):
                s.set(kx_ + math.sin(i_ * 1.3) * 1.5, ky_ + 9 + i_, (230, 70, 70) if i_ % 2 else (250, 240, 220))
        elif nm == "drum":
            dx_, dy_ = hxp - sd * 7, hyp - 4
            s.ell(dx_, dy_, 7.4, 6.6, (172, 60, 50))
            s.ell(dx_, dy_, 5.2, 4.8, (246, 232, 200), flat=True)
            for i_ in range(14):
                ang = i_ / 14 * math.tau
                s.set(dx_ + math.cos(ang) * 6.0, dy_ + math.sin(ang) * 5.4, (242, 204, 96))
            for yy in range(-2, 3):
                for xx in range(-2, 3):
                    if xx * xx + yy * yy <= 5:
                        s.set(dx_ + xx, dy_ + yy, (60, 100, 200) if yy > 0 else (214, 60, 60))
            s.line(hxp, hyp - 2, hxp + sd * 4, hyp - 14, WOOD)
            s.ell(hxp + sd * 4, hyp - 14, 1.5, 1.5, (246, 232, 200), flat=True)
        elif nm == "geomungo":
            bx0, by0 = hxp - 26, hyp + 9
            bx1, by1 = hxp + 15, hyp - 1
            s.line(bx0, by0, bx1, by1, (92, 56, 40), 4)
            s.line(bx0, by0 - 2, bx1, by1 - 2, (150, 100, 68), 1)
            for t_ in (.1, .22, .34):
                s.set(bx0 + (bx1 - bx0) * t_, by0 + (by1 - by0) * t_ - 3, (226, 70, 60))
            s.line(bx0 + 3, by0 - 3, bx1 - 1, by1 - 3, (246, 240, 226))
            s.line(bx0 + 4, by0 - 4, bx1, by1 - 4, (200, 190, 170))
            s.ell(bx1 - 2, by1 - 2, 1.6, 1.6, (226, 70, 60), flat=True)
        elif nm == "herb_basket":
            bx_, by_ = hxp + sd * 1, hyp + 8 * kk
            s.line(hxp, hyp, bx_ - 5, by_ - 1, (150, 110, 60)); s.line(hxp, hyp, bx_ + 5, by_ - 1, (150, 110, 60))
            for i_, dx_ in enumerate((-3.5, -1.2, 1.2, 3.5)):
                s.line(bx_ + dx_, by_ - 1, bx_ + dx_ * 1.4, by_ - 6 - (i_ % 2) * 2, (80, 164, 84))
                s.ell(bx_ + dx_ * 1.4, by_ - 7 - (i_ % 2) * 2, 1.6, 1.2, (110, 190, 100), flat=True)
            s.set(bx_ + 1, by_ - 3, (214, 62, 70)); s.set(bx_ - 2, by_ - 4, (214, 62, 70))
            s.ell(bx_, by_ + 2, 6.4, 4.6, (196, 152, 88))
            for yy in (0, 2, 4):
                s.line(bx_ - 5, by_ + yy, bx_ + 5, by_ + yy, tone((196, 152, 88), .7))
        elif nm == "gourd_big":
            gx_, gyc = hxp + sd * 3, gy - 10
            s.ell(gx_, gyc + 3.4, 8.8, 7.6, (232, 204, 128))
            s.ell(gx_, gyc - 5.4, 5.6, 5.2, (240, 214, 142))
            s.line(gx_, gyc - 10, gx_ + sd * 2, gyc - 13, (90, 140, 70), 2)
            s.ell(gx_ + sd * 5, gyc - 12, 3.2, 1.6, (96, 166, 84), rot=-sd * .5)
        elif nm == "astrolabe":
            c0, c1 = P(21)
            r_ = 8.5 * kk
            s.line(hxp, hyp - 1, c0, c1 + r_, (170, 120, 60), 2)
            for q in range(0, 360, 3):
                an = math.radians(q)
                s.set(c0 + math.cos(an) * r_, c1 + math.sin(an) * r_, (216, 172, 74))
                s.set(c0 + math.cos(an) * r_ * .4, c1 + math.sin(an) * r_, (240, 206, 110))
                s.set(c0 + math.cos(an) * r_, c1 + math.sin(an) * r_ * .3, (190, 140, 60))
                ax_, ay_ = math.cos(an) * r_ * .85, math.sin(an) * r_ * .85 * .5
                s.set(c0 + ax_ * .8 - ay_ * .6, c1 + ax_ * .6 + ay_ * .8, (240, 206, 110))
            s.ell(c0, c1, 2.0, 2.0, (120, 200, 240), gloss=True)
        elif nm == "sundial":
            bx_, by_ = hxp + sd * 3, gy - 11
            for lx_ in (-1, 1):
                s.line(bx_ + lx_ * 3, by_ + 3, bx_ + lx_ * 4.5, gy - 2, (110, 86, 64), 2)
            s.ell(bx_, by_, 7.8, 4.8, (190, 140, 70))
            s.ell(bx_, by_ - 1.2, 6.0, 3.0, (238, 220, 172), flat=True)
            for q in range(5):
                s.line(bx_, by_ - 1, bx_ - 5 + q * 2.5, by_ - 2.4 + abs(q - 2) * .9, (150, 110, 60))
            s.line(bx_, by_ - 1, bx_ + sd * 1.5, by_ - 9, (56, 56, 68), 1)
            s.tri([(bx_ - 1, by_ - 1), (bx_ + 2, by_ - 1), (bx_ + sd * 1.5, by_ - 9)], (70, 70, 84))
        elif nm == "brush_scroll":
            prop("scroll", sd, hxp, hyp)
            prop("brush", sd, hxp + sd * 4, hyp - 1)
        elif nm == "mapae":   # bronze horse-tablet disc, held out front
            mx_, my_ = hxp + sd * 1.5, hyp - 8
            s.ell(mx_, my_, 7.4, 7.4, (122, 82, 40))
            s.ell(mx_, my_, 6.2, 6.2, (206, 150, 70), gloss=True)
            s.ell(mx_, my_, 4.6, 4.6, (226, 176, 90), flat=True)
            for q_ in range(16):
                an_ = q_ / 16 * math.tau
                s.set(mx_ + math.cos(an_) * 6.6, my_ + math.sin(an_) * 6.6, (255, 226, 140))
            for dx_, dy_ in ((-2, 1), (-1, 0), (0, 0), (1, 0), (2, 1), (-2, -1), (2, -1), (0, 2)):   # tiny horses
                s.set(mx_ + dx_, my_ + dy_, (110, 70, 34))
            s.set(mx_ - 3, my_ - 5, (255, 244, 190)); s.set(mx_ - 4, my_ - 4, (255, 244, 190))
            s.line(mx_, my_ - 7, mx_, my_ - 9, (196, 52, 52), 1)
            s.ell(mx_, my_ - 9.6, 1.5, 1.2, (196, 52, 52), flat=True)
        elif nm == "flower_branch":
            x0, y0 = P(-2); x1, y1 = P(24)
            s.line(x0, y0, x1, y1, (118, 80, 52), 2)
            xm, ym = P(14)
            s.line(xm, ym, xm - sd * 7, ym - 6, (118, 80, 52), 1)
            for (fx_, fy_, rr_) in ((x1, y1 - 2, 3.0), (xm - sd * 7, ym - 7, 2.6), (xm + sd * 3, ym - 2, 2.4)):
                for ang_ in range(5):
                    aa_ = ang_ / 5 * math.tau + .4
                    s.ell(fx_ + math.cos(aa_) * rr_ * .7, fy_ + math.sin(aa_) * rr_ * .7, rr_ * .62, rr_ * .62, (255, 176, 204))
                s.ell(fx_, fy_, 1.2, 1.2, (250, 220, 90), flat=True)
            s.ell(xm + sd * 4, ym + 4, 3.0, 1.3, (84, 164, 92), rot=sd * .6)
        elif nm == "shaman_bell":   # chilseong bangul: brass handle with three bells
            x0, y0 = P(-3); x1, y1 = P(12)
            s.line(x0, y0, x1, y1, (214, 170, 70), 2)
            s.line(x0, y0 + 1, x0, y0 + 5, (214, 60, 60), 1)
            for dxb, dyb in ((-7, 2.5), (0, -4), (7, 2.5)):
                bxx, byy = x1 + dxb, y1 + dyb - 3
                s.line(x1, y1, bxx, byy + 2, (214, 170, 70), 1)
                s.ell(bxx, byy, 3.6, 3.6, (240, 200, 84), gloss=True); s.set(bxx - 1, byy - 1, (255, 246, 190))
                s.set(bxx, byy + 2.6, (120, 80, 30))
        elif nm == "swing_rope":   # twin ropes up to a branch; both hands grip
            lx_ = cx - (sw + 4.5)
            rx_ = hxp
            for xx_ in (lx_, rx_):
                s.line(xx_, 11, xx_, hyp - 1, (176, 124, 70), 1)
                s.line(xx_ + 1, 11, xx_ + 1, hyp - 1, (214, 168, 104), 1)
            s.line(lx_ - 4, 10, rx_ + 4, 10, (112, 78, 48), 3)
            s.ell(lx_, hyp - 1, 2.2, 2.2, (196, 60, 70), flat=True)
            s.ell(rx_, hyp - 1, 2.2, 2.2, (196, 60, 70), flat=True)
            for yy_ in range(int(gy + 1), int(gy + 4)):
                s.line(lx_ - 3, yy_, rx_ + 3, yy_, (150, 100, 56) if yy_ == gy + 1 else (110, 74, 44))
        elif nm == "cloud_scroll":   # talisman scroll wreathed in a doryeol cloud
            sx_, sy_ = hxp + sd * 1, hyp - 4
            s.line(sx_ - 5, sy_ - 8, sx_ + 5, sy_ - 8, WOOD, 2)
            s.line(sx_ - 5, sy_ + 5, sx_ + 5, sy_ + 5, WOOD, 2)
            for yy_ in range(int(sy_ - 7), int(sy_ + 5)):
                s.line(sx_ - 4, yy_, sx_ + 4, yy_, (248, 226, 120))
            for yy_ in (-5, -2, 1, 4 - 0):
                s.line(sx_ - 2, sy_ + yy_, sx_ + 2, sy_ + yy_ + (1 if yy_ % 2 else 0), (200, 50, 50))
            for (dx_, dy_, rx2, ry2) in ((sd * 7, 3, 5.5, 3.4), (sd * 11, -2, 4.4, 3.0), (sd * 3, 8, 6.0, 3.0), (sd * 8, 9, 4.0, 2.4)):
                s.ell(sx_ + dx_, sy_ + dy_, rx2, ry2, (236, 232, 252))
                s.ell(sx_ + dx_, sy_ + dy_ + ry2 * .35, rx2 * .8, ry2 * .6, (196, 196, 230), flat=True)
        elif nm == "mirror":   # round bronze hand mirror
            x0, y0 = P(-2); x1, y1 = P(14)
            s.line(x0, y0, x1, y1, (150, 100, 56), 2)
            mx_, my_ = P(21)
            s.ell(mx_, my_, 7.4, 7.4, (150, 98, 44))
            s.ell(mx_, my_, 5.6, 5.6, (150, 214, 236), gloss=True)
            s.line(mx_ - 3, my_ - 2, mx_ - 1, my_ - 4, (255, 255, 255), 1)
            s.set(mx_ + 2, my_ + 2, (255, 255, 255))
            s.set(mx_, my_ + 7.4, (196, 60, 70)); s.set(mx_, my_ + 8.4, (196, 60, 70))
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
    if hw not in ("monk", "helmet", "gat") + NEWHATS_COVER:
        s.ell(cx, cy, hr + (.2 if body == 'child' else .6), hr * .99, hair)
    if hw == "helmet":
        for side in (-1, 1):
            s.ell(cx + side * (hr - .5), cy + hr * .3, 3.4, hr * .72, (150, 158, 172))
        s.ell(cx, cy + hr * .88, hr * .7, 2.6, (150, 158, 172))
    # ears
    for side in (-1, 1):
        if spec.get("big_ears"):
            s.ell(cx + side * (hr + .6), cy + hr * .2, 3.0, 4.4, SKIN)
            s.ell(cx + side * (hr + .9), cy + hr * .2, 1.3, 2.6, tone(SKIN, .82), flat=True)
            s.ell(cx + side * (hr + .9), cy + hr * .2 + 5.2, 1.5, 1.5, GOLD, gloss=True)
        else:
            s.ell(cx + side * (hr - .3), cy + hr * .22, 2.0, 2.6, SKIN)
    # face
    if hw == "monk":
        s.ell(cx, cy, hr, hr * .98, SKIN)
    else:
        s.ell(cx, cy + hr * .13, hr - .6, hr * .86, SKIN)
    # fringe
    if hw in ("none", "braid", "binyeo", "jokduri", "horns", "crown") + NEWHATS_HAIR and not (hw == "crown" and sex == "m"):
        fy = cy - hr * .66
        s.ell(cx, fy, hr * .94, hr * (.34 if body == 'child' else .42), hair)
        if body == "child" or sex == "f":
            for dx in (-.6, 0, .6):
                s.ell(cx + dx * hr, fy + hr * .2, hr * .28, hr * .2, hair)
            # center part
            s.set(cx, cy - hr * .66, tone(hair, 1.4))
    elif hw in ("topknot", "crown", "gat") + NEWHATS_FRINGE:
        s.ell(cx, cy - hr * .72, hr * .88, hr * .34, hair)
    if cloak == "jangot":
        jc = col_of(spec.get("cloak_color")) or (74, 150, 98)
        s.ell(cx, cy - hr * .78, hr + 2.4, hr * .4, jc)
        for side in (-1, 1):
            s.ell(cx + side * (hr + .2), cy + hr * .18, 2.6, hr * .8, jc)
        s.line(cx - hr * .9, cy - hr * .4, cx + hr * .9, cy - hr * .4, tone(jc, 1.25))
    # face features
    es = 3 if body == "child" else 2
    eyec = (60, 38, 40)
    ey = cy + hr * (.18 if body == "child" else .1)
    ex_ = hr * (.5 if body == "child" else .46)
    my = cy + hr * .62

    def feats():
        s.eye(cx - ex_ - es / 2 + .5, ey, es, iris=eyec)
        s.eye(cx + ex_ - es / 2 + .5, ey, es, iris=eyec)
        bc = hair if not elder else (200, 200, 208)
        if brows_st:
            bc = tone(bc, 1.0) if not elder else bc
        if body != "child":
            for side in (-1, 1):
                xb = cx + side * ex_ - 1
                if brows_st is None:
                    s.line(xb - 1, ey - 3, xb + 2, ey - (3 if sex == "f" else 4), bc)
                    continue
                bx = cx + side * ex_ + .5
                if brows_st == "thick":
                    s.line(bx - 2.5, ey - 4, bx + 2.5, ey - 4, bc, 2)
                elif brows_st == "thin":
                    s.line(bx - 2, ey - 4, bx + 2.5, ey - 5, tone(bc, 1.5) if not elder else bc)
                elif brows_st == "angry":   # inner end low
                    y_in, y_out = ey - 3, ey - 6
                    xi, xo = bx - side * 2.5, bx + side * 2.5
                    s.line(xi, y_in, xo, y_out, bc, 2)
                elif brows_st == "kind":    # soft arch, outer end low
                    s.line(bx - side * 2.5, ey - 5, bx, ey - 6, bc)
                    s.line(bx, ey - 6, bx + side * 3, ey - 4, bc)
        if blush_on:
            for side in (-1, 1):
                s.ell(cx + side * hr * .62, ey + es + 2.2, 2.2, 1.3, BLUSH, flat=True)
        mc = (150, 60, 60)
        if expr == "serious":
            s.line(cx - 2, my, cx + 2, my, (120, 54, 56))
        elif expr == "fierce":
            s.line(cx - 2, my, cx + 2, my, (110, 40, 44))
            s.set(cx - 3, my + 1, (110, 40, 44)); s.set(cx + 3, my + 1, (110, 40, 44))
            s.set(cx - 1, my + 1, (255, 255, 255)); s.set(cx + 1, my + 1, (255, 255, 255))
        elif expr == "smirk":   # one-sided sly grin, raised brow
            s.line(cx - 2, my + .5, cx + 1, my, mc)
            s.set(cx + 2, my - 1, mc); s.set(cx + 3, my - 2, mc)
            s.line(cx + ex_ - 2, ey - 6, cx + ex_ + 3, ey - 8, bc, 1)
            s.set(cx + 4, my - 1, tone(SKIN, .78)); s.set(cx + 4, my, tone(SKIN, .78))
        elif expr == "smile":
            s.line(cx - 2, my, cx + 2, my, mc)
            s.set(cx - 3, my - 1, mc); s.set(cx + 3, my - 1, mc)
            s.set(cx - 1, my + 1, (200, 90, 90)); s.set(cx, my + 1, (200, 90, 90)); s.set(cx + 1, my + 1, (200, 90, 90))
        else:
            s.line(cx - 1, my, cx + 1, my, mc)
            s.set(cx - 2, my - 1, mc); s.set(cx + 2, my - 1, mc)
        if body == "elder":
            s.set(cx - ex_ - 2, ey + 4, tone(SKIN, .8)); s.set(cx + ex_ + 2, ey + 4, tone(SKIN, .8))
        if sex == "f" and body != "child":
            s.set(cx - ex_ - 1, ey - 1, INK); s.set(cx + ex_ + 1, ey - 1, INK)

    feats()
    if spec.get("wen"):
        s.ell(cx - hr * .72, cy + hr * .5, 3.6, 3.4, tone(SKIN, .96))
        s.set(cx - hr * .72 - 1, cy + hr * .5 - 1, tone(SKIN, 1.3))

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
        gc = hatc or (52, 44, 58)
        poly(s, [(cx - 6 * u, by), (cx + 6 * u, by), (cx + 5.3 * u, by - 12 * u), (cx - 5.3 * u, by - 12 * u)], gc)
        s.ell(cx, by - 12 * u, 5.3 * u, 2.0 * u, tone(gc, 1.4) if hatc else (74, 64, 82))
        s.line(cx - 5.5 * u, by - 2, cx + 5.5 * u, by - 2, tone(dt, 1.0) if False else (74, 64, 82))
        # brim
        s.ell(cx, by, hr + 8 * u, 4.4 * u, tone(gc, .88) if hatc else (46, 38, 52))
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
            cs_ = spec.get("crown_style")
            if (stage == 2 and cs_ != "ikseon") or cs_ == "myeollyu":   # myeollyugwan
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
        feats()
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

    elif hw == "tanggeon":
        hc = hatc or (44, 38, 52)
        by = cy - hr * .5
        poly(s, [(cx - hr * .82, by), (cx + hr * .82, by), (cx + hr * .72, by - 5 * u), (cx - hr * .72, by - 5 * u)], hc)
        s.ell(cx, by - 7.4 * u, hr * .58, 3.6 * u, tone(hc, 1.5))
        s.line(cx - hr * .82, by - 1, cx + hr * .82, by - 1, tone(hc, 2.0))
        for i in range(-2, 3):
            s.set(cx + i * 2.6 * u, by - 7 * u, tone(hc, .7))
    elif hw == "yugeon":
        hc = hatc or (30, 34, 54)
        by = cy - hr * .42
        poly(s, [(cx - hr * .86, by), (cx + hr * .86, by), (cx + hr * .72, by - 11 * u), (cx - hr * .72, by - 11 * u)], hc)
        s.ell(cx, by - 11 * u, hr * .72, 2.0 * u, tone(hc, 1.5))
        for fx_ in (-.3, .3):
            s.line(cx + fx_ * hr, by - 1, cx + fx_ * hr * .9, by - 12 * u, tone(hc, 1.7))
        s.line(cx - hr * .86, by - 1, cx + hr * .86, by - 1, tone(hc, 2.2))
        for side in (-1, 1):
            s.tri([(cx + side * hr * .86, by), (cx + side * hr * 1.02, by + 9 * u), (cx + side * hr * .62, by + 1)], hc)
            s.line(cx + side * hr * .98, by + 8 * u, cx + side * hr * 1.1, by + 12 * u, a)
    elif hw == "paeraengi":
        hc = hatc or STRAW
        by = cy - hr * .6
        s.ell(cx, by, hr + 7 * u, 3.4 * u, tone(hc, .92))
        s.ell(cx, by - 3 * u, hr * .72, 5.6 * u, hc)
        for i in range(-3, 4):
            s.line(cx + i * 2.6 * u, by - 7 * u, cx + i * 4.4 * u, by + 1, tone(hc, .72))
        s.line(cx - hr - 5 * u, by + 1, cx + hr + 5 * u, by + 1, tone(hc, .72))
        for side in (-1, 1):
            s.line(cx + side * (hr + 3 * u), by + 2, cx + side * hr * 1.0, cy + hr * .5, (200, 60, 60))
    elif hw == "jeonrip":
        hc = hatc or (58, 48, 70)
        by = cy - hr * .5
        s.ell(cx, by, hr + 5 * u, 3.2 * u, tone(hc, .9))
        s.ell(cx, by - 5 * u, hr * .84, 7 * u, hc)
        s.line(cx - hr * .8, by - 2, cx + hr * .8, by - 2, a, 2)
        s.line(cx + hr * .1, by - 11 * u, cx + hr * .1, by - 16 * u, (214, 50, 56), 2)
        s.ell(cx + hr * .1, by - 11 * u, 2.4 * u, 4.2 * u, (214, 50, 56))
        s.set(cx - hr * .4, by - 8 * u, tone(hc, 2.0)); s.set(cx - hr * .5, by - 7 * u, tone(hc, 2.0))
        for side in (-1, 1):
            s.line(cx + side * (hr + 3 * u), by + 2, cx + side * hr * 1.02, cy + hr * .5, (210, 56, 60))
    elif hw == "samo":
        hc = hatc or (30, 26, 36)
        by = cy - hr * .5
        s.ell(cx, by - 6 * u, hr * .8, 8 * u, hc)
        s.line(cx - hr * .78, by - 1, cx + hr * .78, by - 1, tone(a, 1.1), 2)
        for side in (-1, 1):
            s.tube([(cx + side * hr * .7, by - 6 * u), (cx + side * hr * 1.4, by - 5 * u), (cx + side * hr * 2.0, by - 7 * u)], [1.7, 1.5, 1.8], hc)
            s.set(cx + side * hr * 1.4, by - 6 * u, tone(hc, 2.2))
        s.set(cx - hr * .3, by - 10 * u, tone(hc, 2.4)); s.set(cx - hr * .4, by - 9 * u, tone(hc, 2.4))
        if spec.get("hat_flower"):   # peony tucked at the hat side (Cheoyong)
            px_, py_ = cx + hr * .72, by - 3.5 * u
            for ang_ in range(6):
                aa_ = ang_ / 6 * math.tau
                s.ell(px_ + math.cos(aa_) * 3.2, py_ + math.sin(aa_) * 2.8, 2.7, 2.4, (240, 96, 136) if ang_ % 2 else (252, 150, 176))
            s.ell(px_, py_, 2.6, 2.4, (255, 190, 206))
            s.ell(px_, py_, 1.2, 1.1, (250, 214, 90), flat=True)
            s.ell(px_ + 5, py_ + 3.4, 3.0, 1.4, (70, 150, 84), rot=.4)
    elif hw == "satgat":
        hc = hatc or (212, 178, 100)
        by = cy - hr * .5
        poly(s, [(cx, top - 10 * u), (cx - hr - 12 * u, by + 1), (cx + hr + 12 * u, by + 1)], hc)
        s.ell(cx, by + 1, hr + 12 * u, 3.0 * u, tone(hc, .86))
        for i in range(-4, 5):
            s.line(cx + i * .4 * u, top - 9 * u, cx + i * (hr + 10 * u) / 4.6, by, tone(hc, .72))
        s.line(cx - hr - 8 * u, by + 2, cx + hr + 8 * u, by + 2, tone(hc, .6))
        for side in (-1, 1):
            s.line(cx + side * (hr + 8 * u), by + 3, cx + side * hr * 1.0, cy + hr * .55, tone(a, 1.0))
    elif hw == "hwagwan":
        by = cy - hr * .66
        s.ell(cx, top - 1.2 * u, hr * .68, 5.2 * u, (232, 96, 128))
        s.line(cx - hr * .9, by, cx + hr * .9, by, tone(a, 1.15), 2)
        for i, (xx, fc) in enumerate(((-.62, (250, 200, 60)), (-.2, (255, 250, 240)), (.2, (255, 130, 160)), (.62, (250, 200, 60)))):
            s.ell(cx + xx * hr, top - 1.2 * u - (1 - abs(xx)) * 3 * u, 2.4, 2.4, fc, gloss=True)
        for side in (-1, 1):
            s.line(cx + side * hr * .92, by + 1, cx + side * hr * .92, by + 8, tone(a, 1.1))
            s.ell(cx + side * hr * .92, by + 9.5, 1.5, 1.8, (90, 200, 170), flat=True)
    elif hw == "headband":
        bcol = hatc or (250, 248, 240)
        yb = cy - hr * .52
        for dy_ in (0, 1, 2):
            s.line(cx - hr * .96, yb + 1 + dy_, cx - hr * .5, yb + dy_, bcol)
            s.line(cx - hr * .5, yb + dy_, cx + hr * .5, yb + dy_, bcol)
            s.line(cx + hr * .5, yb + dy_, cx + hr * .96, yb + 1 + dy_, bcol)
        s.ell(cx + hr * .92, yb + 1, 2.2, 2.2, bcol, flat=True)
        s.line(cx + hr * .92, yb + 2, cx + hr * 1.35, yb + 8, bcol, 2)
        s.line(cx + hr * .9, yb + 2, cx + hr * .75, yb + 9, bcol, 2)
        s.set(cx - hr * .1, yb, (214, 60, 60)); s.set(cx + hr * .1, yb, (214, 60, 60))
    elif hw == "gache":
        s.ell(cx, top - 2.4 * u, hr * 1.34, 7.4 * u, hair)
        s.ell(cx, top - 6 * u, hr * .8, 4.4 * u, hair)
        for i in range(-3, 4):
            s.set(cx + i * hr * .3, top - 5 * u - abs(i) * -.4 + 1, tone(hair, 2.0))
            s.set(cx + i * hr * .36, top - 1.5 * u, tone(hair, 1.8))
        s.line(cx - hr * 1.5, top - 1.5 * u, cx + hr * 1.5, top - 1.5 * u, tone(a, 1.15), 2)
        for side in (-1, 1):
            s.ell(cx + side * hr * 1.5, top - 1.5 * u, 1.9, 1.9, (220, 50, 70), gloss=True)
            s.line(cx + side * hr * 1.35, top + 4 * u, cx + side * hr * 1.35, top + 14 * u, (226, 60, 70))
        s.ell(cx, top - 8 * u, 3.0 * u, 2.4 * u, (255, 140, 170), gloss=True)
        s.set(cx, top - 8 * u, (255, 230, 120))
    elif hw == "hwarang":
        s.ell(cx, top - 1.2, 3.2 * u, 3.0 * u, hair)
        by = cy - hr * .56
        s.line(cx - hr * .92, by, cx + hr * .92, by, tone(a, 1.1), 2)
        s.ell(cx, by, 1.8, 1.8, (220, 50, 70), gloss=True)
        for ang, ln, fc in ((-.62, 8.5, (240, 240, 246)), (.62, 8.5, (240, 240, 246)), (-.25, 11, (220, 62, 72)), (.25, 11, (220, 62, 72)), (0, 13, (250, 250, 250))):
            bx_, by_ = cx + math.sin(ang) * hr * .5, by - 2
            s.ell(bx_ + math.sin(ang) * ln * u * .5, by_ - math.cos(ang) * ln * u * .5, 1.9 * u, ln * u * .5, fc, rot=ang)
    elif hw == "geumgwan":
        by = cy - hr * .64
        gcol = tone(GOLD, 1.0)
        poly(s, [(cx - hr * .94, by + 1), (cx + hr * .94, by + 1), (cx + hr * .94, by - 4), (cx - hr * .94, by - 4)], gcol)
        if spec.get("crown_style") == "flame":
            for i in range(-3, 4):
                hh = 15 - abs(i) * 3.2
                xx = cx + i * hr * .3
                s.tri([(xx - 2.8, by - 4), (xx, by - 4 - hh * u), (xx + 2.8, by - 4)], gcol)
                s.set(xx, by - 4 - hh * u, (255, 244, 170))
            s.ell(cx, by - 1, 2.0, 2.0, (220, 50, 70), gloss=True)
        for xo, hh in (() if spec.get("crown_style") == "flame" else ((-.62, 9), (0, 13), (.62, 9))):
            xx = cx + xo * hr
            s.line(xx, by - 4, xx, by - 4 - hh * u, gcol, 2)
            for j in (1, 2):
                yy = by - 4 - hh * u * (.3 + .3 * j)
                s.line(xx, yy, xx - 3, yy - 2, gcol); s.line(xx, yy, xx + 3, yy - 2, gcol)
                s.set(xx - 3, yy - 2, (90, 200, 170)); s.set(xx + 3, yy - 2, (90, 200, 170))
            s.ell(xx, by - 5 - hh * u, 1.5, 1.5, (255, 240, 150), gloss=True)
        for side in (-1, 1):
            s.tube([(cx + side * hr * .94, by - 3), (cx + side * hr * 1.15, by + 2), (cx + side * hr * 1.0, by + 9)], [1.1, 1.0, 1.4], gcol)
            s.ell(cx + side * hr * 1.0, by + 10, 1.6, 2.0, (90, 200, 170), flat=True)
        for i in range(-3, 4):
            s.set(cx + i * hr * .28, by - 1, (255, 244, 170))

    # beard & mustache
    bst = "long_legacy" if beard is True else (beard or None)
    if bst or mustache != "none":
        bcol = WHITEHAIR if elder else hair
        if mustache == "long_white" or (bst == "long" and elder):
            bcol_m = WHITEHAIR
        else:
            bcol_m = bcol
        L = 3 + tor * .3 * (1 + stage * .3)
        if bst in ("long_legacy", "full", "long") and mustache == "none":
            mustache = "full"
        if mustache == "thin":
            for side in (-1, 1):
                s.line(cx + side * .5, my - 2, cx + side * 4.5, my - 1, bcol_m)
                s.set(cx + side * 5, my, bcol_m)
        elif mustache == "full":
            s.ell(cx - 2.6, my - 1.6, 2.8, 1.2, bcol_m)
            s.ell(cx + 2.6, my - 1.6, 2.8, 1.2, bcol_m)
        elif mustache == "long_white":
            for side in (-1, 1):
                s.tube([(cx + side * 1.2, my - 2), (cx + side * 4.6, my - .5), (cx + side * 6.2, my + 6)], [1.6, 1.4, .8], WHITEHAIR)
        if bst == "goatee":
            s.tube([(cx, my + 2), (cx, my + 4), (cx + .3, my + 6.5)], [1.9, 1.5, .8], bcol)
        elif bst == "long_legacy":
            s.tube([(cx, my + 2.2), (cx, my + 2.2 + L * .5), (cx + .3, my + 2.2 + L)], [2.6, 2.3, .9], bcol)
        elif bst == "full":
            for side in (-1, 1):
                s.ell(cx + side * hr * .62, cy + hr * .52, 2.6, 4.2, bcol)
            s.ell(cx, my + 3, hr * .55, 3.0, bcol)
            s.tube([(cx, my + 3), (cx, my + 3 + L * .4), (cx + .3, my + 3 + L * .8)], [2.8, 2.4, 1.0], bcol)
        elif bst == "long":
            s.tube([(cx, my + 2.2), (cx, my + 2.2 + L * 1.0), (cx + .3, my + 2.2 + L * 2.1)], [2.8, 2.5, .9], bcol)
        s.line(cx - 1, my + .5, cx + 1, my + .5, (150, 60, 60))
    return s
