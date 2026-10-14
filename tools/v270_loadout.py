"""v270: every match starts with an item in hand, and the announcer's "Are you ready? Let's roll" is gone from the versus card.

- The starting item: the Roller unless you pick another under Abilities (the Strokes page has a third row, Item: the Roller, the Paint
  Trap or the Turret, all yours from the start, each with its own card and Equip like the strokes). Each CPU starts with one of the
  three at random and uses it after a few seconds (none in the lessons). Items still turn up on the canvas as before.
- The lesson: you hold the Roller from the start but its button stays hidden until its step. Then the button comes up, raised above
  the slow-motion shade that used to cover it, and the tip points at it (no roller is dropped by you to pick up any more). Once it's
  rolling, the rival comes round onto the line in front of you and walks down it at you; as he comes in range the game slows, a finger
  shows the swipe up, and the roll is aimed at him. It goes round again until you flatten him (the roller holds out till you do).
- Icons for the three items painted with Ludo.ai in the strokes' own style (tools/assets/item_*_256.webp)."""
import base64, os
A = os.path.dirname(os.path.abspath(__file__)) + '/assets/'
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def cut(s, a, b):
    i = s.index(a); j = s.index(b, i); assert s.count(a) == 1; return s[:i], s[i:j], s[j:]

ITEMS_JS = """
// (v270) the item you start every match holding: the Roller (till you pick another), the Paint Trap or the Turret. All three are yours
// from the start: no crafting, just Equip
const ST_ITEMS = [
  { id: 'roller', name: 'Roller', desc: 'Roll out wide stripes and flatten rivals.', does: ['Tap it: your paint refills and you roll out wide stripes for 9 seconds', 'Swipe up to roll right over a rival and knock them out', 'Use it when you like: it waits in your hand'] },
  { id: 'trap', name: 'Paint Trap', desc: 'A sticky paint mine for the next rival over it.', does: ['Tap it to drop a sticky mine where you are', 'The next rival over it gets splatted and knocked out', 'A rival who rolls over it pops it harmlessly'] },
  { id: 'turret', name: 'Turret', desc: 'Plant it and it fires paint at rivals.', does: ['Tap it to plant a turret on the ground', 'It fires paint at the nearest rival for 7 seconds', 'Each hit drains their paint: empty, and they\\u2019re out'] }];
const stIsItem = id => ST_ITEMS.some(x => x.id === id), cpuItem = () => { const r = Math.random(); return r < 0.4 ? 'roller' : r < 0.7 ? 'turret' : 'trap'; };
"""

