"""카드 속 '살짝살짝' 대기 모션 GIF를 정적 스프라이트에서 굽는다 (PIL만 사용).

픽셀을 새로 그리지 않고 원본 도트를 1px 단위로만 움직여 얼굴·형태가 변하지 않는다.
  - 숨쉬기: 몸 윗부분(머리~가슴)을 1px 눌렀다 펴기 (발은 고정)
  - 카드 안의 위아래 흔들림은 CSS(.card .art .sprite)가 따로 맡는다

usage: python -I tools/pixellab/idle_gif.py <repo> [card_id ...]
출력: assets/creatures/anim/{id}.gif  (96x96, 투명, 무한 루프)
"""
import glob
import os
import sys

from PIL import Image

REPO = sys.argv[1] if len(sys.argv) > 1 else '.'
ONLY = set(sys.argv[2:])
# (squash px, 지속 ms) — 한 호흡 ≈ 1.8s, 끝에 잠깐 멈춤
SEQ = [(0, 420), (1, 260), (1, 420), (0, 260), (0, 500)]
PIVOT = 0.62  # bbox 위에서부터 이 비율까지가 숨쉬며 눌리는 윗몸


def squash(im: Image.Image, px: int) -> Image.Image:
    if px == 0:
        return im.copy()
    box = im.getbbox()
    if not box:
        return im.copy()
    x0, y0, x1, y1 = box
    pivot = y0 + int((y1 - y0) * PIVOT)
    top = im.crop((0, y0, im.width, pivot))
    out = im.copy()
    out.paste((0, 0, 0, 0), (0, y0, im.width, pivot))
    # 윗몸을 px만큼 아래로 내리고, 가슴 경계 행은 원본 그대로 유지(목 끊김 방지)
    out.alpha_composite(top.crop((0, 0, im.width, top.height - px)), (0, y0 + px))
    return out


def save_gif(frames, durations, path):
    """공유 팔레트, 인덱스 0 = 투명."""
    w, h = frames[0].size
    strip = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.alpha_composite(f, (i * w, 0))
    rgb = Image.new('RGB', strip.size, (0, 0, 0))
    rgb.paste(strip.convert('RGB'), mask=strip.split()[3])
    pal = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT).getpalette()[:255 * 3]
    shared = Image.new('P', (1, 1))
    shared.putpalette([255, 0, 255] + pal)
    out = []
    for f in frames:
        q = f.convert('RGB').quantize(palette=shared, dither=Image.Dither.NONE)
        qa, alpha = q.load(), f.split()[3].load()
        for y in range(h):
            for x in range(w):
                if alpha[x, y] < 128:
                    qa[x, y] = 0
                elif qa[x, y] == 0:
                    qa[x, y] = 1
        out.append(q)
    out[0].save(path, save_all=True, append_images=out[1:], duration=durations, loop=0,
                transparency=0, disposal=2, optimize=False)


def main():
    n = 0
    for p in sorted(glob.glob(f'{REPO}/assets/creatures/*.png')):
        cid = os.path.basename(p)[:-4]
        if ONLY and cid not in ONLY:
            continue
        still = Image.open(p).convert('RGBA')
        frames = [squash(still, px) for px, _ in SEQ]
        save_gif(frames, [ms for _, ms in SEQ], f'{REPO}/assets/creatures/anim/{cid}.gif')
        n += 1
    print('baked', n)


if __name__ == '__main__':
    main()
