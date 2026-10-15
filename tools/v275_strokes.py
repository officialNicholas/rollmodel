"""v275: the Strokes page, rebuilt. It had grown long: three tall paper sections, each repeating the equipped stroke above its own rail of
thick-outlined tiles. Now it's a loadout. Up top, three slots side by side (Special, Skill, Item), each showing what you have on; they
are the page's tabs, so only one collection shows at a time, in a grid under them: no scrolling on a phone. The tiles are dark cards with
the stroke's picture on a glow of its slot's color (gold specials, blue skills, red items) and a status line along the foot: Equipped,
Owned, its craft time, the bar and the time left while it's on the bench, the rank it opens at, or New. A craft in progress shows as one
bench bar under the loadout. The card a tile opens is a sheet that rises from the foot of the screen (centred in landscape) with one
button at a time: Craft (and its time), the bench's countdown and Skip, or Equip. Landscape stacks the slots down the left with the
grid on the right. Ol' Bloop's Strokes lesson keeps the Special tab up while he walks you through the Giant."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def region(s, a, b, new):
    assert s.count(a) == 1, (s.count(a), a[:120]); i = s.index(a); j = s.index(b, i); return s[:i] + new + s[j:]

MARKUP = """      <div class="stwrap" id="stWrap">
        <div class="stload" role="tablist" aria-label="Your loadout">
          <button class="stslot" id="stSpecial" type="button" role="tab" data-cat="special" aria-controls="stSpecialRail"><span class="stk">Special</span><span class="stnow" id="stSpecialNow"></span></button>
          <button class="stslot" id="stSkill" type="button" role="tab" data-cat="skill" aria-controls="stSkillRail"><span class="stk">Skill</span><span class="stnow" id="stSkillNow"></span></button>
          <button class="stslot" id="stItem" type="button" role="tab" data-cat="item" aria-controls="stItemRail"><span class="stk">Item</span><span class="stnow" id="stItemNow"></span></button>
        </div>
        <div class="stcraft" id="stCraft" hidden><span class="stcic" id="stCraftIc" aria-hidden="true"></span><span class="stct"><small>On the bench</small><span id="stCraftN">Giant</span></span><b class="stctime" id="stCraftT">20:00</b><button class="stskip" id="stSkip" type="button">Skip</button><span class="stbar" aria-hidden="true"><i id="stCraftBar"></i></span></div>
        <section class="stpanel" id="stPanel" aria-labelledby="stCatH"><div class="stphd"><h3 id="stCatH">Special strokes</h3><small id="stCatS">What the orb gives you</small></div>
          <div class="strail" id="stSpecialRail" role="tabpanel" aria-labelledby="stSpecial"></div>
          <div class="strail" id="stSkillRail" role="tabpanel" aria-labelledby="stSkill" hidden></div>
          <div class="strail" id="stItemRail" role="tabpanel" aria-labelledby="stItem" hidden></div>
        </section>
      </div>
"""

POP = """  <div class="modal stpopm" id="stPop" hidden><div class="stpop" role="dialog" aria-modal="true" aria-labelledby="stPopName">
    <div class="stphead"><b id="stPopKind">Skill</b><span class="stpown" id="stPopOwn" hidden></span><button class="stpx" id="stPopX" type="button" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></button></div>
    <div class="stpbody"><span class="stpart" id="stPopArt" aria-hidden="true"></span><h3 class="stpname" id="stPopName"></h3><p class="stpdesc" id="stPopDesc"></p>
      <ul class="stpdoes" id="stPopDoes" aria-label="What it does"></ul>
      <div class="stptimer" id="stPopTimer" hidden><span class="stpt">On the bench<b id="stPopT">0:00</b></span><button class="stskip" id="stPopSkip" type="button">Skip</button><span class="stbar"><i id="stPopBar"></i></span></div>
      <div class="stpbtns"><button class="stpb craft" id="stPopCraftBtn" type="button">Craft</button><button class="stpb equip" id="stPopEquip" type="button">Equip</button></div>
      <p class="stpnote" id="stPopNote" hidden></p></div>
  </div></div>
