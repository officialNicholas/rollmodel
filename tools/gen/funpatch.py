f='/home/claude/paint-the-canvas.html'; s=open(f).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n, (a[:90], s.count(a)); s=s.replace(a,b)

# ================= 1) floating platforms go see-through when you're under one =================
rep("  for (const o of stageGroup.children.slice()) { stageGroup.remove(o); o.geometry.dispose(); if (o.userData.own) o.material.dispose(); }",
    "  for (const o of stageGroup.children.slice()) { stageGroup.remove(o); o.geometry.dispose(); if (o.userData.own) o.material.dispose(); if (o.userData.ownMats) o.userData.ownMats.forEach(m => m.dispose()); }\n  floaters.length = 0;")
rep("""    const m = new THREE.Mesh(g, [woodMat, woodMat, canvasMat, woodDarkMat, woodMat, woodMat]); m.castShadow = true; m.receiveShadow = true; stageGroup.add(m);
    const o = new THREE.BoxGeometry(w + 0.14, h + 0.14, d + 0.14); o.translate(cx, cy, cz); hulls.push(o);""",
"""    const o = new THREE.BoxGeometry(w + 0.14, h + 0.14, d + 0.14); o.translate(cx, cy, cz);
    if (b[4] > 0) {
      // floating: its own see-through-able materials and outline, so it can fade out while you're under it
      const mats = [woodMat, woodMat, canvasMat, woodDarkMat, woodMat, woodMat].map(mm => { const c = mm.clone(); c.transparent = true; return c; });
      const m = new THREE.Mesh(g, mats); m.castShadow = true; m.receiveShadow = true; m.userData.ownMats = mats; stageGroup.add(m);
      const hm = new THREE.Mesh(o, new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true })); hm.userData.own = true; stageGroup.add(hm);
      floaters.push({ b, mats, hull: hm, k: 1, last: 1 });
    } else {
      const m = new THREE.Mesh(g, [woodMat, woodMat, canvasMat, woodDarkMat, woodMat, woodMat]); m.castShadow = true; m.receiveShadow = true; stageGroup.add(m);
      hulls.push(o);
    }""")
rep("const stageGroup = new THREE.Group(); scene.add(stageGroup);", "const stageGroup = new THREE.Group(); scene.add(stageGroup);\nconst floaters = [];")
rep("  MOVERS.forEach((m, i) => {\n    const g = moverMeshes[i];", """  // a platform overhead (or between the camera and you) fades out so you can see the ground under it, holes and all
  for (const f of floaters) {
    const b = f.b; let want = 1;
    if (drop.visible && (state === 'play' || state === 'paused')) {
      let hide = inR(P.x, P.z, b, 0.9) && P.y + 0.4 < b[4];
      for (let k = 1; k < 8 && !hide; k++) { tv1.lerpVectors(camera.position, drop.position, k / 8); if (tv1.y > b[4] - 0.1 && tv1.y < b[5] + 0.1 && inR(tv1.x, tv1.z, b, 0.15)) hide = true; }
      if (hide) want = 0.18;
    }
    f.k += (want - f.k) * Math.min(1, rdt * 9);
    if (Math.abs(f.k - f.last) > 0.004) { f.last = f.k; const solid = f.k > 0.97; for (const m of f.mats) { m.opacity = solid ? 1 : f.k; m.depthWrite = solid; } f.hull.material.opacity = f.k; f.hull.visible = f.k > 0.45; }
  }
  MOVERS.forEach((m, i) => {
    const g = moverMeshes[i];""")

# ================= 2) overtime on a tie, and lead changes called out =================
rep("const MATCH_T = 90,", "const OT_T = 10, MATCH_T = 90,")
rep("""  const you = teamCov(0), cpu = teamCov(1), id = runId, ry = Math.round(you), rc = Math.round(cpu), win = ry > rc ? 1 : rc > ry ? -1 : 0; // decided on the whole numbers everyone sees""",
"""  const you = teamCov(0), cpu = teamCov(1), id = runId, ry = Math.round(you), rc = Math.round(cpu), win = ry > rc ? 1 : rc > ry ? -1 : 0; // decided on the whole numbers everyone sees
  // dead even at the buzzer: ten more seconds, once
  if (!win && !overtimeUsed) { overtimeUsed = true; matchLeft = OT_T; lastCount = 99; banner('Overtime!', 'Dead even. ' + OT_T + ' more seconds.', true); AU.horn(); buzz([30, 40, 30]); return; }""")
