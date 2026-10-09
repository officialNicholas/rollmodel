p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
# 1. the easy CPU: a touch slower, slower to think and react, sloppier steering, fewer attacks
rep("easy:   { think: 0.9,  react: 0.6,  noise: 0.42, pick: 6, steal: 1.1, inkPad: 0.1,  sunLead: 0,   warnReact: 1.9, pound: 0.6, poundR: 1.6,  hunt: 0.04, ram: 0.15, flingAtk: 0,    flingNav: 0,   evade: 0,    hop: 0,   camp: 0,   puddle: 0,   covPound: 0,   grab: 0.3, pivot: false, speed: 0.9,  slip: 0.35,",
    "easy:   { think: 1.05, react: 0.75, noise: 0.48, pick: 8, steal: 1.0, inkPad: 0.1,  sunLead: 0,   warnReact: 1.9, pound: 0.45, poundR: 1.5, hunt: 0.025, ram: 0.1, flingAtk: 0,    flingNav: 0,   evade: 0,    hop: 0,   camp: 0,   puddle: 0,   covPound: 0,   grab: 0.25, pivot: false, speed: 0.86, slip: 0.35,")
rep("sight: 14, fov: 150, hear: 2.5, poundHear: 9,  memory: 1.5, model: 0, airSling: 0.15, attack: 0.12, dodge: 0.05, orb: 0.45,",
    "sight: 12, fov: 150, hear: 2.5, poundHear: 9,  memory: 1.5, model: 0, airSling: 0.1, attack: 0.08, dodge: 0.04, orb: 0.35,")
# 2. easy (against CPUs): your blood lasts a bit longer
rep("const DIFFS = [['easy', 'Easy', 'Still learning'], ['medium', 'Medium', 'Plays smart'], ['hard', 'Hard', 'Reads you']];\nlet diff = DIFFS.some(d => d[0] === store.diff) ? store.diff : 'medium';",
    "const DIFFS = [['easy', 'Easy', 'Still learning'], ['medium', 'Medium', 'Plays smart'], ['hard', 'Hard', 'Reads you']];\nlet diff = DIFFS.some(d => d[0] === store.diff) ? store.diff : 'medium';\n// easy is a gentler game all round, not just a weaker CPU: your blood lasts longer and the canvases have no holes and less up in the air\nconst easyOn = () => diff === 'easy' && mode !== 'solo', EASY_DRAIN = 0.85;")
rep("else D.paint -= cfg.drain * dt * (D.charging ? STILL_DRAIN : 1); }",
    "else D.paint -= cfg.drain * dt * (D.charging ? STILL_DRAIN : 1) * (D === P && easyOn() ? EASY_DRAIN : 1); }")
# 3. easy canvases
rep("let themeAvoid = null; // a new canvas never comes back in the same look as the one before it",
    "let genOpt = { easy: false, avoid: null }; // set by genWorld: an easy canvas, and the look to avoid (a new canvas never repeats the one before it)")
rep("theme = th0.id === themeAvoid ?", "theme = th0.id === genOpt.avoid ?")
rep("  const arch = pick(['plaza', 'plaza', 'pit', 'spire', 'canopy', 'open', 'rotunda', 'well']);",
    "  const EZ = genOpt.easy; // easy: no holes in the floor and fewer platforms up in the air, so there's less to fall off and into\n  const arch = pick(EZ ? ['plaza', 'plaza', 'spire', 'open', 'open', 'rotunda'] : ['plaza', 'plaza', 'pit', 'spire', 'canopy', 'open', 'rotunda', 'well']);")
