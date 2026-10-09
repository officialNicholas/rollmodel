import sys, re
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)
def cut_between(a, b, new):
    """replace from the start of a up to (not including) b"""
    global s
    i = s.find(a); j = s.find(b, i)
    if i < 0 or j < 0 or s.count(a) != 1: print('CUT MISS', repr(a[:60]), i, j); sys.exit(1)
    s = s[:i] + new + s[j:]

# ================= CSS =================
cut_between("/* ranks: the blood bar */", ".cfx{position:absolute;", """/* the canvas you're about to play, with a shuffle */
.cvrow{display:flex;align-items:center;gap:10px;padding:8px 8px 8px 14px;border:3px solid #0B0618;border-radius:16px;background:var(--velvet)}
.cvname{display:grid;gap:4px;flex:1;min-width:0;justify-items:start}
.cvname small{font:800 11px/1 system-ui,-apple-system,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.cvname b{font-family:var(--font-display);font-weight:400;font-size:19px;line-height:1.05;color:var(--bone)}
.cvname b.pop{animation:cvpop .35s cubic-bezier(.3,1.7,.5,1)}
@keyframes cvpop{0%{transform:scale(.7);opacity:.3}100%{transform:none;opacity:1}}
.btn.cvbtn{width:auto;flex:none;min-height:42px;font-size:15px;padding:6px 14px;display:flex;align-items:center;gap:6px;box-shadow:0 3px 0 #0B0618;background:var(--paper)}
.btn.cvbtn:active{transform:translateY(3px);box-shadow:0 0 0 #0B0618}
.cvbtn svg{width:18px;height:18px;flex:none}
.btn.two{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;line-height:1.05}
.btn.two small{font:800 12px/1 system-ui,-apple-system,sans-serif;letter-spacing:.02em;opacity:.85}
kbd{display:inline-block;min-width:1.4em;padding:1px 5px;margin:0 1px;border:2px solid #0B0618;border-bottom-width:3px;border-radius:6px;background:var(--bone);color:var(--outline);font:800 11px/1.3 system-ui,-apple-system,sans-serif;text-align:center;vertical-align:1px}
""")

# ================= menu markup =================
rep("""    <div class="rankbar" id="rankBar"><div class="xprow"><b id="rkName">Fledgling</b><span id="rkNext"></span></div><div class="xpbar"><i id="rkFill"></i></div><p class="xpnote" id="rkInfo"></p></div>
    <p class="lede">You're a drop of vampire blood, and a blob of holy water wants this canvas too. Cover more of it than the holy water in 90 seconds. Every match is a new canvas: a studio, a crypt, a cathedral, a manor or a night garden.</p>""",
"""    <p class="lede">You're a drop of vampire blood. Cover more of the canvas than the holy water in 90 seconds.</p>
    <div class="cvrow"><div class="cvname"><small>Next canvas</small><b id="cvName">The Studio</b></div><button class="btn ghost cvbtn" id="shuffleBtn" type="button" aria-label="Shuffle to a new canvas"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7h3.5c2 0 3.2 1 4.3 2.6l2.4 3.8C14.3 15 15.5 16 17.5 16H21M3 16h3.5c1.4 0 2.4-.5 3.2-1.4M13.3 8.4c.8-.9 1.8-1.4 3.2-1.4H21M18 4l3 3-3 3M18 13l3 3-3 3" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>Shuffle</button></div>""")
rep("""    <button class="btn ghost daily" id="dailyBtn" type="button"><span>Tonight's canvas</span><small id="dailyInfo">A new one every night</small></button>\n""", "")