rep("  runT = 0; matchLeft = MATCH_T; lastCount = 99;", "  runT = 0; matchLeft = MATCH_T; lastCount = 99; overtimeUsed = false; lastLead = 0; lastLeadT = -9; leadAcc = 0;")
rep("let lives = 1;", "let lives = 1, overtimeUsed = false, lastLead = 0, lastLeadT = -9, leadAcc = 0;")
rep("    const cnt = Math.ceil(matchLeft); if (cnt <= 5 && cnt !== lastCount && cnt > 0) { lastCount = cnt; AU.count(cnt); }",
"""    const cnt = Math.ceil(matchLeft); if (cnt <= 5 && cnt !== lastCount && cnt > 0) { lastCount = cnt; AU.count(cnt); }
    // who's ahead, called out when it flips
    leadAcc += dt; if (leadAcc > 0.3 && runT > 8) { leadAcc = 0; const a = Math.round(teamCov(0)), c = Math.round(teamCov(1)), ld = a > c ? 1 : c > a ? -1 : 0; if (ld && ld !== lastLead) { if (lastLead && clock - lastLeadT > 3) { popText(ld > 0 ? 'You take the lead!' : 'Holy water leads'); AU.lead(ld > 0); } lastLead = ld; lastLeadT = clock; } }""")
rep("    spot() {", "    lead(up) { if (up) [659, 880, 1175].forEach((f, i) => tone('triangle', f, 0, 0.12, 0.08, i * 0.06)); else [523, 415].forEach((f, i) => tone('triangle', f, 0, 0.16, 0.07, i * 0.09)); },\n    xp() { tone('triangle', 1200 + Math.random() * 300, 0, 0.05, 0.03); },\n    rankUp() { [523, 659, 784, 1047, 1319, 1568].forEach((f, i) => tone('triangle', f, 0, 0.2, 0.12, i * 0.07)); tone('sine', 1568, 0, 1.2, 0.06, 0.45, sfx, 0.01); },\n    spot() {")

# ================= 3) ranks, XP, streaks and bests =================
rep("""const save = () => { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} };""", """const save = () => { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} };
// ---------- ranks: every match earns blood (XP); keep climbing ----------
const RANKS = [['Fledgling', 0], ['Nightling', 300], ['Prowler', 800], ['Stalker', 1600], ['Night Stalker', 2800], ['Count', 4500], ['Elder', 7000], ['Ancient', 10000], ['Eternal', 15000]];
function rankOf(xp) { let i = 0; while (i + 1 < RANKS.length && xp >= RANKS[i + 1][1]) i++; const lo = RANKS[i][1], hi = RANKS[i + 1] ? RANKS[i + 1][1] : lo + 6000; return { i, name: RANKS[i][0], lo, hi, k: Math.min(1, (xp - lo) / (hi - lo)), next: RANKS[i + 1] ? RANKS[i + 1][0] : null }; }
const FLAME = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2c1 4 5 6 5 11a5 5 0 0 1-10 0c0-2 1-3.5 2-4.5 0 2 1 3 2 3-1-3 0-6 1-9.5z"/></svg>';""")
rep("""  store.runs = (store.runs || 0) + 1; save();""", """  store.runs = (store.runs || 0) + 1;
  // blood earned: playing, coverage, winning (more on harder holy water), knockouts and a win streak
  const mult = diff === 'hard' ? 1.5 : diff === 'easy' ? 0.6 : 1, xp0 = store.xp || 0;
  store.streak = win > 0 ? (store.streak || 0) + 1 : win < 0 ? 0 : (store.streak || 0); store.bestStreak = Math.max(store.bestStreak || 0, store.streak);
  const gained = Math.round((40 + you * 3 + (win > 0 ? 100 : win === 0 ? 30 : 0) + P.kos * 30) * mult + (win > 0 ? Math.min(5, store.streak - 1) * 20 : 0));
  store.xp = xp0 + gained;
  store.bestCov = store.bestCov || {}; const newBest = ry > (store.bestCov[diff] || 0); if (newBest) store.bestCov[diff] = ry;
  let dailyBest = null; if (daily) { const dk = dailyKey(); if (!store.daily || store.daily.date !== dk) store.daily = { date: dk, best: null, plays: 0 }; store.daily.plays++; const mg = ry - rc; if (store.daily.best === null || mg > store.daily.best) { store.daily.best = mg; dailyBest = mg; } }
  Object.assign(endInfo, { xp0, gained, newBest, streak: store.streak, dailyBest, daily });
  save();""")