"""

JS_TILE = r"""const ST_HAMMER = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12.6 3.6l7.8 7.8-2.5 2.5-2.1-2.1-8.4 8.4a1.9 1.9 0 0 1-2.7-2.7l8.4-8.4-2.1-2.1z" fill="currentColor"/></svg>';
const ST_GLASS = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 3h11M6.5 21h11M8 3c0 5.2 8 5.6 8 9s-8 3.8-8 9M16 3c0 5.2-8 5.6-8 9s8 3.8 8 9" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>';
const ST_CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 12.5l4.6 4.6L19.5 6.7" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const stPct = o => (100 * (1 - craftLeft() / (o.craft * 60000))).toFixed(1) + '%';
// (v275) the tiles: the picture on a glow of its slot's color, the name, and a status line along the foot: Equipped, Owned (Yours for the
// items), the craft time on one still to craft, its bar and the time left while it's on the bench, the rank it opens at, or New
const ST_CATS = { special: { h: 'Special strokes', s: 'What the orb gives you', rail: 'stSpecialRail', slot: 'stSpecial' }, skill: { h: 'Skills', s: 'Always on, all match', rail: 'stSkillRail', slot: 'stSkill' }, item: { h: 'Items', s: 'You start every match holding it', rail: 'stItemRail', slot: 'stItem' } };
let stCat = 'special';
const stCatOf = id => stIsItem(id) ? 'item' : stIsSkill(id) ? 'skill' : 'special';
function stSetCat(cat, quiet) {
  if (!ST_CATS[cat]) cat = 'special'; const was = stCat; stCat = cat;
  for (const k in ST_CATS) { const on = k === cat, sl = $(ST_CATS[k].slot), r = $(ST_CATS[k].rail); sl.classList.toggle('on', on); sl.setAttribute('aria-selected', on ? 'true' : 'false'); sl.tabIndex = on ? 0 : -1; r.hidden = !on; }
  const P = $('stPanel'); P.dataset.cat = cat; $('stCatH').textContent = ST_CATS[cat].h; $('stCatS').textContent = ST_CATS[cat].s;
  if (was !== cat && !quiet) { AU.ui(); buzz(5); const r = $(ST_CATS[cat].rail); r.classList.remove('in'); void r.offsetWidth; r.classList.add('in'); }
}
function stTile(o, skill) {
  const d = strokesOf(), item = skill === 'item', own = item || d.own.includes(o.id), on = own && (item ? strokeItem() : skill ? strokeSkill() : strokeSpecial()) === o.id, cr = !!d.craft && d.craft.id === o.id, ready = own && !on && d.fresh === o.id, lock = !own && !cr && !strokesDue();
  const st = on ? 'equipped' : cr ? 'crafting, ' + mmss(craftLeft()) + ' left' : own ? (item ? 'yours' : 'owned') : lock ? 'locked until rank ' + ABIL_RANK : 'craft it in ' + o.craft + ' minutes';
  const foot = on ? '<span class="stost on">' + ST_CHECK + 'Equipped</span>' : cr ? '<span class="stost cr"><span class="stcb"><i></i></span><b>' + mmss(craftLeft()) + '</b></span>' : ready ? '<span class="stost new">New</span>'
    : own ? '<span class="stost own">' + (item || ST_STARTERS.includes(o.id) ? 'Yours' : 'Owned') + '</span>' : lock ? '<span class="stost lk">' + STROKE_LOCK + 'Rank ' + ABIL_RANK + '</span>' : '<span class="stost raw">' + ST_GLASS + o.craft + ' min</span>';
  return '<button class="stopt' + (on ? ' on' : '') + (cr ? ' crafting' : '') + (ready ? ' ready' : '') + (!own && !cr ? ' raw' : '') + (lock ? ' lock' : '') + '" type="button" data-' + (item ? 'it' : skill ? 'sk' : 'st') + '="' + o.id + '" aria-pressed="' + on + '" aria-haspopup="dialog" aria-label="' + escAttr(o.name + ', ' + st) + '"' + (cr ? ' style="--p:' + stPct(o) + '"' : '') + '>'
    + '<span class="stoi">' + STROKE_ICON[o.id] + '</span><span class="stn">' + o.name + '</span>' + foot + '</button>';
}
"""

JS_POP = r"""function stPopRender() {
  if (!stPopId) return; const id = stPopId, o = stDef(id); if (!o) return closeStPop(true);
  const d = strokesOf(), skill = stIsSkill(id), item = stIsItem(id), own = item || d.own.includes(id), on = own && (item ? strokeItem() : skill ? strokeSkill() : strokeSpecial()) === id, cr = !!d.craft && d.craft.id === id, busy = !!d.craft && !cr, due = strokesDue();
  const card = $('stPop').querySelector('.stpop'); card.classList.toggle('skill', skill || item); card.dataset.cat = stCatOf(id);
  if (card.dataset.id === id && card.dataset.own === '0' && own) { const a = $('stPopArt'); a.style.animation = 'none'; void a.offsetWidth; a.style.animation = ''; } // (just crafted: the picture pops again)
  card.dataset.id = id; card.dataset.own = own ? '1' : '0';
  $('stPopKind').textContent = item ? 'Item' : skill ? 'Skill' : 'Special stroke';
  const ow = $('stPopOwn'); ow.hidden = !own; ow.innerHTML = ST_CHECK + (on ? 'Equipped' : item || ST_STARTERS.includes(id) ? 'Yours' : 'Crafted');
  if ($('stPopArt').dataset.id !== id) { $('stPopArt').dataset.id = id; $('stPopArt').innerHTML = STROKE_ICON[id]; }
  $('stPopName').textContent = o.name; $('stPopDesc').textContent = o.desc;
  $('stPopDoes').innerHTML = o.does.map(t => '<li>' + t + '</li>').join('');
  // (one button at a time: Craft while it's not yours, the bench's countdown while it's crafting, then Equip)
  const cb = $('stPopCraftBtn'), eb = $('stPopEquip');
  $('stPopTimer').hidden = !cr; cb.hidden = own || cr; eb.hidden = !own;
  cb.disabled = busy || !due; cb.classList.remove('done'); cb.innerHTML = (due ? '' : STROKE_LOCK) + 'Craft<small>' + o.craft + ' min</small>';
  eb.disabled = on; eb.classList.toggle('on', on); eb.innerHTML = on ? ST_CHECK + 'Equipped' : 'Equip';
  const note = own ? '' : busy ? 'One craft at a time: ' + spName(d.craft.id) + ' is on the bench' : !due ? 'Reach rank ' + ABIL_RANK + ' to craft it' : '';
  $('stPopNote').hidden = !note; $('stPopNote').textContent = note;
  stPopTick();
}
"""

JS_RENDER = r"""function renderStrokes() {
  const d = strokesOf(); craftTick();
  const now = (id, list, el, k) => { const o = list.find(x => x.id === id) || list[0]; el.innerHTML = '<span class="stic">' + STROKE_ICON[o.id] + '</span><span class="stname">' + o.name + '</span>'; $(ST_CATS[k].slot).setAttribute('aria-label', ST_CATS[k].slot === 'stSpecial' ? 'Special stroke: ' + o.name : (k === 'skill' ? 'Skill: ' : 'Item: ') + o.name); };
  now(strokeSpecial(), SPECIALS, $('stSpecialNow'), 'special'); now(strokeSkill(), SKILLS, $('stSkillNow'), 'skill'); now(strokeItem(), ST_ITEMS, $('stItemNow'), 'item');
  for (const k of ['special', 'skill']) $(ST_CATS[k].slot).classList.toggle('fresh', !!d.fresh && stCatOf(d.fresh) === k); // (a dot on the slot with something newly crafted)
  const soon = '<span class="stopt soon" aria-hidden="true"><span class="stoi">' + stImg('soon') + '</span><span class="stn">More soon</span><span class="stost">&nbsp;</span></span>';
  $('stSpecialRail').innerHTML = SPECIALS.map(o => stTile(o, false)).join('') + soon;
  $('stSkillRail').innerHTML = SKILLS.map(o => stTile(o, true)).join('') + soon; $('stItemRail').innerHTML = ST_ITEMS.map(o => stTile(o, 'item')).join('') + soon;
  const crafting = d.craft, cEl = $('stCraft'); cEl.hidden = !crafting;
  if (crafting) { const sp = stDef(crafting.id); cEl.dataset.cat = stCatOf(crafting.id); $('stCraftN').textContent = sp.name; if ($('stCraftIc').dataset.id !== sp.id) { $('stCraftIc').dataset.id = sp.id; $('stCraftIc').innerHTML = STROKE_ICON[sp.id]; }
    $('stCraftT').textContent = mmss(craftLeft()); $('stCraftBar').style.setProperty('--p', stPct(sp)); }
  stSetCat(stCat, true); paintAbil(); stPopRender();
}
function strokesFrame() { if (!strokesOpen()) return; const d = strokesOf(); if (d.craft) { const id = d.craft.id; if (!craftTick()) { renderStrokes(); stToast(stReady(id)); } else { const sp = stDef(id), p = stPct(sp), t = mmss(craftLeft()); $('stCraftT').textContent = t; $('stCraftBar').style.setProperty('--p', p); for (const el of document.querySelectorAll('#mStrokes .stopt.crafting')) { el.style.setProperty('--p', p); const b = el.querySelector('.stost b'); if (b) b.textContent = t; } stPopTick(); } } }
"""

CSS = r"""
/* (v275) the Strokes page as a loadout: three slots up top (the tabs), one collection in a grid under them, a bench bar while crafting, and
   a card that rises from the foot of the screen. Each slot has its color: gold specials, blue skills, red items */
