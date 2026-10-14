// Challenge mode scenarios. Each is a short puzzle with a goal:
// goal: { points } | { evolutions } | { bonusColors } | { special }
// maxTurns counts the human's turns. startTokens/startTableau set up the puzzle.

export const CHALLENGES = [
  {
    id: 'ch1',
    name: '첫 걸음',
    desc: '15턴 안에 10점 달성하기',
    goal: { points: 10 },
    maxTurns: 15,
    difficulty: 'easy',
    startTokens: { monster: 2, super: 2, hyper: 2, heal: 0, quick: 0, master: 0 },
    startTableau: [],
  },
  {
    id: 'ch2',
    name: '속전속결',
    desc: '10턴 안에 8점 달성하기',
    goal: { points: 8 },
    maxTurns: 10,
    difficulty: 'easy',
    startTokens: { monster: 3, super: 3, hyper: 0, heal: 0, quick: 0, master: 0 },
    startTableau: [],
  },
  {
    id: 'ch3',
    name: '성장의 길',
    desc: '20턴 안에 3회 성장시키기',
    goal: { evolutions: 3 },
    maxTurns: 20,
    difficulty: 'normal',
    startTokens: { monster: 1, super: 1, hyper: 1, heal: 1, quick: 1, master: 0 },
    startTableau: [],
  },
  {
    id: 'ch4',
    name: '오보(五寶) 가호',
    desc: '18턴 안에 노리개·나전함·복주머니·청자·백자 5종 보너스 모두 모으기',
    goal: { bonusColors: 5 },
    maxTurns: 18,
    difficulty: 'normal',
    startTokens: { monster: 2, super: 0, hyper: 2, heal: 0, quick: 2, master: 0 },
    startTableau: [],
  },
  {
    id: 'ch5',
    name: '설화 수집',
    desc: '25턴 안에 희귀·전설 2장 영입하기',
    goal: { special: 2 },
    maxTurns: 25,
    difficulty: 'normal',
    startTokens: { monster: 2, super: 2, hyper: 2, heal: 2, quick: 1, master: 1 },
    startTableau: [],
  },
  {
    id: 'ch6',
    name: '천하제일의 증명',
    desc: '어려움 AI 상대로 20턴 안에 12점 달성하기',
    goal: { points: 12 },
    maxTurns: 20,
    difficulty: 'hard',
    startTokens: { monster: 2, super: 2, hyper: 2, heal: 2, quick: 2, master: 0 },
    startTableau: [],
  },
];

export function challengeProgress(challenge, ctrl, getPoints, bonusList) {
  const me = ctrl.me;
  const g = challenge.goal;
  if (g.points != null) return { cur: getPoints(me), target: g.points, label: '점' };
  if (g.evolutions != null) return { cur: me.evolved.length, target: g.evolutions, label: '성장' };
  if (g.bonusColors != null) {
    const colors = new Set();
    for (const card of me.tableau) for (const b of bonusList(card)) colors.add(b);
    return { cur: colors.size, target: g.bonusColors, label: '종류' };
  }
  if (g.special != null) {
    const n = me.tableau.filter((c) => c.tier === 'rare' || c.tier === 'legend').length;
    return { cur: n, target: g.special, label: '장' };
  }
  return { cur: 0, target: 1, label: '' };
}

export function challengeWon(challenge, ctrl, getPoints, bonusList) {
  const p = challengeProgress(challenge, ctrl, getPoints, bonusList);
  return p.cur >= p.target;
}