rep("""  $('endNote').textContent = bits.join(' ');""", """  $('endNote').textContent = bits.join(' ');
  // the blood bar: fill up, and rank up if it gets there
  const { xp0, gained, newBest, streak } = endInfo, r0 = rankOf(xp0), r1 = rankOf(xp0 + gained), fill = $('xpFill');
  $('xpRank').textContent = r0.name; $('xpGain').textContent = '+0'; fill.style.transition = 'none'; fill.style.width = (r0.k * 100).toFixed(1) + '%';
  const notes = []; if (streak >= 2) notes.push(FLAME + '<span>' + streak + ' wins in a row</span>'); if (newBest) notes.push('<span class="pill">New best on ' + lv[1] + '</span>'); if (endInfo.daily) notes.push('<span>Tonight\\'s canvas: best ' + fmtMargin(store.daily.best) + '</span>');
  $('xpNote').innerHTML = notes.join(' ');
  const rid = runId; let shown = 0; const t0 = performance.now() + 450;
  const countUp = () => { if (rid !== runId || end.hidden) return; const k = Math.min(1, Math.max(0, (performance.now() - t0) / 1100)), v = Math.round(gained * (1 - Math.pow(1 - k, 3))); if (v !== shown) { if (v - shown >= 6 || k >= 1) AU.xp(); shown = v; $('xpGain').textContent = '+' + v + ' blood'; } if (k < 1) requestAnimationFrame(countUp); };
  requestAnimationFrame(countUp);
  setTimeout(() => {
    if (rid !== runId) return; fill.style.transition = '';
    if (r1.i > r0.i) { fill.style.width = '100%'; setTimeout(() => { if (rid !== runId) return; fill.style.transition = 'none'; fill.style.width = '0%'; $('xpRank').textContent = r1.name; kick($('xpRank'), 'up'); AU.rankUp(); confettiDom(); void fill.offsetWidth; fill.style.transition = ''; fill.style.width = (r1.k * 100).toFixed(1) + '%'; $('xpNote').insertAdjacentHTML('afterbegin', '<span class="pill">Rank up!</span> '); }, 1150); }
    else fill.style.width = (r1.k * 100).toFixed(1) + '%';
  }, 450);""")
rep("""        <div class="result"><p class="big" id="endPct">0%</p><span class="vsl">vs</span><p class="big cpu" id="endPctC">0%</p><span class="pill" id="endPill" hidden>New best</span></div>""",
"""        <div class="result"><p class="big" id="endPct">0%</p><span class="vsl">vs</span><p class="big cpu" id="endPctC">0%</p><span class="pill" id="endPill" hidden>New best</span></div>
        <div class="xp"><div class="xprow"><b id="xpRank">Fledgling</b><span id="xpGain">+0 blood</span></div><div class="xpbar"><i id="xpFill"></i></div><p class="xpnote" id="xpNote"></p></div>""")