# how to play: shorter, and the controls line follows what you're playing with
cut_between('      <ul class="rules">', '    </details>', """      <ul class="rules">
        <li><span class="dot hand">↔</span><span id="howCtl">Drag sideways to steer. Tap to jump. Hold to stop, then pull down and let go to fling. The arrow button pounds.</span></li>
        <li><span class="dot holy"></span>Cover more of the canvas than the holy water in 90 seconds. Painting over its color takes the ground back.</li>
        <li><span class="dot ink"></span>Painting uses blood. Rolling over your own color barely uses any. Coffins refill you. A drained one sinks and a fresh one rises somewhere else.</li>
        <li><span class="dot hand">➚</span>A harder fling lands a bigger splat. Fling into the holy water to send it flying, best near the edge. On the way down you can load another fling to sling yourself again.</li>
        <li><span class="dot hand">↓</span>Pound to splat a big circle. It's ready 10 seconds in. If the holy water is inside the circle, even hiding in a coffin, it's out for 5 seconds. Pound mid-fling for a bigger missile splat.</li>
        <li><span class="dot hand">↑</span>Pound inside a coffin to burst out with the same big splat and blast anyone close away. Fling into a coffin someone's hiding in to bounce them out.</li>
        <li><span class="dot holy"></span>Roll into the holy water faster than it's moving, or land on it, to flatten it for 2 seconds.</li>
        <li><span class="dot sun"></span>When the sun comes up you get 4 seconds to hide in a coffin or a shadow. It also hardens paint, which slows you down until the rain softens it.</li>
        <li><span class="dot boil"></span>Rain leaves puddles. Roll through one and your paint counts half for 2 seconds. Pound a puddle to splash it away and refill.</li>
        <li><span class="dot ink"></span>Touch the glowing orb to go giant for 5 seconds: faster, bigger splats, blood that doesn't run out, and you squish the holy water by rolling into it. A giant pound is huge but ends it.</li>
        <li><span class="dot holy"></span>The holy water only knows what it sees and hears. ! means it spotted you, ? means it lost you. Duck behind something tall to shake it. On Hard it learns how you play.</li>
        <li><span class="dot sun"></span>Falling off, running dry or burning puts you back in 2 seconds. A knockout keeps you out for 5.</li>
      </ul>
""")

# ================= pause and end markup =================
rep("""<div class="row"><button class="btn ghost" id="restartBtn" type="button">Restart</button><button class="btn ghost" id="quitBtn" type="button">Stages</button></div>""",
    """<div class="row"><button class="btn ghost" id="restartBtn" type="button">Restart</button><button class="btn ghost" id="quitBtn" type="button">Menu</button></div>""")
rep("""        <div class="xp"><div class="xprow"><b id="xpRank">Fledgling</b><span id="xpGain">+0 blood</span></div><div class="xpbar"><i id="xpFill"></i></div><p class="xpnote" id="xpNote"></p></div>\n""", "")
rep("""    <div class="row"><button class="btn ghost" id="menuBtn" type="button">Stages</button><button class="btn ghost" id="replayBtn" type="button">Replay</button></div>
    <button class="btn" id="endBtn" type="button">Next stage</button>""",
"""    <div class="row"><button class="btn ghost" id="menuBtn" type="button">Menu</button><button class="btn ghost" id="replayBtn" type="button">Same canvas</button></div>
    <button class="btn two" id="endBtn" type="button"><span>Rematch</span><small>New canvas</small></button>""")

# ================= storage: drop the old progression fields =================
rep("  ['best', 'stars', 'seen'].forEach(k => { if (!d[k] || typeof d[k] !== 'object') d[k] = {}; });\n  return d;",
    "  ['best', 'stars', 'seen'].forEach(k => { if (!d[k] || typeof d[k] !== 'object') d[k] = {}; });\n  for (const k of ['xp', 'daily', 'lastDay', 'dayStreak', 'streak', 'bestStreak']) delete d[k];\n  return d;")
cut_between("// ---------- ranks: every match earns blood (XP); keep climbing ----------", "\n// ---------- renderer ----------", "")
rep("    xp() { tone('triangle', 1200 + Math.random() * 300, 0, 0.05, 0.03); },\n", "")
rep("    rankUp() { [523, 659, 784, 1047, 1319, 1568].forEach((f, i) => tone('triangle', f, 0, 0.2, 0.12, i * 0.07)); tone('sine', 1568, 0, 1.2, 0.06, 0.45, sfx, 0.01); },\n", "")

