#!/usr/bin/env python3
"""Pick-up items are held and used on demand (roller, turret), paced fairly; the count is a sound effect and the announcer only calls Go. On top of ui35_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui35_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ----- the count: a sound effect for 3, 2, 1; the announcer only calls Go
rep("if (n > 0) { showCount(String(n)); AU.cd(n); AU.say('cd' + n, 0.9); buzz(8);", "if (n > 0) { showCount(String(n)); AU.cd(n); buzz(8);")
rep("for (const k of ['ready', 'cd3', 'cd2', 'cd1', 'go']) AU.say(k, 0);", "for (const k of ['ready', 'go']) AU.say(k, 0);")
rep("    cd(n) { return P_('cd' + Math.min(3, Math.max(1, n | 0)), { vary: 0 }); },", "    cd(n) { return P_('cd' + Math.min(3, Math.max(1, n | 0)), { vary: 0, v: 1.25 }); },")

# ----- the items: held, used when you choose
rep("const PU = {\n  roller: { name: 'Roller', dur: 9, tip: 'Roller! Wide stripes for 9 seconds. Paint refilled.' },",
    "const PU = {\n  roller: { name: 'Roller', dur: 9, tip: 'Roller! Wide stripes for 9 seconds. Paint refilled.' },\n  turret: { name: 'Turret', dur: 7, tip: 'Turret! Plant and fire paint for 7 seconds.' },")
# the turret pick-up: the turret's own base and barrel, small, in the bubble
rep("  else { add(PU_G.tip, puIconMat, V(0, -0.13, 0), [Math.PI, 0, 0]); add(PU_G.neck, puIconMat, V(0, 0.18, 0)); }\n  const bub = new THREE.Mesh(bubbleG, bubbleMat);",
    "  else if (type === 'turret') { const t = new THREE.Group(); t.position.y = -0.12; t.scale.setScalar(0.72); spin.add(t); for (const geo of [TURRET_RIG.baseG, TURRET_RIG.barrelG]) { const o = new THREE.Mesh(geo, rigSolidM); o.castShadow = true; t.add(o); const h = new THREE.Mesh(geo, outlineMat); h.scale.setScalar(1.12); t.add(h); } eyes = t; }\n  else { add(PU_G.tip, puIconMat, V(0, -0.13, 0), [Math.PI, 0, 0]); add(PU_G.neck, puIconMat, V(0, 0.18, 0)); }\n  const bub = new THREE.Mesh(bubbleG, bubbleMat);")
# the spawner replaces the fixed rollers and their 7-second respawns: one item on the stage at a time (two in a three-way), never
# more items about than there are players short of one, a breather after each pickup, and the spot leans toward whoever is behind
rep("""function placePowers() {
  powers.forEach(pw => pw.g && scene.remove(pw.g)); powers = [];
  POWER_SPOTS.filter(s => s[3]).forEach((s, i) => { const pw = { phase: i * 2.1 }; placePower(pw, s[3], s); powers.push(pw); });
}""", """const itemSpawn = { t: 7, last: null };
function placePowers() {
  powers.forEach(pw => pw.g && scene.remove(pw.g)); powers = []; itemSpawn.t = 6 + Math.random() * 3; itemSpawn.last = null;
}
function spawnItem() {
  const alive = ACTIVE.filter(D => D.st !== 'out');
  const spots = POWER_SPOTS.filter(sp => alive.every(D => Math.hypot(D.x - sp[0], D.z - sp[2]) > 5) && !powers.some(o => Math.hypot(o.x - sp[0], o.z - sp[2]) < 3));
  if (!spots.length) { itemSpawn.t = 2; return; }
  let trail = alive[0]; for (const D of alive) if (teamCov(D.team) < teamCov(trail.team)) trail = D;
  let best = null, bs = 1e9; for (const sp of spots) { const sc = Math.hypot(trail.x - sp[0], trail.z - sp[2]) + Math.random() * 9; if (sc < bs) { bs = sc; best = sp; } }
  const type = itemSpawn.last === 'roller' ? (Math.random() < 0.65 ? 'turret' : 'roller') : (Math.random() < 0.65 ? 'roller' : 'turret');
  const pw = { phase: Math.random() * 6, pop: 0, grace: 0, owner: null }; placePower(pw, type, best); powers.push(pw); itemSpawn.last = type; itemSpawn.t = 9 + Math.random() * 4;
  if (Math.hypot(P.x - best[0], P.z - best[2]) < 16) AU.spot();
}
function itemTick(dt) {
  const alive = ACTIVE.filter(D => D.st !== 'out'), busy = alive.filter(D => D.held || D.power || D.turret).length, cap = mode === 'trio' ? 2 : 1;
  itemSpawn.t -= dt;
  if (itemSpawn.t <= 0 && powers.length < cap && powers.length + busy < alive.length && matchLeft > 6) spawnItem();
  for (const pw of powers) { if (pw.pop < 1) pw.pop = Math.min(1, pw.pop + dt * 3); if (pw.grace > 0) pw.grace -= dt; }
}
// what you hold goes back on the stage when you pick up something else, dropped just behind you
function dropHeld(D) {
  const x = D.x - Math.sin(D.yaw) * 1.1, z = D.z - Math.cos(D.yaw) * 1.1, gy = surfaceUnder(x, z, D.y + 0.5, true);
  const pw = { phase: Math.random() * 6, pop: 0, grace: 2.5, owner: D }; placePower(pw, D.held, [x, gy > -Infinity ? gy : D.y, z]); powers.push(pw); D.held = null;
}
// using what you hold: the roller rolls, the turret plants (on the ground)
function useHeld(D) {
  if (!D.held || D.st !== 'play' || D.flatT > 0 || D.stunT > 0 || D.rocket || D.turret || D.giantT > 0 || D.knockT > 0) return false;
  const type = D.held; if (type === 'turret' && D.air) return false;
  D.held = null; D.heldT = 0;
  if (type === 'turret') { startTurret(D); for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; return true; }
  D.paint = 1; burst2(D, 16); D.power = { type, t: PU[type].dur }; emote(D, 'glee', 0.9);
  if (D === P) { shake = Math.max(shake, 0.08); AU.power(); buzz(15); banner('Roller!', 'Wide stripes. Paint refilled'); } else if (hearable(D)) AU.power();
  for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0;
  return true;
}""")
rep("""function respawnPower(pw) {
  const free = POWER_SPOTS.filter(s => Math.hypot(s[0] - P.x, s[2] - P.z) > 8 && !powers.some(o => o !== pw && o.g && Math.hypot(o.x - s[0], o.z - s[2]) < 3));
  const s = free.length ? free[(Math.random() * free.length) | 0] : POWER_SPOTS[0];
  placePower(pw, 'roller', s);
}
""", "")
# picking one up: it goes in hand
rep("""  scene.remove(pw.g); pw.g = null; pw.gone = 7;
  D.paint = 1; burst2(D, 16); D.power = { type, t: PU[type].dur }; emote(D, 'glee', 0.9);
  if (D === P) { shake = Math.max(shake, 0.08); AU.pop(); AU.power(); buzz(15); }
}""", """  scene.remove(pw.g); pw.g = null; const ix = powers.indexOf(pw); if (ix >= 0) powers.splice(ix, 1);
  if (D.held) dropHeld(D);
  D.held = type; D.heldT = 0; emote(D, 'glee', 0.6); itemSpawn.t = Math.max(itemSpawn.t, 8 + Math.random() * 4);
  if (D === P) { shake = Math.max(shake, 0.06); AU.pop(); buzz(12); hint('item', say('Got the ' + PU[type].name.toLowerCase() + '. Tap its button to use it', 'Got the ' + PU[type].name.toLowerCase() + '. Press F to use it'), 3.5); }
}""")
rep("if (D.st === 'play') for (const pw of powers) if (pw.g && Math.abs(D.y - pw.y) < 1.6 && Math.hypot(D.x - pw.x, D.z - pw.z) < 0.95) { collectPower(D, pw); break; }",
    "if (D.st === 'play') for (const pw of powers) if (pw.g && !(pw.grace > 0 && pw.owner === D) && Math.abs(D.y - pw.y) < 1.6 && Math.hypot(D.x - pw.x, D.z - pw.z) < 0.95) { collectPower(D, pw); break; }")
rep("  for (const pw of powers) { if (!pw.g && pw.gone > 0) { pw.gone -= dt; if (pw.gone <= 0) respawnPower(pw); } else if (pw.g && pw.pop < 1) pw.pop = Math.min(1, pw.pop + dt * 3); }",
    "  itemTick(dt);")
rep("  for (const D of [P, H, H2]) { D.slamCD = D.slamMax = SLAM_FIRST; D.wearOff = false; D.wearPop = 1; }", "  for (const D of [P, H, H2]) { D.slamCD = D.slamMax = SLAM_FIRST; D.wearOff = false; D.wearPop = 1; D.held = null; D.heldT = 0; }")
# the orb keeps the super moves; the turret is an item now
rep("const gift = window.__orbKind || ['giant', 'rocket', 'turret'][(Math.random() * 3) | 0];", "const gift = window.__orbKind || ['giant', 'rocket'][(Math.random() * 2) | 0];")
# the CPU: goes for an item only with its hands free; uses the roller once it is rolling on open ground, the turret when someone is in range or after a while
rep("  if (Math.random() < AI.grab) { let best = null, bd = 8; for (const pw of powers) { if (!pw.g) continue;", "  if (!D.held && Math.random() < AI.grab) { let best = null, bd = 8; for (const pw of powers) { if (!pw.g || (pw.grace > 0 && pw.owner === D)) continue;")
rep("  if (D.st === 'ko') { ai.path = null; ai.plan = null; ai.flight = null; ai.evadeT = 0; ai.attackT = 0; ai.wasRdy = false; return; }\n",
    """  if (D.st === 'ko') { ai.path = null; ai.plan = null; ai.flight = null; ai.evadeT = 0; ai.attackT = 0; ai.wasRdy = false; return; }
  if (D.held && D.st === 'play') { D.heldT = (D.heldT || 0) + dt; const O = other(D), near = O && O.st === 'play' && Math.hypot(O.x - D.x, O.z - D.z) < TURRET_FAR * 0.75;
    if (!D.air && !D.charging && (D.held === 'turret' ? (near && D.heldT > 0.6) || D.heldT > 6 : D.heldT > 1 + Math.random() * 1.5)) useHeld(D); }
