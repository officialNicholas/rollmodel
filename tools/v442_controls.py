"""v442: quicker steering, an Invert steering switch, Turning 65% by default (up to 100%), the Screen switch in a match's Settings,
"Paint the Stage" in place of "Versus", and no gifts: everything but the Spooky SZN pieces is in the Paint Shop from the start.

- Steering answers sooner: a shorter drag reaches a full turn (58 points, was 70), the dead zone is smaller (4, was 6), small drags
  turn more (the curve is nearly straight, 1.1, was 1.35), and the two smoothing steps between the finger and the turn act about
  twice as fast (the finger filter 75 a second, was 45; the turn itself 58, was 36, and 80 turning the other way, was 50).
- Settings has Invert steering (Normal / Inverted): inverted, a swipe right turns you left. Swipes only (the arrow keys stay as they are).
  It is in a match's Settings too.
- Turning runs from 40% to 100% (was 50% to 150%), 65% by default (was 80%). A save on the old default (80) moves to the new one, once;
  one above 100 comes down to 100.
- Screen (Upright / Wide) is in a match's Settings as well as the lobby's (it was hidden there). A screen that turns either way (an
  iPad, iPhone Duo) still follows how it's held, as before.
- The Versus CPU event is Paint the Stage ("Out-paint the CPUs", "Most paint wins"); online, Versus is Paint the Stage too.
- No gifts: nothing turns up on the canvas any more (no rare item box, no free Zombie eyes on the first Spooky SZN canvas), and the
  lesson hands out nothing. Everything but the Spooky SZN pieces is for sale in the Paint Shop from the start (the pirate hat, top hat
  and tiara had to be found first). The Spooky SZN pieces are not for sale ("A Spooky SZN exclusive"), the fangs aside (40 dabs, as
  v441 made them). Pieces already found or owned stay so."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

INV_ROW = ('        <div class="sopt wide"><p class="slab">Invert steering</p><div class="seg duo tog pick" id="invPick" role="group" aria-label="Invert steering">'
           '<button type="button" data-v="off" aria-pressed="true"><span>Normal</span></button><button type="button" data-v="on" aria-pressed="false"><span>Inverted</span></button></div>'
           '<p class="gnote" id="invNote">Swipe right to turn right.</p></div>\n')

INV_JS = r"""
// (v442) Invert steering: a swipe right turns you left (store.steerInv). Swipes only
function invPaint() { const on = !!store.steerInv; for (const b of $('invPick').children) b.setAttribute('aria-pressed', String((b.dataset.v === 'on') === on)); $('invNote').textContent = on ? 'Swipe right to turn left.' : 'Swipe right to turn right.'; }
function invSet(on) { if (!!store.steerInv === !!on) return; if (on) store.steerInv = 1; else delete store.steerInv; save(); invPaint(); }
$('invPick').addEventListener('click', e => { const b = e.target.closest('button[data-v]'); if (!b) return; AU.init(); AU.ui(); invSet(b.dataset.v === 'on'); });
invPaint();
"""

def apply(s):
    # ---- steering: sooner and more direct
    s = rep(s, "const MAX_DRAG = 70, DEAD = 6, HOLD_MS = 150, TAP_MS = 300;", "const MAX_DRAG = 58, DEAD = 4, HOLD_MS = 150, TAP_MS = 300; /* (v442: was 70 and 6) */")
    s = rep(s, "steerIn = t.moved ? Math.sign(dx) * Math.pow(a, 1.35) : 0;", "steerIn = t.moved ? Math.sign(dx) * Math.pow(a, 1.1) * (store.steerInv ? -1 : 1) : 0; /* (v442: nearly straight, was 1.35; Invert steering) */")
    s = rep(s, "if (D === P && !P.ai) { steerS += (input - steerS) * Math.min(1, dt * 45); input = steerS; }",
            "if (D === P && !P.ai) { steerS += (input - steerS) * Math.min(1, dt * 75); input = steerS; } /* (v442: 75, was 45) */")
    s = rep(s, "D.turn += (wantL - D.turn) * Math.min(1, dt * (D === P && !P.ai ? (wantL * D.turn < 0 ? 50 : 36) : 20));",
            "D.turn += (wantL - D.turn) * Math.min(1, dt * (D === P && !P.ai ? (wantL * D.turn < 0 ? 80 : 58) : 20)); /* (v442: 80 and 58, were 50 and 36) */")
    # ---- Turning: 40% to 100%, 65% by default
    s = rep(s, "const turnPct = () => { const v = +store.turn; return v >= 50 && v <= 150 ? Math.round(v / 5) * 5 : 80; },",
            "const turnPct = () => { const v = +store.turn; return v > 0 ? Math.min(100, Math.max(40, Math.round(v / 5) * 5)) : 65; }, /* (v442: 40 to 100, 65 by default) */")
    s = rep(s, '<b class="trnv" id="turnVal">80%</b><button class="trndef" id="turnDef" type="button" aria-label="Turning back to default (80%)">Default</button>',
            '<b class="trnv" id="turnVal">65%</b><button class="trndef" id="turnDef" type="button" aria-label="Turning back to default (65%)">Default</button>')
    s = rep(s, '<input type="range" id="turnPick" min="50" max="150" step="5" value="80"', '<input type="range" id="turnPick" min="40" max="100" step="5" value="65"')
    s = rep(s, "el.style.setProperty('--v', ((v - 50) / 100 * 100).toFixed(1) + '%');", "el.style.setProperty('--v', ((v - 40) / 60 * 100).toFixed(1) + '%');")
    s = rep(s, "const d = $('turnDef'); if (d) d.disabled = v === 80; };", "const d = $('turnDef'); if (d) d.disabled = v === 65; };")
    s = rep(s, "$('turnDef').addEventListener('click', () => { AU.init(); AU.ui(); store.turn = 80; save(); show(); });",
            "$('turnDef').addEventListener('click', () => { AU.init(); AU.ui(); delete store.turn; save(); show(); });")
    s = rep(s, "store.turn = clamp(v, 50, 150); show();", "store.turn = clamp(v, 40, 100); show();")
    s = rep(s, "{ const pairs = [[$('turnPick'), $('turnVal')]];",
            "if (!store.turn442) { store.turn442 = 1; if (+store.turn === 80) delete store.turn; else if (+store.turn > 100) store.turn = 100; save(); } // (v442: the old default moves to the new one, once)\n"
            "{ const pairs = [[$('turnPick'), $('turnVal')]];")
    # ---- Invert steering, under Turning (in a match's Settings too)
    a = '<p class="gnote" id="turnNote">How fast you turn when you swipe.</p></div>\n'
    s = rep(s, a, a + INV_ROW)
    a = "  window.__turnShow = show; show(); }\n"
    s = rep(s, a, a + INV_JS.lstrip('\n'))
    s = rep(s, "function paintSettings() { try {", "function paintSettings() { try { invPaint(); } catch (e) {} try {")
    # ---- Screen in a match's Settings too (only Visuals, which restarts the game, stays out)
    s = rep(s, "function setPlayRows(on) { for (const id of ['orientPick', 'gfxPick']) {", "function setPlayRows(on) { for (const id of ['gfxPick']) { /* (v442: Screen stays) */")
    # ---- Paint the Stage
    s = rep(s, '<span class="evtx"><b>Versus CPU</b><small>1v1 or a 3-way</small></span>', '<span class="evtx"><b>Paint the Stage</b><small>Out-paint the CPUs</small></span>')
    s = rep(s, '<button class="evmain" id="evVs" type="button" aria-expanded="false" aria-controls="evVsPick"><span class="evbar"></span>',
            '<button class="evmain" id="evVs" type="button" aria-expanded="false" aria-controls="evVsPick"><span class="evbar"><i>Most paint wins</i></span>')
    s = rep(s, "const PY_MODES = [['duel', 'Versus', '1v1'],", "const PY_MODES = [['duel', 'Paint the Stage', '1v1'],")
    s = rep(s, "const PY_FULL = { duel: 'Versus', trio: 'Versus 3-way',", "const PY_FULL = { duel: 'Paint the Stage', trio: 'Paint the Stage 3-way',")
    s = rep(s, "' online is coming next. Versus is on now.'", "' online is coming next. Paint the Stage is on now.'", 2)
    s = rep(s, "<span class=\"evtx\"><b>Versus</b><small>Real rivals, no CPUs</small></span>", "<span class=\"evtx\"><b>Paint the Stage</b><small>Real rivals, no CPUs</small></span>")
    s = rep(s, 'aria-label="Versus 1 v 1: find one real rival"', 'aria-label="Paint the Stage 1 v 1: find one real rival"')
    s = rep(s, 'aria-label="Versus 3-way: find two real rivals"', 'aria-label="Paint the Stage 3-way: find two real rivals"')
    s = rep(s, "nm = PY_FULL[qm] || 'Versus';", "nm = PY_FULL[qm] || 'Paint the Stage';")
    s = rep(s, "(ptHost() ? 'cancel and pick Versus' : 'the host can pick Versus')", "(ptHost() ? 'cancel and pick Paint the Stage' : 'the host can pick Paint the Stage')")
    # ---- no gifts: nothing turns up on the canvas, the lesson hands out nothing
    s = rep(s, "  if (NM) return; // (v306: no rare finds online)", "  return; // (v442: no gifts, nothing turns up on the canvas. v306: none online)")
    s = rep(s, "Object.assign(gift, { id: 'flower', on: false, got: false, pop: 0, at: 1e9 });", "Object.assign(gift, { id: null, on: false, got: false, pop: 0, at: 1e9 }); /* (v442: no gift) */")
    s = rep(s, "    if (!owns('flower')) unlockItem('flower'); if (!owns('fangs')) unlockItem('fangs'); if (!newItem || newItem === 'flower') newItem = ['flower', 'fangs'];\n", "")
    # ---- the Paint Shop: everything but the Spooky SZN pieces for sale from the start (those are exclusives; the fangs are for sale)
    s = rep(s, "needFind = w => !OUTRIGHT.has(w.id) && (!!w.season || w.slot === 'head');", "needFind = w => !OUTRIGHT.has(w.id) && !!w.season; /* (v442: only the Spooky SZN pieces, which aren't for sale) */")
    s = rep(s, "', locked. Find it on ' + where)) + '\">'", "', a Spooky SZN exclusive, not for sale')) + '\">'")
    s = rep(s, "owns(w.id) && needFind(w) ? 'Found on ' + where : 'In stock') : 'Find it on ' + where) + '</span>", "owns(w.id) && needFind(w) ? 'Found on ' + where : 'In stock') : 'Spooky SZN exclusive') + '</span>")
    s = rep(s, "shopNote('Find the ' + w.name.toLowerCase() + ' on ' + WEAR_WHERE[w.stage] + ' first.'); return; }", "shopNote('The ' + w.name.toLowerCase() + ' is a Spooky SZN exclusive, not for sale.'); return; }")
    s = rep(s, "', locked. ' + (w.gift ? 'A free gift on ' : 'Find it on ') + WEAR_WHERE[w.stage])", "', a Spooky SZN exclusive, not for sale')")
    s = rep(s, "'In stock now') : 'Found on ' + where + ' only';", "'In stock now') : 'A Spooky SZN exclusive';")
    s = rep(s, "else { doH = STROKE_LOCK + 'Find it'; doDis = true; doLab = w.name + ' is locked'; note = 'Find it on ' + where + ', then it’s for sale here'; } }",
            "else { doH = STROKE_LOCK + 'Locked'; doDis = true; doLab = w.name + ' is a Spooky SZN exclusive'; note = 'A Spooky SZN exclusive, not sold in the Paint Shop'; } }")
    s = rep(s, "lkToast('Find it on ' + WEAR_WHERE[w.stage] + ' first'); return; }", "lkToast('A Spooky SZN exclusive, not for sale'); return; }")
    s = rep(s, "if (w && w.gift) { line = bought(w.id) ? 'A free gift from the Spooky SZN' : 'A free gift on the Spooky SZN stages'; if (!bought(w.id)) { doH = STROKE_LOCK + 'Free gift'; doCls = ''; doDis = true; doLab = w.name + ', a free gift on the Spooky SZN stages'; note = 'They turn up as a free gift the first time you play a Spooky SZN stage'; } }",
            "if (w && w.gift) { line = bought(w.id) ? 'From the Spooky SZN' : 'A Spooky SZN exclusive'; if (!bought(w.id)) { doH = STROKE_LOCK + 'Locked'; doCls = ''; doDis = true; doLab = w.name + ', a Spooky SZN exclusive'; note = 'A Spooky SZN exclusive, not sold in the Paint Shop'; } }")
    s = rep(s, "(it.gift ? ', a free gift on the Spooky SZN stages' : ', in the Paint Shop')", "(it.gift ? ', a Spooky SZN exclusive' : ', in the Paint Shop')")
    return s