rep("""    <div class="mhead"><h1 class="title">Paint the World <em>Red</em></h1></div>""", """    <div class="mhead"><h1 class="title">Paint the World <em>Red</em></h1></div>
    <div class="rankbar" id="rankBar"><div class="xprow"><b id="rkName">Fledgling</b><span id="rkInfo"></span></div><div class="xpbar"><i id="rkFill"></i></div></div>""")
rep(""".small .title{font-size:34px}""", """.small .title{font-size:34px}
/* ranks: the blood bar */
.xp,.rankbar{display:grid;gap:6px}
.xprow{display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-weight:900;font-size:15px}
.xprow b{font-family:var(--font-display);font-weight:400;font-size:18px;color:var(--bone);display:inline-block}
.xprow b.up{animation:rankpop .6s cubic-bezier(.3,1.8,.5,1)}
@keyframes rankpop{0%{transform:scale(.4);color:var(--rival)}100%{transform:none}}
.xprow span{font-size:13px;color:var(--muted);display:flex;align-items:center;gap:4px}
.xprow svg,.xpnote svg{width:16px;height:16px;fill:#FF7A2E;flex:none}
.xpbar{height:12px;border-radius:99px;border:2.5px solid #0B0618;background:var(--velvet);overflow:hidden}
.xpbar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#9E0D24,var(--ink) 55%,#FF5A6E);border-radius:99px;transition:width 1.1s cubic-bezier(.2,.8,.2,1)}
.xpnote{margin:0;font-size:13px;font-weight:800;color:var(--bone);display:flex;flex-wrap:wrap;align-items:center;gap:6px}
.xpnote:empty{display:none}
.daily{display:flex;flex-direction:column;align-items:center;gap:3px;line-height:1.1}
.daily small{font:800 12px/1 system-ui,-apple-system,sans-serif;color:var(--muted);letter-spacing:.02em}
.cfx{position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:6}
.cfx i{position:absolute;top:-12px;width:8px;height:14px;border-radius:2px;animation:cfall 1.6s cubic-bezier(.3,.6,.4,1) forwards}
@keyframes cfall{to{transform:translate(var(--dx),110vh) rotate(var(--r));opacity:.9}}""")
# menu: rank strip + tonight's canvas button
rep("""    <button class="btn" id="startBtn" type="button">Play vs holy water</button>""", """    <button class="btn" id="startBtn" type="button">Play vs holy water</button>
    <button class="btn ghost daily" id="dailyBtn" type="button"><span>Tonight's canvas</span><small id="dailyInfo">A new one every night</small></button>""")
rep("""  $('stages').innerHTML = h; $('startBtn').textContent = 'Play vs holy water';""", """  $('stages').innerHTML = h; $('startBtn').textContent = 'Play vs holy water';
  const r = rankOf(store.xp || 0), st = store.streak || 0;
  $('rkName').textContent = r.name; $('rkFill').style.width = (r.k * 100).toFixed(1) + '%';
  $('rkInfo').innerHTML = (st >= 2 ? FLAME + st + ' streak · ' : '') + (r.next ? Math.max(0, r.hi - (store.xp || 0)) + ' blood to ' + r.next : 'Top rank');
  const d = store.daily && store.daily.date === dailyKey() ? store.daily : null;
  $('dailyInfo').textContent = d && d.best !== null ? 'Your best tonight: ' + fmtMargin(d.best) : 'A new one every night';""")

