"""30x30 pixel orb icons for the five 령주 + 여의주."""
import json, math, sys
from PIL import Image
sys.path.insert(0, sys.argv[1]); from core import hx, tone
REPO = sys.argv[2]
m = json.load(open(f"{REPO}/docs/design/roster.json"))["mapping"]
def find_hex(key):
    s = json.dumps(m)
    import re
    for blk in (m.get("colors") or m.get("tokens") or m.get("elements") or []):
        pass
    return None
COLORS = {"monster": "#D63B35", "super": "#343B4D", "hyper": "#E3B130", "heal": "#2E9C8A", "quick": "#F1EEE4"}
L = (-.55, -.65, .52); n = math.sqrt(sum(v*v for v in L)); L = [v/n for v in L]
def orb(col, pearl=False):
    im = Image.new("RGBA", (30, 30), (0,0,0,0)); p = im.load()
    c = hx(col); r = [tone(c,.55), tone(c,.8), c, tone(c,1.3), (255,255,255)]
    cx = cy = 14.5; R = 11.5
    for y in range(30):
        for x in range(30):
            dx, dy = (x+.5-cx)/R, (y+.5-cy)/R; d = dx*dx+dy*dy
            if d <= 1:
                nz = math.sqrt(1-d); i = dx*L[0]+dy*L[1]+nz*L[2]
                k = 0 if i < .1 else 1 if i < .4 else 2 if i < .75 else 3 if i < .93 else 4
                p[x,y] = r[k] + (255,)
            elif d <= 1.22:
                p[x,y] = ((140,138,128) if sum(c) > 650 else tone(c,.3)) + (255,)
    if pearl:  # golden flame wisps around the pearl
        for a in range(0, 360, 45):
            t = math.radians(a); x = int(cx + math.cos(t)*14); y = int(cy + math.sin(t)*14)
            if 0 <= x < 30 and 0 <= y < 30: p[x,y] = (242,209,107,255)
    return im
for k, col in COLORS.items(): orb(col).save(f"{REPO}/assets/items/{k}.png")
orb("#5CCFE0", pearl=True).save(f"{REPO}/assets/items/master.png")
print("ok")