""")
# the button, and the key
rep("""<button class="slamBtn" id="slamBtn" type="button" aria-label="Ground pound" hidden>""",
    """<button class="itemBtn" id="itemBtn" type="button" aria-label="Use item" hidden></button><button class="slamBtn" id="slamBtn" type="button" aria-label="Ground pound" hidden>""")
rep("$('slamBtn').addEventListener('pointerdown', e => { e.preventDefault(); e.stopPropagation(); AU.init(); if (state === 'play') useSlam(P); });",
    """$('slamBtn').addEventListener('pointerdown', e => { e.preventDefault(); e.stopPropagation(); AU.init(); if (state === 'play') useSlam(P); });
const ITEM_ICON = { roller: '<svg viewBox="0 0 40 40" aria-hidden="true"><rect x="5" y="9" width="30" height="13" rx="6.5"/><path d="M20 22v7h7" fill="none" stroke-width="3.2" stroke-linecap="round"/><rect x="25" y="27" width="7" height="9" rx="2"/></svg>', turret: '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M7 30a13 13 0 0 1 26 0z"/><path d="M20 20L33 9" fill="none" stroke-width="5" stroke-linecap="round"/><circle cx="20" cy="21" r="4.5"/></svg>' };
$('itemBtn').addEventListener('pointerdown', e => { e.preventDefault(); e.stopPropagation(); AU.init(); if (state === 'play' && !useHeld(P)) { AU.nope(); kick($('itemBtn'), 'nope'); } });
$('itemBtn').addEventListener('click', e => { e.preventDefault(); if (state === 'play' && e.detail === 0) useHeld(P); });""")
rep("  if ((k === 'e' || k === 'E') && !e.repeat) { e.preventDefault(); if (state === 'play') useSlam(P); return; }",
    "  if ((k === 'e' || k === 'E') && !e.repeat) { e.preventDefault(); if (state === 'play') useSlam(P); return; }\n  if ((k === 'f' || k === 'F') && !e.repeat) { e.preventDefault(); if (state === 'play' && !useHeld(P)) AU.nope(); return; }")
# the HUD keeps the button in step with what you hold
rep("  const pwc = $('pw');\n", """  { const ib = $('itemBtn'), held = state === 'play' && P.st === 'play' ? P.held : null; if (ib.hidden === !!held) ib.hidden = !held;
    if (held && ib.dataset.k !== held) { ib.dataset.k = held; ib.innerHTML = '<i class="sdisc" aria-hidden="true"></i>' + ITEM_ICON[held] + '<span class="ilbl">' + PU[held].name + '</span>'; ib.setAttribute('aria-label', 'Use the ' + PU[held].name.toLowerCase()); restartCls(ib, 'in'); } else if (!held) ib.dataset.k = ''; }
  const pwc = $('pw');
