#!/usr/bin/env python3
"""Drops: the paint you earn. Found items go on sale in the locker and are bought before they are worn. On top of ui8_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui8_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

DROP = '<svg class="dropi" viewBox="0 0 16 20" aria-hidden="true"><path d="M8 1.5C8 1.5 2 9 2 12.5a6 6 0 0 0 12 0C14 9 8 1.5 8 1.5z"/></svg>'
CSS = '''
/* ===== drops: the paint you earn, and what a found item costs ===== */
.dropi{width:.8em;height:1em;fill:var(--ink);vertical-align:-.12em;filter:drop-shadow(1px 1px 0 rgba(23,19,32,.35))}
.plate.stat.drops b{display:inline-flex;align-items:center;gap:3px}
.lkbal{display:inline-flex;align-items:center;gap:5px;margin-left:auto;margin-right:8px;padding:6px 10px 6px 8px;background:#fff url(art/m_paperbg.webp) center/300px;border-radius:4px;box-shadow:3px 4px 0 rgba(23,19,32,.2);font:900 15px/1 var(--font-head);color:var(--black);white-space:nowrap}
.lkbal .dropi{width:13px;height:16px}
.lkbal.bump{animation:tilepop .42s cubic-bezier(.2,1.6,.4,1)}
.dropgain{display:grid;justify-items:end;gap:2px;font:900 15px/1 var(--font-head);color:var(--black);white-space:nowrap}
.dropgain small{font:800 9px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.reprow{grid-template-columns:auto minmax(0,1fr) auto auto}
.ltile.sale{border:2px solid var(--ink);background:#fff;box-shadow:2px 3px 0 rgba(23,19,32,.14)}
.ltile.sale svg{filter:none;opacity:1}
.ltile .ltag{position:absolute;left:50%;top:-9px;transform:translateX(-50%) rotate(-3deg);display:inline-flex;align-items:center;gap:2px;padding:3px 7px;background:var(--ink);color:#fff;border-radius:3px;font:900 11px/1 var(--font-head);box-shadow:2px 2px 0 rgba(23,19,32,.35);white-space:nowrap}
.ltile .ltag .dropi{fill:#fff;width:9px;height:11px;filter:none}
.ltile.sale .ltn{color:var(--black)}
.ltile.broke .ltag{background:#8E8698}
.niprice{display:inline-flex;align-items:center;gap:4px;margin-left:8px;padding:2px 8px;border-radius:3px;background:var(--ink);color:#fff;font:900 13px/1 var(--font-head)}
.niprice .dropi{fill:#fff;width:9px;height:12px;filter:none}
@media (max-height:520px) and (min-aspect-ratio:1/1){.lkbal{padding:4px 8px 4px 6px;font-size:13px}}
/* the orientation preview keeps to its box (a percentage height inside an auto grid row resolved to nothing) */
.oart{display:flex;justify-content:center;align-items:center}
.ocard[data-o="port"] .oart img{height:100%;width:auto;max-height:100%}
.ocard[data-o="land"] .oart img{width:100%;height:auto;max-height:100%;object-fit:cover}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]

# markup: the lobby plate, the locker balance, the results gain, the price on the find
rep('<b id="statBest">0%</b><span>Best</span></div>', '<b id="statBest">0%</b><span>Best</span></div>\n        <div class="plate stat drops" title="Drops"><b id="statDrops">' + DROP + '0</b><span>Drops</span></div>')
rep('<div class="lktop"><h2 class="ctitle" id="lookTitle">Locker</h2><button class="lnbtn"', '<div class="lktop"><h2 class="ctitle" id="lookTitle">Locker</h2><span class="lkbal" id="lkBal" aria-label="Drops">' + DROP + '<b id="lkBalN">0</b></span><button class="lnbtn"')
rep('<b class="xpgain" id="xpGain">+0<small>XP</small></b></div>', '<b class="xpgain" id="xpGain">+0<small>XP</small></b><b class="dropgain" id="dropGain" hidden>+0<small>drops</small></b></div>')

# the store: a balance and a bought list; what was already found before drops existed counts as bought
rep("const OWNED = new Set(Array.isArray(store.owned) ? store.owned.filter(id => WEAR.some(w => w.id === id)) : []);",
    """const OWNED = new Set(Array.isArray(store.owned) ? store.owned.filter(id => WEAR.some(w => w.id === id)) : []);
