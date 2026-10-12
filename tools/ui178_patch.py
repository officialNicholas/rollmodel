#!/usr/bin/env python3
"""v241: Strokes. The Abilities tile opens the Strokes page once it's unlocked (rank 3): two slots, your Special Stroke (what the orb gives
you: the Rocket, or the Giant once it's crafted) and your Skill (Swim faster). The Giant is free to craft at rank 3: a tap starts a
20-minute craft, Skip ends it (an ad will, later). And Ol' Bloop's lesson on it: praise, then the slots, then the Giant crafted and
equipped."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui177_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'D.swimBoost > 1' in s, 'the swim boost is not in the adapter'
# ---- the page's markup, after the events page
CSS = r"""
/* strokes: the dark page like the events, two paper slots, the equipped stroke big, the options in a rail; a craft bar with a countdown */
.mstrokes .stwrap{position:absolute;left:0;right:0;top:calc(max(14px,env(safe-area-inset-top)) + 66px);bottom:0;z-index:1;display:grid;grid-template-columns:minmax(0,1fr);align-content:start;gap:18px;padding:4px max(18px,env(safe-area-inset-right)) calc(max(16px,env(safe-area-inset-bottom)) + 16px) max(18px,env(safe-area-inset-left));overflow-y:auto;overscroll-behavior:contain}
.mstrokes .stsub{margin:-6px 0 0;font:700 13px/1.3 var(--font-ui);color:#B8B0C8}
.stslot{position:relative;min-width:0;border-radius:16px;background:#F4EEE3;box-shadow:0 0 0 2.5px #171320,6px 7px 0 rgba(0,0,0,.4);animation:evin .45s cubic-bezier(.2,1.2,.35,1) both}
.stslot:nth-child(3){animation-delay:.07s}
.sthead{display:flex;align-items:baseline;justify-content:space-between;gap:10px;padding:10px 14px 9px;border-radius:14px 14px 0 0;background:#171320;color:#fff}
.sthead b{font:900 17px/1 var(--font-head);font-style:italic;text-transform:uppercase;letter-spacing:.04em;color:var(--gold);text-shadow:.05em .05em 0 rgba(0,0,0,.6)}
.sthead small{font:700 11px/1.2 var(--font-ui);color:#B8B0C8;text-align:right}
.stnow{display:grid;grid-template-columns:72px minmax(0,1fr);gap:12px;align-items:center;padding:14px 14px 10px}
.stnow .stic{width:72px;height:72px;display:grid;place-items:center;border-radius:18px;background:#fff;box-shadow:0 0 0 2.5px #171320,3px 3px 0 rgba(23,19,32,.25)}
.stnow .stic svg{width:52px;height:52px}
.stnow .stname{display:block;font:900 24px/1 var(--font-head);color:#171320;text-transform:uppercase;letter-spacing:.01em}
.stnow .stdesc{display:block;margin-top:4px;font:600 13px/1.3 var(--font-ui);color:#4A4458}
.stnow .ststamp{display:inline-block;margin-top:7px;padding:3px 8px 2px;border-radius:999px;background:var(--gold);color:#171320;font:900 10px/1 var(--font-head);letter-spacing:.1em;box-shadow:0 0 0 2px #171320}
.strail{display:flex;gap:10px;padding:4px 14px 14px;overflow-x:auto;scrollbar-width:none}
.strail::-webkit-scrollbar{display:none}
.stopt{appearance:none;position:relative;flex:0 0 auto;display:grid;grid-template-rows:auto auto auto;justify-items:center;gap:5px;width:104px;margin:0;padding:10px 8px 9px;border:0;border-radius:14px;background:#fff;color:#171320;box-shadow:0 0 0 2.5px #171320,3px 3px 0 rgba(23,19,32,.25);cursor:pointer;font:inherit;-webkit-tap-highlight-color:transparent;transition:transform .14s cubic-bezier(.3,1.6,.5,1)}
.stopt:active{transform:translate(1px,2px)}
.stopt svg{width:38px;height:38px}
.stopt .stn{font:900 13px/1 var(--font-head);text-transform:uppercase}
.stopt .sts{display:flex;align-items:center;gap:3px;padding:3px 7px 2px;border-radius:999px;font:900 9px/1 var(--font-head);letter-spacing:.08em;background:#E9E3D6;color:#4A4458}
.stopt .sts svg{width:9px;height:9px}
.stopt.on{box-shadow:0 0 0 3px var(--gold),0 0 0 5.5px #171320,3px 3px 0 rgba(23,19,32,.25)}
.stopt.on .sts{background:var(--gold);color:#171320}
.stopt.lock svg:not(.sts svg){opacity:.45;filter:grayscale(1)}
.stopt.lock .stn{color:#8A8396}
.stopt.free .sts{background:#46E07A;color:#0B2A14}
.stopt.ready .sts{background:#E3122F;color:#fff}
.stopt.soon{background:repeating-linear-gradient(135deg,#F4EEE3 0 8px,#ECE5D8 8px 16px);box-shadow:0 0 0 2.5px rgba(23,19,32,.35);cursor:default;color:#8A8396}
.stopt.soon .stn{color:#8A8396}
.stcraft{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;margin:0 14px 14px;padding:10px 12px;border-radius:12px;background:#171320;color:#fff}
.stcraft .stct{font:800 12px/1.2 var(--font-ui);color:#B8B0C8}
.stcraft .stct b{display:block;font:900 22px/1 var(--font-head);color:#fff;font-variant-numeric:tabular-nums;letter-spacing:.02em}
.stcraft .stbar{grid-column:1/-1;height:8px;border-radius:999px;background:#2A2436;overflow:hidden}
.stcraft .stbar i{display:block;height:100%;width:var(--p,0%);background:linear-gradient(90deg,#F2C14E,#FFE39A);border-radius:999px;transition:width .5s linear}
.stcraft .stskip{appearance:none;margin:0;padding:10px 16px;border:0;border-radius:999px;background:var(--gold);color:#171320;font:900 14px/1 var(--font-head);letter-spacing:.08em;text-transform:uppercase;box-shadow:0 0 0 2px #171320,0 3px 0 #171320;cursor:pointer;-webkit-tap-highlight-color:transparent}
.stcraft .stskip:active{transform:translateY(2px);box-shadow:0 0 0 2px #171320,0 1px 0 #171320}
.mstrokes .sttoast{position:absolute;left:50%;bottom:calc(max(16px,env(safe-area-inset-bottom)) + 18px);z-index:3;transform:translateX(-50%);padding:9px 14px;border-radius:999px;background:#171320;color:#fff;font:800 13px/1 var(--font-ui);box-shadow:0 0 0 2px var(--gold);white-space:nowrap;animation:sttoast 2.2s ease both;pointer-events:none}
@keyframes sttoast{0%{opacity:0;transform:translate(-50%,10px)}12%,80%{opacity:1;transform:translate(-50%,0)}100%{opacity:0}}
.plate.abil:not(.locked).fresh .abtag{animation:abpulse 1.4s ease-in-out infinite}
@keyframes abpulse{50%{transform:translateX(-50%) rotate(4deg) scale(1.15)}}
"""
rep("/* abilities: violet construction paper, cut by hand,", CSS + "/* abilities: violet construction paper, cut by hand,")
ROCKET = '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M32 4c9 6 14 18 14 32v6H18v-6C18 22 23 10 32 4z" fill="#F4EEE3" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/><path d="M18 30l-9 10 9 4zM46 30l9 10-9 4z" fill="#E3122F" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/><circle cx="32" cy="26" r="6" fill="#7CC8FF" stroke="#171320" stroke-width="3.2"/><path d="M25 44h14l-7 16z" fill="#F2C14E" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/></svg>'
GIANT = '<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="34" cy="30" r="24" fill="#E3122F" stroke="#171320" stroke-width="3.2"/><circle cx="26" cy="27" r="4.2" fill="#fff" stroke="#171320" stroke-width="2.4"/><circle cx="42" cy="27" r="4.2" fill="#fff" stroke="#171320" stroke-width="2.4"/><circle cx="27" cy="28" r="1.8" fill="#171320"/><circle cx="43" cy="28" r="1.8" fill="#171320"/><path d="M27 38q7 5 14 0" fill="none" stroke="#171320" stroke-width="2.6" stroke-linecap="round"/><circle cx="9" cy="54" r="6" fill="#F2C14E" stroke="#171320" stroke-width="2.6"/><path d="M14 46l6-4M12 60l6 2" fill="none" stroke="#171320" stroke-width="2.4" stroke-linecap="round"/></svg>'
SWIM = '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M6 40c6-6 12-6 18 0s12 6 18 0 12-6 18 0" fill="none" stroke="#7CC8FF" stroke-width="5" stroke-linecap="round"/><path d="M6 52c6-6 12-6 18 0s12 6 18 0 12-6 18 0" fill="none" stroke="#7CC8FF" stroke-width="5" stroke-linecap="round"/><path d="M12 22h26M30 12l12 10-12 10" fill="none" stroke="#171320" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
LOCK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.5 10.5V7.8a4.5 4.5 0 0 1 9 0v2.7" fill="none" stroke="currentColor" stroke-width="3"/><rect x="4.5" y="10" width="15" height="12" rx="2.6" fill="currentColor"/></svg>'
HTML = """
    <div class="mevents mstrokes" id="mStrokes" hidden><div class="evwash" aria-hidden="true"><i></i></div>
      <div class="evhead"><button class="sback" id="stBack" type="button" aria-label="Back to the lobby"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4.5 7.5 12l7.5 7.5" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button><h2 id="stTitle">Strokes</h2></div>
      <div class="stwrap" id="stWrap"><p class="stsub">Your special move and your skill. New ones open as you rank up.</p>
        <section class="stslot" id="stSpecial" aria-labelledby="stSpecialH"><div class="sthead"><b id="stSpecialH">Special stroke</b><small>What the orb gives you</small></div><div class="stnow" id="stSpecialNow"></div><div class="strail" id="stSpecialRail" role="group" aria-label="Special strokes"></div><div class="stcraft" id="stCraft" hidden><span class="stct">Crafting the Giant<b id="stCraftT">20:00</b></span><button class="stskip" id="stSkip" type="button">Skip</button><span class="stbar"><i id="stCraftBar"></i></span></div></section>
        <section class="stslot" id="stSkill" aria-labelledby="stSkillH"><div class="sthead"><b id="stSkillH">Skill</b><small>Always on</small></div><div class="stnow" id="stSkillNow"></div><div class="strail" id="stSkillRail" role="group" aria-label="Skills"></div></section>
      </div>
    </div>
"""
rep('    <div class="mevents" id="mEvents" hidden>', HTML + '    <div class="mevents" id="mEvents" hidden>')
# ---- the data, the page, the craft, the lesson
JS = r"""
// ---------- strokes: your special stroke (what the orb gives you) and your skill; the Giant crafted free at rank 3 ----------
const STROKE_ICON = { rocket: @ROCKET@, giant: @GIANT@, swim: @SWIM@ };
const SPECIALS = [{ id: 'rocket', name: 'Rocket', desc: 'Blast up over the canvas, then dive down in a splash.' }, { id: 'giant', name: 'Giant', desc: 'Grow huge, paint wide, stomp rivals flat.', craft: 20 }];
const SKILLS = [{ id: 'swim', name: 'Swim faster', desc: 'A touch more pace every time you glide.' }];
const SWIM_BOOST = 1.08, STROKE_LOCK = @LOCK@;
function strokesOf() { const d = store.strokes || (store.strokes = {}); if (!d.special) d.special = 'rocket'; if (!d.skill) d.skill = 'swim'; if (!Array.isArray(d.own)) d.own = ['rocket', 'swim']; for (const k of ['rocket', 'swim']) if (!d.own.includes(k)) d.own.push(k); return d; }
const strokeOwned = id => strokesOf().own.includes(id), strokeSpecial = () => { const d = strokesOf(); return strokeOwned(d.special) ? d.special : 'rocket'; }, strokeSkill = () => strokesOf().skill;
const strokesOpen = () => menuPage === 'strokes', strokesDue = () => repOf(store.xp || 0).lv >= ABIL_RANK; // (the page opens at rank 3)
let stTick = 0, stToastT = 0;
function craftLeft() { const c = strokesOf().craft; return c ? Math.max(0, c.end - Date.now()) : 0; }
function craftTick() { const d = strokesOf(), c = d.craft; if (!c) return false; if (craftLeft() > 0) return true; d.craft = null; if (!d.own.includes(c.id)) d.own.push(c.id); d.fresh = c.id; save(); AU.fanfare && AU.fanfare(); return false; }
function craftStart(id) { const d = strokesOf(), sp = SPECIALS.find(x => x.id === id); if (!sp || d.craft || d.own.includes(id)) return; d.craft = { id, end: Date.now() + sp.craft * 60000 }; save(); AU.pop(); buzz(10); renderStrokes(); }
function craftSkip() { const d = strokesOf(); if (!d.craft) return; d.craft.end = Date.now(); craftTick(); AU.ui(); buzz([10, 30, 10]); renderStrokes(); stToast('The Giant is ready!'); }
function equipSpecial(id) { const d = strokesOf(); if (!d.own.includes(id) || d.special === id) return; d.special = id; if (d.fresh === id) d.fresh = null; save(); AU.ready && AU.ready(); buzz(8); renderStrokes(); stToast(SPECIALS.find(x => x.id === id).name + ' is your special stroke'); }
function stToast(msg) { const w = $('mStrokes'), old = w.querySelector('.sttoast'); if (old) old.remove(); const t = document.createElement('span'); t.className = 'sttoast'; t.setAttribute('role', 'status'); t.textContent = msg; w.appendChild(t); clearTimeout(stToastT); stToastT = setTimeout(() => t.remove(), 2300); }
const mmss = ms => { const t = Math.ceil(ms / 1000), m = Math.floor(t / 60), sc = t % 60; return m + ':' + (sc < 10 ? '0' : '') + sc; };
function renderStrokes() {
  const d = strokesOf(); craftTick();
  const now = (id, list, el) => { const o = list.find(x => x.id === id) || list[0]; el.innerHTML = '<span class="stic">' + STROKE_ICON[o.id] + '</span><span><span class="stname">' + o.name + '</span><span class="stdesc">' + o.desc + '</span><span class="ststamp">Equipped</span></span>'; };
  now(strokeSpecial(), SPECIALS, $('stSpecialNow')); now(strokeSkill(), SKILLS, $('stSkillNow'));
  const crafting = d.craft, left = craftLeft();
  $('stSpecialRail').innerHTML = SPECIALS.map(o => { const own = d.own.includes(o.id), on = own && strokeSpecial() === o.id, cr = crafting && crafting.id === o.id, free = !own && !cr && strokesDue(), ready = own && !on && d.fresh === o.id;
    const st = on ? 'Equipped' : cr ? 'Crafting' : ready ? 'Ready!' : own ? 'Tap to equip' : free ? 'Free to craft' : STROKE_LOCK + 'Rank ' + ABIL_RANK;
    return '<button class="stopt' + (on ? ' on' : '') + (cr ? ' crafting' : '') + (ready ? ' ready' : '') + (free ? ' free' : '') + (!own && !cr && !free ? ' lock' : '') + '" type="button" data-st="' + o.id + '" aria-pressed="' + on + '" aria-label="' + escAttr(o.name + ', ' + st) + '">' + STROKE_ICON[o.id] + '<span class="stn">' + o.name + '</span><span class="sts">' + st + '</span></button>'; }).join('')
    + '<span class="stopt soon" aria-hidden="true"><svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="20" fill="none" stroke="#8A8396" stroke-width="4" stroke-dasharray="7 7"/></svg><span class="stn">More soon</span><span class="sts">Rank up</span></span>';
  $('stSkillRail').innerHTML = SKILLS.map(o => '<button class="stopt on" type="button" data-sk="' + o.id + '" aria-pressed="true" aria-label="' + escAttr(o.name + ', equipped') + '">' + STROKE_ICON[o.id] + '<span class="stn">' + o.name + '</span><span class="sts">Equipped</span></button>').join('')
    + '<span class="stopt soon" aria-hidden="true"><svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="20" fill="none" stroke="#8A8396" stroke-width="4" stroke-dasharray="7 7"/></svg><span class="stn">More soon</span><span class="sts">Rank up</span></span>';
  const cEl = $('stCraft'); cEl.hidden = !crafting; if (crafting) { const sp = SPECIALS.find(x => x.id === crafting.id), tot = sp.craft * 60000; $('stCraftT').textContent = mmss(left); $('stCraftBar').style.setProperty('--p', (100 * (1 - left / tot)).toFixed(1) + '%'); }
  paintAbil();
}
function strokesFrame() { if (!strokesOpen()) return; const d = strokesOf(); if (d.craft) { if (!craftTick()) { renderStrokes(); stToast('The Giant is ready!'); } else { $('stCraftT').textContent = mmss(craftLeft()); const sp = SPECIALS.find(x => x.id === d.craft.id); $('stCraftBar').style.setProperty('--p', (100 * (1 - craftLeft() / (sp.craft * 60000))).toFixed(1) + '%'); } } }
function openStrokes() {
  if (state !== 'menu' || building || lookOpen || shopOpen || strokesOpen()) return;
  if (menuPage === 'worlds') { closeSeason(); $('mWorld').hidden = true; } if (menuPage === 'events') closeEvents();
  menuPage = 'strokes'; menu.dataset.page = 'strokes'; $('mHome').hidden = true; $('mStrokes').hidden = false; document.body.classList.add('evon'); closeSide(true); renderStrokes();
  for (const c of $('mStrokes').querySelectorAll('.stslot')) { c.style.animation = 'none'; void c.offsetWidth; c.style.animation = ''; }
  clearInterval(stTick); stTick = setInterval(strokesFrame, 500); setTimeout(() => $('stBack').focus({ preventScroll: true }), 40);
}
function closeStrokes() { if (!strokesOpen()) return; clearInterval(stTick); $('mStrokes').hidden = true; document.body.classList.remove('evon'); menuPage = 'home'; menu.dataset.page = 'home'; $('mHome').hidden = false; paintAbil(); renderLobbyUI && renderLobbyUI(); setTimeout(() => $('abilBtn').focus({ preventScroll: true }), 40); }
$('stBack').addEventListener('click', () => { AU.init(); AU.ui(); closeStrokes(); });
$('stSkip').addEventListener('click', () => { AU.init(); craftSkip(); });
$('stSpecialRail').addEventListener('click', e => { const b = e.target.closest('.stopt[data-st]'); if (!b) return; AU.init(); const id = b.dataset.st, d = strokesOf();
  if (d.own.includes(id)) { if (strokeSpecial() !== id) equipSpecial(id); else AU.ui(); return; }
  if (d.craft) { AU.nope(); stToast('One craft at a time'); return; }
  if (strokesDue()) craftStart(id); else { AU.nope(); stToast('Reach rank ' + ABIL_RANK + ' to craft the ' + id); } });
$('stSkillRail').addEventListener('click', e => { if (e.target.closest('.stopt[data-sk]')) { AU.init(); AU.ui(); } });
""".replace("@ROCKET@", repr(ROCKET)).replace("@GIANT@", repr(GIANT)).replace("@SWIM@", repr(SWIM)).replace("@LOCK@", repr(LOCK))
# (the icons as JS strings: python repr gives single quotes, which is fine JS)
rep("// abilities: on the rail, locked until rank 3; past that, coming soon (a tap says which)", JS + "\n// abilities: on the rail, locked until rank 3; past that, the Strokes page")
# ---- the tile: unlocked, it opens the page (and pulses while a fresh Giant waits)
rep("function paintAbil() { const b = $('abilBtn'), on = repOf(store.xp || 0).lv >= ABIL_RANK; b.classList.toggle('locked', !on); $('abilTag').innerHTML = on ? 'Soon' : ABIL_LOCK + 'Rank ' + ABIL_RANK; b.setAttribute('aria-label', on ? 'Abilities, coming soon' : 'Abilities, locked until rank ' + ABIL_RANK); }",
    "function paintAbil() { const b = $('abilBtn'), on = repOf(store.xp || 0).lv >= ABIL_RANK, d = strokesOf(), fresh = on && (!!d.fresh || (!!d.craft && craftLeft() <= 0)); b.classList.toggle('locked', !on); b.classList.toggle('fresh', fresh); $('abilTag').innerHTML = on ? (fresh ? 'New!' : 'Strokes') : ABIL_LOCK + 'Rank ' + ABIL_RANK; b.setAttribute('aria-label', on ? 'Strokes: your special stroke and your skill' : 'Abilities, locked until rank ' + ABIL_RANK); }")
rep("$('abilBtn').addEventListener('click', () => { AU.init(); AU.nope(); const b = $('abilBtn'), rail = b.parentElement, on = !b.classList.contains('locked'), old = b.querySelector('.abtoast'); if (old) old.remove();\n  const t = document.createElement('span'); t.className = 'abtoast'; t.setAttribute('role', 'status'); t.textContent = on ? 'Abilities are coming soon' : 'Reach rank ' + ABIL_RANK + ' to unlock Abilities';",
    "$('abilBtn').addEventListener('click', () => { AU.init(); const b = $('abilBtn'), rail = b.parentElement, on = !b.classList.contains('locked'), old = b.querySelector('.abtoast'); if (old) old.remove(); if (on) { AU.ui(); openStrokes(); return; } AU.nope();\n  const t = document.createElement('span'); t.className = 'abtoast'; t.setAttribute('role', 'status'); t.textContent = 'Reach rank ' + ABIL_RANK + ' to unlock Strokes';")
rep('<span>Abilities</span><b class="abtag" id="abilTag" aria-hidden="true"></b></button>', '<span>Strokes</span><b class="abtag" id="abilTag" aria-hidden="true"></b></button>')
# ---- the orb gives you your special stroke (rivals still get either); the swim skill's pace
rep("const gift = tut ? 'rocket' : window.__orbKind || ['giant', 'rocket'][(Math.random() * 2) | 0];",
    "const gift = tut ? 'rocket' : window.__orbKind || (D === P ? strokeSpecial() : ['giant', 'rocket'][(Math.random() * 2) | 0]); /* (yours: the special stroke you equipped) */")
rep("  for (const D of ACTIVE) { D.eyeSink = D.eyeShut = D.eyeWide = 0; D.flowT = 1; D.flowK = 0; }",
    "  for (const D of ACTIVE) { D.eyeSink = D.eyeShut = D.eyeWide = 0; D.flowT = 1; D.flowK = 0; D.swimBoost = D === P && strokeSkill() === 'swim' ? SWIM_BOOST : 1; }")
# ---- the lesson: at rank 3, praise, then the page, then the Giant crafted and equipped
rep("function tutWelcomeDone(open) {", r"""// strokes: once you're rank 3 (and the first lessons are done), Ol' Bloop stops you in the lobby: look how far you've come; then let's
// learn some more: the Strokes page, the Giant crafted (Skip, this one's on him) and equipped
function tutStrokesDue() { return tutPh() === 'done' && !store.tut.strokes && strokesDue() && state === 'menu' && menuPage === 'home' && !lookOpen && !shopOpen && !building && !irisBusy && setModal.hidden && nameModal.hidden && howModal.hidden && $('tutGo').hidden && !vic; }
function tutStrokesCard(n) {
  const el = $('tutGo'); el.dataset.mode = 'strokes' + n;
  if (n === 1) tutCardText(['Look at <em>you</em>, rookie!', 'Rank ' + repOf(store.xp || 0).lv + ' already. You’ve come a long way since that first canvas, and I’ve been watching.', 'Aw, thanks', '']);
  else tutCardText(['Let’s learn <em>some more</em>', 'And get even better. You’ve unlocked Strokes: your special move, and a skill. Come see.', 'Show me', '']);
  if (el.hidden) { el.hidden = false; el.classList.remove('on'); void el.offsetWidth; el.classList.add('on'); } tutCardCoach(); if (n === 1) { AU.fanfare && AU.fanfare(); AU.bloop(0.55); menu.classList.add('tutoring'); } else AU.bloop(0.5); setTimeout(() => $('tgGo').focus({ preventScroll: true }), 60);
}
function tutStrokesGo() { const el = $('tutGo'), m = el.dataset.mode; if (m === 'strokes1') return tutStrokesCard(2); el.classList.remove('on'); el.hidden = true; coachCorner(null); el.dataset.mode = ''; store.tut.strokes = 'on'; tutSet('strokes'); setTimeout(() => openStrokes(), 250); }
function tutStrokesEnd() { tutSDone = 0; store.tut.strokes = 1; tutSet('done'); save(); tutHide(); menu.classList.remove('tutoring'); }
function tutStrokesTick() {
  if (state !== 'menu' || building || irisBusy || !setModal.hidden || !nameModal.hidden || !howModal.hidden) return tutHide();
  if (shopOpen) return tutShow('Back to the lobby', 'shopBack', 'back'); if (lookOpen) return tutShow('Back to the lobby', 'lkDone', 'back');
  if (menuPage === 'worlds') return tutShow('Back to the lobby', 'worldBack', 'back'); if (menuPage === 'events') return tutShow('Back to the lobby', 'evBack', 'back');
  if (!strokesOpen()) return tutShow('Tap Strokes to open it', 'abilBtn', 'sOpen');
  const d = strokesOf(), giant = () => $('stSpecialRail').querySelector('.stopt[data-st="giant"]');
  if (!d.own.includes('giant')) { if (d.craft) return tutShow('Crafting takes 20 minutes. Tap Skip, this one’s on me', 'stSkip', 'sSkip'); return tutShow('Your Special Stroke is what the orb gives you. The Giant is yours now: tap it to craft it', giant, 'sGiant'); }
  if (strokeSpecial() !== 'giant') return tutShow('It’s ready! Tap the Giant to make it your special stroke', giant, 'sEquip');
  if (!tutSDone) { tutSDone = performance.now(); tutShow('Giant it is! Grab the orb in a match and go big. Your Skill is below: Swim faster is on', null, 'sDone', false, true, null, true); }
  else if (performance.now() - tutSDone > 5200) tutStrokesEnd();
}
function tutWelcomeDone(open) {""")
rep("$('tgGo').addEventListener('click', () => { AU.init(); AU.ui(); if ($('tutGo').dataset.mode === 'welcome') tutWelcomeDone(true); else tutCard(false); });",
    "$('tgGo').addEventListener('click', () => { AU.init(); AU.ui(); const m = $('tutGo').dataset.mode; if (m === 'welcome') tutWelcomeDone(true); else if (m === 'strokes1' || m === 'strokes2') tutStrokesGo(); else tutCard(false); });")
rep("  if (tutPh() === 'done') { if (menu.classList.contains('tutoring')) menu.classList.remove('tutoring');",
    "  if (tutPh() === 'done' && tutStrokesDue()) { if (!tutStrokesAt) tutStrokesAt = performance.now(); if (performance.now() - tutStrokesAt > 1200) tutStrokesCard(1); return; } /* (a beat of the lobby, then the praise) */\n  if (tutPh() === 'done') { if (menu.classList.contains('tutoring')) menu.classList.remove('tutoring');")
rep("const tutBootEl = $('boot'), tutOrientEl = $('orient');", "const tutBootEl = $('boot'), tutOrientEl = $('orient'); let tutStrokesAt = 0, tutSDone = 0;")
rep("  if (ph !== 'shop' && ph !== 'locker' && ph !== 'vote') {", "  if (ph === 'strokes') { tutStrokesTick(); return; }\n  if (ph !== 'shop' && ph !== 'locker' && ph !== 'vote') {")
# the page like the shop and the locker: no dim, the control ringed
rep("  { const nb = shopOpen || lookOpen; if (tutDim.classList.contains('noblur') !== nb)", "  { const nb = shopOpen || lookOpen || strokesOpen(); if (tutDim.classList.contains('noblur') !== nb)")
rep('<p class="ver">Version 240</p>', '<p class="ver">Version 241</p>')
open(DST, 'w').write(s)
print('ui178 ok', n0, '->', len(s))