#mStrokes{--sk:#F2C14E;--sk-deep:#8A5A0E;--skrgb:242,193,78}
#mStrokes [data-cat="skill"],#stPop .stpop[data-cat="skill"]{--sk:#7CC8FF;--sk-deep:#1F5E96;--skrgb:124,200,255}
#mStrokes [data-cat="item"],#stPop .stpop[data-cat="item"]{--sk:#FF6B7D;--sk-deep:#8E1426;--skrgb:255,107,125}
#stPop .stpop,#stPop .stpop[data-cat="special"]{--sk:#F2C14E;--sk-deep:#8A5A0E;--skrgb:242,193,78}
#mStrokes .stwrap{display:flex;flex-direction:column;gap:14px;padding-top:2px}
#mStrokes .stload{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
#mStrokes .stslot{appearance:none;position:relative;display:flex;flex-direction:column;align-items:center;gap:6px;min-width:0;margin:0;padding:10px 6px 12px;border:0;border-radius:18px;background:linear-gradient(180deg,#2A2338 0%,#1C1726 100%);box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 0 0 1px rgba(255,255,255,.06),0 10px 22px rgba(0,0,0,.35);color:#F4EEE3;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:transform .16s ease,box-shadow .2s ease,background .2s ease;animation:evin .45s cubic-bezier(.2,1.2,.35,1) both}
#mStrokes .stslot:nth-child(2){animation-delay:.05s}#mStrokes .stslot:nth-child(3){animation-delay:.1s}
#mStrokes .stslot:active{transform:scale(.97)}
#mStrokes .stslot .stk{align-self:stretch;display:flex;align-items:center;justify-content:center;gap:6px;font:800 11px/1 var(--font-cond);letter-spacing:.2em;text-transform:uppercase;color:var(--sk)}
#mStrokes .stslot .stk::before{content:"";width:6px;height:6px;border-radius:2px;background:var(--sk);transform:rotate(45deg)}
#mStrokes .stslot .stnow{display:flex;flex-direction:column;align-items:center;gap:6px;min-width:0;width:100%;padding:0}
#mStrokes .stslot .stic{position:relative;display:grid;place-items:center;width:68px;height:68px;border-radius:50%;background:radial-gradient(circle at 50% 42%,rgba(var(--skrgb),.34) 0,rgba(var(--skrgb),.10) 55%,transparent 72%);box-shadow:none}
#mStrokes .stslot .stic .stimg{width:60px;height:60px;object-fit:contain;filter:drop-shadow(0 4px 6px rgba(0,0,0,.45))}
#mStrokes .stslot .stic svg{width:48px;height:48px}
#mStrokes .stslot .stname{display:block;max-width:100%;font:800 15px/1.02 var(--font-cond);font-style:italic;letter-spacing:.03em;text-transform:uppercase;color:#F4EEE3;text-align:center;text-wrap:balance}
#mStrokes .stslot.on{background:linear-gradient(180deg,rgba(var(--skrgb),.2) 0%,rgba(var(--skrgb),0) 72%),linear-gradient(180deg,#2A2338 0%,#1E1828 72%);box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 0 0 2px var(--sk),0 12px 26px rgba(0,0,0,.45),0 0 26px rgba(var(--skrgb),.28)}
#mStrokes .stslot.on::after{content:"";position:absolute;left:50%;bottom:-9px;width:14px;height:14px;margin-left:-7px;background:#1E1828;box-shadow:2px 2px 0 0 var(--sk);transform:rotate(45deg);border-radius:0 0 3px 0}
#mStrokes .stslot.fresh::before{content:"";position:absolute;right:9px;top:9px;width:9px;height:9px;border-radius:50%;background:#FF3B5C;box-shadow:0 0 0 2px #1C1726;animation:stdot 1.2s ease-in-out infinite}
#mStrokes .stslot:focus-visible{outline:3px solid #7CC8FF;outline-offset:3px}
/* the bench */
#mStrokes .stcraft{position:relative;display:grid;grid-template-columns:40px minmax(0,1fr) auto auto;grid-template-rows:auto auto;align-items:center;column-gap:10px;row-gap:9px;margin:0;padding:10px 10px 11px 10px;border-radius:16px;background:linear-gradient(90deg,rgba(var(--skrgb),.16),rgba(var(--skrgb),0) 75%),#1C1726;box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 0 0 1px rgba(var(--skrgb),.40);color:#F4EEE3}
#mStrokes .stcraft[hidden]{display:none}
#mStrokes .stcic{display:grid;place-items:center;width:40px;height:40px}#mStrokes .stcic .stimg{width:40px;height:40px;object-fit:contain}#mStrokes .stcic svg{width:32px;height:32px}
#mStrokes .stcraft .stct{display:flex;flex-direction:column;gap:3px;min-width:0;font:800 15px/1.05 var(--font-cond);font-style:italic;letter-spacing:.03em;text-transform:uppercase;color:#F4EEE3}
#mStrokes .stcraft .stct small{font:800 10px/1 var(--font-ui);font-style:normal;letter-spacing:.16em;color:var(--sk)}
#mStrokes .stctime{font:800 24px/1 var(--font-cond);font-style:italic;font-variant-numeric:tabular-nums;color:#F4EEE3}
#mStrokes .stcraft .stbar{grid-column:1/-1;height:6px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden}
#mStrokes .stcraft .stbar i{display:block;height:100%;width:var(--p,0%);border-radius:999px;background:linear-gradient(90deg,var(--sk-deep),var(--sk));box-shadow:0 0 10px rgba(var(--skrgb),.60);transition:width .5s linear}
#mStrokes .stskip,#stPop .stskip{appearance:none;margin:0;padding:9px 14px 8px;border:0;border-radius:12px;background:linear-gradient(180deg,#FFE08A,#F2C14E 55%,#E0A72A);color:#2A1A04;font:800 14px/1 var(--font-cond);font-style:italic;letter-spacing:.08em;text-transform:uppercase;box-shadow:inset 0 1px 0 rgba(255,255,255,.6),0 3px 0 #8A5A0E,0 6px 12px rgba(0,0,0,.35);cursor:pointer;-webkit-tap-highlight-color:transparent}
#mStrokes .stskip:active,#stPop .stskip:active{transform:translateY(2px);box-shadow:inset 0 1px 0 rgba(255,255,255,.6),0 1px 0 #8A5A0E}
/* the collection */
#mStrokes .stpanel{display:flex;flex-direction:column;gap:10px;min-width:0}
#mStrokes .stphd{display:flex;align-items:baseline;justify-content:space-between;gap:12px;padding:2px 2px 0}
#mStrokes .stphd h3{margin:0;font:800 19px/1 var(--font-cond);font-style:italic;letter-spacing:.04em;text-transform:uppercase;color:#F4EEE3}
#mStrokes .stphd small{font:700 12px/1.2 var(--font-ui);color:#A79FB8;text-align:right}
#mStrokes .strail{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;padding:0;overflow:visible}
#mStrokes .strail[hidden]{display:none}
#mStrokes .strail.in .stopt{animation:stin .32s cubic-bezier(.2,1.1,.35,1) both}
#mStrokes .strail.in .stopt:nth-child(2){animation-delay:.03s}#mStrokes .strail.in .stopt:nth-child(3){animation-delay:.06s}#mStrokes .strail.in .stopt:nth-child(4){animation-delay:.09s}#mStrokes .strail.in .stopt:nth-child(5){animation-delay:.12s}
@keyframes stin{from{opacity:0;transform:translateY(10px) scale(.97)}}
#mStrokes .stopt{appearance:none;position:relative;display:flex;flex-direction:column;align-items:center;gap:7px;width:auto;min-width:0;margin:0;padding:12px 6px 10px;border:0;border-radius:16px;background:linear-gradient(180deg,#262032 0%,#1B1624 100%);box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 0 0 1px rgba(255,255,255,.06),0 8px 18px rgba(0,0,0,.3);color:#F4EEE3;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:transform .15s ease}
#mStrokes .stopt:active{transform:scale(.96)}
#mStrokes .stopt .stoi{display:grid;place-items:center;width:64px;height:64px;border-radius:50%;background:radial-gradient(circle at 50% 42%,rgba(var(--skrgb),.26) 0,transparent 70%)}
#mStrokes .stopt .stoi .stimg{width:56px;height:56px;object-fit:contain;filter:drop-shadow(0 4px 5px rgba(0,0,0,.45))}
#mStrokes .stopt .stoi svg{width:44px;height:44px}
#mStrokes .stopt .stn{font:800 14px/1.02 var(--font-cond);font-style:italic;letter-spacing:.03em;text-transform:uppercase;color:#F4EEE3;text-align:center;text-wrap:balance;min-height:2.04em;display:flex;align-items:center}
#mStrokes .stopt .stost{display:flex;align-items:center;justify-content:center;gap:4px;height:20px;padding:0 8px;border-radius:999px;font:800 10px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:#A79FB8;white-space:nowrap}
#mStrokes .stopt .stost svg{width:11px;height:11px}
#mStrokes .stopt .stost.on{background:var(--sk);color:#1A1322}
#mStrokes .stopt .stost.raw{color:#E9C46A}
#mStrokes .stopt .stost.new{background:#FF3B5C;color:#fff}
#mStrokes .stopt .stost.lk{color:#8A8396}
#mStrokes .stopt .stost.cr{gap:7px;padding:0 2px;color:#F4EEE3;letter-spacing:.02em}
#mStrokes .stopt .stost.cr b{font:800 13px/1 var(--font-cond);font-style:italic;font-variant-numeric:tabular-nums}
#mStrokes .stopt .stcb{position:static;display:block;width:42px;height:5px;border-radius:999px;background:rgba(255,255,255,.1);box-shadow:none;overflow:hidden}
#mStrokes .stopt .stcb i{display:block;height:100%;width:var(--p,0%);border-radius:999px;background:linear-gradient(90deg,var(--sk-deep),var(--sk))}
#mStrokes .stopt.on{background:linear-gradient(180deg,rgba(var(--skrgb),.15) 0%,rgba(var(--skrgb),0) 80%),linear-gradient(180deg,#2A2338 0%,#1E1828 80%);box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 0 0 2px var(--sk),0 10px 22px rgba(0,0,0,.4),0 0 22px rgba(var(--skrgb),.22)}
#mStrokes .stopt.raw .stoi .stimg,#mStrokes .stopt.lock .stoi .stimg{opacity:.92;filter:grayscale(.75) brightness(.78) drop-shadow(0 4px 5px rgba(0,0,0,.45))}
#mStrokes .stopt.raw .stn,#mStrokes .stopt.lock .stn{color:#BDB5CC}
#mStrokes .stopt.crafting{box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 0 0 1.5px rgba(var(--skrgb),.55),0 8px 18px rgba(0,0,0,.3)}
#mStrokes .stopt.ready::after{content:"";position:absolute;right:9px;top:9px;width:9px;height:9px;border-radius:50%;background:#FF3B5C;box-shadow:0 0 0 2px #262032;animation:stdot 1.2s ease-in-out infinite}
#mStrokes .stopt.soon{background:rgba(20,16,28,.55);box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.1);cursor:default}
#mStrokes .stopt.soon .stoi{background:none}#mStrokes .stopt.soon .stimg{opacity:.28;filter:grayscale(1)}
#mStrokes .stopt.soon .stn{color:#6E6680}
#mStrokes .stopt:focus-visible{outline:3px solid #7CC8FF;outline-offset:3px}
#mStrokes .stopt .stb{display:none}
/* the card: a sheet risen from the foot of the screen, dark like the page, its slot's color in the glow behind the picture */
#stPop.stpopm{align-items:end;padding:0;background:rgba(10,7,16,.55)}
#stPop .stpop{width:min(100%,460px);max-height:calc(100% - 40px);border-radius:24px 24px 0 0;background:linear-gradient(180deg,#2A2338 0%,#1A1523 46%);color:#F4EEE3;box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 -12px 40px rgba(0,0,0,.5);padding-bottom:max(10px,env(safe-area-inset-bottom));animation:stsheet .34s cubic-bezier(.2,1,.3,1) both}
@keyframes stsheet{from{transform:translateY(100%)}}
#stPop .stpop::before{content:"";position:absolute;left:50%;top:8px;width:40px;height:4px;margin-left:-20px;border-radius:999px;background:rgba(255,255,255,.18)}
#stPop .stphead{position:relative;display:flex;align-items:center;gap:10px;padding:18px 14px 0 18px;border-radius:0;background:none}
#stPop .stphead b{font:800 12px/1 var(--font-cond);font-style:normal;letter-spacing:.22em;text-transform:uppercase;color:var(--sk);text-shadow:none}
#stPop .stpown{display:flex;align-items:center;gap:4px;padding:4px 8px 3px;border-radius:999px;background:rgba(255,255,255,.07);font:800 10px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:#CFC8DC}
#stPop .stpown[hidden]{display:none}#stPop .stpown svg{width:11px;height:11px;color:#46E07A}
#stPop .stpx{margin-left:auto;width:34px;height:34px;background:rgba(255,255,255,.08);color:#F4EEE3}
#stPop .stpbody{gap:10px;padding:6px 20px 16px}
#stPop .stpart{width:132px;height:132px;border-radius:50%;background:radial-gradient(circle at 50% 45%,rgba(var(--skrgb),.40) 0,rgba(var(--skrgb),.12) 50%,transparent 70%);box-shadow:none}
#stPop .stpart .stimg{width:112px;height:112px;filter:drop-shadow(0 8px 10px rgba(0,0,0,.5))}
#stPop .stpname{margin:0;font:800 34px/.95 var(--font-cond);font-style:italic;letter-spacing:.02em;color:#F7F2EA}
#stPop .stpdesc{color:#B8B0C8;font:600 14px/1.35 var(--font-ui)}
#stPop .stpdoes{gap:0;margin:4px 0 0;padding:4px 14px;background:rgba(255,255,255,.04);box-shadow:inset 0 0 0 1px rgba(255,255,255,.06);border-radius:16px}
#stPop .stpdoes li{padding:10px 0 10px 26px;font:600 14px/1.3 var(--font-ui);color:#E6E0EE;border-top:1px solid rgba(255,255,255,.06)}
#stPop .stpdoes li:first-child{border-top:0}
#stPop .stpdoes li::before{left:0;top:calc(10px + .2em);width:14px;height:14px;border-radius:50%;background:rgba(var(--skrgb),.22);box-shadow:inset 0 0 0 2px var(--sk);transform:none}
#stPop .stpdoes li::after{content:"";position:absolute;left:5px;top:calc(10px + .2em + 5px);width:4px;height:4px;border-radius:50%;background:var(--sk)}
#stPop .stpbtns{grid-template-columns:minmax(0,1fr);margin-top:4px}
#stPop .stpb{min-height:54px;border-radius:16px;font:800 20px/1 var(--font-cond);font-style:italic;letter-spacing:.06em;box-shadow:inset 0 1px 0 rgba(255,255,255,.55),0 4px 0 var(--bd,#8A5A0E),0 10px 20px rgba(0,0,0,.35)}
#stPop .stpb:active:not(:disabled){transform:translateY(3px);box-shadow:inset 0 1px 0 rgba(255,255,255,.55),0 1px 0 var(--bd,#8A5A0E)}
#stPop .stpb.equip{--bd:#8A5A0E;background:linear-gradient(180deg,#FFE08A,#F2C14E 55%,#E0A72A);color:#2A1A04}
#stPop .stpb.craft{--bd:#14753A;background:linear-gradient(180deg,#8CF2AE,#46E07A 55%,#2BBF5C);color:#06290F}
#stPop .stpb small{margin-left:6px;padding:4px 7px 3px;background:rgba(0,0,0,.14);font:800 11px/1 var(--font-ui);font-style:normal;letter-spacing:.06em}
#stPop .stpb svg{width:17px;height:17px}
#stPop .stpb:disabled{background:rgba(255,255,255,.06);color:#8A8396;box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.1)}
#stPop .stpb.on:disabled{background:rgba(70,224,122,.1);color:#BFF5D0;box-shadow:inset 0 0 0 1.5px rgba(70,224,122,.45)}
#stPop .stpb.on:disabled svg{color:#46E07A}
#stPop .stptimer{margin-top:4px;padding:12px 12px 12px 14px;border-radius:16px;background:rgba(255,255,255,.05);box-shadow:inset 0 0 0 1px rgba(var(--skrgb),.40)}
#stPop .stptimer .stpt{font:800 10px/1 var(--font-ui);letter-spacing:.16em;text-transform:uppercase;color:var(--sk)}
#stPop .stptimer .stpt b{margin-top:5px;font:800 28px/1 var(--font-cond);font-style:italic;color:#F4EEE3}
#stPop .stptimer .stbar{height:6px;background:rgba(255,255,255,.08)}
#stPop .stptimer .stbar i{background:linear-gradient(90deg,var(--sk-deep),var(--sk))}
#stPop .stpnote{color:#8A8396}
/* landscape: the slots down the left, the grid on the right; the card centred */
@media (min-aspect-ratio:1/1) and (max-height:600px){
  #mStrokes .stwrap{display:grid;grid-template-columns:minmax(220px,30%) minmax(0,1fr);grid-template-rows:auto minmax(0,1fr);align-content:start;column-gap:18px;row-gap:12px}
  #mStrokes .stload{grid-column:1;grid-row:1/3;grid-template-columns:minmax(0,1fr);align-content:start;gap:8px}
  #mStrokes .stslot{flex-direction:row;align-items:center;gap:10px;padding:8px 12px 8px 8px;text-align:left}
  #mStrokes .stslot .stk{order:2;position:absolute;left:78px;top:14px;justify-content:flex-start}
  #mStrokes .stslot .stnow{flex-direction:row;gap:10px;align-items:center}
  #mStrokes .stslot .stic{flex:none;width:58px;height:58px}#mStrokes .stslot .stic .stimg{width:52px;height:52px}
  #mStrokes .stslot .stname{padding-top:16px;text-align:left;font-size:17px}
  #mStrokes .stslot.on::after{left:auto;right:-9px;top:50%;bottom:auto;margin:-7px 0 0;box-shadow:2px -2px 0 0 var(--sk);border-radius:0 3px 0 0}
  #mStrokes .stcraft{grid-column:2;grid-row:1}
  #mStrokes .stpanel{grid-column:2;grid-row:2}
  #mStrokes .stcraft:not([hidden])+.stpanel{grid-row:2}
  #mStrokes .stcraft[hidden]+.stpanel{grid-row:1/3}
  #mStrokes .strail{grid-template-columns:repeat(auto-fill,minmax(104px,1fr))}
  #mStrokes .stopt{padding:10px 6px 8px;gap:5px}#mStrokes .stopt .stoi{width:56px;height:56px}#mStrokes .stopt .stoi .stimg{width:50px;height:50px}
  #stPop.stpopm{align-items:center;padding:16px}
  #stPop .stpop{width:min(100%,600px);border-radius:24px;padding-bottom:0;animation:cardlift .34s cubic-bezier(.2,1.25,.35,1) both}
  #stPop .stpop::before{display:none}
  #stPop .stphead{padding:14px 12px 0 18px}
  #stPop .stpbody{grid-template-columns:128px minmax(0,1fr);grid-template-areas:"art name" "art desc" "art does" "art timer" "art btns" "art note";align-items:start;row-gap:8px;column-gap:18px;padding:4px 18px 16px}
  #stPop .stpart{grid-area:art;align-self:center;width:124px;height:124px}#stPop .stpart .stimg{width:104px;height:104px}
  #stPop .stpname{font-size:30px;align-self:end}#stPop .stpdesc{margin:0}
  #stPop .stpdoes{margin:0;padding:0 12px;grid-template-columns:minmax(0,1fr);column-gap:0}
  #stPop .stpdoes li{padding:6px 0 6px 24px;font-size:13px}#stPop .stpdoes li::before{top:calc(6px + .2em)}#stPop .stpdoes li::after{top:calc(6px + .2em + 5px)}
  #stPop .stptimer{padding:9px 10px 9px 12px}#stPop .stptimer .stpt b{font-size:24px}
  #stPop .stpb{min-height:46px;font-size:18px}
}
@media (max-aspect-ratio:1/1),(min-height:601px){#mStrokes .strail .stopt.soon:nth-child(3n+1){display:none}} /* (portrait: More soon only where it doesn't start a row of its own) */
@media (max-width:359px){#mStrokes .stcraft{column-gap:8px;padding:9px 8px 10px}#mStrokes .stcraft .stct small{letter-spacing:.08em}#mStrokes .stctime{font-size:20px}#mStrokes .stskip{padding:8px 11px 7px;font-size:13px}#mStrokes .stslot .stic,#mStrokes .stopt .stoi{width:54px;height:54px}#mStrokes .stslot .stic .stimg,#mStrokes .stopt .stoi .stimg{width:48px;height:48px}#mStrokes .stslot .stname,#mStrokes .stopt .stn{font-size:13px}#mStrokes .stload,#mStrokes .strail{gap:8px}}
@media (min-aspect-ratio:1/1){body.stpage .tut[data-pos="low"][data-lowc]{max-width:min(46vw,384px)}}
@media (prefers-reduced-motion:reduce){#mStrokes .stslot,#mStrokes .strail.in .stopt,#stPop .stpop,#mStrokes .stslot.fresh::before{animation:none}}
"""

def apply(s):
    # the markup: the loadout, the bench, the grid
    s = region(s, '      <div class="stwrap" id="stWrap"><p class="stsub">', '    </div>\n    <div class="mevents" id="mEvents" hidden>', MARKUP)
    s = region(s, '  <div class="modal stpopm" id="stPop" hidden>', '  <div class="modal" id="commModal" hidden>', POP)
    # the style, after the old (its rules are scoped to the page and the card, so they win)
    i = s.index('</style>', s.index('.stpnote[hidden]{display:none}')); s = s[:i] + CSS + s[i:]
    # the tiles, the card, the page
    s = region(s, '// (v257) the tiles: the picture, the name, and Equipped on the one you have on', "// (v257) a stroke's card, over the page", JS_TILE)
    s = region(s, 'function stPopRender() {', 'function openStPop(id) {', JS_POP)
    s = region(s, 'function renderStrokes() {', 'function openStrokes() {', JS_RENDER)
    s = rep(s, "  stSkillSel = null; menuPage = 'strokes';", "  stSkillSel = null; stCat = 'special'; menuPage = 'strokes';")
    s = rep(s, "  for (const c of $('mStrokes').querySelectorAll('.stslot')) { c.style.animation = 'none'; void c.offsetWidth; c.style.animation = ''; }",
            "  for (const c of $('mStrokes').querySelectorAll('.stslot')) { c.style.animation = 'none'; void c.offsetWidth; c.style.animation = ''; } { const r = $('stSpecialRail'); r.classList.remove('in'); void r.offsetWidth; r.classList.add('in'); }")
    # (a flag on the page for Ol' Bloop's plate: narrower on a wide screen here, so it can sit to the left of the grid it points into)
    s = rep(s, "document.body.classList.add('evon'); closeSide(true); renderStrokes();", "document.body.classList.add('evon', 'stpage'); closeSide(true); renderStrokes();")
    s = rep(s, "$('mStrokes').hidden = true; document.body.classList.remove('evon');", "$('mStrokes').hidden = true; document.body.classList.remove('evon', 'stpage');")
    # the slots are the tabs (arrows move along them)
    s = rep(s, "$('stSkip').addEventListener('click', () => { AU.init(); craftSkip(); });",
            "$('stSkip').addEventListener('click', () => { AU.init(); craftSkip(); });\n"
            "for (const k of ['special', 'skill', 'item']) $(ST_CATS[k].slot).addEventListener('click', () => { AU.init(); stSetCat(k); });\n"
            "$('mStrokes').querySelector('.stload').addEventListener('keydown', e => { const ks = ['special', 'skill', 'item'], i = ks.indexOf(stCat), dl = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0; if (!dl) return; e.preventDefault(); const k = ks[(i + dl + 3) % 3]; stSetCat(k); $(ST_CATS[k].slot).focus(); });")
    # a stroke crafted elsewhere in the page's life shows on its own tab: the toast's tab comes up with it
    # (Ol' Bloop's lesson: the Special tab stays up while he walks you through the Giant)
    s = rep(s, "  const d = strokesOf(), giant = () => $('stSpecialRail').querySelector('.stopt[data-st=\"giant\"]');",
            "  if (stCat !== 'special') stSetCat('special', true); // (v275: the Giant is on the Special tab)\n"
            "  const d = strokesOf(), giant = () => $('stSpecialRail').querySelector('.stopt[data-st=\"giant\"]');")
    s = rep(s, "'Giant it is! Grab the orb in a match and go big. Skills are below: Swim faster is on, and you can craft the others'",
            "'Giant it is! Grab the orb in a match and go big. Skills and items have their own tabs up top'")
    return s
