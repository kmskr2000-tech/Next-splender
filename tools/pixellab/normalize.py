"""PixelLab 결과 PNG를 카드용 96x96 투명 스프라이트로 정규화한다.

사용: python -I tools/pixellab/normalize.py <src_dir> <repo_root>
  src_dir 안의 {card_id}.png 를 읽어 assets/creatures/{card_id}.png 로 저장.
  - 알파 경계로 크롭 → 96x96 캔버스 가운데, 바닥 여백 11px (기존 생성기와 동일)
  - 96px를 넘으면 정수 배율 축소 없이 nearest로 맞춤(도트 보존 우선, 드묾)
"""
import sys
from pathlib import Path
from PIL import Image

CANVAS = 96
BOTTOM = 11


def normalize(im: Image.Image) -> Image.Image:
    im = im.convert('RGBA')
    # 반투명 가장자리 잡티 제거: 알파 낮은 픽셀은 투명 처리
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 40:
                px[x, y] = (0, 0, 0, 0)
            elif a < 255:
                px[x, y] = (r, g, b, 255)
    box = im.getbbox()
    if not box:
        raise ValueError('empty image')
    c = im.crop(box)
    limit = CANVAS - 4
    if c.width > limit or c.height > limit:
        s = min(limit / c.width, limit / c.height)
        c = c.resize((max(1, round(c.width * s)), max(1, round(c.height * s))), Image.NEAREST)
    out = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    y = max(2, CANVAS - BOTTOM - c.height)
    out.alpha_composite(c, ((CANVAS - c.width) // 2, y))
    return out


def main(src: str, root: str) -> None:
    dst = Path(root) / 'assets' / 'creatures'
    for p in sorted(Path(src).glob('*.png')):
        normalize(Image.open(p)).save(dst / p.name)
        print('ok', p.stem)


if __name__ == '__main__':
    main(*sys.argv[1:3])