# ================= end of match: no blood, no streaks, no nightly bonus =================
cut_between("  // blood earned: playing, coverage, winning (more on harder holy water), knockouts and a win streak", "  save();\n  const [a, b] = fmtPair(you, cpu);",
"""  store.bestCov = store.bestCov || {}; const newBest = ry > (store.bestCov[diff] || 0); if (newBest) store.bestCov[diff] = ry;
  endInfo.newBest = newBest;
""")

# ================= menus =================
rep("""  $('stages').innerHTML = h; $('startBtn').textContent = 'Play vs holy water';
  const r = rankOf(store.xp || 0), st = store.streak || 0;""", """  $('stages').innerHTML = h; $('startBtn').textContent = 'Play vs holy water'; $('cvName').textContent = TH.label;""")
cut_between("  $('rkName').textContent = r.name;", "}\n$('stages').addEventListener", "")

cut_between("let mapUsed = true, daily = false;", "function confettiDom()", """let mapUsed = true;
// play this exact canvas again
function replay() {
  if (building) return; const sd = GEN.seed; building = true; AU.init(); menu.hidden = true; end.hidden = true; pauseEl.hidden = true; hud.classList.add('off'); banner('Same canvas', TH.label);
  setTimeout(() => { genWorld(sd); mapUsed = false; building = false; start(); }, 60);
}
// a different canvas from the menu, if you don't fancy this one
function shuffleCanvas() {
  if (building || state !== 'menu') return; freshMap(); resetRun(); decorate();
  P.x = START.x; P.z = START.z; P.yaw = START.yaw; H.x = CSTART.x; H.z = CSTART.z; H.yaw = CSTART.yaw;
  const n = $('cvName'); n.textContent = TH.label; kick(n, 'pop');
}
""")
cut_between("function confettiDom()", "function freshMap()", "")

# the end screen: result, new best, and a stats line
rep("  $('endEyebrow').textContent = (endInfo.daily ? \"Tonight's canvas · \" : '') + lv[1] + ' holy water';", "  $('endEyebrow').textContent = lv[1] + ' holy water';")
rep("  bits.push('Wins on ' + lv[1] + ': ' + ((store.wins && store.wins[diff]) || 0) + '.');", "  bits.push('Wins on ' + lv[1] + ': ' + ((store.wins && store.wins[diff]) || 0) + '. Best: ' + ((store.bestCov && store.bestCov[diff]) || 0) + '%.');")
cut_between("  // the blood bar: fill up, and rank up if it gets there", "  $('frame').hidden = !img;", "  $('endPill').hidden = !endInfo.newBest;\n")
rep("  $('pMeta').textContent = 'Blood and holy water on canvas · ' + fmtTime(time);", "  $('pMeta').textContent = TH.label + ' · ' + fmtTime(time);")
rep("  $('endBtn').textContent = 'Rematch'; $('replayBtn').hidden = true; $('menuBtn').textContent = 'Change difficulty'; end.dataset.next = '';", "  end.dataset.next = '';")

# buttons
rep("$('startBtn').addEventListener('click', uiClick(() => { daily = false; start(); }));\n$('dailyBtn').addEventListener('click', uiClick(startDaily));\n$('endBtn').addEventListener('click', uiClick(again));\n$('replayBtn').addEventListener('click', uiClick(start));",
    "$('startBtn').addEventListener('click', uiClick(start));\n$('shuffleBtn').addEventListener('click', uiClick(shuffleCanvas));\n$('endBtn').addEventListener('click', uiClick(start));\n$('replayBtn').addEventListener('click', uiClick(replay));")
rep("$('restartBtn').addEventListener('click', uiClick(again));", "$('restartBtn').addEventListener('click', uiClick(replay));")

# leaving the tab or the window pauses, and no key stays stuck down
rep("document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); AU.suspend(document.hidden); });",
    "document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); AU.suspend(document.hidden); });\nwindow.addEventListener('blur', () => { keyL = keyR = false; pause(); });")

