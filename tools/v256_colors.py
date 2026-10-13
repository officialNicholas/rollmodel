"""v256: colours. Everyone has a colour of their own: you, the one you picked; each rival, one it rolls each match (which can be the
same as yours). What a screen shows is worked out on that screen: you always see yourself in your own colour, and a rival in your
colour (or one too close to tell apart at a glance, or too like another rival's) is shown in the colour that stands furthest from the
rest, on your screen only. Online, each player would see themselves in their own colour the same way. In 2v2 each team wears one
colour: with CPUs, your teammate wears yours and the other pair wears its leader's own (kept well clear of yours); two people on one
team (online, later) would have their two colours mixed into the team's. The two teams never look alike."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
JS = r"""// ---------- (v256) colours: your own, the rivals' own, and what this screen shows of them (see v256_colors) ----------
const s2l = c => c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4), l2s = c => c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
function hexLab(h) { const r = s2l(((h >> 16) & 255) / 255), g = s2l(((h >> 8) & 255) / 255), b = s2l((h & 255) / 255);
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b), m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b), s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  return [0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s, 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s, 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s]; }
function labHex(L, a, b) { const l = Math.pow(L + 0.3963377774 * a + 0.2158037573 * b, 3), m = Math.pow(L - 0.1055613458 * a - 0.0638541728 * b, 3), s = Math.pow(L - 0.0894841775 * a - 1.2914855480 * b, 3);
  const q = v => Math.round(clamp(l2s(clamp(v, 0, 1)), 0, 1) * 255);
  return (q(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s) << 16) | (q(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s) << 8) | q(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s); }
const hexLch = h => { const [L, a, b] = hexLab(h); return [L, Math.hypot(a, b), Math.atan2(b, a)]; }, lchHex = (L, C, H) => labHex(L, C * Math.cos(H), C * Math.sin(H));
const colDist = (p, q) => { const a = hexLab(p), b = hexLab(q); return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]); };
const hexCss6 = h => '#' + h.toString(16).padStart(6, '0').toUpperCase();
function mkCol(hex) { const [L, C, H] = hexLch(hex); return { id: 'mix', hex, dry: lchHex(L * 0.6, C * 0.62, H), hi: hexCss6(lchHex(Math.min(0.94, L + 0.17), C * 0.72, H)), lo: hexCss6(lchHex(L * 0.68, C * 0.95, H)) }; }
// (how far apart two colours have to be: a rival against you or another rival, and one 2v2 team against the other)
const COL_SEP = 0.16, TEAM_SEP = 0.22;
const RIVAL_COLS = [...PALETTE.map(p => ({ id: p.id, hex: p.hex, dry: p.dry, hi: p.hi, lo: p.lo })),
  { id: 'blue', hex: 0x2E9BFF, dry: 0x1C5592, hi: '#7CC4FF', lo: '#1C5592', classic: 1 }, { id: 'violet', hex: 0x8E5CFF, dry: 0x46297F, hi: '#C4A8FF', lo: '#46297F', classic: 1 }, { id: 'teal', hex: 0x19C9A6, dry: 0x0E6B58, hi: '#7FE8D3', lo: '#0E6B58', classic: 1 }];
