"""v468: no weather any more; the heat is a special stroke, Heat Stroke; Weather Repel (the umbrella) is gone.

- The user: "Remove the rain and heat effects. Make Heat Stroke a special stroke instead. And remove umbrella. Because rain is gone.
  Heat doesn't "dry paint" anymore".
- Matches no longer have weather: no rain (no wet floor, puddles or watered-down paint) and no random heat wave. The second match's
  sun and rain tips are gone with them. Online, the server's weather is ignored too.
- Heat Stroke, a new special stroke (rank 4, 450 dabs): use it and the sun comes out over everyone else for 6 seconds, after a
  1.5 second warning. Rivals caught out in the open burn their paint dry (as the sun did); a basin, the shade, a rocket or being a
  giant keep them safe. You and your teammate are never touched. Unlike the old heat wave it no longer hardens the paint on the floor.
  CPUs use it too. Its orb button reads "Heat".
- Weather Repel is taken off the Strokes page. Anyone who had it gets its 300 dabs back and Swim faster on in its place. Swim faster's
  card no longer talks about rain.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HEAT_SVG = ("data:image/svg+xml," + "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
  "%3Cg stroke='%23171320' stroke-width='3' stroke-linejoin='round'%3E"
  "%3Cpath d='M32 3l4 9h-8zM32 61l-4-9h8zM3 32l9-4v8zM61 32l-9 4v-8zM11.5 11.5l9.2 3.4-5.8 5.8zM52.5 52.5l-9.2-3.4 5.8-5.8zM52.5 11.5l-3.4 9.2-5.8-5.8zM11.5 52.5l3.4-9.2 5.8 5.8z' fill='%23FF8A1F'/%3E"
  "%3Ccircle cx='32' cy='32' r='15' fill='%23FFC93C'/%3E%3C/g%3E"
  "%3Cpath d='M25 30q3-3 6 0M33 30q3-3 6 0' fill='none' stroke='%23171320' stroke-width='2.6' stroke-linecap='round'/%3E"
  "%3Cpath d='M26 37q6 5 12 0' fill='none' stroke='%23171320' stroke-width='2.6' stroke-linecap='round'/%3E"
  "%3Cpath d='M44 20c3 4 3 7 0 9-3-2-3-5 0-9z' fill='%237CC8FF' stroke='%23171320' stroke-width='1.8'/%3E%3C/svg%3E")

HEAT_JS = r"""
// ---------- (v468) Heat Stroke: the sun comes out over everyone but you and your team. Out in the open they burn their paint dry;
// a basin, the shade, a rocket or being a giant keeps them safe. It doesn't harden the paint on the floor ----------
let heatBy = null; const HEAT_WARN = 1.5, HEAT_T = 6;
const heatSafe = D => !!heatBy && (D === heatBy || ally(D, heatBy));
function startHeat(D) {
  heatBy = D; setWx('warn', HEAT_WARN); D.wob = 1; D.squash = 0.75; emote(D, 'glee', 1.2); AU.heatWarn();
  if (D === P) { shake = Math.max(shake, 0.12); buzz([10, 30, 10]); banner('Heat stroke!', 'Rivals out in the open dry up'); }
  else if (ally(D, P)) banner(nameOf(D) + '’s heat stroke!', 'It burns your rivals');
  else { banner(nameOf(D) + '’s heat stroke!', 'Hide in a ' + potWord() + ' or the shade'); AU.spot && AU.spot(); }
  for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0;
}
"""

UPDATE_NEW = """function updateWeather(dt) {
  wxLeft -= dt; if (wxLeft > 0) return;
  // (v468) no weather of its own any more: the sun only comes out for a Heat Stroke, and it never hardens the paint
  if (wxPhase === 'warn') { setWx('sun', HEAT_T); sunsSeen++; AU.heatOn(); flashScreen(); }
  else if (wxPhase === 'sun') { setWx('dusk', 1.2); AU.dusk(); }
  else { heatBy = null; setWx('clear', 1e9); }
}"""

def apply(s):
    i = s.index("function updateWeather(dt) {"); j = s.index("\nfunction stepBlob(D, dt) {", i)
    s = s[:i] + UPDATE_NEW + s[j:]
    s = rep(s, "if (NM) netWeather(); else updateWeather(dt);", "updateWeather(dt); /* (v468: the server's weather is ignored) */")
    s = rep(s, "D.exposed = wxPhase === 'sun' && !D.air && D.skill !== 'repel'", "D.exposed = wxPhase === 'sun' && !heatSafe(D) && !D.air")
    s = rep(s, "const sunny = wxPhase === 'sun' || (wxPhase === 'warn' && SUN_WARN - wxLeft >= AI.warnReact);",
               "const sunny = !heatSafe(D) && (wxPhase === 'sun' || wxPhase === 'warn'); // (v468: the warning's short now)")
    s = rep(s, "function startFreeze(D) {", HEAT_JS.strip() + "\nfunction startFreeze(D) {")
    s = rep(s, "  if (gift === 'freeze') { startFreeze(D); return; }", "  if (gift === 'heat') { startHeat(D); return; } // (v468)\n  if (gift === 'freeze') { startFreeze(D); return; }")
    s = rep(s, "r < 0.46 ? (r < 0.15 ? 'freeze' : r < 0.31 ? 'storm' : 'bomb')", "r < 0.5 ? (r < 0.12 ? 'freeze' : r < 0.24 ? 'storm' : r < 0.37 ? 'heat' : 'bomb')")
    s = rep(s, "ORB_LBL = { rocket: 'Rocket', giant: 'Giant', freeze: 'Freeze', storm: 'Storm', bomb: 'Bomb' }", "ORB_LBL = { rocket: 'Rocket', giant: 'Giant', freeze: 'Freeze', storm: 'Storm', bomb: 'Bomb', heat: 'Heat' }")
    # the second match: no sun or rain lesson
    s = rep(s, "if (matchLeft <= MATCH_T * 0.5 && !t.ms) { t.ph = 'sun';", "if (false) { t.ph = 'sun';")
    # the strokes: Heat Stroke in, Weather Repel out (refunded)
    s = rep(s, "does: ['You glide much faster than normal', 'Much faster in the rain, with a sure grip on the wet'] }", "does: ['You glide much faster than normal'] }")
    a = "const ST_STARTERS = ['rocket', 'swim', 'roller'];"
    s = rep(s, a,
        "SPECIALS.splice(SPECIALS.findIndex(x => x.id === 'storm'), 0, { id: 'heat', rank: 4, name: 'Heat Stroke', desc: 'Bring out the sun on your rivals: out in the open, their paint dries up.', does: ['A short warning, then the sun beats down for 6 seconds', 'Rivals out in the open burn their paint dry', 'A basin or the shade keeps them safe; you and your team never feel it'] }); // (v468)\n"
        "SKILLS.splice(SKILLS.findIndex(x => x.id === 'repel'), 1); // (v468: Weather Repel is gone with the weather)\n" + a)
    s = rep(s, "const ST_PRICE = { turret: 200,", "const ST_PRICE = { heat: 450, turret: 200,")
    a = "for (const k of ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets', 'storm', 'shock', 'bomb', 'pboost', 'jackpot']) STROKE_ICON[k] = stImg(k);"
    s = rep(s, a, a + "\nST_IMG.heat = \"" + HEAT_SVG + "\"; STROKE_ICON.heat = stImg('heat'); // (v468)")
    s = rep(s, "  if (!d.b370) {", "  if (!d.rp468) { d.rp468 = 1; if (d.own.includes('repel')) { d.own = d.own.filter(k => k !== 'repel'); store.drops = (store.drops || 0) + 300; } } // (v468: Weather Repel refunded)\n  if (!d.b370) {")
    return s
