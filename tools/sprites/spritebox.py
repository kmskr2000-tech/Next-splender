"""Regenerate src/ui/spritebox.js (opaque bbox per creature sprite). Run after build.py.

usage: python -I tools/sprites/spritebox.py .
"""
import glob, json, os, sys
from PIL import Image

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
box = {}
for p in sorted(glob.glob(f"{REPO}/assets/creatures/*.png")):
    bb = Image.open(p).convert("RGBA").getbbox() or (0, 0, 96, 96)
    box[os.path.basename(p)[:-4]] = list(bb)
with open(f"{REPO}/src/ui/spritebox.js", "w") as f:
    f.write("// Generated: opaque bounding box [x0,y0,x1,y1] of each 96x96 creature sprite, used to crop/zoom card art.\n")
    f.write("export const SPRITE_BOX = " + json.dumps(box, separators=(",", ":")) + ";\n")
print(len(box), "boxes")
