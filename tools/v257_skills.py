"""v257: the Strokes page. Skills are crafted like the special strokes (Swim faster is yours from the start; Weather Repel takes 15
minutes, Deep Pockets 20, Skip as before). A tap on any stroke or skill opens its card: the picture, what it does (only what it does
for you: no downsides listed and no plus signs), a Craft button (the countdown and Skip while it's on the bench) and an Equip button
(only once it's crafted). The tiles carry no 'Tap to see' or 'Showing': just Equipped on the one you have on, a hammer on the ones
still to craft, a bar along the foot of the one being crafted. The box at the top of each slot shows what you have on.
Saves: the skills that were handed out free before go back on the bench, all but the one you have on. The Strokes lesson walks the
card (tap the Giant, Craft, Skip, Equip). The Flash Freeze card says 5 seconds (it was changed in v256). Deep Pockets has a simpler picture: a
denim pocket with the game's own orb peeking out (pocketorb257.py)."""
import base64, os
A = os.path.dirname(os.path.abspath(__file__)) + '/assets/'
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def cut(s, a, b, new):
    i = s.index(a); j = s.index(b, i) + len(b); assert s.count(a) == 1, a[:80]; return s[:i] + new + s[j:]

SPECIALS = r"""const SPECIALS = [{ id: 'rocket', name: 'Rocket', desc: 'Blast up over the canvas, then dive down in a splash.', does: ['Blast up high and hover over the canvas', 'Steer your mark, then dive down in a huge splash', 'Rivals under the splash get knocked out'] },
  { id: 'giant', name: 'Giant', desc: 'Grow huge, paint wide, stomp rivals flat.', craft: 20, does: ['Grow three times your size for 5 seconds', 'Move faster, with paint that never runs dry while it lasts', 'Your ground pound lands half as wide again'] },
  { id: 'freeze', name: 'Flash Freeze', desc: 'A flash over the canvas: every rival frozen solid for 5 seconds.', craft: 25, does: ['A flash over the whole canvas', 'Every rival frozen solid for 5 seconds', 'Paint all you like while they’re stuck'] }];
"""
SKILLS = r"""// v251: three skills, one on at a time. (v257) Crafted like the special strokes (Swim faster is yours from the start); a tap on one shows its card
const SKILLS = [
  { id: 'swim', name: 'Swim faster', desc: 'Built for speed, wet or dry.', does: ['8% more pace every time you glide', 'Twice as fast when the rain comes'] },
  { id: 'repel', name: 'Weather Repel', desc: 'Rain and heat roll right off you.', craft: 15, does: ['Rain and its puddles never water your paint down', 'The sun’s heat can’t burn you'] },
  { id: 'pockets', name: 'Deep Pockets', desc: 'Carry more, use it when you like.', craft: 20, does: ['Hold two power-ups and use either one', 'Your orb stays in its slot until you use it'] }];
const ST_STARTERS = ['rocket', 'swim']; // (yours from the start: everything else is crafted)
"""
SPNAME = r"""const stDef = id => SPECIALS.find(x => x.id === id) || SKILLS.find(x => x.id === id), stIsSkill = id => SKILLS.some(x => x.id === id);
const spName = id => (stDef(id) || { name: id }).name, ORB_LBL = { rocket: 'Rocket', giant: 'Giant', freeze: 'Freeze' };
const stReady = id => (stIsSkill(id) ? spName(id) : 'The ' + spName(id)) + ' is ready!';
"""
STROKESOF = r"""function strokesOf() { const d = store.strokes || (store.strokes = {}); if (!d.special) d.special = 'rocket'; if (!d.skill) d.skill = 'swim'; if (!Array.isArray(d.own)) d.own = ['rocket', 'swim']; for (const k of ST_STARTERS) if (!d.own.includes(k)) d.own.push(k);
  if (!d.sk257) { d.sk257 = 1; d.own = d.own.filter(k => !['repel', 'pockets'].includes(k) || k === d.skill); } // (v257: skills are crafted now; the ones handed out before go back on the bench, all but the one you have on)
  if (!SKILLS.some(x => x.id === d.skill) || !d.own.includes(d.skill)) d.skill = 'swim'; return d; }
"""
CRAFT = r"""function craftStart(id) { const d = strokesOf(), sp = stDef(id); if (!sp || !sp.craft || d.craft || d.own.includes(id)) return; d.craft = { id, end: Date.now() + sp.craft * 60000 }; save(); AU.pop(); buzz(10); renderStrokes(); }
function craftSkip() { const d = strokesOf(); if (!d.craft) return; const id = d.craft.id; d.craft.end = Date.now(); craftTick(); AU.ui(); buzz([10, 30, 10]); renderStrokes(); stToast(stReady(id)); }
"""
CARD = r"""// (v257) the tiles: the picture, the name, and Equipped on the one you have on; a hammer on one still to craft, a bar along the foot of the one being crafted
const ST_HAMMER = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12.6 3.6l7.8 7.8-2.5 2.5-2.1-2.1-8.4 8.4a1.9 1.9 0 0 1-2.7-2.7l8.4-8.4-2.1-2.1z" fill="currentColor"/></svg>';
const ST_GLASS = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 3h11M6.5 21h11M8 3c0 5.2 8 5.6 8 9s-8 3.8-8 9M16 3c0 5.2-8 5.6-8 9s8 3.8 8 9" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>';
const ST_CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 12.5l4.6 4.6L19.5 6.7" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const stPct = o => (100 * (1 - craftLeft() / (o.craft * 60000))).toFixed(1) + '%';
function stTile(o, skill) {
  const d = strokesOf(), own = d.own.includes(o.id), on = own && (skill ? strokeSkill() : strokeSpecial()) === o.id, cr = !!d.craft && d.craft.id === o.id, ready = own && !on && d.fresh === o.id, lock = !own && !cr && !strokesDue();
  const st = on ? 'equipped' : cr ? 'crafting, ' + mmss(craftLeft()) + ' left' : own ? 'crafted' : lock ? 'locked until rank ' + ABIL_RANK : 'not crafted yet';
  return '<button class="stopt' + (on ? ' on' : '') + (cr ? ' crafting' : '') + (ready ? ' ready' : '') + (!own && !cr ? ' raw' : '') + (lock ? ' lock' : '') + '" type="button" data-' + (skill ? 'sk' : 'st') + '="' + o.id + '" aria-pressed="' + on + '" aria-haspopup="dialog" aria-label="' + escAttr(o.name + ', ' + st) + '"' + (cr ? ' style="--p:' + stPct(o) + '"' : '') + '>'
    + STROKE_ICON[o.id] + '<span class="stn">' + o.name + '</span><span class="sts' + (on ? '' : ' nil') + '">Equipped</span>'
    + (cr ? '<span class="stb" aria-hidden="true">' + ST_GLASS + '</span><span class="stcb" aria-hidden="true"><i></i></span>' : !own ? '<span class="stb" aria-hidden="true">' + (lock ? STROKE_LOCK : ST_HAMMER) + '</span>' : '') + '</button>';
}
// (v257) a stroke's card, over the page: what it does, Craft (then its countdown and Skip) and Equip
let stPopId = null, stPopT = 0;
function stPopTick() { if (!stPopId) return; const d = strokesOf(), o = stDef(stPopId); if (!o || !d.craft || d.craft.id !== stPopId) return; $('stPopT').textContent = mmss(craftLeft()); $('stPopBar').style.setProperty('--p', stPct(o)); }
function stPopRender() {
  if (!stPopId) return; const id = stPopId, o = stDef(id); if (!o) return closeStPop(true);
  const d = strokesOf(), skill = stIsSkill(id), own = d.own.includes(id), on = own && (skill ? strokeSkill() : strokeSpecial()) === id, cr = !!d.craft && d.craft.id === id, busy = !!d.craft && !cr, due = strokesDue();
  const card = $('stPop').querySelector('.stpop'); card.classList.toggle('skill', skill);
  if (card.dataset.id === id && card.dataset.own === '0' && own) { const a = $('stPopArt'); a.style.animation = 'none'; void a.offsetWidth; a.style.animation = ''; } // (just crafted: the picture pops again)
  card.dataset.id = id; card.dataset.own = own ? '1' : '0';
  $('stPopKind').textContent = skill ? 'Skill' : 'Special stroke';
  if ($('stPopArt').dataset.id !== id) { $('stPopArt').dataset.id = id; $('stPopArt').innerHTML = STROKE_ICON[id]; }
  $('stPopName').textContent = o.name; $('stPopDesc').textContent = o.desc;
  $('stPopDoes').innerHTML = o.does.map(t => '<li>' + t + '</li>').join('');
  const cb = $('stPopCraftBtn'), eb = $('stPopEquip');
  $('stPopTimer').hidden = !cr; cb.hidden = cr;
  cb.disabled = own || busy || !due; cb.classList.toggle('done', own);
  cb.innerHTML = own ? ST_CHECK + (ST_STARTERS.includes(id) ? 'Yours' : 'Crafted') : 'Craft<small>' + o.craft + ' min</small>';
  eb.disabled = !own || on; eb.classList.toggle('on', on); eb.innerHTML = on ? ST_CHECK + 'Equipped' : (own ? '' : STROKE_LOCK) + 'Equip';
  const note = own ? '' : busy ? 'One craft at a time: ' + spName(d.craft.id) + ' is on the bench' : !due ? 'Reach rank ' + ABIL_RANK + ' to craft it' : '';
  $('stPopNote').hidden = !note; $('stPopNote').textContent = note;
  stPopTick();
}
function openStPop(id) {
  if (!stDef(id) || !strokesOpen()) return; const d = strokesOf(); if (d.fresh === id) { d.fresh = null; save(); }
  clearTimeout(stPopT); stPopId = id; const m = $('stPop'), was = m.hidden; m.hidden = false; renderStrokes(); AU.ui(); buzz(6);
  if (was) { const c = m.querySelector('.stpop'); c.style.animation = 'none'; void c.offsetWidth; c.style.animation = ''; }
  setTimeout(() => { if (stPopId !== id) return; const cb = $('stPopCraftBtn'), eb = $('stPopEquip'), b = !cb.hidden && !cb.disabled ? cb : !eb.disabled ? eb : $('stPopX'); b.focus({ preventScroll: true }); }, 40);
}
function closeStPop(quiet) { clearTimeout(stPopT); if (!stPopId) return; const id = stPopId; stPopId = null; $('stPop').hidden = true; if (!quiet) AU.ui(); const t = document.querySelector('.stopt[data-st="' + id + '"], .stopt[data-sk="' + id + '"]'); if (t && strokesOpen()) t.focus({ preventScroll: true }); }
function skillCard() {}
"""
RENDER = r"""function renderStrokes() {
  const d = strokesOf(); craftTick();
  const now = (id, list, el) => { const o = list.find(x => x.id === id) || list[0]; el.innerHTML = '<span class="stic">' + STROKE_ICON[o.id] + '</span><span><span class="stname">' + o.name + '</span><span class="stdesc">' + o.desc + '</span><span class="ststamp">Equipped</span></span>'; };
  now(strokeSpecial(), SPECIALS, $('stSpecialNow')); now(strokeSkill(), SKILLS, $('stSkillNow'));
  const soon = '<span class="stopt soon" aria-hidden="true">' + stImg('soon') + '<span class="stn">More soon</span><span class="sts nil">Equipped</span></span>';
  $('stSpecialRail').innerHTML = SPECIALS.map(o => stTile(o, false)).join('') + soon;
  $('stSkillRail').innerHTML = SKILLS.map(o => stTile(o, true)).join('') + soon;
  const crafting = d.craft, cEl = $('stCraft'); cEl.hidden = !crafting;
  if (crafting) { const sp = stDef(crafting.id), slot = stIsSkill(crafting.id) ? $('stSkill') : $('stSpecial'); if (cEl.parentNode !== slot) slot.appendChild(cEl); $('stCraftT').textContent = mmss(craftLeft());
    { const ct = cEl.querySelector('.stct'); if (ct && ct.firstChild && ct.firstChild.nodeType === 3) ct.firstChild.nodeValue = 'Crafting ' + (stIsSkill(crafting.id) ? '' : 'the ') + sp.name; } $('stCraftBar').style.setProperty('--p', stPct(sp)); }
  paintAbil(); stPopRender();
}
function strokesFrame() { if (!strokesOpen()) return; const d = strokesOf(); if (d.craft) { const id = d.craft.id; if (!craftTick()) { renderStrokes(); stToast(stReady(id)); } else { const sp = stDef(id), p = stPct(sp); $('stCraftT').textContent = mmss(craftLeft()); $('stCraftBar').style.setProperty('--p', p); const t = document.querySelector('.stopt.crafting'); if (t) t.style.setProperty('--p', p); stPopTick(); } } }
"""
LISTEN = r"""$('stSpecialRail').addEventListener('click', e => { const b = e.target.closest('.stopt[data-st]'); if (!b) return; AU.init(); openStPop(b.dataset.st); });
$('stSkillRail').addEventListener('click', e => { const b = e.target.closest('.stopt[data-sk]'); if (!b) return; AU.init(); openStPop(b.dataset.sk); });
$('stPopX').addEventListener('click', () => { AU.init(); closeStPop(); });
$('stPop').addEventListener('click', e => { if (e.target === $('stPop')) { AU.init(); closeStPop(); } });
$('stPopCraftBtn').addEventListener('click', () => { AU.init(); const id = stPopId, d = strokesOf(); if (!id || d.own.includes(id)) return; if (d.craft) { AU.nope(); stToast('One craft at a time'); return; } if (!strokesDue()) { AU.nope(); stToast('Reach rank ' + ABIL_RANK + ' to craft ' + spName(id)); return; } craftStart(id); });
$('stPopSkip').addEventListener('click', () => { AU.init(); craftSkip(); });
$('stPopEquip').addEventListener('click', () => { AU.init(); const id = stPopId; if (!id || !strokeOwned(id)) return; if (stIsSkill(id)) equipSkill(id); else equipSpecial(id); clearTimeout(stPopT); stPopT = setTimeout(() => closeStPop(true), 420); }); // (Equipped shows for a beat, then the card goes)
document.addEventListener('keydown', e => { if (e.key === 'Escape' && stPopId) { e.preventDefault(); e.stopPropagation(); closeStPop(); } }, true);
"""
POP_HTML = r"""  <div class="modal stpopm" id="stPop" hidden><div class="stpop" role="dialog" aria-modal="true" aria-labelledby="stPopName">
    <div class="stphead"><b id="stPopKind">Skill</b><button class="stpx" id="stPopX" type="button" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/></svg></button></div>
    <div class="stpbody"><span class="stpart" id="stPopArt" aria-hidden="true"></span><h3 class="stpname" id="stPopName"></h3><p class="stpdesc" id="stPopDesc"></p>
      <ul class="stpdoes" id="stPopDoes" aria-label="What it does"></ul>
      <div class="stptimer" id="stPopTimer" hidden><span class="stpt">Crafting<b id="stPopT">0:00</b></span><button class="stskip" id="stPopSkip" type="button">Skip</button><span class="stbar"><i id="stPopBar"></i></span></div>
      <div class="stpbtns"><button class="stpb craft" id="stPopCraftBtn" type="button">Craft</button><button class="stpb equip" id="stPopEquip" type="button">Equip</button></div>
      <p class="stpnote" id="stPopNote" hidden></p></div>
  </div></div>
"""
CSS = r"""/* (v257) the Strokes page: tiles with just a name (and Equipped on the one you have on), and a card over the page for each stroke */
.stopt .sts.nil{visibility:hidden}
.strail{padding-top:10px}
.stopt .stb{position:absolute;right:-6px;top:-6px;z-index:1;display:grid;place-items:center;width:25px;height:25px;border-radius:50%;background:#171320;color:#F4EEE3;box-shadow:0 0 0 2.5px #F4EEE3}
.stopt .stb svg{width:13px;height:13px}
.stopt.raw .stimg{filter:saturate(.3) brightness(1.08);opacity:.7}
.stopt.raw .stn{color:#5A5468}
.stopt.crafting .stb{background:var(--gold);color:#171320}
.stopt .stcb{position:absolute;left:12px;right:12px;bottom:11px;height:6px;border-radius:999px;background:#E9E3D6;box-shadow:inset 0 0 0 1.5px rgba(23,19,32,.18);overflow:hidden}
.stopt .stcb i{display:block;height:100%;width:var(--p,0%);border-radius:999px;background:linear-gradient(90deg,#F2C14E,#E3A70F);transition:width .5s linear}
.stopt.ready::after{content:"";position:absolute;right:-5px;top:-5px;width:15px;height:15px;border-radius:50%;background:#E3122F;box-shadow:0 0 0 2.5px #F4EEE3;animation:stdot 1.2s ease-in-out infinite}
@keyframes stdot{50%{transform:scale(1.25)}}
.stopt:focus-visible{outline:3px solid #7CC8FF;outline-offset:3px}
.stpopm{z-index:14}
.stpop{position:relative;width:min(100%,348px);max-height:100%;overflow:auto;box-sizing:border-box;border-radius:18px;background:#F4EEE3;color:#171320;box-shadow:0 0 0 3px #171320,7px 8px 0 rgba(0,0,0,.45);scrollbar-width:none;overscroll-behavior:contain;animation:cardlift .34s cubic-bezier(.2,1.25,.35,1) both}
.stpop::-webkit-scrollbar{display:none}
.stphead{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 9px 9px 16px;border-radius:15px 15px 0 0;background:#171320}
.stphead b{font:900 15px/1 var(--font-head);font-style:italic;text-transform:uppercase;letter-spacing:.06em;color:var(--gold);text-shadow:.05em .05em 0 rgba(0,0,0,.6)}
.stpop.skill .stphead b{color:#7CC8FF}
.stpx{appearance:none;display:grid;place-items:center;width:36px;height:36px;margin:0;padding:0;border:0;border-radius:50%;background:#2E2840;color:#fff;cursor:pointer;-webkit-tap-highlight-color:transparent}
.stpx:active{transform:scale(.92)}
.stpx svg{width:16px;height:16px}
.stpbody{display:grid;grid-template-columns:minmax(0,1fr);justify-items:center;gap:8px;padding:16px 18px 18px;text-align:center}
.stpart{display:grid;place-items:center;width:116px;height:116px;border-radius:28px;background:#fff;box-shadow:0 0 0 3px #171320,4px 5px 0 rgba(23,19,32,.25);animation:stpart .5s .05s cubic-bezier(.3,1.6,.5,1) both}
@keyframes stpart{from{transform:scale(.6) rotate(-8deg);opacity:0}}
.stpart .stimg{width:96px;height:96px;object-fit:contain}.stpart svg{width:76px;height:76px}
.stpname{margin:6px 0 0;font:900 28px/1 var(--font-head);text-transform:uppercase;letter-spacing:.01em;color:#171320;text-wrap:balance}
.stpdesc{margin:0;max-width:30ch;font:600 14px/1.35 var(--font-ui);color:#4A4458}
.stpdoes{display:grid;gap:9px;width:100%;margin:4px 0 2px;padding:13px 14px;list-style:none;box-sizing:border-box;border-radius:14px;background:#fff;box-shadow:inset 0 0 0 2px rgba(23,19,32,.12);text-align:left}
.stpdoes li{position:relative;padding-left:21px;font:700 14px/1.3 var(--font-ui);color:#2E2840}
.stpdoes li::before{content:"";position:absolute;left:2px;top:.34em;width:10px;height:10px;border-radius:50% 50% 50% 18%;background:var(--ink);box-shadow:0 0 0 2px #171320;transform:rotate(-30deg)}
.stpop.skill .stpdoes li::before{background:#7CC8FF}
.stpbtns{display:grid;grid-template-columns:1fr 1fr;gap:10px;width:100%;margin-top:6px}
.stpbtns .stpb[hidden]+.stpb{grid-column:1/-1}
.stpb{appearance:none;display:flex;align-items:center;justify-content:center;gap:6px;min-width:0;min-height:52px;margin:0;padding:10px 10px;border:0;border-radius:14px;font:900 17px/1 var(--font-head);letter-spacing:.05em;text-transform:uppercase;cursor:pointer;-webkit-tap-highlight-color:transparent;box-shadow:0 0 0 2.5px #171320,0 4px 0 #171320;transition:transform .1s}
.stpb[hidden]{display:none}
.stpb:active:not(:disabled){transform:translateY(3px);box-shadow:0 0 0 2.5px #171320,0 1px 0 #171320}
.stpb small{margin-left:2px;padding:3px 6px 2px;border-radius:999px;background:rgba(11,42,20,.16);font:900 10px/1 var(--font-head);letter-spacing:.04em;white-space:nowrap}
.stpb svg{flex:none;width:16px;height:16px}
.stpb.craft{background:#46E07A;color:#0B2A14}
.stpb.equip{background:var(--gold);color:#171320}
.stpb:disabled{cursor:default;background:#E2DBCD;color:#8A8396;box-shadow:0 0 0 2.5px rgba(23,19,32,.3),0 3px 0 rgba(23,19,32,.3)}
.stpb:disabled small{background:rgba(23,19,32,.08)}
.stpb.done:disabled,.stpb.on:disabled{background:#fff;color:#171320;box-shadow:0 0 0 2.5px #171320,0 3px 0 rgba(23,19,32,.3)}
.stpb.done:disabled svg,.stpb.on:disabled svg{color:#1E9B4F}
.stpb.on:disabled{animation:stpon .35s cubic-bezier(.3,1.6,.5,1)}
@keyframes stpon{40%{transform:scale(1.06)}}
.stptimer{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;width:100%;box-sizing:border-box;margin-top:6px;padding:10px 12px;border-radius:12px;background:#171320;color:#fff;text-align:left}
.stptimer[hidden]{display:none}
.stptimer .stpt{font:800 12px/1.2 var(--font-ui);color:#B8B0C8}
.stptimer .stpt b{display:block;font:900 22px/1 var(--font-head);color:#fff;font-variant-numeric:tabular-nums;letter-spacing:.02em}
.stptimer .stbar{grid-column:1/-1;height:8px;border-radius:999px;background:#2A2436;overflow:hidden}
.stptimer .stbar i{display:block;height:100%;width:var(--p,0%);background:linear-gradient(90deg,#F2C14E,#FFE39A);border-radius:999px;transition:width .5s linear}
.stptimer .stskip{appearance:none;margin:0;padding:10px 16px;border:0;border-radius:999px;background:var(--gold);color:#171320;font:900 14px/1 var(--font-head);letter-spacing:.08em;text-transform:uppercase;box-shadow:0 0 0 2px #171320,0 3px 0 #171320;cursor:pointer;-webkit-tap-highlight-color:transparent}
.stptimer .stskip:active{transform:translateY(2px);box-shadow:0 0 0 2px #171320,0 1px 0 #171320}
.stpnote{margin:2px 0 0;font:700 12px/1.3 var(--font-ui);color:#7A7388}
.stpnote[hidden]{display:none}
@media (prefers-reduced-motion:reduce){.stpop,.stpart,.stopt.ready::after,.stpb.on:disabled{animation:none}}
@media (max-height:520px) and (min-aspect-ratio:1/1){
  .stpop{width:min(100%,560px)}
  .stpbody{grid-template-columns:96px minmax(0,1fr);grid-template-areas:"art name" "art desc" "does does" "timer timer" "btns btns" "note note";justify-items:start;align-items:center;column-gap:16px;row-gap:7px;padding:12px 16px 14px;text-align:left}
  .stpart{grid-area:art;width:92px;height:92px;border-radius:22px}.stpart .stimg{width:76px;height:76px}.stpart svg{width:60px;height:60px}
  .stpname{grid-area:name;align-self:end;margin:0;font-size:24px}.stpdesc{grid-area:desc;align-self:start}
  .stpdoes{grid-area:does;padding:10px 12px;gap:6px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));column-gap:16px}
  .stptimer{grid-area:timer;margin-top:0}.stpbtns{grid-area:btns;margin-top:2px}.stpnote{grid-area:note}
  .stpb{min-height:46px}
}"""