""")
css = '''
/* the item button: what you are holding, on a cream sticker by the pound button; tap it when you want it */
.itemBtn{position:absolute;left:max(22px,calc(env(safe-area-inset-left) + 14px));bottom:max(24px,calc(env(safe-area-inset-bottom) + 16px));width:80px;height:80px;padding:0;border:0;border-radius:50%;background:none;cursor:pointer;pointer-events:auto;display:grid;place-items:center;filter:drop-shadow(4px 6px 0 rgba(23,19,32,.3));z-index:5;-webkit-tap-highlight-color:transparent;touch-action:none}
.itemBtn .sdisc{position:absolute;inset:0;border-radius:50%;background:radial-gradient(circle at 36% 30%,#FFFCF5,#F3EBDC 62%,#D8CCB6);-webkit-mask:url(art/m_dot.webp) center/100% 100% no-repeat;mask:url(art/m_dot.webp) center/100% 100% no-repeat}
.itemBtn svg{position:relative;z-index:1;width:38px;height:38px;fill:var(--ink);stroke:var(--black);stroke-width:1.6;stroke-linejoin:round;margin-top:-12px;filter:drop-shadow(0 2px 0 rgba(0,0,0,.25))}
.itemBtn .ilbl{position:absolute;left:50%;bottom:13px;transform:translateX(-50%);z-index:1;font:900 10px/1 var(--font-head);font-style:italic;text-transform:uppercase;letter-spacing:.08em;color:var(--black);white-space:nowrap}
.itemBtn.in{animation:slamin .4s cubic-bezier(.3,1.7,.5,1),itemglow 1.6s ease-in-out .4s infinite}
@keyframes itemglow{50%{filter:drop-shadow(4px 6px 0 rgba(23,19,32,.3)) drop-shadow(0 0 12px rgba(var(--ink-rgb),.8))}}
.itemBtn:active{transform:translateY(3px) scale(.95)}
.itemBtn.nope{animation:nope .35s}
.hud.off .itemBtn{pointer-events:none;opacity:0}
@media (max-height:520px) and (min-aspect-ratio:1/1){.itemBtn{left:auto;right:max(156px,calc(env(safe-area-inset-right) + 148px));bottom:max(22px,calc(env(safe-area-inset-bottom) + 14px));width:70px;height:70px}.itemBtn svg{width:34px;height:34px;margin-top:-10px}.itemBtn .ilbl{bottom:11px;font-size:9px}}
@media (prefers-reduced-motion:reduce){.itemBtn.in,.itemBtn.nope{animation:none}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]
rep('<p class="ver">Version 105</p>', '<p class="ver">Version 106</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
