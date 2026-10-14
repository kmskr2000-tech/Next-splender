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

## 대기 호흡 애니메이션 (sprite-gen Breathe)
sprite-gen v2.44.0 (Apache-2.0, https://github.com/aldegad/sprite-gen @ 87f25d3) 의 Breathe 레이어로 idle GIF를 굽는다.
```
python3 -m venv .sg && .sg/bin/pip install "git+https://github.com/aldegad/sprite-gen@87f25d314679cd57dd3d2a74aad39cf91d66cea2"
.sg/bin/python -I tools/sprites/breathe_idle.py .            # 전체
.sg/bin/python -I tools/sprites/breathe_idle.py . t2-002     # 일부
```
캔버스를 꽉 채운 스프라이트(rare-005, t3-010, t3-012)는 sprite-gen이 잘림을 거부해 기존 GIF를 유지한다.