ITEM_STEP = """  // (v270) you've held the Roller since the start; now its button comes up (above the slow-motion shade) and the tip points at it
  { id: 'item', max: 50, enter() { tutHide(); tut.slowK = 1; tut.sub = ''; tut.wait = 0.7; if (!P.held && !(P.power && P.power.type === 'roller')) P.held = 'roller'; tut.hideItem = false; $('itemBtn').classList.add('tutup'); }, /* (a beat for the button to pop up, then its tip) */
    exit() { $('itemBtn').classList.remove('tutup'); },
    tick(dt) { if (P.st === 'play' && !P.held && !(P.power && P.power.type === 'roller')) P.held = 'roller'; /* (whatever became of it, it's back in your hand) */
      if (tut.wait > 0) { tut.wait -= dt; return false; }
      if (tut.sub !== 'use' && P.held === 'roller' && P.st === 'play') { tut.sub = 'use'; tut.slowK = 0.35; tutShow(say('This is your *ROLLER*. *TAP* it!', 'This is your *ROLLER*. Press *F*!'), 'itemBtn', 'use', true); }
      return !!(P.power && P.power.type === 'roller'); } },
  // (v270) rolling: the rival comes round onto the line in front of you and walks down it at you. As he comes in range it slows right
  // down, a finger shows the swipe up and the roll is aimed at him. Round again if you miss (the roller holds out) till he's flattened
  { id: 'rollover', max: 45, enter() { tutHide(); tut.slowK = 1; tut.sub = ''; tut.rAim = true; tut.kos0 = P.kos; tut.drive = H; tut.driveMode = 'line'; if (H.ai) { H.ai.plan = null; H.ai.path = null; } tutRivalIn(7, true); },
    exit() { tut.rAim = false; if (tut.driveMode === 'line') { tut.drive = null; tut.driveMode = null; } TUT_AI.speed = 0.8; tut.items = true; itemSpawn.t = Math.max(itemSpawn.t, 10); },
    tick(dt) { if (P.kos > tut.kos0) return true;
      const have = !!(P.power && P.power.type === 'roller'); if (have) P.power.t = Math.max(P.power.t, 2.5); else if (P.st === 'play' && !P.held) P.held = 'roller'; /* (out of it somehow: it's handed back) */
      if (!have && P.held === 'roller' && P.st === 'play') { if (tut.sub !== 'again') { tut.sub = 'again'; tut.slowK = 0.35; $('itemBtn').classList.add('tutup'); tutShow(say('*TAP* your *ROLLER*!', 'Press *F* for your *ROLLER*!'), 'itemBtn', 'use2', true); } return false; }
      if (tut.sub === 'again') $('itemBtn').classList.remove('tutup');
      const fx = Math.sin(P.yaw), fz = Math.cos(P.yaw), rx = H.x - P.x, rz = H.z - P.z, ahead = rx * fx + rz * fz, side = Math.abs(rx * fz - rz * fx), d = Math.hypot(rx, rz);
      if (H.st === 'play' && P.st === 'play' && (ahead < 0 || d > 14)) tutRivalIn(7, true); /* (behind you or far off: he's brought round in front again) */
      const inLine = H.st === 'play' && P.st === 'play' && !P.air && P.rollT <= 0 && ahead > 1.5 && ahead < 5.5 && side < 1.2 + ahead * 0.15 && lineClear(P, H.x, H.z, P.y) && tutRunClear(P.yaw, ahead + 3.5); /* (and room to roll on past him: no drop, no wall) */
      const sub = inLine ? 'now' : P.rollT > 0 ? tut.sub : 'wait';
      if (sub !== tut.sub) { tut.sub = sub;
        if (sub === 'now') { tut.slowK = 0.25; if (P.rollCD > 0) P.rollCD = 0; tutShow(say('*NOW!* Swipe up to roll over him!', '*NOW!* Press *SHIFT* to roll over him!'), null, 'rroll', true, true); }
        else { tut.slowK = 1; tutShow(say('Roll right over the rival to knock him out!', 'Roll right over the rival to knock him out!'), null, 'rollwait', false, true); } }
      return false; } },
"""

LINE_JS = """// (v270) level ground (no drop, no wall) every metre from you out to dist along yaw: room for a roll
function tutRunClear(yaw, dist) { const fx = Math.sin(yaw), fz = Math.cos(yaw); for (let s = 1; s <= dist; s++) { const x = P.x + fx * s, z = P.z + fz * s; if (Math.abs(x) > ARENA - 1 || Math.abs(z) > ARENA - 1) return false; const y = surfaceUnder(x, z, P.y + 0.3); if (!(Math.abs(y - P.y) < 0.35) || blockedAt(x, z, y)) return false; } return true; }
// (v270) the roll-over lesson's rival: round onto the line in front of you (as tutAhead), then down it towards you, slowly, so that a
// swipe up meets him; about 3 m out he stops and waits for it
function tutLine(D) {
  const fx = Math.sin(P.yaw), fz = Math.cos(P.yaw), rx = D.x - P.x, rz = D.z - P.z, ahead = rx * fx + rz * fz, side = rx * fz - rz * fx;
  if (ahead > 1.3 && Math.abs(side) < 1 + ahead * 0.2) { TUT_AI.speed = ahead > 4.5 ? 0.45 : ahead > 3 ? 0.15 : 0.02; if (D.charging) cancelCharge(D); D.steer = -clamp(wrapA(Math.atan2(-rx, -rz) - D.yaw) * 3, -1, 1); return; } // (about 3 m out he stands and waits)
  return tutAhead(D);
}
"""

