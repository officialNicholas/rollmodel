"""v471: Heat Stroke gets its acted-out scene on the Strokes page, like the other strokes.

- The user, of Heat Stroke's card showing only the sun icon: "This needs a character reenactment like the rest".
- The scene (about 5.6 s, looping and mirrored like the others): your character faces you, then crouches and charges as warm sparks
  rise off it; the sun flares (a gold ring and a warm glow over the whole picture). The rival out in the open starts to steam: its
  paint drains, it looks scared and tries to crawl away more and more slowly, then dries out and goes dizzy. Meanwhile your character
  rolls round painting freely, and ends grinning at you as the glow fades.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """
/* (v471) the Heat Stroke scene: a warm glow over the picture while the sun is out */
.sgflash.sunon{opacity:1!important;animation:none!important;background:radial-gradient(ellipse at 50% 22%,rgba(255,220,100,.62) 0,rgba(255,160,50,.3) 48%,rgba(255,140,30,.06) 85%)}
"""

JS = r"""
// (v471) Heat Stroke: a charge, the sun flares, the rival out in the open steams and dries up while you paint freely
const COL_SUN = new THREE.Color(0xFFC93C);
function sgHeat(dt, t, s) {
  const A = SGD.A, B = SGD.B, DA = A.D, DB = B.D, cA = TEAMS[0].css, F = SGD.sp, fl = sgH().flash;
  if (t < 1.2 && B.show) { const p = sgCS(0.2 * s, -0.3); sgGo(B, p[0], p[1], 0.8, dt); DB.ip.expr = 'content'; }
  if (t < 0.4) { if (fl && fl.classList.contains('sunon')) fl.className = 'sgflash'; sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'ready'; }
  else if (t < 1.2) { if (sgOnce('wind')) { DA.squash = 0.7; DA.wob = 1; emote(DA, 'glee', 0.8); F.fx = 0; }
    sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, B); DA.ip.expr = 'focus';
    F.fx -= dt; if (F.fx <= 0) { F.fx = 0.1; const x = sgLX(A), z = sgLZ(A); for (let i = 0; i < 3; i++) { const a = Math.random() * 6.2832; sgPart(x + Math.cos(a) * 0.35, 0.2, z + Math.sin(a) * 0.35, Math.cos(a) * 0.3, 1.8 + Math.random(), Math.sin(a) * 0.3, 0.4, i % 2 ? COL_BURN : COL_SUN, 0.5); } } }
  else if (sgOnce('sun')) { const x = sgLX(A), z = sgLZ(A); sgRing(x, z, 3.2, 0xFFC93C); sgRing(x, z, 1.9, 0xFFFFFF); if (fl) fl.className = 'sgflash sunon'; sgShk(0.35); emote(DA, 'glee', 1.2);
    for (let i = 0; i < 20; i++) { const a = Math.random() * 6.2832, r = Math.random() * SG_R * 0.9; sgPart(Math.cos(a) * r, 0.1, Math.sin(a) * r, 0, 1 + Math.random() * 1.4, 0, 0.5 + Math.random() * 0.4, i % 2 ? COL_SUN : COL_BURN, 0.3 + Math.random() * 0.25); } }
  // the rival out in the open: steaming, its paint draining, crawling off slower and slower, then dried out and dizzy
  if (t >= 1.2 && t < 4.5 && B.show && DB.st === 'play') {
    DB.paint = Math.max(0.04, 1 - (t - 1.2) / 2.5);
    F.st = (F.st || 0) - dt; if (F.st <= 0) { F.st = 0.05; const bx = sgLX(B), bz = sgLZ(B); sgPart(bx + (Math.random() - 0.5) * 0.5, 0.5, bz + (Math.random() - 0.5) * 0.5, (Math.random() - 0.5) * 0.4, 1.3 + Math.random() * 1.2, (Math.random() - 0.5) * 0.4, 0.55, Math.random() < 0.55 ? COL_WHITE : COL_BURN, 0.45); }
    if (t > 1.6 && t < 3.7) { const p = sgCS(0.95 * s, -0.75); sgGo(B, p[0], p[1], 0.15 + 0.55 * DB.paint, dt); } }
  if (t >= 3.7 && B.show && sgOnce('dry')) { const bx = sgLX(B), bz = sgLZ(B); sgHalt(B, dt); DB.stunT = 1.5; DB.squash = 0.6; DB.wob = 1; sgRing(bx, bz, 0.9, 0xFFB45A); for (let i = 0; i < 10; i++) { const a = Math.random() * 6.2832; sgPart(bx, 0.45, bz, Math.cos(a) * 1.4, 1 + Math.random() * 1.5, Math.sin(a) * 1.4, 0.4, COL_DULL, 0.45); } }
  // you: free to paint while they bake
  if (t >= 1.45 && t < 4.4) {
    if (!F.path) { F.path = [sgCS(-0.55 * s, 1.0), sgCS(-0.05 * s, 1.05), sgCS(-0.25 * s, 0.45), sgCS(-0.95 * s, 0.25), sgCS(-1.05 * s, 0.8)]; F.pi = 0; }
    let p = F.path[F.pi]; if (Math.hypot(p[0] - sgLX(A), p[1] - sgLZ(A)) < 0.2 && F.pi < F.path.length - 1) p = F.path[++F.pi];
    const lx = sgLX(A), lz = sgLZ(A); sgGo(A, p[0], p[1], 2.4, dt); sgStripe(lx, lz, sgLX(A), sgLZ(A), 0.62, cA); sgWatch(A, B); DA.ip.expr = 'glee'; }
  if (t >= 4.4) { if (sgOnce('cool') && fl) fl.className = 'sgflash'; sgHalt(A, dt); sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = DB.stunT > 0 ? 'smirk' : 'glee'; }
}
"""

def apply(s):
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    s = rep(s, "freeze: 6.6, storm: 5.8, bomb: 5.2 }", "freeze: 6.6, storm: 5.8, bomb: 5.2, heat: 5.6 }")
    s = rep(s, "  else if (k === 'bomb') { sgAtC(A, -0.55 * s, 0.4); sgAtC(B, 0.45 * s, -0.25); }", "  else if (k === 'bomb') { sgAtC(A, -0.55 * s, 0.4); sgAtC(B, 0.45 * s, -0.25); }\n  else if (k === 'heat') { sgAtC(A, -0.85 * s, 0.45); sgAtC(B, 0.55 * s, -0.4); } // (v471)")
    s = rep(s, "  else if (k === 'bomb') sgBomb(dt, t, s);", "  else if (k === 'bomb') sgBomb(dt, t, s);\n  else if (k === 'heat') sgHeat(dt, t, s); // (v471)")
    s = rep(s, "sgStormOff(); sgBombOff(); SGD.iceK = 0;", "sgStormOff(); sgBombOff(); { const fl = sgH().flash; if (fl && fl.classList.contains('sunon')) fl.className = 'sgflash'; } SGD.iceK = 0;")
    s = rep(s, "function sgFreeze(dt, t, s) {", JS.strip() + "\nfunction sgFreeze(dt, t, s) {")
    return s