rep("  add('deck', 1, 2); add('tower', 1, 2); add('wall', 0, 1); add('corner', 0, 1); add('pad', 0, 2); add('block', 0, 1); add('pit', 0, 1); add('island', 0, 1); add('plateau', arch === 'plaza' || arch === 'rotunda' ? 0 : 1, 1);\n  for (const k in TK) add(k, TK[k][0], TK[k][1]); // the theme's own pieces",
    "  if (EZ) { add('deck', 0, 1); add('tower', 1, 2); add('wall', 0, 1); add('corner', 0, 1); add('pad', 0, 1); add('block', 0, 1); add('plateau', arch === 'plaza' || arch === 'rotunda' ? 0 : 1, 1); }\n  else { add('deck', 1, 2); add('tower', 1, 2); add('wall', 0, 1); add('corner', 0, 1); add('pad', 0, 2); add('block', 0, 1); add('pit', 0, 1); add('island', 0, 1); add('plateau', arch === 'plaza' || arch === 'rotunda' ? 0 : 1, 1); }\n  for (const k in TK) { if (EZ && k === 'rpit') continue; add(k, TK[k][0], EZ && k === 'rpad' ? Math.min(1, TK[k][1]) : TK[k][1]); } // the theme's own pieces")
rep("  const target = (2 * ARENA) * (2 * ARENA) * rr(0.13, 0.19);\n  for (let t = 0; t < 120 && area() < target; t++) { const [cx, cz] = spot(); place(kit[pick(['block', 'corner', 'pad', 'pit', 'tower', theme.fill, theme.fill])](cx, cz)); }",
    "  const target = (2 * ARENA) * (2 * ARENA) * (EZ ? rr(0.11, 0.15) : rr(0.13, 0.19)), ezFill = theme.fill === 'rpad' ? 'drum' : theme.fill;\n  for (let t = 0; t < 120 && area() < target; t++) { const [cx, cz] = spot(); place(kit[pick(EZ ? ['block', 'corner', 'tower', 'block', ezFill, ezFill] : ['block', 'corner', 'pad', 'pit', 'tower', theme.fill, theme.fill])](cx, cz)); }")
rep("function genWorld(seed) {\n  const t0 = performance.now(); GEN.n++;",
    "function genWorld(seed, opt) {\n  opt = opt || {}; const easy = opt.easy !== undefined ? !!opt.easy : easyOn(), avoid = opt.avoid || null;\n  genOpt = { easy, avoid };\n  const t0 = performance.now(); GEN.n++;")
rep("Object.assign(GEN, { seed, sym: L.sym, arch: L.arch, tries: t + 1, fallback: false });", "Object.assign(GEN, { seed, sym: L.sym, arch: L.arch, tries: t + 1, fallback: false, easy, avoid });")
rep("Object.assign(GEN, { seed, sym: 'classic', arch: 'classic', tries: 5, fallback: true });", "Object.assign(GEN, { seed, sym: 'classic', arch: 'classic', tries: 5, fallback: true, easy, avoid });")
rep("const GEN = { seed: 0, sym: '', arch: '', tries: 0, ms: 0, fallback: false, n: 0 };", "const GEN = { seed: 0, sym: '', arch: '', tries: 0, ms: 0, fallback: false, n: 0, easy: false, avoid: null };")
rep("function freshMap() { themeAvoid = TH.id; genWorld((Math.random() * 4294967296) >>> 0); themeAvoid = null; mapUsed = false; }",
    "function freshMap() { genWorld((Math.random() * 4294967296) >>> 0, { avoid: TH.id }); mapUsed = false; }")
rep("setTimeout(() => { genWorld(sd); mapUsed = false; building = false; start(); }, 60);",
    "const op = { easy: GEN.easy, avoid: GEN.avoid }; setTimeout(() => { genWorld(sd, op); mapUsed = false; building = false; start(); }, 60);")
rep("function start() {\n  if (building) return;",
    "function start() {\n  if (building) return;\n  if (!mapUsed && GEN.easy !== easyOn()) mapUsed = true; // the canvas waiting in the menu was made for the other difficulty")
rep("$('stages').addEventListener('click', e => { const t = e.target.closest('button'); if (!t) return; AU.init(); AU.ui(); diff = t.dataset.d; store.diff = diff; save(); renderStages(); });",
    "$('stages').addEventListener('click', e => { const t = e.target.closest('button'); if (!t) return; AU.init(); AU.ui(); const was = easyOn(); diff = t.dataset.d; store.diff = diff; save();\n  if (state === 'menu' && !building && easyOn() !== was) { freshMap(); resetRun(); decorate(); menuPose(); kick($('cvName'), 'bump'); } // easy has its own gentler canvases\n  renderStages(); });")
open(p,'w').write(s); print('ok')
