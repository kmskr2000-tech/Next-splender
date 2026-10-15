"""PixelLab REST로 카드 오브젝트마다 대기 루프 애니메이션(v3, 4프레임, 약 1 generation)을 요청한다.

usage: python -I tools/pixellab/animate_all.py <repo> [card_id ...]
  - tools/pixellab/objects.json(card_id -> PixelLab object id)을 읽는다
  - 키는 env PIXELLAB_API_KEY 에서만 읽고 출력하지 않는다
  - 요청 결과는 tools/pixellab/anim_jobs.json 에 누적(이미 요청한 카드는 건너뜀)
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

REPO = sys.argv[1] if len(sys.argv) > 1 else '.'
ONLY = set(sys.argv[2:])
API = 'https://api.pixellab.ai/v2'
KEEP = 'face and eyes stay exactly the same, same colors, no new objects'
DESC = {
    'person': f'idle loop: whole body bobs down one pixel and back up, hair, hat ornaments and clothes sway slightly, {KEEP}',
    'creature': f'idle loop: gentle breathing, body bobs one pixel, tail, wings, whiskers or mane sway slightly, {KEEP}',
    'object': 'idle loop: gentle one pixel floating bob with a soft shimmer of light, shape and colors stay exactly the same',
}


def main():
    key = os.environ['PIXELLAB_API_KEY']
    objs = json.load(open(f'{REPO}/tools/pixellab/objects.json'))
    kinds = {c['id']: c['kind'] for c in json.load(open(f'{REPO}/docs/design/roster-korea.json'))['cards']}
    log_path = f'{REPO}/tools/pixellab/anim_jobs.json'
    log = json.load(open(log_path)) if os.path.exists(log_path) else {}
    for cid, oid in objs.items():
        if (ONLY and cid not in ONLY) or (not ONLY and cid in log):
            continue
        body = json.dumps({'animation_description': DESC[kinds[cid]], 'frame_count': 4,
                           'display_name': 'card_idle'}).encode()
        req = urllib.request.Request(f'{API}/objects/{oid}/animations', data=body, method='POST',
                                     headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
        for wait in (2, 4, 8, 16) + (30,) * 60:  # 429(동시 작업 한도)면 30초씩 기다리며 재시도
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    res = json.load(r)
                log[cid] = {'object': oid, 'group': res.get('animation_group_id'), 'status': 'queued'}
                print('queued', cid)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(30)
                    continue
                print('fail', cid, e.code, e.read()[:200].decode(errors='replace'))
                break
            except urllib.error.URLError as e:  # 프록시 연결 끊김: 백오프 후 재시도
                print('retry', cid, e.reason)
                time.sleep(wait)
        time.sleep(1)
        json.dump(log, open(log_path, 'w'), indent=1)


if __name__ == '__main__':
    main()