def apply(s):
    # ---- the versus card: no "ready" line (Are you ready? Let's roll), on the card or after the canvas vote; "go" still preloads
    s = rep(s, "el.hidden = false; AU.whoosh(); for (const k of ['ready', 'go']) AU.say(k, 0); buzz([15, 30, 15]);",
            "el.hidden = false; AU.whoosh(); AU.say('go', 0); buzz([15, 30, 15]); // (v270: no \"Are you ready? Let's roll\" here or after the vote)")
    s = rep(s, "setTimeout(() => { if (!(id !== runId && state !== 'menu')) AU.say('ready'); }, 900); ", "")
    s = rep(s, "at(260, () => { $('vtally').classList.add('on'); AU.say('ready'); });", "at(260, () => { $('vtally').classList.add('on'); });")

    # ---- Abilities (the Strokes page): a third row, Item
    s = rep(s, '<div class="strail" id="stSkillRail" role="group" aria-label="Skills"></div></section>',
            '<div class="strail" id="stSkillRail" role="group" aria-label="Skills"></div></section>\n'
            '        <section class="stslot" id="stItem" aria-labelledby="stItemH"><div class="sthead"><b id="stItemH">Item</b><small>You start every match holding it</small></div><div class="stnow" id="stItemNow"></div><div class="strail" id="stItemRail" role="group" aria-label="Items"></div></section>')
    s = rep(s, ".stslot:nth-child(3){animation-delay:.07s}", ".stslot:nth-child(3){animation-delay:.07s}.stslot:nth-child(4){animation-delay:.14s}")
    s = rep(s, "const ST_STARTERS = ['rocket', 'swim']; // (yours from the start: everything else is crafted)\n",
            "const ST_STARTERS = ['rocket', 'swim']; // (yours from the start: everything else is crafted)\n" + ITEMS_JS.lstrip('\n'))
    img = {k: 'data:image/webp;base64,' + base64.b64encode(open(A + 'item_' + k + '_256.webp', 'rb').read()).decode() for k in ['roller', 'trap', 'turret']}
    s = rep(s, "for (const k of ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets']) STROKE_ICON[k] = stImg(k);\n",
            "for (const k of ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets']) STROKE_ICON[k] = stImg(k);\n"
            "// (v270) the starting items' pictures, painted the same way\n"
            "Object.assign(ST_IMG, { " + ", ".join(f"{k}: '{v}'" for k, v in img.items()) + " }); for (const k of ['roller', 'trap', 'turret']) STROKE_ICON[k] = stImg(k);\n")
    s = rep(s, "const stDef = id => SPECIALS.find(x => x.id === id) || SKILLS.find(x => x.id === id),",
            "const stDef = id => SPECIALS.find(x => x.id === id) || SKILLS.find(x => x.id === id) || ST_ITEMS.find(x => x.id === id),")
    s = rep(s, "  if (!SKILLS.some(x => x.id === d.skill) || !d.own.includes(d.skill)) d.skill = 'swim'; return d; }",
            "  if (!SKILLS.some(x => x.id === d.skill) || !d.own.includes(d.skill)) d.skill = 'swim'; if (!stIsItem(d.item)) d.item = 'roller'; return d; }")
    s = rep(s, "const strokeOwned = id => strokesOf().own.includes(id),", "const strokeOwned = id => stIsItem(id) || strokesOf().own.includes(id),")
    s = rep(s, "strokeSkill = () => strokesOf().skill;", "strokeSkill = () => strokesOf().skill, strokeItem = () => strokesOf().item;")
    s = rep(s, "const d = strokesOf(), own = d.own.includes(o.id), on = own && (skill ? strokeSkill() : strokeSpecial()) === o.id,",
            "const d = strokesOf(), own = skill === 'item' || d.own.includes(o.id), on = own && (skill === 'item' ? strokeItem() : skill ? strokeSkill() : strokeSpecial()) === o.id,")
    s = rep(s, ": own ? 'crafted' : lock ?", ": own ? (skill === 'item' ? 'yours' : 'crafted') : lock ?")
    s = rep(s, "'\" type=\"button\" data-' + (skill ? 'sk' : 'st') + '=\"'", "'\" type=\"button\" data-' + (skill === 'item' ? 'it' : skill ? 'sk' : 'st') + '=\"'")
    s = rep(s, "const d = strokesOf(), skill = stIsSkill(id), own = d.own.includes(id), on = own && (skill ? strokeSkill() : strokeSpecial()) === id,",
            "const d = strokesOf(), skill = stIsSkill(id), item = stIsItem(id), own = item || d.own.includes(id), on = own && (item ? strokeItem() : skill ? strokeSkill() : strokeSpecial()) === id,")
    s = rep(s, "card.classList.toggle('skill', skill);", "card.classList.toggle('skill', skill || item);")
    s = rep(s, "$('stPopKind').textContent = skill ? 'Skill' : 'Special stroke';", "$('stPopKind').textContent = item ? 'Item' : skill ? 'Skill' : 'Special stroke';")
    s = rep(s, "cb.innerHTML = own ? ST_CHECK + (ST_STARTERS.includes(id) ? 'Yours' : 'Crafted')", "cb.innerHTML = own ? ST_CHECK + (item || ST_STARTERS.includes(id) ? 'Yours' : 'Crafted')")
    s = rep(s, "const t = document.querySelector('.stopt[data-st=\"' + id + '\"], .stopt[data-sk=\"' + id + '\"]');",
            "const t = document.querySelector('.stopt[data-st=\"' + id + '\"], .stopt[data-sk=\"' + id + '\"], .stopt[data-it=\"' + id + '\"]');")
    s = rep(s, "function renderStrokes() {",
            "function equipItem(id) { const d = strokesOf(); if (!stIsItem(id) || d.item === id) return; d.item = id; save(); AU.ready && AU.ready(); buzz(8); renderStrokes(); stToast(spName(id) + ' is your starting item'); }\nfunction renderStrokes() {")
    s = rep(s, "now(strokeSpecial(), SPECIALS, $('stSpecialNow')); now(strokeSkill(), SKILLS, $('stSkillNow'));",
            "now(strokeSpecial(), SPECIALS, $('stSpecialNow')); now(strokeSkill(), SKILLS, $('stSkillNow')); now(strokeItem(), ST_ITEMS, $('stItemNow'));")
    s = rep(s, "$('stSkillRail').innerHTML = SKILLS.map(o => stTile(o, true)).join('') + soon;",
            "$('stSkillRail').innerHTML = SKILLS.map(o => stTile(o, true)).join('') + soon; $('stItemRail').innerHTML = ST_ITEMS.map(o => stTile(o, 'item')).join('') + soon;")
    a = "$('stSkillRail').addEventListener('click', e => { const b = e.target.closest('.stopt[data-sk]'); if (!b) return; AU.init(); openStPop(b.dataset.sk); });"
    s = rep(s, a, a + "\n$('stItemRail').addEventListener('click', e => { const b = e.target.closest('.stopt[data-it]'); if (!b) return; AU.init(); openStPop(b.dataset.it); });")
    s = rep(s, "if (stIsSkill(id)) equipSkill(id); else equipSpecial(id);", "if (stIsItem(id)) equipItem(id); else if (stIsSkill(id)) equipSkill(id); else equipSpecial(id);")

    s = rep(s, "You\u2019ve unlocked Strokes: your special move, and a skill.", "You\u2019ve unlocked Strokes: your special move, a skill and the item you start with.")
    # ---- the match: everyone starts holding an item
    s = rep(s, "  for (const D of ACTIVE) { if (D.st === 'out') continue;\n    if (D.introAct)",
            "  // (v270) everyone starts holding an item: yours is the one picked under Abilities (the lesson's always the Roller, its button kept back\n"
            "  // till its step); each CPU one of the three at random (none in the lessons), kept a few seconds before it's used\n"
            "  startItems();\n"
            "  for (const D of ACTIVE) { if (D.st === 'out') continue;\n    if (D.introAct)")
    s = rep(s, "function goTime() {", "function startItems() { for (const D of ACTIVE) { if (D.st === 'out') continue; D.held2 = null; D.heldT = 0; D.held = D === P ? (tut ? 'roller' : strokeItem()) : (tut || tut2 || tut3) ? null : cpuItem(); if (D !== P) D.heldT = -(2 + Math.random() * 6); } }\nfunction goTime() {")
    s = rep(s, "  if (window.__skipIntro) { state = 'play';", "  if (window.__skipIntro) { startItems(); state = 'play';")
    s = rep(s, "  hint('steer', say('Drag to steer', 'A D or arrows to steer'), 3);\n}\nfunction showMenu() {",
            "  hint('steer', say('Drag to steer', 'A D or arrows to steer'), 3);\n"
            "  if (!tut && P.held) setTimeout(() => { if (state === 'play' && P.held && P.st === 'play') hint('startitem', say('You start with your ' + PU[P.held].name.toLowerCase() + '. Tap its button to use it', 'You start with your ' + PU[P.held].name.toLowerCase() + '. Press F to use it'), 3.5); }, 4200); // (v270: once)\n"
            "}\nfunction showMenu() {")

    # ---- the lesson: the item button kept back till its step, and above the slow-motion shade when it comes
    s = rep(s, "noTurret: true, pips: new Set(), bonus: 0, praiseN: 0 };", "noTurret: true, hideItem: true, pips: new Set(), bonus: 0, praiseN: 0 };")
    s = rep(s, "{ const ib = $('itemBtn'), held = state === 'play' && P.st === 'play' ? P.held : null;",
            "{ const ib = $('itemBtn'), held = state === 'play' && P.st === 'play' && !(tut && tut.hideItem) ? P.held : null;")
    s = rep(s, "function useHeld(D) {\n  if (!D.held || D.st !== 'play'", "function useHeld(D) {\n  if (!D.held || (D === P && tut && tut.hideItem) || D.st !== 'play'")
    s = rep(s, ".itemBtn.nope{animation:nope .35s}", ".itemBtn.nope{animation:nope .35s}.itemBtn.tutup{z-index:8}")
    pre, old, post = cut(s, "  { id: 'item', max: 50,", "  { id: 'orb', max: 55,")
    assert "{ id: 'free2', max: 30," in old and old.count("  { id: '") == 2
    s = pre + ITEM_STEP + post
    s = rep(s, "const TUT_PIP = { move: 0, sling: 1, basin: 2, pound: 3, dodge: 4, rocketdodge: 4, item: 5, orb: 6, flower: 7 };",
            "const TUT_PIP = { move: 0, sling: 1, basin: 2, pound: 3, dodge: 4, rocketdodge: 4, item: 5, rollover: 5, orb: 6, flower: 7 };")
    s = rep(s, "  if (tut.driveMode === 'ahead') return tutAhead(D);\n", "  if (tut.driveMode === 'ahead') return tutAhead(D);\n  if (tut.driveMode === 'line') return tutLine(D);\n")
    s = rep(s, "function tutAhead(D) {", LINE_JS + "function tutAhead(D) {")
    a = "    tv1.set(x, y + 0.3, z).project(camera); if (!(tv1.z < 1 && Math.abs(tv1.x) < 0.8 && tv1.y > -0.7 && tv1.y < 0.8)) continue;\n"
    s = rep(s, a, a + "    if (straight && !tutRunClear(a, d + 3.5)) continue; // (v270: and level ground on past him, for the roll)\n")
    s = rep(s, "function tutRivalIn(dist) {", "function tutRivalIn(dist, straight) { // (straight: as near dead ahead as it can, for the roll-over)")
    s = rep(s, "for (const da of [0.45, -0.45, 0.25, -0.25, 0.7, -0.7, 0, 0.95, -0.95, 1.2, -1.2]) {",
            "for (const da of (straight ? [0, 0.1, -0.1, 0.2, -0.2, 0.32, -0.32, 0.45, -0.45] : [0.45, -0.45, 0.25, -0.25, 0.7, -0.7, 0, 0.95, -0.95, 1.2, -1.2])) {")
    # the roll in the roll-over lesson: aimed at the rival when he's roughly ahead
    s = rep(s, "  if (D.charging) clearCharge(D);\n  const base = cfg.speed * spdK(D)",
            "  if (D.charging) clearCharge(D);\n"
            "  if (D === P && tut && tut.rAim && H.st === 'play') { const dx = H.x - P.x, dz = H.z - P.z, da = wrapA(Math.atan2(dx, dz) - P.yaw); if (Math.hypot(dx, dz) < 9 && Math.abs(da) < 0.8) P.yaw += da; } // (v270: the lesson's roll goes at him)\n"
            "  const base = cfg.speed * spdK(D)")
    return s
