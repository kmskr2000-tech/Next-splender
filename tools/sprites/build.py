"""Build creature sprites + idle GIFs + item icons from docs/design/roster.json.

usage: python -I build.py <sprites_dir> <repo_dir>
"""
import importlib
import json
import math
import re
import sys

from PIL import Image

SP, REPO = sys.argv[1], sys.argv[2]
sys.path.insert(0, SP)
from core import Sprite, hx, tone  # noqa: E402

ROSTER = sys.argv[3] if len(sys.argv) > 3 else "roster.json"
roster = json.load(open(f"{REPO}/docs/design/{ROSTER}"))
cards = roster["cards"]


def stage_of(cid):
    if cid.startswith(("rare", "legend")):
        return 2
    return {"t1": 0, "t2": 1, "t3": 2}[cid[:2]]


def norm(feats):
    out = []
    for f in feats:
        m = re.match(r"multi_tail\((\d+)\)", f)
        out.append(f"multi_tail:{m.group(1)}" if m else f)
    return out


def idle_frames(img):
    """4-frame idle: squash/stretch breathing anchored at the ground line."""
    frames = []
    bbox = img.getbbox() or (0, 0, 96, 96)
    for i, (sx, sy) in enumerate([(1, 1), (1.0, 0.97), (1, 1), (1.0, 1.02)]):
        w, h = img.size
        nh = max(1, round(h * sy))
        f = img.resize((w, nh), Image.NEAREST)
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.alpha_composite(f, (0, h - nh) if bbox[3] > 70 else (0, (h - nh) // 2))
        frames.append(canvas)
    return frames


def save_gif(frames, path):
    """Shared palette across frames; index 0 reserved for transparency."""
    w, h = frames[0].size
    strip = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.alpha_composite(f, (i * w, 0))
    rgb = Image.new("RGB", strip.size, (0, 0, 0))
    rgb.paste(strip.convert("RGB"), mask=strip.split()[3])
    pal_img = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    pal = pal_img.getpalette()[:255 * 3]
    shared = Image.new("P", (1, 1))
    shared.putpalette([255, 0, 255] + pal)
    out = []
    for f in frames:
        q = f.convert("RGB").quantize(palette=shared, dither=Image.Dither.NONE)
        # pixels quantized to the magenta slot are opaque colours: remap to nearest real colour
        qa = q.load(); alpha = f.split()[3].load()
        for y in range(h):
            for x in range(w):
                if alpha[x, y] < 128:
                    qa[x, y] = 0
                elif qa[x, y] == 0:
                    qa[x, y] = 1
        out.append(q)
    out[0].save(path, save_all=True, append_images=out[1:], duration=[320, 220, 320, 220], loop=0,
                transparency=0, disposal=2, optimize=False)


missing = set()
made = 0
for c in cards:
    sp = c.get("sprite") or {}
    arch = sp.get("archetype") or c.get("archetype")
    pal = c.get("palette") or sp.get("palette")
    try:
        mod = importlib.import_module(arch)
    except (ModuleNotFoundError, TypeError):
        missing.add(str(arch))
        continue
    if arch in ("person", "object"):
        spec = {k: v for k, v in sp.items() if k not in ("archetype", "palette")}
        spr = mod.draw(pal, stage_of(c["id"]), spec)
    else:
        spr = mod.draw(pal, stage_of(c["id"]), norm(sp.get("features") or c.get("features") or []))
    img = spr.render()
    img.save(f"{REPO}/assets/creatures/{c['id']}.png")
    save_gif(idle_frames(img), f"{REPO}/assets/creatures/anim/{c['id']}.gif")
    made += 1

print("made", made, "missing archetypes", sorted(missing))
