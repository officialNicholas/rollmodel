# Settings: Graphics or Performance visuals, plus adaptive tuning that knows about the mode
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
gear=open('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/gear.txt').read().strip()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:90], c)
    s = s.replace(a, b)

# CSS
rep(""".nametag b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:800}""",
""".nametag b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:800}
.setb{position:absolute;top:max(12px,env(safe-area-inset-top));right:68px;z-index:1}
.setb svg{width:22px;height:22px;stroke:none;fill-rule:evenodd}
.seg.duo{grid-template-columns:1fr 1fr}
.sgrp{display:grid;gap:10px}
.gnote{margin:0;min-height:2.7em;text-align:center;font-size:15px;font-weight:700;line-height:1.35;color:var(--muted)}""")

# the gear on the title screen
rep("""<b id="nameShow">Player</b><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/></svg></button>
""", """<b id="nameShow">Player</b><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/></svg></button>
      <button class="ib setb" id="setBtn" type="button" aria-label="Settings" aria-haspopup="dialog"><svg viewBox="0 0 24 24" aria-hidden="true"><path d=\"""" + gear + """\"/></svg></button>
""")

# the settings card
rep("""  <div class="modal" id="pause" hidden>""", """  <div class="modal" id="setModal" hidden>
    <div class="card" role="dialog" aria-modal="true" aria-labelledby="setTitle">
      <h2 class="ctitle" id="setTitle">Settings</h2>
      <div class="sgrp">
        <p class="lhead">Visuals</p>
        <div class="seg duo" id="gfxPick" role="group" aria-label="Visuals"><button type="button" data-g="hi" aria-pressed="false">Graphics</button><button type="button" data-g="perf" aria-pressed="false">Performance</button></div>
        <p class="gnote" id="gfxNote" aria-live="polite"></p>
      </div>
      <button class="btn play sm" id="setDone" type="button">Done</button>
    </div>
  </div>

  <div class="modal" id="pause" hidden>""")

# JS: open, pick, apply with a restart
rep("""howModal.addEventListener('click', e => { if (e.target === howModal) closeHow(); });
""", """howModal.addEventListener('click', e => { if (e.target === howModal) closeHow(); });
// ---------- settings: Graphics or Performance visuals. The choice is saved and the game restarts to apply it ----------
const setModal = $('setModal'), GFX_NOTE = { hi: 'Full lighting, reflections, glow and extra detail. Best on newer phones and computers.', perf: 'Simpler lighting and fewer effects, for the smoothest play on any device.' };
let gfxPick = GFX;
function paintSettings() { for (const b of $('gfxPick').children) b.setAttribute('aria-pressed', String(b.dataset.g === gfxPick)); $('gfxNote').textContent = GFX_NOTE[gfxPick]; $('setDone').textContent = gfxPick === GFX ? 'Done' : 'Restart to apply'; }
function openSettings() { if (state !== 'menu' || lookOpen) return; gfxPick = GFX; paintSettings(); setModal.hidden = false; setTimeout(() => $('gfxPick').querySelector('[aria-pressed="true"]').focus({ preventScroll: true }), 30); }
function closeSettings() { if (setModal.hidden) return; setModal.hidden = true; $('setBtn').focus({ preventScroll: true }); }
function doneSettings() { if (gfxPick === GFX) return closeSettings(); store.gfx = gfxPick; save(); $('setDone').disabled = true; $('setDone').textContent = 'Restarting'; setTimeout(() => location.reload(), 120); }
$('setBtn').addEventListener('click', uiClick(openSettings));
$('gfxPick').addEventListener('click', e => { const b = e.target.closest('button[data-g]'); if (!b || b.dataset.g === gfxPick) return; AU.ui(); gfxPick = b.dataset.g; paintSettings(); });
$('setDone').addEventListener('click', uiClick(doneSettings));
setModal.addEventListener('click', e => { if (e.target === setModal) closeSettings(); });
""")
rep("""  if (!howModal.hidden) { if (k === 'Escape') { e.preventDefault(); closeHow(); } return; }
""", """  if (!howModal.hidden) { if (k === 'Escape') { e.preventDefault(); closeHow(); } return; }
  if (!setModal.hidden) { if (k === 'Escape') { e.preventDefault(); closeSettings(); } return; }
""")
# the settings card closes with the rest when a match starts or the menu resets
rep("""menu.hidden = false; end.hidden = true; pauseEl.hidden = true; howModal.hidden = true; hud.classList.add('off');""",
    """menu.hidden = false; end.hidden = true; pauseEl.hidden = true; howModal.hidden = true; setModal.hidden = true; hud.classList.add('off');""")

# adaptive tuning: start from this mode's resolution and shadow size; in Graphics mode the glow is the first thing to go when frames run long
rep("""let perfT = 0, perfN = 0, perfGood = 0, curPR = Math.min(2, window.devicePixelRatio || 1); const maxPR = curPR;""",
    """let perfT = 0, perfN = 0, perfGood = 0, curPR = Math.min(HI ? 2 : 1.5, window.devicePixelRatio || 1); const maxPR = curPR;
const SH_FULL = HI ? (MOBILE ? 2048 : 4096) : 1024, SH_LITE = 1024;""")
rep("""  shadowLite = k; const sz = k ? 1024 : 2048;""", """  shadowLite = k; const sz = k ? SH_LITE : SH_FULL;""")
rep("""  if (avg > 0.0205 && curPR > 1) { curPR = Math.max(1, curPR - (avg > 0.03 ? 0.5 : 0.25)); renderer.setPixelRatio(curPR); resize(); perfGood = 0; }""",
    """  if (avg > 0.0205 && post && post.bloom) { post.bloom = false; perfGood = 0; }
  else if (avg > 0.0205 && curPR > 1) { curPR = Math.max(1, curPR - (avg > 0.03 ? 0.5 : 0.25)); renderer.setPixelRatio(curPR); resize(); perfGood = 0; }""")
rep("""  else if (avg < 0.0135 && (shadowLite > 0 || curPR < maxPR)) { if (++perfGood >= 4) { if (shadowLite > 0) setShadowLite(shadowLite - 1); else { curPR = Math.min(maxPR, curPR + 0.25); renderer.setPixelRatio(curPR); resize(); } perfGood = 0; } }""",
    """  else if (avg < 0.0135 && (shadowLite > 0 || curPR < maxPR || (post && !post.bloom))) { if (++perfGood >= 4) { if (shadowLite > 0) setShadowLite(shadowLite - 1); else if (curPR < maxPR) { curPR = Math.min(maxPR, curPR + 0.25); renderer.setPixelRatio(curPR); resize(); } else post.bloom = true; perfGood = 0; } }""")
open(p,'w').write(s); print('patched')
