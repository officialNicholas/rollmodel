import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# ---------- markup: a nameplate on top of the dock, and a name card ----------
rep("""    <div class="dock">
      <div class="swatches" id="swatches" role="group" aria-label="Your color"></div>""",
"""    <div class="dock">
      <button class="nametag" id="nameBtn" type="button" aria-label="Change your name"><span class="ntd" aria-hidden="true"></span><b id="nameShow">Player</b><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/></svg></button>
      <div class="swatches" id="swatches" role="group" aria-label="Your color"></div>""")
rep("""  <div class="modal" id="pause" hidden>""", """  <div class="modal" id="nameModal" hidden>
    <form class="card" id="nameForm" role="dialog" aria-modal="true" aria-labelledby="nameTitle" autocomplete="off">
      <h2 class="ctitle" id="nameTitle">What's your name?</h2>
      <p class="cnote">It goes up in lights when you win.</p>
      <div class="namefield"><input id="nameInput" type="text" maxlength="12" autocomplete="off" autocapitalize="words" autocorrect="off" spellcheck="false" enterkeyhint="go" aria-label="Your name"><button class="dice" id="nameDice" type="button" aria-label="Pick a random name"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="4.5" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="8.5" cy="8.5" r="1.6"/><circle cx="15.5" cy="15.5" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="15.5" cy="8.5" r="1.6"/><circle cx="8.5" cy="15.5" r="1.6"/></svg></button></div>
      <button class="btn play sm" id="nameOk" type="submit">Let's go</button>
    </form>
  </div>

  <div class="modal" id="pause" hidden>""")
rep("""<div class="pchip you" id="chipYou"><i></i><div><b id="endPct">0%</b><span>You</span></div>""", """<div class="pchip you" id="chipYou"><i></i><div><b id="endPct">0%</b><span id="chipYouName">You</span></div>""")

# ---------- style ----------
rep(".swatches{display:flex;", """.nametag{justify-self:center;margin:-38px 0 -2px;display:inline-flex;align-items:center;gap:8px;max-width:100%;min-height:42px;box-sizing:border-box;padding:0 14px 0 9px;border-radius:99px;background:var(--plum-2);border:3px solid var(--line);box-shadow:0 4px 0 var(--line);color:var(--bone);font:800 17px/1 var(--font-ui);cursor:pointer;transition:transform .15s cubic-bezier(.3,1.6,.5,1)}
.nametag b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:800}
.nametag svg{width:16px;height:16px;flex:none;color:var(--muted)}
.nametag .ntd{flex:none;width:18px;height:18px;margin-top:3px;background:var(--ink);border:2.5px solid var(--line);border-radius:50% 50% 50% 0;transform:rotate(135deg)}
.nametag:hover{transform:translateY(-2px)}
.nametag:active{transform:translateY(2px);box-shadow:0 1px 0 var(--line)}
.nametag:focus-visible,.dice:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.cnote{margin:-4px 0 0;text-align:center;font-size:15px;font-weight:700;line-height:1.35;color:var(--muted)}
.namefield{display:flex;gap:8px}
.namefield input{flex:1;min-width:0;height:56px;box-sizing:border-box;padding:0 16px;border-radius:16px;border:3px solid var(--line);background:var(--bone);color:var(--outline);font:400 26px/1 var(--font-display);text-align:center;outline:none;box-shadow:inset 0 3px 0 rgba(0,0,0,.12);-webkit-user-select:text;user-select:text}
.namefield input:focus{box-shadow:inset 0 3px 0 rgba(0,0,0,.12),0 0 0 3px var(--gold)}
.dice{appearance:none;flex:none;width:56px;height:56px;border-radius:16px;border:3px solid var(--line);background:var(--plum-2);color:var(--bone);display:grid;place-items:center;padding:0;cursor:pointer;box-shadow:0 4px 0 var(--line)}
.dice svg{width:26px;height:26px;fill:currentColor}
.dice:active{transform:translateY(3px) rotate(-12deg);box-shadow:0 1px 0 var(--line)}
.swatches{display:flex;""")

