"""Avatar portraits (bust crop of person sprites) for trainer-1..4."""
import sys
from PIL import Image
sys.path.insert(0, sys.argv[1]); import person
REPO = sys.argv[2]
SPECS = [
  ({"main": "#2E6FB7", "accent": "#F2C14E", "detail": "#1D3B66"}, {"body": "youth", "sex": "m", "headwear": "topknot", "outfit": "hanbok", "props": []}),
  ({"main": "#D9465B", "accent": "#F7D24A", "detail": "#7A2233"}, {"body": "youth", "sex": "f", "headwear": "braid", "outfit": "hanbok", "props": []}),
  ({"main": "#8A6A3E", "accent": "#C9A76A", "detail": "#4B3820"}, {"body": "youth", "sex": "m", "headwear": "gat", "outfit": "scholar", "props": []}),
  ({"main": "#3E9A6B", "accent": "#F2A6B8", "detail": "#22573C"}, {"body": "youth", "sex": "f", "headwear": "binyeo", "outfit": "hanbok", "props": []}),
]
BG = ["#DCEBFA", "#FCE1E4", "#F6EBD3", "#DDF2E5"]
for i, (pal, spec) in enumerate(SPECS):
    img = person.draw(pal, 1, spec).render()
    bb = img.getbbox(); cx = (bb[0] + bb[2]) // 2
    crop = img.crop((cx - 22, bb[1] - 2, cx + 22, bb[1] + 42))
    canvas = Image.new("RGBA", crop.size, BG[i]); canvas.alpha_composite(crop)
    canvas.resize((176, 176), Image.NEAREST).save(f"{REPO}/assets/trainers/trainer-{i+1}.webp", lossless=True)
    canvas.resize((176, 176), Image.NEAREST).save(f"/tmp/claude-0/sprites/av{i+1}.png")
print("ok")