// drops: paint earned at the end of a match. A found item goes on sale in the locker; it is worn once it is bought
const PRICE = w => w.season ? 150 : w.slot === 'head' ? 120 : 80;
const BOUGHT = new Set(Array.isArray(store.bought) ? store.bought.filter(id => OWNED.has(id)) : [...OWNED]);
if (!Array.isArray(store.bought)) { store.bought = [...BOUGHT]; }
if (!(store.drops >= 0)) store.drops = 0;
const bought = id => BOUGHT.has(id);
function buyItem(id) { const w = WEAR.find(x => x.id === id); if (!w || !OWNED.has(id) || BOUGHT.has(id) || store.drops < PRICE(w)) return false; store.drops -= PRICE(w); BOUGHT.add(id); store.bought = [...BOUGHT]; save(); return true; }
function showDrops() { const n = store.drops || 0; if ($('statDrops')) $('statDrops').lastChild.nodeValue = String(n); if ($('lkBalN')) $('lkBalN').textContent = String(n); }""")
rep("const ok = (v, slot) => WEAR.some(w => w.id === v && w.slot === slot) && OWNED.has(v) ? v : null;", "const ok = (v, slot) => WEAR.some(w => w.id === v && w.slot === slot) && BOUGHT.has(v) ? v : null;")
# the code unlocks and buys everything
rep("if (v === '1234') { for (const w of WEAR) OWNED.add(w.id); store.owned = [...OWNED]; save();", "if (v === '1234') { for (const w of WEAR) { OWNED.add(w.id); BOUGHT.add(w.id); } store.owned = [...OWNED]; store.bought = [...BOUGHT]; save();")

# the locker: found items carry a price tag; worn ones are the bought ones
rep("""  rail.innerHTML = WEAR.filter(w => w.cat === lookCat).map(w => { const own = owns(w.id), fr = own && fresh.has(w.id);
    return '<button class="ltile' + (own ? '' : ' locked') + (fr ? ' fresh' : '') + '" type="button" data-w="' + w.id + '"' + (own ? ' aria-pressed="' + (myLook[w.slot] === w.id) + '"' : ' aria-disabled="true"') + ' aria-label="' + w.name + (own ? (fr ? ', new' : '') : ', locked') + '"><svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w.id] + '</svg><span class="ltn">' + w.name + '</span>' + (own ? '' : LOCK_ICON) + '</button>'; }).join('');""",
    """  rail.innerHTML = WEAR.filter(w => w.cat === lookCat).map(w => { const found = owns(w.id), own = found && bought(w.id), sale = found && !own, fr = own && fresh.has(w.id), broke = sale && (store.drops || 0) < PRICE(w);
    return '<button class="ltile' + (own ? '' : sale ? ' sale' : ' locked') + (broke ? ' broke' : '') + (fr ? ' fresh' : '') + '" type="button" data-w="' + w.id + '"' + (own ? ' aria-pressed="' + (myLook[w.slot] === w.id) + '"' : sale ? '' : ' aria-disabled="true"') + ' aria-label="' + w.name + (own ? (fr ? ', new' : '') : sale ? ', ' + PRICE(w) + ' drops' : ', locked') + '">' + (sale ? '<span class="ltag">' + DROP_SVG + PRICE(w) + '</span>' : '') + '<svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w.id] + '</svg><span class="ltn">' + w.name + '</span>' + (found ? '' : LOCK_ICON) + '</button>'; }).join('');
  showDrops();""")
rep("const LOCK_ICON = '<span class=\"lk\" aria-hidden=\"true\">", "const DROP_SVG = '" + DROP + "';\nconst LOCK_ICON = '<span class=\"lk\" aria-hidden=\"true\">")
rep("""  if (!owns(w.id)) { AU.nope(); kick(b, 'nope'); note('Find the ' + w.name.toLowerCase() + ' on ' + WEAR_WHERE[w.stage] + '.'); return; }""",
    """  if (!owns(w.id)) { AU.nope(); kick(b, 'nope'); note('Find the ' + w.name.toLowerCase() + ' on ' + WEAR_WHERE[w.stage] + '.'); return; }
  if (!bought(w.id)) { if (!buyItem(w.id)) { AU.nope(); kick(b, 'nope'); note('Needs ' + (PRICE(w) - (store.drops || 0)) + ' more drops. Matches pay in drops.', true); return; } AU.power(); note('Bought the ' + w.name.toLowerCase() + '!'); kick($('lkBal'), 'bump'); }""")

# the find: it goes to the locker with its price, not straight onto the blob
rep("$('niWhere').textContent = 'Found on ' + WEAR_WHERE[w.stage].replace(/^the /, 'the ');", "$('niWhere').innerHTML = 'Found on ' + escAttr(WEAR_WHERE[w.stage].replace(/^the /, 'the ')) + '<span class=\"niprice\">' + DROP_SVG + PRICE(w) + '</span>'; $('niTry').textContent = bought(w.id) ? 'Try it on' : 'See it in the locker';")
rep("hideNewItem(); if (w) { if (w.cat !== 'face') for (const o of WEAR) if (o.cat === w.cat && o.slot !== w.slot) myLook[o.slot] = null; myLook[w.slot] = w.id; lookCat = w.cat; store.fresh = (store.fresh || []).filter(x => x !== id); saveLook(); }",
    "hideNewItem(); if (w) { lookCat = w.cat; if (bought(w.id)) { if (w.cat !== 'face') for (const o of WEAR) if (o.cat === w.cat && o.slot !== w.slot) myLook[o.slot] = null; myLook[w.slot] = w.id; store.fresh = (store.fresh || []).filter(x => x !== id); saveLook(); } }")

# the pay: a match ends in drops too, more for a win
rep("  const fin = commProgress(endInfo); gain += fin.length * COMM_XP; endInfo.xp0 = store.xp || 0; store.xp = endInfo.xp0 + gain; endInfo.xp = gain; endInfo.comms = fin;",
    "  const fin = commProgress(endInfo); gain += fin.length * COMM_XP; endInfo.xp0 = store.xp || 0; store.xp = endInfo.xp0 + gain; endInfo.xp = gain; endInfo.comms = fin;\n  const drops = Math.round(8 + ry * 0.35 + (win > 0 ? 30 : win === 0 && mode !== 'solo' ? 12 : 0) + (newBest ? 10 : 0) + (mode === 'trio' ? 6 : 0)) + fin.length * 20; store.drops = (store.drops || 0) + drops; endInfo.drops = drops;")
rep("  $('repRowName').textContent = r0.name; $('xpGain').innerHTML = '+' + info.xp + '<small>XP</small>'; xpFrame(m, (XP_FRAMES - 1) * r0.x / r0.need);",
    "  $('repRowName').textContent = r0.name; $('xpGain').innerHTML = '+' + info.xp + '<small>XP</small>'; xpFrame(m, (XP_FRAMES - 1) * r0.x / r0.need);\n  const dg = $('dropGain'); dg.hidden = !(info.drops > 0); if (info.drops > 0) dg.innerHTML = '+' + info.drops + DROP_SVG + '<small>drops</small>';")
rep("  let wins = 0; for (const k in (store.wins || {})) wins += store.wins[k] || 0; $('statWins').textContent = wins;", "  let wins = 0; for (const k in (store.wins || {})) wins += store.wins[k] || 0; $('statWins').textContent = wins; showDrops();")
# the sling yelp: one fling in four, not every one
rep("AU.fling(c); buzz(12); if (c > 0.62) AU.vox('whee'); else if (c > 0.3 && Math.random() < 0.5) AU.vox('hup'); }", "AU.fling(c); buzz(12); if (Math.random() < 0.27) { if (c > 0.62) AU.vox('whee'); else if (c > 0.3) AU.vox('hup'); } }")
rep('<p class="ver">Version 78</p>', '<p class="ver">Version 79</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
