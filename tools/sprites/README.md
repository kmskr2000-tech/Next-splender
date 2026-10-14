# 도트 크리처 스프라이트 생성기

`docs/design/roster.json`(archetype, features, palette)로 96x96 스프라이트와 4프레임 idle GIF를 만든다.

```
pip install pillow
python -I tools/sprites/build.py tools/sprites .   # assets/creatures/{id}.png, anim/{id}.gif
python -I tools/sprites/items.py tools/sprites .   # assets/items/*.png (령주 6종)
python -I tools/sprites/contact.py . sheet.png     # 90장 미리보기
```

- `core.py`: 1px 캔버스, 구형 3단 셰이딩, 선택적 외곽선
- 아키타입 11종: feline canine hoofed bear critter serpent fish turtle bird spirit insect
- 단계: t1=0, t2=1, t3/rare/legend=2
python -I tools/sprites/spritebox.py .   # 스프라이트 변경 후 카드 크롭 데이터 재생성
