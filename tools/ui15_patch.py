#!/usr/bin/env python3
"""A longer idle on the beat, the locker landing splat, three eye styles, the canvases gallery. On top of ui14_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui14_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---------- the beat: where the song is, for anything that wants to move with it ----------
rep("    _trk(k) { return k ? !!(TRK[k] && TRK[k].buf) : trk && trk.key; },", "    _trk(k) { return k ? !!(TRK[k] && TRK[k].buf) : trk && trk.key; },\n    beat() { if (!ctx || !trk || trk.t0 === undefined) return null; return { t: T() - trk.t0, bpm: trk.key === 'menu' ? 148 : trk.key === 'win' || trk.key === 'lost' ? 120 : bpm }; },")

# ---------- the idle: a long, varied cycle. It listens to the song (head nodding on the beat), bounces on the beat, stands still a
# while, looks at its hands, wags its tail, hides behind its ears, pulls faces; never the same thing twice running ----------
rep("const IDLE_ACTS = [['bounce', 0.9], ['look', 1.7], ['wiggle', 1.3], ['yawn', 1.9], ['shimmy', 1.2], ['look', 1.7], ['bounce', 0.9], ['shimmy', 1.2]];",
    """const IDLE_ACTS = [['listen', 3.4, 3], ['bounce', 2.1, 2], ['still', 2.6, 3], ['hands', 2.6, 2], ['wag', 1.6, 2], ['peek', 2.6, 1], ['face', 2.0, 2], ['look', 1.7, 2], ['yawn', 1.9, 1], ['shimmy', 1.2, 2], ['wiggle', 1.3, 1]];