# ================= 4) tonight's canvas =================
rep("let mapUsed = true;\nfunction freshMap() {", """let mapUsed = true, daily = false;
const dailyKey = () => { const d = new Date(); return d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate(); };
const fmtMargin = m => (m > 0 ? '+' : '') + m + '%';
// everyone gets the same canvas tonight
function startDaily() {
  if (building) return; daily = true; building = true; AU.init(); menu.hidden = true; end.hidden = true; pauseEl.hidden = true;
  banner("Tonight's canvas", 'A new one every night', true);
  setTimeout(() => { genWorld((dailyKey() * 2654435761) >>> 0); mapUsed = false; building = false; start(); }, 60);
}
const again = () => daily ? startDaily() : start();
function confettiDom() { if (reduceMotion) return; const box = document.createElement('div'); box.className = 'cfx'; const cols = ['#E3122F', '#FFD86B', '#8B3DFF', '#FFFFFF', '#FF6A1A']; for (let i = 0; i < 70; i++) { const c = document.createElement('i'); c.style.left = (Math.random() * 100) + '%'; c.style.background = cols[i % cols.length]; c.style.setProperty('--dx', ((Math.random() - 0.5) * 120).toFixed(0) + 'px'); c.style.setProperty('--r', ((Math.random() - 0.5) * 900).toFixed(0) + 'deg'); c.style.animationDelay = (Math.random() * 0.35).toFixed(2) + 's'; box.appendChild(c); } stage.appendChild(box); setTimeout(() => box.remove(), 2400); }
function freshMap() {""")
rep("$('startBtn').addEventListener('click', uiClick(start));", "$('startBtn').addEventListener('click', uiClick(() => { daily = false; start(); }));\n$('dailyBtn').addEventListener('click', uiClick(startDaily));")
rep("$('endBtn').addEventListener('click', uiClick(start));", "$('endBtn').addEventListener('click', uiClick(again));")
rep("$('restartBtn').addEventListener('click', uiClick(start));", "$('restartBtn').addEventListener('click', uiClick(again));")
rep("""  $('endEyebrow').textContent = lv[1] + ' holy water';""", """  $('endEyebrow').textContent = (endInfo.daily ? "Tonight's canvas · " : '') + lv[1] + ' holy water';""")
rep("    if (state === 'menu') start(); else if (state === 'dead' && !end.hidden) $('endBtn').click();", "    if (state === 'menu') { daily = false; start(); } else if (state === 'dead' && !end.hidden) $('endBtn').click();")

# ================= 5) smoother: resolution follows the frame rate =================
rep("""function frame(t) {
  const rdt = Math.min(0.05, Math.max(0, (t - last) / 1000)); last = t;""", """// keep it smooth: if frames run long, render at a slightly lower resolution; when there's headroom, go back up
let perfT = 0, perfN = 0, perfGood = 0, curPR = Math.min(2, window.devicePixelRatio || 1); const maxPR = curPR;
function tunePerf(ft) {
  if (document.hidden || ft > 0.25 || window.__fixedPR) return;
  perfT += ft; perfN++; if (perfN < 45) return;
  const avg = perfT / perfN; perfT = 0; perfN = 0;
  if (avg > 0.0205 && curPR > 1) { curPR = Math.max(1, curPR - 0.25); renderer.setPixelRatio(curPR); resize(); perfGood = 0; }
  else if (avg < 0.0135 && curPR < maxPR) { if (++perfGood >= 4) { curPR = Math.min(maxPR, curPR + 0.25); renderer.setPixelRatio(curPR); resize(); perfGood = 0; } }
  else perfGood = 0;
}
function frame(t) {
  tunePerf((t - last) / 1000);
  const rdt = Math.min(0.05, Math.max(0, (t - last) / 1000)); last = t;""")
rep("renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));", "renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));")

# ================= 6) Hard doesn't walk into your pound when its own isn't ready =================
rep("      if (matchLeft < 15 && lead > 2) aggro *= 1 + AI.model;        // behind late: it needs a swing\n    }",
    "      if (matchLeft < 15 && lead > 2) aggro *= 1 + AI.model;        // behind late: it needs a swing\n      if (oPoundIn(D) <= 0.6 && !slamReady(D) && o.flat <= 0) aggro = 0; // your pound is up and its isn't: stay out of reach\n    }")
rep("    if (stuck && !slamReady(D) && od < 7 && Math.random() < AI.ram * 0.6 && pn) return aiGo(D, pn, 'hunt');", "    if (stuck && !slamReady(D) && od < 7 && !(AI.model > 0 && oPoundIn(D) <= 0.6) && Math.random() < AI.ram * 0.6 && pn) return aiGo(D, pn, 'hunt');")
open(f,'w').write(s)
print('patched')
