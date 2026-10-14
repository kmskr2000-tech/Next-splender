#!/usr/bin/env python3
"""Placeholder sprite generator (temporary; replaced by generated art later).
Usage: /tmp/claude-0/bl/bin/python tools/sprites/placeholder.py
Writes: assets/creatures/{id}.png (96x96), assets/items/{key}.png (30x30),
        assets/trainers/trainer-{1..4}.webp (256x256).
Does not overwrite existing files unless --force.
"""
import re, sys, random
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
FORCE = '--force' in sys.argv
COLORS = {'monster': (239, 68, 68), 'super': (59, 130, 246), 'hyper': (113, 113, 122),
          'heal': (236, 72, 153), 'quick': (234, 179, 8), 'master': (139, 92, 246)}
OUT = (10, 10, 18)

def save(img, path, **kw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not FORCE:
        return False
    img.save(path, **kw)
    return True

def creature(cid, bonus, tier):
    rnd = random.Random(cid)
    base = COLORS[bonus]
    g = 12  # 12x12 grid, 8px per cell -> 96px
    cells = [[0] * g for _ in range(g)]
    half = g // 2
    rows = range(2, 11) if tier < 3 else range(1, 11)
    for y in rows:
        w = rnd.randint(2, half - 1 if tier < 3 else half)
        for x in range(half - w, half):
            cells[y][x] = 1
    for y in range(g):  # mirror
        for x in range(half):
            cells[y][g - 1 - x] = cells[y][x]
    img = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    def px(x, y, c): d.rectangle([x * 8, y * 8, x * 8 + 7, y * 8 + 7], fill=c)
    for y in range(g):
        for x in range(g):
            if cells[y][x]:
                edge = any(not (0 <= y + dy < g and 0 <= x + dx < g and cells[y + dy][x + dx])
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                px(x, y, OUT if edge else base)
    ys = [y for y in range(g) if any(cells[y])]
    ey = ys[0] + 2
    for x in (4, 7):
        if cells[ey][x]: px(x, ey, (255, 255, 255))
    return img

def ball(key):
    img = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([1, 1, 28, 28], fill=COLORS[key], outline=OUT, width=2)
    d.ellipse([10, 10, 19, 19], fill=(255, 255, 255), outline=OUT, width=2)
    return img

def trainer(i):
    c = [(239, 68, 68), (59, 130, 246), (234, 179, 8), (236, 72, 153)][i - 1]
    img = Image.new('RGB', (256, 256), c)
    d = ImageDraw.Draw(img)
    d.ellipse([88, 50, 168, 130], fill=(255, 224, 189), outline=OUT, width=6)
    d.rectangle([60, 150, 196, 256], fill=OUT)
    d.text((120, 80), str(i), fill=OUT)
    return img

def main():
    src = (ROOT / 'src/data/cards.js').read_text(encoding='utf-8')
    n = 0
    for m in re.finditer(r"id: '([\w-]+)', tier: '?(\w+)'?.*?bonus: (\[[^\]]*\]|'\w+')", src):
        cid, tier, b = m.group(1), (int(m.group(2)) if m.group(2).isdigit() else 3), m.group(3)
        bonus = re.findall(r"\w+", b)[0]
        n += save(creature(cid, bonus, tier), ROOT / f'assets/creatures/{cid}.png')
    for k in COLORS:
        n += save(ball(k), ROOT / f'assets/items/{k}.png')
    for i in range(1, 5):
        n += save(trainer(i), ROOT / f'assets/trainers/trainer-{i}.webp', quality=80)
    print('written', n)

main()
