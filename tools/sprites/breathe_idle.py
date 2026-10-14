"""Bake idle breathing GIFs from static creature sprites with sprite-gen's Breathe layer.

Requires sprite-gen pinned at v2.44.0 (Apache-2.0, https://github.com/aldegad/sprite-gen,
commit 87f25d314679cd57dd3d2a74aad39cf91d66cea2) installed in the running interpreter.

usage: python -I tools/sprites/breathe_idle.py <repo> [card_id ...]
"""
import glob
import os
import sys

from PIL import Image
from sprite_gen.effects.breathe import bake_breathe_sequence, recommended_breathe_frames

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
ONLY = set(sys.argv[2:])
CFG = {"depth": 0.05, "breaths": 1, "lag": 0.1}
FRAME_MS = 230  # ~4fps: one breath ≈ 1.4s


def save_gif(frames, path):
    """Shared palette across frames; index 0 reserved for transparency."""
    w, h = frames[0].size
    strip = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.alpha_composite(f, (i * w, 0))
    rgb = Image.new("RGB", strip.size, (0, 0, 0))
    rgb.paste(strip.convert("RGB"), mask=strip.split()[3])
    pal = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT).getpalette()[:255 * 3]
    shared = Image.new("P", (1, 1))
    shared.putpalette([255, 0, 255] + pal)
    out = []
    for f in frames:
        q = f.convert("RGB").quantize(palette=shared, dither=Image.Dither.NONE)
        qa, alpha = q.load(), f.split()[3].load()
        for y in range(h):
            for x in range(w):
                if alpha[x, y] < 128:
                    qa[x, y] = 0
                elif qa[x, y] == 0:
                    qa[x, y] = 1
        out.append(q)
    out[0].save(path, save_all=True, append_images=out[1:], duration=FRAME_MS, loop=0,
                transparency=0, disposal=2, optimize=False)


n = recommended_breathe_frames(CFG)
ok, failed = 0, []
for p in sorted(glob.glob(f"{REPO}/assets/creatures/*.png")):
    cid = os.path.basename(p)[:-4]
    if ONLY and cid not in ONLY:
        continue
    still = Image.open(p).convert("RGBA")
    try:
        frames, _ = bake_breathe_sequence([still] * n, CFG)
    except SystemExit as e:  # sprite-gen refuses shapes it cannot breathe safely
        failed.append((cid, str(e)[:80]))
        continue
    save_gif([f.convert("RGBA") for f in frames], f"{REPO}/assets/creatures/anim/{cid}.gif")
    ok += 1
print(f"baked {ok}, skipped {len(failed)}")
for cid, why in failed:
    print(" ", cid, why)