# ---------- logic ----------
rep("const NAMES = ['You', 'Holy water', 'Wolfsbane'], nameOf = D => NAMES[D.team];",
"""const NAMES = ['You', 'Holy water', 'Wolfsbane'], nameOf = D => D === P ? playerName() : NAMES[D.team];
// your name: asked for before your first match, changed any time from the nameplate on the menu
const NAME_MAX = 12, NAME_IDEAS = ['Nightshade', 'Crimson', 'Vesper', 'Count Drip', 'Velvet', 'Lady Fang', 'Noir', 'Rouge', 'Vlad', 'Mina', 'Hemlock', 'Ruby', 'Bat Boy', 'Midnight', 'Carmilla', 'Dusk'];
const cleanName = t => String(t || '').replace(/[\\u0000-\\u001f<>]/g, '').replace(/\\s+/g, ' ').trim().slice(0, NAME_MAX);
const playerName = () => cleanName(store.name) || 'You';
const randomName = () => { let n; do { n = NAME_IDEAS[(Math.random() * NAME_IDEAS.length) | 0]; } while (n === store.name && NAME_IDEAS.length > 1); return n; };""")
rep("const hud = $('hud'), menu = $('menu'), end = $('end'), pauseEl = $('pause');", """const hud = $('hud'), menu = $('menu'), end = $('end'), pauseEl = $('pause'), nameModal = $('nameModal');
function paintName() { const n = playerName(); NAMES[0] = n; $('nameShow').textContent = store.name ? n : 'Add your name'; $('chipYouName').textContent = n; }
let nameFirst = false;
function openName(first) {
  nameFirst = !!first; const inp = $('nameInput');
  $('nameTitle').textContent = first ? "What's your name?" : 'Your name'; $('nameOk').textContent = first ? "Let's go" : 'Save';
  inp.value = cleanName(store.name) || randomName(); nameModal.hidden = false;
  try { inp.focus({ preventScroll: true }); inp.select(); } catch (e) {}
}
function closeName() { if (nameModal.hidden) return; nameModal.hidden = true; nameFirst = false; try { $('nameInput').blur(); } catch (e) {} }
$('nameForm').addEventListener('submit', e => {
  e.preventDefault(); AU.init(); AU.ui();
  store.name = cleanName($('nameInput').value) || randomName(); save(); paintName();
  const go = nameFirst; closeName(); if (go) start();
});
$('nameDice').addEventListener('click', () => { AU.init(); AU.pop(); const inp = $('nameInput'); inp.value = randomName(); try { inp.focus({ preventScroll: true }); inp.select(); } catch (e) {} });
$('nameInput').addEventListener('keydown', e => { e.stopPropagation(); if (e.key === 'Escape') { e.preventDefault(); closeName(); } });
nameModal.addEventListener('click', e => { if (e.target === nameModal) closeName(); });
$('nameBtn').addEventListener('click', () => { AU.init(); AU.ui(); openName(false); });""")
# the first Play asks for a name
rep("$('startBtn').addEventListener('click', uiClick(start));", "$('startBtn').addEventListener('click', uiClick(() => { if (!store.name) openName(true); else start(); }));")
# typing in a text field never steers or pounds
rep("window.addEventListener('keydown', e => {\n  const k = e.key; AU.init();", "window.addEventListener('keydown', e => {\n  if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;\n  if (!nameModal.hidden) { if (e.key === 'Escape') { e.preventDefault(); closeName(); } return; }\n  const k = e.key; AU.init();")
# the menu's keyboard start also asks for a name the first time
rep("if (state === 'menu') start(); else if (state === 'dead' && !end.hidden) $('endBtn').click();", "if (state === 'menu') { if (!store.name) openName(true); else start(); } else if (state === 'dead' && !end.hidden) $('endBtn').click();")
# paint the nameplate's drop in your color, and the name at startup
rep(".nametag .ntd{flex:none;width:18px;height:18px;margin-top:3px;background:var(--ink);", ".nametag .ntd{flex:none;width:18px;height:18px;margin-top:3px;background:var(--ink);")
rep("colorId = PALETTE.some(p => p.id === store.color) ? store.color : 'red'; renderSwatches(); setColor(colorId); applyMode(); if (ARENA !== 26.4) mapUsed = true;",
    "colorId = PALETTE.some(p => p.id === store.color) ? store.color : 'red'; renderSwatches(); setColor(colorId); applyMode(); if (ARENA !== 26.4) mapUsed = true; paintName();")
open(F, 'w').write(s)
print('ok')
