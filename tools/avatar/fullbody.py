"""꾸미기 아바타 전신화 (D28): 64x64 상반신 파츠 아래에 하체(64x96 캔버스의 64~95행)를 도트로 그린다.
PixelLab 생성량 소진으로 직접 그림. 옷 아랫단 색은 각 옷 파츠의 맨 아래 줄에서 뽑아 이어 붙인다.
출력 (assets/avatar):
  legs_<style>.png  색을 바꾸지 않는 부분(바지·버선·신·바지 끈)  style = pants | robe | armor
  hands_<style>.png 손 (옷자락 위에 그린다)
  hem_<cloth>.png   옷 색을 따라가는 부분(저고리 아랫단·도포 자락·갑옷 치마) → 옷 색(tint) 필터를 같이 받는다
usage: python -I tools/avatar/fullbody.py <repo>
"""
import sys
from PIL import Image

R = sys.argv[1] if len(sys.argv) > 1 else '.'
A = f'{R}/assets/avatar'
W, H = 64, 96
OUT = (3, 3, 4, 255)
SKIN, SKIN_D = (254, 212, 187, 255), (226, 168, 140, 255)
STYLE = {'base': 'pants', 'hanbok': 'pants', 'saekdong': 'pants', 'dopo': 'robe', 'gwanbok': 'robe', 'armor': 'armor'}


def load(name):
    im = Image.open(f'{A}/{name}.png').convert('RGBA')
    c = Image.new('RGBA', (W, H)); c.alpha_composite(im, (0, 0)); return c


def shade(c, k):
    return (max(0, int(c[0] * k)), max(0, int(c[1] * k)), max(0, int(c[2] * k)), 255)


def bottom_row(img):
    """맨 아래 줄(63행)의 색과 좌우 끝."""
    px = img.load(); row = [px[x, 63] for x in range(W)]
    xs = [x for x in range(W) if row[x][3] > 128]
    return row, (min(xs), max(xs)) if xs else (13, 50)


def put(px, x, y, c):
    if 0 <= x < W and 0 <= y < H: px[x, y] = c


def outline(img):
    """불투명 픽셀 둘레에 1px 외곽선."""
    px = img.load(); src = img.copy().load()
    for y in range(64, H):
        for x in range(W):
            if src[x, y][3] > 0: continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 64 <= ny < H and src[nx, ny][3] > 0 and src[nx, ny] != OUT:
                    px[x, y] = OUT; break


def hem(cloth, style):
    """옷 색 부분. 63행 색을 기준으로 아래로 이어 그림."""
    img = load(f'cloth_{cloth}') if cloth != 'base' else load('base')
    row, (x0, x1) = bottom_row(img)
    out = Image.new('RGBA', (W, H)); px = out.load()
    body = [c for c in row[x0 + 2:x1 - 1] if c[3] > 128 and sum(c[:3]) > 60]
    main = max(set(body), key=body.count) if body else (200, 200, 200, 255)
    if style == 'pants':  # 저고리 아랫단 4줄: 63행 무늬를 그대로 내리고 맨 아래는 어두운 단
        for y in range(64, 68):
            for x in range(x0 + 1, x1):
                c = row[x] if row[x][3] > 128 else main
                put(px, x, y, shade(c, .82) if y == 67 else c)
    elif style == 'robe':  # 발목까지 내려오는 자락: 아래로 갈수록 넓어지고, 가장자리와 아래가 어둡다
        for y in range(64, 89):
            t = (y - 64) / 24; l = x0 + 1 - int(t * 4); r = x1 - 1 + int(t * 4)
            for x in range(l, r + 1):
                edge = min(x - l, r - x)
                k = .78 if edge < 2 else (.9 if edge < 4 else 1.0)
                if y >= 86: k = .62  # 아랫단 테두리
                c = shade(main, k)
                if x in (31, 32) and y < 86: c = shade(main, .7)  # 앞섶 선
                put(px, x, y, c)
    else:  # armor: 비늘 갑옷 치마 13줄, 3줄마다 어두운 띠 + 금 징
        for y in range(64, 77):
            tp = (y - 64) // 3
            for x in range(x0 + 1 + tp, x1 - tp):
                c = main if (y - 64) % 3 else shade(main, .55)
                if (y - 64) % 3 == 1 and (x - x0) % 5 == 2: c = (237, 182, 79, 255)
                put(px, x, y, c)
    outline(out)
    return out


def legs(style):
    """색 고정 부분: 바지·버선·신·손."""
    out = Image.new('RGBA', (W, H)); px = out.load()
    if style == 'pants':
        WHITE, WHITE_D, TIE = (244, 242, 236, 255), (200, 197, 190, 255), (150, 152, 164, 255)
        for y in range(68, 86):  # 넉넉한 바지 두 가랑이
            spread = 1 if y < 78 else 0
            for (l, r) in ((19 - spread, 30), (33, 44 + spread)):
                for x in range(l, r + 1):
                    c = WHITE_D if x in (l, l + 1, r) or y >= 83 else WHITE
                    put(px, x, y, c)
        for (l, r) in ((21, 28), (35, 42)):
            for x in range(l, r + 1): put(px, x, 84, TIE); put(px, x, 85, TIE)
        feet(px, WHITE)
    elif style == 'robe':
        feet(px, None)
    else:
        PANT, PANT_D = (58, 52, 64, 255), (40, 36, 46, 255)
        for y in range(77, 86):
            for (l, r) in ((21, 29), (34, 42)):
                for x in range(l, r + 1): put(px, x, y, PANT_D if x in (l, r) else PANT)
        for y in range(84, 92):  # 가죽 장화
            for (l, r) in ((20, 29), (34, 43)):
                for x in range(l - (1 if y > 89 else 0), r + 1): put(px, x, y, (52, 34, 26, 255) if y < 90 else (30, 20, 16, 255))
    outline(out)
    return out


def hands_img(style):
    out = Image.new('RGBA', (W, H)); hands(out.load(), style); outline(out); return out


def feet(px, sock):
    """버선과 코가 살짝 들린 검은 신."""
    if sock:
        for y in range(86, 89):
            for (l, r) in ((22, 28), (35, 41)):
                for x in range(l, r + 1): put(px, x, y, sock)
    for y in range(89, 93):
        for (l, r) in ((20, 29), (34, 43)):
            for x in range(l, r + 1):
                put(px, x, y, (24, 22, 28, 255) if y < 92 else (8, 8, 10, 255))
        if y == 89: put(px, 19, y, (24, 22, 28, 255)); put(px, 44, y, (24, 22, 28, 255))


def hands(px, style):
    y0 = 66 if style != 'robe' else 70
    for (cx) in (13, 50):
        for y in range(y0, y0 + 5):
            for x in range(cx - 2, cx + 3):
                if (x - cx) ** 2 + (y - y0 - 2) ** 2 <= 6: put(px, x, y, SKIN_D if y == y0 + 4 or x == cx + (2 if cx > 32 else -2) else SKIN)


def main():
    for st in ('pants', 'robe', 'armor'):
        legs(st).save(f'{A}/legs_{st}.png')
        hands_img(st).save(f'{A}/hands_{st}.png')
    for cloth, st in STYLE.items():
        hem(cloth, st).save(f'{A}/hem_{cloth}.png')
    print('ok')


if __name__ == '__main__':
    main()
