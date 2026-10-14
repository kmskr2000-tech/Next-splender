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

roster = json.load(open(f"{REPO}/docs/design/roster.json"))
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
    # GIF needs palette + transparency index
    pal = []
    for f in frames:
        p = f.convert("RGBA")
        bg = Image.new("RGBA", p.size, (255, 0, 255, 255))
        bg.alpha_composite(p)
        q = bg.convert("RGB").quantize(colors=63, method=Image.Quantize.MEDIANCUT)
        pal.append(q)
    # find magenta index per frame
    out = []
    for q in pal:
        p = q.getpalette()
        idx = min(range(len(p) // 3), key=lambda i: (p[i * 3] - 255) ** 2 + p[i * 3 + 1] ** 2 + (p[i * 3 + 2] - 255) ** 2)
        q.info["transparency"] = idx
        out.append(q)
    out[0].save(path, save_all=True, append_images=out[1:], duration=[320, 220, 320, 220], loop=0,
                transparency=out[0].info["transparency"], disposal=2)


missing = set()
made = 0
for c in cards:
    arch = c["archetype"]
    try:
        mod = importlib.import_module(arch)
    except ModuleNotFoundError:
        missing.add(arch)
        continue
    spr = mod.draw(c["palette"] | {k: v for k, v in c["palette"].items()}, stage_of(c["id"]), norm(c["features"]))
    img = spr.render()
    img.save(f"{REPO}/assets/creatures/{c['id']}.png")
    save_gif(idle_frames(img), f"{REPO}/assets/creatures/anim/{c['id']}.gif")
    made += 1

print("made", made, "missing archetypes", sorted(missing))