const rivalColOf = id => RIVAL_COLS.find(c => c.id === id);
let rivalCol = [null, rivalColOf('blue'), rivalColOf('violet'), rivalColOf('teal')], teamTint = false; // (each rival's own colour; teamTint: a match is on, so 2v2's team colours apply)
function rollRivalCols() { const pool = RIVAL_COLS.slice(); for (const i of [1, 2, 3]) rivalCol[i] = pool.splice((Math.random() * pool.length) | 0, 1)[0]; }
// a rival in your colour (or one too like it, or too like another rival's): the colour that stands furthest from all the others
function standApart(c, taken, sep = COL_SEP) { if (taken.every(t => colDist(t, c.hex) >= sep)) return c; let best = c, bd = -1; for (const o of RIVAL_COLS) { const d = Math.min(...taken.map(t => colDist(t, o.hex))) + (o.classic ? 0.015 : 0); if (d > bd) { bd = d; best = o; } } return best; }
// two colours mixed the way paint looks mixed: halfway round the colour wheel, as rich as the richer of the two
function mixCol(a, b) { if (a.hex === b.hex) return a; const [L1, C1, H1] = hexLch(a.hex), [L2, C2, H2] = hexLch(b.hex), d = Math.atan2(Math.sin(H2 - H1), Math.cos(H2 - H1)); return mkCol(lchHex(clamp((L1 + L2) / 2, 0.56, 0.8), Math.max(C1, C2) * 0.96, H1 + d / 2)); }
// a 2v2 team's colour. Two people on one team (online, later) mix theirs; a team with a CPU on it wears its person's colour, and a team
// of CPUs wears its leader's own. Only you count as a person for now.
const slotHuman = i => i === 0, slotCol = (i, mine) => i === 0 ? mine : rivalCol[i];
function teamCol(a, b, mine) { const ha = slotHuman(a), hb = slotHuman(b); return ha && hb ? mixCol(slotCol(a, mine), slotCol(b, mine)) : hb && !ha ? slotCol(b, mine) : slotCol(a, mine); }
// the second team's colour turned round the wheel until it's clearly not the first's
function teamApart(B, A) { if (colDist(B.hex, A.hex) >= TEAM_SEP) return B; const [L, C, H] = hexLch(B.hex); let best = B, bd = colDist(B.hex, A.hex); for (let k = 1; k <= 7; k++) for (const sg of [1, -1]) { const h = lchHex(L, Math.max(C, 0.16), H + sg * k * 0.42), d = colDist(h, A.hex); if (d > bd) { bd = d; best = mkCol(h); } if (bd >= TEAM_SEP) return best; } return best; }
// your colour on the canvas, the HUD and you: what setColor does, without changing your pick
function inkApply(c) {
  const css = hexCss6(c.hex);
  TEAMS[0].wet = c.hex; TEAMS[0].dry = c.dry; TEAMS[0].css = css; C.ink = c.hex;
  COL_INK.setHex(c.hex); TEAM_COLS[0].setHex(c.hex);
  paintUniforms.uWetA.value[0].setHex(c.hex); paintUniforms.uDryA.value[0].setHex(c.dry);
  teamMats[0].color.setHex(c.hex); splashMat.color.setHex(c.hex); xrayMat.color.setHex(c.hex); dropMat.color.setHex(c.hex);
  crownMats[0].color.setHex(c.hex); crownMats[0].emissive.setHex(c.hex).multiplyScalar(0.18);
  arrowMat.color.setHex(c.hex); puIconMat.color.setHex(c.hex); confMats[0].color.setHex(c.hex);
  CAN_INK_TOP.setHex(c.hex).multiplyScalar(0.86); CAN_EMPTY_TOP.setHex(c.hex).multiplyScalar(0.25);
  partPool(colMat(c.hex));
  const r = document.documentElement.style;
  r.setProperty('--ink', css); edgeRGB(css, EDGE.ink); r.setProperty('--ink-hi', c.hi); r.setProperty('--ink-lo', c.lo); r.setProperty('--ink-rgb', [(c.hex >> 16) & 255, (c.hex >> 8) & 255, c.hex & 255].join(','));
}
function teamHues() {
  const mine = colorOf(), show = [mine];
  if (mode === 'duo' && teamTint) { const A = teamCol(0, 3, mine), B = teamApart(standApart(teamCol(1, 2, mine), [A.hex], TEAM_SEP), A); show[0] = A; show[1] = B; show[2] = B; show[3] = A; }
  else { const taken = [mine.hex]; for (const i of [1, 2, 3]) { const c = standApart(rivalCol[i], taken); taken.push(c.hex); show[i] = c; } }
  if (TEAMS[0].wet !== show[0].hex) inkApply(show[0]);
  const Ls = [null, LH, L2, L3];
  for (const i of [1, 2, 3]) { const t = show[i], L = Ls[i];
    TEAMS[i].wet = t.hex; TEAMS[i].dry = t.dry; TEAMS[i].css = hexCss6(t.hex); TEAM_COLS[i].setHex(t.hex); paintUniforms.uWetA.value[i].setHex(t.hex); paintUniforms.uDryA.value[i].setHex(t.dry);
    teamMats[i].color.setHex(t.hex); crownMats[i].color.setHex(t.hex); crownMats[i].emissive.setHex(t.hex).multiplyScalar(0.18); L.col.setHex(t.hex); L.xrayMat.color.setHex(t.hex);
    const wc = new THREE.Color(t.hex).lerp(COL_WHITE, 0.5); L.warn.material.color.copy(wc); L.warnFill.material.color.copy(wc); if (L.warnBase) L.warnBase.copy(wc); partPool(colMat(t.hex)); }
  const r = document.documentElement.style; for (const [i, k] of [[1, 'holy'], [2, 'wolf'], [3, 'fox']]) { r.setProperty('--' + k, hexCss6(show[i].hex)); r.setProperty('--' + k + '-hi', show[i].hi); }
  recolorSplashes();
}
"""
CSS = """/* (v256) the score numbers and pause card follow each rival's colour for the match (they were fixed blue and violet) */
.vsn.cpu,.pscore .cpu{color:var(--holy)}
.vsn.cpu2{color:var(--wolf)}
.dot.holy{background:var(--holy)}
"""
def apply(s):
    a = s.index("// the rivals' colours: the third always stands apart from yours;")
    b = s.index("  recolorSplashes();\n}\n", a) + len("  recolorSplashes();\n}\n")
    old = s[a:b]; assert old.count('function teamHues()') == 1 and old.count('\n') == 14, old[:200]
    s = s[:a] + JS + s[b:]
    # (each match: the rivals roll their colours, and the match's colours apply; back in the lobby you're your own colour again)
    s = rep(s, "function rollRivalLooks() { const heads =", "function rollRivalLooks() { rollRivalCols(); teamTint = true; teamHues(); const heads =")
    s = rep(s, "  tutLeave(); clearShot(); $('gframe').hidden = true; $('gwall').hidden = true; pickRivalNames(); state = 'menu';",
               "  teamTint = false; tutLeave(); clearShot(); $('gframe').hidden = true; $('gwall').hidden = true; pickRivalNames(); state = 'menu';")
    s = rep(s, "\n</style>\n\n<div id=\"stage\">", "\n" + CSS.strip() + "\n</style>\n\n<div id=\"stage\">")
    return s