# ================= keyboard =================
rep("  const k = e.key; AU.init();\n  if (k === 'Escape' || k === 'p' || k === 'P') { e.preventDefault(); if (state === 'paused') resume(); else pause(); return; }",
    """  const k = e.key; AU.init();
  if (!keysUI && (k.startsWith('Arrow') || (k.length === 1 && 'wasdeWASDE '.includes(k)))) { keysUI = true; paintHow(); }
  const endUp = state === 'dead' && !end.hidden;
  if (k === 'Escape' || k === 'p' || k === 'P') { e.preventDefault(); if (state === 'paused') resume(); else if (endUp && k === 'Escape') showMenu(); else pause(); return; }
  if ((k === 'r' || k === 'R') && !e.repeat && (state === 'paused' || endUp)) { replay(); return; }""")
rep("""  else if ((k === ' ' || k === 'ArrowUp' || k === 'w' || k === 'W') && !e.repeat) {
    if (document.activeElement && document.activeElement.tagName === 'BUTTON' && k === ' ') return;
    e.preventDefault();
    if (state === 'menu') { daily = false; start(); }""", """  else if ((k === ' ' || k === 'Enter' || k === 'ArrowUp' || k === 'w' || k === 'W') && !e.repeat) {
    if (document.activeElement && (document.activeElement.tagName === 'BUTTON' || document.activeElement.tagName === 'SUMMARY') && (k === ' ' || k === 'Enter')) return;
    e.preventDefault();
    if (state === 'menu') start();""")
# a finger on the glass switches the tips back to touch
rep("  e.preventDefault(); try { canvas.setPointerCapture(e.pointerId); } catch (err) {}",
    "  e.preventDefault(); try { canvas.setPointerCapture(e.pointerId); } catch (err) {}\n  if (e.pointerType === 'touch' && keysUI) { keysUI = false; paintHow(); }")

# ================= tips that match your controls =================
rep("const bannerEl = $('banner');", r"""// on a phone the tips talk about touch; with a keyboard they name the keys
let keysUI = !!(window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches);
const say = (touch, keys) => keysUI ? keys : touch;
function paintHow() { const el = $('howCtl'); if (el) el.innerHTML = keysUI ? '<kbd>A</kbd> <kbd>D</kbd> or the arrows steer. <kbd>Space</kbd> jumps. Hold <kbd>S</kbd> to stop and load a fling, let go to fling. <kbd>E</kbd> pounds. <kbd>P</kbd> pauses, <kbd>M</kbd> mutes.' : 'Drag sideways to steer. Tap to jump. Hold to stop, then pull down and let go to fling. The arrow button pounds.'; }
paintHow();
const bannerEl = $('banner');""")
rep("hint('steer', 'Drag to steer', 3)", "hint('steer', say('Drag to steer', 'A and D or the arrow keys steer'), 3)")
rep("hint('jump', 'Tap to jump', 2.4)", "hint('jump', say('Tap to jump', 'Space to jump'), 2.4)")
rep("hint('hold', 'Hold to stop. Pull down to fling.', 3.2)", "hint('hold', say('Hold to stop. Pull down to fling.', 'Hold S to stop and load a fling'), 3.2)")
rep("hint('burst', 'Pound in a coffin to burst out of it', 3)", "hint('burst', say('Pound in a coffin to burst out of it', 'Press E in a coffin to burst out of it'), 3)")
rep("hint('pound', 'Pound near the holy water to knock it out', 3)", "hint('pound', say('Pound near the holy water to knock it out', 'Press E near the holy water to pound it'), 3)")
rep("hint('airsling', 'Hold and pull on the way down to sling yourself', 3)", "hint('airsling', say('Hold and pull on the way down to sling yourself', 'Hold S on the way down to sling yourself'), 3)")

# leftovers that no longer exist
for gone in ['dailyKey', 'startDaily', 'rankOf', 'RANKS', 'xpFill', 'rkName', 'dailyInfo', 'daily', 'again(', 'FLAME', 'firstTonight', 'store.xp', 'confettiDom']:
    for m in re.finditer(re.escape(gone), s):
        ctx = s[max(0, m.start() - 40): m.end() + 40].replace('\n', ' ')
        print('LEFT', gone, '::', ctx)
open(F, 'w').write(s)
print('ok')
