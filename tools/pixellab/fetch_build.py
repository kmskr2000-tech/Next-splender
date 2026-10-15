"""PixelLab 오브젝트를 내려받아 카드용 정적 PNG + 대기 모션 GIF를 함께 만든다.

usage: python -I tools/pixellab/fetch_build.py <repo> <cache_dir> [card_id ...]
  - tools/pixellab/objects.json 의 오브젝트 ZIP을 api.pixellab.ai 에서 받는다(키: env PIXELLAB_API_KEY)
    (backblaze 직링크는 환경 네트워크 정책에 막혀 있어 API 경유 ZIP을 쓴다)
  - 정적 이미지와 애니메이션 프레임 전체의 합집합 경계로 한 번만 위치를 정해,
    PNG와 GIF가 픽셀 단위로 겹친다 (카드 크롭 데이터 spritebox 공유)
  - 애니메이션이 없거나 motion_reject.txt 에 있으면 idle_gif.squash(1px 숨쉬기)로 대체
출력: assets/creatures/{id}.png, assets/creatures/anim/{id}.gif
"""
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from idle_gif import SEQ, save_gif, squash  # noqa: E402

CANVAS, BOTTOM, LIMIT = 96, 11, 92
FRAME_MS = [520, 260, 260, 260, 260]  # 0번(원본)에서 잠깐 쉬고 1~4번 흔들림


def clean(im):
    im = im.convert('RGBA')
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            px[x, y] = (0, 0, 0, 0) if a < 40 else (r, g, b, 255)
    return im


def fetch(oid, cache):
    path = f'{cache}/{oid}.zip'
    if not os.path.exists(path):
        req = urllib.request.Request(f'https://api.pixellab.ai/mcp/objects/{oid}/download',
                                     headers={'Authorization': f'Bearer {os.environ["PIXELLAB_API_KEY"]}'})
        for wait in (2, 4, 8, 16, 0):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
                break
            except urllib.error.URLError:  # 프록시 터널 끊김: 백오프 후 재시도
                if not wait:
                    raise
                time.sleep(wait)
        with open(path, 'wb') as f:
            f.write(data)
    return zipfile.ZipFile(path)


def frames_from(z):
    names = z.namelist()
    base = clean(Image.open(io.BytesIO(z.read('rotations/unknown.png'))))
    groups = {}
    for n in names:
        if n.startswith('animations/') and n.endswith('.png'):
            groups.setdefault(n.split('/')[1], []).append(n)
    anim = []
    if groups:
        # card_idle 요청 묶음(설명이 'idle loop'로 시작). 시험용 묶음이 섞여 있어도 이것을 우선
        loops = sorted(k for k in groups if k.startswith('idle_loop'))
        key = loops[-1] if loops else sorted(groups)[-1]
        anim = [clean(Image.open(io.BytesIO(z.read(n)))) for n in sorted(groups[key])]
    return base, anim


def place(frames):
    box = None
    for f in frames:
        b = f.getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    w, h = box[2] - box[0], box[3] - box[1]
    s = min(1.0, LIMIT / w, LIMIT / h)
    out = []
    for f in frames:
        c = f.crop(box)
        if s < 1:
            c = c.resize((max(1, round(w * s)), max(1, round(h * s))), Image.NEAREST)
        can = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
        can.alpha_composite(c, ((CANVAS - c.width) // 2, max(2, CANVAS - BOTTOM - c.height)))
        out.append(can)
    return out


def main():
    repo, cache = sys.argv[1], sys.argv[2]
    only = set(sys.argv[3:])
    os.makedirs(cache, exist_ok=True)
    objs = json.load(open(f'{repo}/tools/pixellab/objects.json'))
    rej_path = f'{repo}/tools/pixellab/motion_reject.txt'  # 검수 불합격(얼굴 변형·소품 생김 등) → 1px 숨쉬기
    reject = set(open(rej_path).read().split()) if os.path.exists(rej_path) else set()
    fallback = []
    for cid, oid in sorted(objs.items()):
        if only and cid not in only:
            continue
        base, anim = frames_from(fetch(oid, cache))
        if len(anim) >= 2 and cid not in reject:
            placed = place([base] + anim)
            still, gif, ms = placed[0], placed[1:], FRAME_MS[:len(placed) - 1]
            if len(gif) != len(ms):
                ms = [260] * len(gif)
        else:
            still = place([base])[0]
            gif, ms = [squash(still, px) for px, _ in SEQ], [d for _, d in SEQ]
            fallback.append(cid)
        still.save(f'{repo}/assets/creatures/{cid}.png')
        save_gif(gif, ms, f'{repo}/assets/creatures/anim/{cid}.gif')
        print('ok', cid, 'anim' if cid not in fallback else 'squash')
    print('fallback(squash):', ' '.join(fallback) or '-')


if __name__ == '__main__':
    main()