let idleLast = '';
function pickIdle() { if (window.__idleForce) { const f = IDLE_ACTS.find(a => a[0] === window.__idleForce); if (f) return f; } const pool = []; for (const a of IDLE_ACTS) if (a[0] !== idleLast) for (let i = 0; i < a[2]; i++) pool.push(a); const a = pool[(Math.random() * pool.length) | 0]; idleLast = a[0]; return a; }
const beatNow = () => { const B = AU.beat ? AU.beat() : null; return B ? B.t * B.bpm / 60 : clock * 2.47; };""")
rep("  idle.sway = idle.push = idle.hop = idle.spin = idle.sq = idle.rise = idle.roll = idle.pitch = idle.bank = 0;", "  idle.sway = idle.push = idle.hop = idle.spin = idle.sq = idle.rise = idle.roll = idle.pitch = idle.bank = idle.hand = idle.earCover = 0;")
rep("if (idle.t <= 0) { const a = IDLE_ACTS[(Math.random() * IDLE_ACTS.length) | 0]; idle.act = a[0]; idle.dur = a[1]; idle.u = 0; if (idle.act === 'yawn') emote(P, 'yawn', a[1]);",
    "if (window.__idleForce && idle.t > 0.15) idle.t = 0.15; if (idle.t <= 0) { const a = pickIdle(); idle.act = a[0]; idle.dur = a[1]; idle.u = 0; idle.b0 = beatNow(); if (idle.act === 'yawn') emote(P, 'yawn', a[1]); if (idle.act === 'face') emote(P, ['glee', 'smug', 'ouch', 'bonk'][(Math.random() * 4) | 0], a[1] * 0.8); if (idle.act === 'listen' || idle.act === 'bounce') idle.dur = Math.max(a[1], (idle.act === 'listen' ? 8 : 4) * 60 / (AU.beat && AU.beat() ? AU.beat().bpm : 148));")
rep("      if (idle.act === 'bounce') { const k = (u * 2) % 1; idle.hop = Math.sin(k * Math.PI) * (u < 0.5 ? 0.3 : 0.2); idle.rise = Math.sin(k * Math.PI) * 0.35; idle.sq = k < 0.1 || k > 0.88 ? 0.32 : 0; }",
    """      const env = Math.sin(Math.min(1, u * 4) * Math.PI / 2) * (1 - smoothstep(0.82, 1, u)), bt = beatNow() - idle.b0;
      if (idle.act === 'bounce') { const k = (bt / 2) % 1, p = Math.sin(k * Math.PI); idle.hop = p * 0.3 * env; idle.rise = p * 0.32 * env; idle.sq = (k < 0.08 || k > 0.9 ? 0.3 : 0) * env; }
      else if (idle.act === 'listen') { const ph = bt % 1, p = Math.pow(Math.max(0, Math.cos(ph * 6.2832)), 3), bar = Math.floor(bt); idle.pitch = -0.11 * p * env; idle.roll = (bar % 2 ? 0.06 : -0.06) * p * env; idle.sq = 0.07 * p * env; idle.rise = 0.05 * p * env; lyT = 0.02 * env; }
      else if (idle.act === 'still') { lyT = 0.01; }
      else if (idle.act === 'hands') { const h = u < 0.5 ? smoothstep(0.08, 0.22, u) * (1 - smoothstep(0.4, 0.5, u)) : smoothstep(0.55, 0.68, u) * (1 - smoothstep(0.88, 1, u)); idle.hand = (u < 0.5 ? 1 : -1) * h; idle.pitch = 0.13 * h; idle.roll = (u < 0.5 ? -0.05 : 0.05) * h; lxT = (u < 0.5 ? -0.07 : 0.07) * h; lyT = -0.07 * h; }
      else if (idle.act === 'wag') { const ph = u * Math.PI * 9; idle.spin = Math.sin(ph) * 0.2 * env; idle.bank = Math.sin(ph) * 0.11 * env; idle.sway = Math.sin(ph + 0.4) * 0.55 * env; idle.sq = 0.05 * env; idle.rise = 0.04 * env * Math.abs(Math.sin(ph)); }
      else if (idle.act === 'peek') { const k = smoothstep(0.08, 0.3, u) * (1 - smoothstep(0.7, 0.92, u)); idle.earCover = k; idle.pitch = 0.07 * k; idle.sq = 0.06 * k; }
      else if (idle.act === 'face') { idle.roll = 0.12 * Math.sin(u * Math.PI * 2) * env; lxT = 0.09 * Math.sin(u * Math.PI * 3); lyT = 0.03 * Math.sin(u * Math.PI * 5); idle.sq = 0.08 * Math.abs(Math.sin(u * Math.PI * 4)) * env; }""")
rep("      if (u >= 1) { idle.act = null; idle.t = 2.2 + Math.random() * 2.8; } }", "      if (u >= 1) { idle.act = null; idle.t = 1.4 + Math.random() * 2.6; } }")
# the home gets the same idle as the locker, in place of the hop every second
rep("    if (D === P && lookOpen && !lookIntro) { sq = idle.sq || 0.04 + 0.035 * Math.sin(clock * 2.3); rise = idle.rise; hop = idle.hop; spinY = idle.spin; }",
    "    if (D === P && (lookOpen || menuPage === 'home') && !lookIntro) { sq = idle.sq || 0.04 + 0.035 * Math.sin(clock * 2.3); rise = idle.rise; hop = idle.hop; spinY = idle.spin; }")
rep("const showK = D === P && state === 'menu' && lookOpen; o.headRoll = showK ? idle.roll : 0; o.headPitch = showK ? idle.pitch : 0; o.hand = IPo ? IPo.hand : 0;",
    "const showK = D === P && state === 'menu' && (lookOpen || menuPage === 'home'); o.headRoll = showK ? idle.roll : 0; o.headPitch = showK ? idle.pitch : 0; o.earCover = showK ? idle.earCover : 0; o.hand = IPo ? IPo.hand : showK ? idle.hand : 0;")
# ears over the eyes: both ears fold forward and in
rep("+ 1.15 * Math.max(0, (o.earUp || 0) * sd), -0.75, 1.5)", "+ 1.15 * Math.max(0, (o.earUp || 0) * sd) - 1.0 * (o.earCover || 0), -0.75, 1.5)")
rep("- 0.6 * s.wallK + 0.12 * s.brace, -1.1, 0.8);", "- 0.6 * s.wallK + 0.12 * s.brace + 0.6 * (o.earCover || 0), -1.1, 0.8);")

# ---------- the locker landing: the splat first, then the paint rises over it ----------
rep("    I.landed = true; AU.splat(0.9); buzz(14);\n    addSplat(P.x, P.y, P.z, P.yaw, 0.72, -8, false, false, 0);\n    for (let i = 0; i < 16; i++) {",
    "    I.landed = true; AU.splat(1.2); AU.land(0.8); buzz(18); shockwave(P.x, P.y, P.z, 1.6, TEAMS[0].wet); splash(P, 1.4); shake = Math.max(shake, 0.08);\n    addSplat(P.x, P.y, P.z, P.yaw, 0.95, -8, false, false, 0);\n    for (let i = 0; i < 24; i++) {")
rep("I.coatOn(0.7); I.coatShape(0, 7); I.coatBurst(0.34); };", "I.coatOn(0.7); I.coat.c = 0.001; I.coat.rise = 0.32; I.coatShape(0, 7); I.coatBurst(0.72); };")
rep("      if (C.melt) { C.c = Math.max(0, C.c - dt / 0.36); if (C.c <= 0) C.melt = false; }", "      if (C.rise > 0) { C.c = Math.min(1, C.c + dt / C.rise); if (C.c >= 1) C.rise = 0; }\n      else if (C.melt) { C.c = Math.max(0, C.c - dt / 0.36); if (C.c <= 0) C.melt = false; }")
rep("I.coat = { c: 0, b: 0, bT: 0, bRate: 8, burstT: -1, melt: false, fade: 0, seed: Math.random() * 40 };", "I.coat = { c: 0, b: 0, bT: 0, bRate: 8, burstT: -1, melt: false, fade: 0, rise: 0, seed: Math.random() * 40 };")
rep("I.coatOn = b => { const C = I.coat; C.c = 1; C.melt = false; C.fade = 0; C.burstT = -1; C.b = C.bT = b || 0; };", "I.coatOn = b => { const C = I.coat; C.c = 1; C.melt = false; C.fade = 0; C.rise = 0; C.burstT = -1; C.b = C.bT = b || 0; };")

# ---------- three eye styles: round (as drawn), edgy (almond, slanted, a thick ink rim), dot (solid pupils) ----------
rep("uniform vec3 sPaint, fIris;\nvarying vec3 vFace, vSlimeP;", "uniform vec3 sPaint, fIris; uniform float fStyle;\nvarying vec3 vFace, vSlimeP;")
rep("fPupil: { value: new THREE.Vector4(0, -0.03, 1, 0) },", "fPupil: { value: new THREE.Vector4(0, -0.03, 1, 0) }, fStyle: { value: 0 },")
rep("    I.setIris = c => { U.fIris.value.set(c[0], c[1], c[2]); };", "    I.setIris = c => { U.fIris.value.set(c[0], c[1], c[2]); };\n    I.setEyeStyle = k => { U.fStyle.value = k; };")
rep("SI.setIris((EYE_COLS[look.iris] || EYE_COLS.brown).lin); }", "SI.setIris((EYE_COLS[look.iris] || EYE_COLS.brown).lin); if (SI.setEyeStyle) SI.setEyeStyle(EYE_STYLE_K[look.eyes] || 0); }")
rep("const EYE_KEYS = Object.keys(EYE_COLS);", "const EYE_KEYS = Object.keys(EYE_COLS);\nconst EYE_STYLES = { round: 'Round', edgy: 'Edgy', dot: 'Dot' }, EYE_STYLE_K = { round: 0, edgy: 1, dot: 2 };")
rep("  vec2 fq = vFace.xy * fComp.xy; vec2 cuv = fq * 0.5 + 0.5;\n  vec4 eA = texture2D(fCol, fCell(fCells.x, cuv)), eB = texture2D(fCol, fCell(fCells.z, cuv)), eye = mix(eA, eB, fMix.x);\n  vec3 emL = mix(texture2D(fMsk, fCell(fCells.x, cuv)).rgb, texture2D(fMsk, fCell(fCells.z, cuv)).rgb, fMix.x); vec2 em = emL.rg;\n  vec4 bl = texture2D(fCol, fCell(fMix.w, cuv)); eye = mix(eye, bl, fMix.y); em *= 1.0 - fMix.y;",
    """  vec2 fq = vFace.xy * fComp.xy; vec2 cuv = fq * 0.5 + 0.5;
  // the eye style: 1 narrows and slants the eyes into almonds and rims them in ink; 2 draws them as solid dots
  vec2 fqe = fq; if (fStyle > 0.5 && fStyle < 1.5) { float sd0 = fq.x < 0.0 ? -1.0 : 1.0; vec2 pc0 = vec2(sd0 * 0.4, 0.16); vec2 l = fq - pc0; l.y = l.y * 1.4 + 0.03; l.x = (l.x + l.y * sd0 * 0.5) * 1.06; fqe = pc0 + l; }
  vec2 cuvE = fqe * 0.5 + 0.5;
  vec4 eA = texture2D(fCol, fCell(fCells.x, cuvE)), eB = texture2D(fCol, fCell(fCells.z, cuvE)), eye = mix(eA, eB, fMix.x);
  vec3 emL = mix(texture2D(fMsk, fCell(fCells.x, cuvE)).rgb, texture2D(fMsk, fCell(fCells.z, cuvE)).rgb, fMix.x); vec2 em = emL.rg;
  vec4 bl = texture2D(fCol, fCell(fMix.w, cuvE)); eye = mix(eye, bl, fMix.y); em *= 1.0 - fMix.y;
  float dotK = 0.0; if (fStyle > 1.5) { eye.a = 0.0; em = vec2(0.0); }""")
rep("  float lsh = 0.0; if (fLash.x + fLash.y > 0.0) lsh = mix(emL.b, texture2D(fMsk, fCell(fMix.w, cuv)).b, fMix.y) * (fq.x < 0.0 ? fLash.x : fLash.y);\n  vec3 c = mix(diffuseColor.rgb, eye.rgb, eye.a);",
    """  float lsh = 0.0; if (fLash.x + fLash.y > 0.0) lsh = mix(emL.b, texture2D(fMsk, fCell(fMix.w, cuvE)).b, fMix.y) * (fq.x < 0.0 ? fLash.x : fLash.y);
  vec3 c = mix(diffuseColor.rgb, eye.rgb, eye.a);
  if (fStyle > 0.5 && fStyle < 1.5) { float d1 = max(max(texture2D(fCol, fCell(fCells.x, cuvE + vec2(0.024, 0.0))).a, texture2D(fCol, fCell(fCells.x, cuvE - vec2(0.024, 0.0))).a), max(texture2D(fCol, fCell(fCells.x, cuvE + vec2(0.0, 0.028))).a, texture2D(fCol, fCell(fCells.x, cuvE - vec2(0.0, 0.028))).a));
    float rim = clamp(d1 - eye.a, 0.0, 1.0) * (1.0 - 0.5 * fMix.y); c = mix(c, vec3(0.03, 0.012, 0.02), rim); dotK = rim; }
  if (fStyle > 1.5) { float bk = 1.0 - fMix.y * 0.92; for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy * 0.6; vec2 dd = (fq - pc) * vec2(1.0, 1.0 / max(0.08, bk)); float r = length(dd);
    float dk = 1.0 - smoothstep(0.125, 0.145, r); c = mix(c, vec3(0.03, 0.012, 0.02), dk); float hl = 1.0 - smoothstep(0.03, 0.046, length((fq - pc - vec2(-0.045, 0.05)) * vec2(1.0, 1.0 / max(0.08, bk)))); c = mix(c, vec3(1.0), hl * dk); dotK = max(dotK, dk); } }""")
# the pupils sit in the slanted eye
blk_a = s.index("  // the pupils: a deep brown iris"); blk_b = s.index("  c = mix(c, vec3(0.016, 0.0025, 0.007), lsh);", blk_a)
blk = s[blk_a:blk_b]; assert blk.count("fq - pc") == 3, blk.count("fq - pc"); s = s[:blk_a] + blk.replace("fq - pc", "fqe - pc") + s[blk_b:]
rep("  faceInk = max(max(eye.a, mo.a), lsh) * vFace.z;", "  faceInk = max(max(max(eye.a, mo.a), lsh), dotK) * vFace.z;")
# the look remembers the style; rivals get one too
rep("return { eyes: 'round', head: ok(l.head, 'head'),", "return { eyes: EYE_STYLES[l.eyes] ? l.eyes : 'round', head: ok(l.head, 'head'),")
rep("iris: Math.random() < 0.45 ? 'brown' : EYE_KEYS[1 + (Math.random() * 4 | 0)] }; } }", "iris: Math.random() < 0.45 ? 'brown' : EYE_KEYS[1 + (Math.random() * 4 | 0)], eyes: ['round', 'round', 'edgy', 'dot'][(Math.random() * 4) | 0] }; } }")
# the locker: a row of three styles beside the colors
rep('<div class="leyes"><p class="lhead">Eyes</p><div class="irises" id="irises" role="group" aria-label="Eye color"></div></div>',
    '<div class="leyes"><p class="lhead">Eyes</p><div class="irises estyles" id="eyeStyles" role="group" aria-label="Eye style"></div><div class="irises" id="irises" role="group" aria-label="Eye color"></div></div>')
rep("  $('irises').innerHTML = EYE_KEYS.map(", """  const ES_ICON = { round: '<svg viewBox="0 0 40 40"><ellipse cx="20" cy="20" rx="13" ry="12" fill="#fff" stroke="#171320" stroke-width="2.5"/><circle cx="21" cy="21" r="6" fill="#8A5636"/><circle cx="21.5" cy="21.5" r="3" fill="#171320"/><circle cx="19" cy="18.5" r="1.6" fill="#fff"/></svg>', edgy: '<svg viewBox="0 0 40 40"><path d="M6 23C10 13 22 11 34 15C30 24 18 29 6 23Z" fill="#171320"/><path d="M8.5 22.5C12 15.5 22 14 31.5 16.5C28 23 18 26.5 8.5 22.5Z" fill="#fff"/><circle cx="20" cy="20" r="4.6" fill="#8A5636"/><circle cx="20.5" cy="20.4" r="2.4" fill="#171320"/><circle cx="18.6" cy="18.4" r="1.3" fill="#fff"/></svg>', dot: '<svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="9.5" fill="#171320"/><circle cx="16.5" cy="16.5" r="3" fill="#fff"/></svg>' };
  $('eyeStyles').innerHTML = Object.keys(EYE_STYLES).map(k => '<button class="eyes" type="button" data-es="' + k + '" aria-label="' + EYE_STYLES[k] + ' eyes" title="' + EYE_STYLES[k] + '" aria-pressed="' + (myLook.eyes === k) + '">' + ES_ICON[k] + '</button>').join('');
  $('irises').innerHTML = EYE_KEYS.map(""")
rep("$('irises').addEventListener('click', e => {", "$('eyeStyles').addEventListener('click', e => { const b = e.target.closest('.eyes'); if (!b || b.dataset.es === myLook.eyes) return; AU.init(); myLook.eyes = b.dataset.es; saveLook(); const sl = $('lookRail').scrollLeft; renderLook(); $('lookRail').scrollLeft = sl; railEdge(); AU.pop(); { const t = $('eyeStyles').querySelector('[data-es=\"' + myLook.eyes + '\"]'); if (t) kick(t, 'pop'); } eyeShow = { t: 0, kind: 0 }; idle.t = Math.max(idle.t, 4); });\n$('irises').addEventListener('click', e => {")

# ---------- the canvases: the gallery of what is unlocked; your pick is the vote's default ----------
rep('id="worldTitle">Pick a canvas<', 'id="worldTitle" data-sub="5 canvases unlocked">Canvases<')
rep("$('worldTitle').textContent = 'Pick a canvas';", "$('worldTitle').textContent = 'Canvases';")
rep('<small>Canvas &middot; tap to change</small>', '<small>Canvases &middot; your pick</small>')

CSS = '''
/* ===== eye styles, and the gallery's sub-line ===== */
.leyes{flex-wrap:wrap;row-gap:8px}
.estyles{gap:6px;margin-right:4px}
.eyes{appearance:none;width:36px;height:36px;padding:0;border:0;border-radius:6px;background:#fff;box-shadow:2px 3px 0 rgba(23,19,32,.18);cursor:pointer;display:grid;place-items:center;transition:transform .2s cubic-bezier(.3,1.6,.5,1)}
.eyes svg{width:30px;height:30px}
.eyes[aria-pressed="true"]{box-shadow:0 0 0 2.5px var(--ink),2px 3px 0 rgba(23,19,32,.25);transform:translateY(-2px)}
.eyes.pop{animation:tilepop .42s cubic-bezier(.2,1.6,.4,1)}
.whead h2{position:relative}
.whead h2::after{content:attr(data-sub);position:absolute;left:50%;top:100%;transform:translateX(-50%);margin-top:4px;font:800 10px/1 var(--font-ui);letter-spacing:.16em;text-transform:uppercase;color:#B8B0C8;white-space:nowrap;text-shadow:none}
.mworld.sopen .whead h2::after{display:none}
@media (max-height:520px) and (min-aspect-ratio:1/1){.eyes{width:30px;height:30px}.eyes svg{width:24px;height:24px}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]
rep('<p class="ver">Version 84</p>', '<p class="ver">Version 85</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
