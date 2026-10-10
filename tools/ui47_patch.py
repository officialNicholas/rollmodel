#!/usr/bin/env python3
"""Zombie eyes: a fourth eye style for the Halloween season. Found on the Halloween canvases, bought in the Paint Shop, then picked in the locker's Eyes tab. Milky green irises of two sizes, bloodshot whites, heavy drooping lids, shadows under the eyes. On top of ui46_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui46_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---- the shader: style 3 ----
rep("  float sqd = (fStyle > 0.5 && fStyle < 1.5) ? 1.0 : 0.0; vec2 fqe = fq;", "  float sqd = (fStyle > 0.5 && fStyle < 1.5) ? 1.0 : 0.0, zmb = fStyle > 2.5 ? 1.0 : 0.0; vec2 fqe = fq;")
rep("  float dotK = 0.0; if (fStyle > 1.5) { eye.a = 0.0; em = vec2(0.0); }", "  float dotK = 0.0; if (fStyle > 1.5 && fStyle < 2.5) { eye.a = 0.0; em = vec2(0.0); }\n  if (zmb > 0.5) eye.rgb = eye.rgb * vec3(0.78, 0.9, 0.6) + vec3(0.05, 0.06, 0.0) * eye.a; // (the whites gone a sickly yellow-green)")
rep("  if (fStyle > 1.5) { float bk = 1.0 - fMix.y * 0.92;", "  if (fStyle > 1.5 && fStyle < 2.5) { float bk = 1.0 - fMix.y * 0.92;")
rep("    float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy, dd = (fqe - pc) * vec2(1.0, 0.92); float r = length(dd), ri = mix(0.165, 0.205, sqd) * fPupil.z, rp = mix(0.092, 0.1, sqd) * fPupil.z;\n    float ia = (1.0 - smoothstep(ri - 0.014, ri, r)) * em.r;\n    vec3 ic = mix(fIris, fIris * 0.2, smoothstep(0.0, ri, r)); ic = mix(ic, vec3(0.004, 0.002, 0.003), 1.0 - smoothstep(rp - 0.012, rp, r));\n    ic += fIris * 1.12 * smoothstep(ri * 0.35, ri * 0.95, r) * smoothstep(0.2, -0.6, dd.y / ri) * (1.0 - smoothstep(ri * 0.95, ri, r));",
    "    float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy, dd = (fqe - pc) * vec2(1.0, 0.92); float r = length(dd), ri = mix(0.165, 0.205, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.92 : 1.14, zmb), rp = mix(0.092, 0.1, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.5 : 0.78, zmb);\n    vec3 irC = mix(fIris, vec3(0.42, 0.6, 0.3), zmb); // (zombie: one small iris, one large, both a milky green whatever color was picked)\n    float ia = (1.0 - smoothstep(ri - 0.014, ri, r)) * em.r;\n    vec3 ic = mix(irC, irC * 0.2, smoothstep(0.0, ri, r)); ic = mix(ic, vec3(0.004, 0.002, 0.003), 1.0 - smoothstep(rp - 0.012, rp, r));\n    ic += irC * 1.12 * smoothstep(ri * 0.35, ri * 0.95, r) * smoothstep(0.2, -0.6, dd.y / ri) * (1.0 - smoothstep(ri * 0.95, ri, r));\n    ic = mix(ic, vec3(0.72, 0.78, 0.62), zmb * 0.42 * smoothstep(rp, ri * 0.9, r) * (0.6 + 0.4 * sin(atan(dd.y, dd.x) * 11.0 + r * 60.0))); // (a cloudy film over it)")
rep("    c = mix(c, vec3(1.0), clamp(cl, 0.0, 1.0) * em.r * (1.0 - 0.85 * em.g));\n  }\n  c = mix(c, vec3(0.016, 0.0025, 0.007), lsh);",
    """    c = mix(c, vec3(1.0), clamp(cl, 0.0, 1.0) * (1.0 - 0.75 * zmb) * em.r * (1.0 - 0.85 * em.g));
  }
  // zombie: red veins across the whites, a heavy lid drooping over each eye (lower on the left), dark rings under them
  if (zmb > 0.5) { for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w), dd = fq - pc; float r = length(dd), an = atan(dd.y, dd.x);
      float vn = smoothstep(0.86, 0.99, sin(an * 7.0 + sin(r * 38.0 + an * 3.0) * 0.7 + sd * 1.3)) * smoothstep(0.12, 0.2, r) * (1.0 - smoothstep(0.3, 0.42, r)); c = mix(c, vec3(0.55, 0.03, 0.04), vn * eye.a * (1.0 - em.r * 0.7));
      float lidY = pc.y + (i == 0 ? 0.05 : 0.13) - sd * dd.x * 0.22, lid = eye.a * smoothstep(lidY - 0.012, lidY + 0.012, fq.y), crease = eye.a * (1.0 - smoothstep(0.0, 0.03, abs(fq.y - lidY)));
      c = mix(c, vec3(0.1, 0.045, 0.08), lid); c = mix(c, vec3(0.36, 0.2, 0.28), crease * 0.9);
      float ring = (1.0 - eye.a) * smoothstep(0.52, 0.3, length(dd * vec2(0.9, 1.35))) * smoothstep(0.02, -0.2, dd.y); c = mix(c, c * vec3(0.42, 0.34, 0.5), ring * 0.8); } }
  c = mix(c, vec3(0.016, 0.0025, 0.007), lsh);""")

# the mouth to go with the eyes: the drawn mouth gives way to a crooked stitched grin with a few jagged teeth
rep("  vec4 mA = texture2D(fCol, fCell(fCells.y, cuv)), mB = texture2D(fCol, fCell(fCells.w, cuv)), mo = mix(mA, mB, fMix.x) * fMix.z * (1.0 - sCoatM);\n  c = mix(c, mo.rgb, mo.a);\n  faceInk = max(max(max(eye.a, mo.a), lsh), dotK) * vFace.z;",
    """  vec4 mA = texture2D(fCol, fCell(fCells.y, cuv)), mB = texture2D(fCol, fCell(fCells.w, cuv)), mo = mix(mA, mB, fMix.x) * fMix.z * (1.0 - sCoatM) * (1.0 - zmb);
  c = mix(c, mo.rgb, mo.a);
  float zma = 0.0; if (zmb > 0.5) { float yl = -0.3 + 0.08 * fq.x - 0.12 * fq.x * fq.x, dl = fq.y - yl, inx = smoothstep(0.48, 0.44, abs(fq.x)), fw = fwidth(fq.y) + 0.004;
    float line = (1.0 - smoothstep(0.02 - fw, 0.02 + fw, abs(dl))) * inx, st = (1.0 - smoothstep(0.01, 0.01 + fw, abs(mod(fq.x + 0.075, 0.15) - 0.075))) * (1.0 - smoothstep(0.06, 0.06 + fw, abs(dl))) * inx * step(0.08, abs(fq.x));
    float tooth = 0.0; for (int i = 0; i < 3; i++) { float cx = i == 0 ? -0.2 : i == 1 ? 0.03 : 0.24, w = 0.036 * (1.0 - clamp(-dl / 0.09, 0.0, 1.0)); tooth = max(tooth, (1.0 - smoothstep(w - fw, w + fw, abs(fq.x - cx))) * step(-0.09, dl) * step(dl, 0.0)); }
    zma = max(line, st) * (1.0 - sCoatM); c = mix(c, vec3(0.03, 0.012, 0.02), zma); c = mix(c, vec3(0.93, 0.9, 0.78), tooth * (1.0 - line) * (1.0 - sCoatM)); zma = max(zma, tooth * (1.0 - sCoatM)); }
  faceInk = max(max(max(max(eye.a, mo.a), lsh), dotK), zma) * vFace.z;""")

# ---- the style, its icon, its price, how it is found and bought ----
rep("const EYE_STYLES = { round: 'Round', edgy: 'Squid', dot: 'Dot' }, EYE_STYLE_K = { round: 0, edgy: 1, dot: 2 };", "const EYE_STYLES = { round: 'Round', edgy: 'Squid', dot: 'Dot', zombie: 'Zombie' }, EYE_STYLE_K = { round: 0, edgy: 1, dot: 2, zombie: 3 };\nconst NO_IRIS = k => k === 'dot' || k === 'zombie'; // (styles whose iris color is fixed)")
rep("const PRICES = { flower: 170, bowtie: 220, lashes: 260, glasses: 320, patch: 390, fangs: 470, tiara: 560, tophat: 680, pirate: 820, halo: 1000, hat: 1300 };",
    "const PRICES = { flower: 170, bowtie: 220, lashes: 260, glasses: 320, patch: 390, fangs: 470, tiara: 560, tophat: 680, pirate: 820, halo: 1000, zombie: 1150, hat: 1300 };")
rep("for (const w of WEAR) w.cat = WEAR_CAT[w.slot] || 'face';", "for (const w of WEAR) w.cat = WEAR_CAT[w.slot] || 'face';\n// things to find and buy that are not worn on the body: an eye style\nconst EXTRA = [{ id: 'zombie', name: 'Zombie eyes', slot: 'eyes', cat: 'eyes', season: 1, stage: 'halloween' }], ITEMS = WEAR.concat(EXTRA);")
rep("const OWNED = new Set(Array.isArray(store.owned) ? store.owned.filter(id => WEAR.some(w => w.id === id)) : []);", "const OWNED = new Set(Array.isArray(store.owned) ? store.owned.filter(id => ITEMS.some(w => w.id === id)) : []);")
rep("  if (store.itemIn > 0) return; const left = WEAR.filter(w => w.stage === stageSet() && !owns(w.id)); if (!left.length) return;", "  if (store.itemIn > 0) return; const left = ITEMS.filter(w => w.stage === stageSet() && !owns(w.id)); if (!left.length) return;")
rep("  const w = WEAR.find(x => x.id === id), el = $('newItem'); if (!w) return showEnd(endImg);", "  const w = ITEMS.find(x => x.id === id), el = $('newItem'); if (!w) return showEnd(endImg);")
rep("$('niTry').addEventListener('click', () => { AU.init(); AU.ui(); const id = newItem, w = WEAR.find(x => x.id === id);", "$('niTry').addEventListener('click', () => { AU.init(); AU.ui(); const id = newItem, w = ITEMS.find(x => x.id === id);")
rep("function buyItem(id) { const w = WEAR.find(x => x.id === id);", "function buyItem(id) { const w = ITEMS.find(x => x.id === id);")
rep("  if (v === '1234') { for (const w of WEAR) { OWNED.add(w.id); BOUGHT.add(w.id); }", "  if (v === '1234') { for (const w of ITEMS) { OWNED.add(w.id); BOUGHT.add(w.id); }")
rep("  $('unlockLink').parentNode.hidden = WEAR.every(w => owns(w.id));", "  $('unlockLink').parentNode.hidden = ITEMS.every(w => owns(w.id));")
# the shop sells it
rep("const SHOP_CATS = [['head', 'Headgear'], ['face', 'Facial'], ['cloth', 'Clothing']];", "const SHOP_CATS = [['head', 'Headgear'], ['face', 'Facial'], ['cloth', 'Clothing'], ['eyes', 'Eyes']];")
rep("  for (const [c, label] of SHOP_CATS) { const items = WEAR.filter(w => w.cat === c && !bought(w.id)); if (!items.length) continue; any = true;", "  for (const [c, label] of SHOP_CATS) { const items = ITEMS.filter(w => w.cat === c && !bought(w.id)); if (!items.length) continue; any = true;")
rep("$('shopGrid').addEventListener('click', e => { const b = e.target.closest('.shitem'); if (!b) return; AU.init(); const w = WEAR.find(x => x.id === b.dataset.w); if (!w) return;", "$('shopGrid').addEventListener('click', e => { const b = e.target.closest('.shitem'); if (!b) return; AU.init(); const w = ITEMS.find(x => x.id === b.dataset.w); if (!w) return;")
# the icon (drawn like the worn items, so the shop and the new-item card can use it)
rep("const WEAR_ICON = {", "const WEAR_ICON = {\n  zombie: '<path d=\"M4 20c4-8 11-11 17-10 7 1 12 5 15 10-3 6-9 10-16 10S7 26 4 20z\" fill=\"#DCE8B4\" stroke=\"#171320\" stroke-width=\"2.5\" stroke-linejoin=\"round\"/><path d=\"M9 17l4 3M13 24l-3 3M27 16l-3 4M26 26l3 2\" stroke=\"#C8303A\" stroke-width=\"1.3\" stroke-linecap=\"round\"/><circle cx=\"21\" cy=\"21\" r=\"6.5\" fill=\"#6E9A4E\"/><circle cx=\"21.6\" cy=\"21.6\" r=\"2.4\" fill=\"#171320\"/><path d=\"M4 20c4-8 11-11 17-10 7 1 12 5 15 10-1.4-1.5-3.2-1.6-7 0-5 2-12 1-19-1-2.5-.7-4.5.2-6 1z\" fill=\"#3A2740\" stroke=\"#171320\" stroke-width=\"2.5\" stroke-linejoin=\"round\"/><path d=\"M8 21c7 2.5 13 3 19 1\" fill=\"none\" stroke=\"#7B5A78\" stroke-width=\"1.4\" stroke-linecap=\"round\"/>',")
a = s.index("const ES_ICON_T = {"); b = s.index("};;", a) + 3
s = s[:b] + " ES_ICON_T.zombie = '<svg viewBox=\"0 0 40 40\">' + WEAR_ICON.zombie + '</svg>';" + s[b:]
# the Eyes tab: a locked style shows its lock and sends you to the shop; its iris row is fixed
rep("  $('eyeStyles').innerHTML = Object.keys(EYE_STYLES).map(k => '<button class=\"eyes\" type=\"button\" data-es=\"' + k + '\" aria-label=\"' + EYE_STYLES[k] + ' eyes\" title=\"' + EYE_STYLES[k] + '\" aria-pressed=\"' + (myLook.eyes === k) + '\">' + ES_ICON[k] + '</button>').join('');",
    "  $('eyeStyles').innerHTML = Object.keys(EYE_STYLES).map(k => { const it = EXTRA.find(x => x.id === k), lk = it && !bought(k); return '<button class=\"eyes' + (lk ? ' locked' : '') + '\" type=\"button\" data-es=\"' + k + '\" aria-label=\"' + EYE_STYLES[k] + ' eyes' + (lk ? ', ' + PRICE(it) + ' dabs in the Paint Shop' : '') + '\" title=\"' + EYE_STYLES[k] + (lk ? ' (Paint Shop)' : '') + '\" aria-pressed=\"' + (myLook.eyes === k) + '\">' + ES_ICON[k] + (lk ? LOCK_ICON : '') + '</button>'; }).join('');")
rep("$('irises').classList.toggle('off', myLook.eyes === 'dot'); $('irises').setAttribute('aria-disabled', myLook.eyes === 'dot' ? 'true' : 'false');", "$('irises').classList.toggle('off', NO_IRIS(myLook.eyes)); $('irises').setAttribute('aria-disabled', NO_IRIS(myLook.eyes) ? 'true' : 'false');")
rep("$('eyeStyles').addEventListener('click', e => { const b = e.target.closest('.eyes'); if (!b || b.dataset.es === myLook.eyes) return; AU.init(); myLook.eyes = b.dataset.es;",
    "$('eyeStyles').addEventListener('click', e => { const b = e.target.closest('.eyes'); if (!b || b.dataset.es === myLook.eyes) return; AU.init(); if (b.classList.contains('locked')) { const it = EXTRA.find(x => x.id === b.dataset.es); AU.nope(); kick(b, 'nope'); note(owns(b.dataset.es) ? EYE_STYLES[b.dataset.es] + ' eyes are ' + PRICE(it) + ' dabs in the Paint Shop.' : 'Find the ' + EYE_STYLES[b.dataset.es].toLowerCase() + ' eyes on ' + WEAR_WHERE[it.stage] + '.'); return; } myLook.eyes = b.dataset.es;")
rep("$('irises').addEventListener('click', e => { const b = e.target.closest('.eyec'); if (!b || b.dataset.i === myLook.iris || myLook.eyes === 'dot') return;", "$('irises').addEventListener('click', e => { const b = e.target.closest('.eyec'); if (!b || b.dataset.i === myLook.iris || NO_IRIS(myLook.eyes)) return;")
# a style you no longer own (a cleared save) falls back to round
rep("function renderLook() {\n  const fresh = new Set(store.fresh || []);", "function renderLook() {\n  const fresh = new Set(store.fresh || []);\n  if (EXTRA.some(x => x.id === myLook.eyes) && !bought(myLook.eyes)) { myLook.eyes = 'round'; saveLook(); }")

css = '''
/* zombie eyes: a locked style in the Eyes tab */
.eyes{position:relative}
.eyes.locked svg{filter:grayscale(.55) brightness(.85);opacity:.7}
.eyes .lk{position:absolute;right:-5px;top:-5px;width:16px;height:16px;display:grid;place-items:center;border-radius:5px;background:var(--black);color:var(--cream)}
.eyes .lk svg{width:10px;height:10px;filter:none;opacity:1}
.eyes.nope{animation:nope .35s}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