def apply(s):
    s = cut(s, "const SPECIALS = [{ id: 'rocket'", "];\n", SPECIALS)
    s = cut(s, "// v251: three skills, one on at a time;", "}];\n", SKILLS)
    s = cut(s, "const spName = id => (SPECIALS.find(", "freeze: 'Freeze' };\n", SPNAME)
    s = cut(s, "function strokesOf() {", " return d; }\n", STROKESOF)
    s = cut(s, "function craftStart(id) {", "renderStrokes(); }\n", CRAFT.split('\n')[0] + '\n')
    s = cut(s, "function craftSkip() {", "is ready!'); }\n", CRAFT.split('\n')[1] + '\n')
    # the skill box and its breakdown: the box now shows what you have on (the card shows the rest)
    s = cut(s, "let stSkillSel = null;", "\n}\n", "let stSkillSel = null; // (v257: unused; each stroke's card shows what it does)\n" + CARD)
    s = cut(s, "function renderStrokes() {", "  paintAbil();\n}\n", RENDER.split('function strokesFrame')[0])
    s = cut(s, "function strokesFrame() {", "\n", 'function strokesFrame' + RENDER.split('function strokesFrame')[1])
    s = cut(s, "$('stSpecialRail').addEventListener('click', e => {", "$('stSkillNow').addEventListener('click', e => { const b = e.target.closest('.stequip'); if (!b) return; AU.init(); equipSkill(b.dataset.eq); });\n", LISTEN)
    s = rep(s, "function closeStrokes() { if (!strokesOpen()) return; clearInterval(stTick);", "function closeStrokes() { if (!strokesOpen()) return; closeStPop(true); clearInterval(stTick);")
    s = rep(s, "$('stBack').addEventListener('click', () => { AU.init(); AU.ui(); closeStrokes(); });", "$('stBack').addEventListener('click', () => { AU.init(); if (stPopId) return closeStPop(); AU.ui(); closeStrokes(); });")
    s = rep(s, '<p class="stsub">Your special move and your skill. New ones open as you rank up.</p>', '<p class="stsub">Tap one to see what it does. Craft it, then equip it.</p>')
    # the lesson: tap the Giant, Craft, Skip, Equip (on the card)
    a = "  if (!d.own.includes('giant')) { if (d.craft) return tutShow('Crafting takes 20 minutes. Tap Skip, this one’s on me', 'stSkip', 'sSkip', false, false, null, false, true); return tutShow('Your Special Stroke is what the orb gives you. The Giant is yours now: tap it to craft it', giant, 'sGiant', false, false, null, false, true); }\n  if (strokeSpecial() !== 'giant') return tutShow('It’s ready! Tap the Giant to make it your special stroke', giant, 'sEquip', false, false, null, false, true);\n"
    b = ("  if (stPopId && stPopId !== 'giant' && !(d.craft && d.craft.id === stPopId)) closeStPop(true); // (v257: the lesson walks the Giant's card)\n"
         "  if (!d.own.includes('giant')) { if (d.craft) return tutShow('Crafting takes 20 minutes. Tap Skip, this one’s on me', stPopId === d.craft.id ? 'stPopSkip' : 'stSkip', 'sSkip', false, false, null, false, true);\n"
         "    if (stPopId === 'giant') return tutShow('Tap Craft to start on it', 'stPopCraftBtn', 'sCraft', false, false, null, false, true);\n"
         "    return tutShow('Your Special Stroke is what the orb gives you. The Giant is yours to craft: tap it', giant, 'sGiant', false, false, null, false, true); }\n"
         "  if (strokeSpecial() !== 'giant') { if (stPopId === 'giant') return tutShow('It’s ready! Tap Equip to make it your special stroke', 'stPopEquip', 'sEquip', false, false, null, false, true);\n"
         "    return tutShow('It’s ready! Tap the Giant', giant, 'sEquipT', false, false, null, false, true); }\n"
         "  if (stPopId) return; // (Equipped shows on the card for a beat, then it goes)\n")
    s = rep(s, a, b)
    s = rep(s, "tutShow('Giant it is! Grab the orb in a match and go big. Your Skill is below: Swim faster is on'", "tutShow('Giant it is! Grab the orb in a match and go big. Skills are below: Swim faster is on, and you can craft the others'")
    s = rep(s, '  <div class="modal" id="commModal" hidden>', POP_HTML + '  <div class="modal" id="commModal" hidden>')
    # (the lessons stand back while a dialog is up: not for a stroke's card, which the Strokes lesson walks)
    s = rep(s, "document.querySelector('.modal:not([hidden])')) return tutHide();", "document.querySelector('.modal:not([hidden]):not(#stPop)')) return tutHide();")
    s = rep(s, "\n</style>\n\n<div id=\"stage\">", "\n" + CSS.strip() + "\n</style>\n\n<div id=\"stage\">")
    # Deep Pockets' picture, simpler: a denim pocket (Ludo.ai, the sticker style of the rest) with the game's own orb in it, rendered with its shader
    k = "pockets: 'data:image/webp;base64,"; i = s.index(k, s.index('const ST_IMG = {')); j = s.index("'", i + len(k)); assert s.count(k) == 1
    s = s[:i] + k + base64.b64encode(open(A + 'pockets257_256.webp', 'rb').read()).decode() + s[j:]
    return s
