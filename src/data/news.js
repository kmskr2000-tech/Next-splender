// 로비 소식 배너 (D25). 왼쪽부터 순서대로 가로 스크롤. action 은 홈 버튼의 data-action 과 같다.
export const NEWS = [
  { id: 'season0', kicker: '랭킹전', title: '시범 시즌 0 진행 중', body: '배치고사 5판 뒤 첫 품계가 정해져요.', action: 'mode', mode: 'ranked', cls: 'n-red', art: 'legend-002' },
  { id: 'lines', kicker: '새 인물', title: '달토끼 · 해치 · 우투리 합류', body: '세 라인이 새 얼굴로 바뀌었어요.', action: 'dex', cls: 'n-jade', art: 't2-010' },
  { id: 'friendly', kicker: '친목전', title: '방 만들고 친구 초대', body: '방 제목·비밀번호·이모티콘 채팅.', action: 'mode', mode: 'friendly', cls: 'n-blue', art: 't2-011' },
  { id: 'look', kicker: '꾸미기', title: '나만의 도사 만들기', body: '머리·모자·표정·옷·색을 골라요.', action: 'profile', cls: 'n-gold', art: null },
];
