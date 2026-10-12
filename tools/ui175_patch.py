#!/usr/bin/env python3
"""v240 locker entrance: no more dropping into the scene. A pool of your paint opens on the carpet, and the axolotl crawls up out of it,
nose first, onto its spot, covered in paint; it shakes the paint off as it settles, and the face and the accessories come in after that.
(The paint-bead drop stays for the fallback slime.)"""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui174_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the timeline: the pool opens, a beat, it rises and crawls out, settles; then the face and the accessories
rep("function startIntro() { lookIntro = reduceMotion ? { t: IN_LAND, landed: true } : { t: 0 }; }",
    """const CR = { pool: 0.42, rise0: 0.6, rise1: 1.9, land: 1.9, end: 2.85, back: 0.8, deep: 1.25 }; // (crawl-out: when the pool opens, when it starts up, when it's out, when it's done; how far back it starts, how deep)
function startIntro() { const I = VP && VP.slime; lookIntro = reduceMotion ? { t: IN_LAND, landed: true } : I && I.kind === 'axo' ? { t: 0, crawl: true, land: CR.land, vis: CR.rise0, sink: CR.deep, back: CR.back, pose: { pitch: 0, sq: 0, rise: 0 } } : { t: 0 }; }
// the crawl-out, frame by frame: the pool, the depth and the distance still to crawl, the nose up as it comes, the settle
function crawlFrame(I) {
  const t = I.t, pool = dipPool, U = pool.userData.U, V = VP;
  const R = clamp(((V && V.half) || 1.2) * 0.9, 0.9, 1.5), yw = V.yawDraw || 0, fx = Math.sin(yw), fz = Math.cos(yw);
  const open = t < CR.land ? easeBack(Math.min(1, t / CR.pool)) : 1 - dipEase((t - CR.land - 0.1) / (CR.end - CR.land - 0.1));
  const cx = P.x - fx * CR.back * 0.55, cz = P.z - fz * CR.back * 0.55; // (the pool sits where it comes up, behind its spot)
  pool.visible = pool.userData.mask.visible = open > 0.01; pool.position.set(cx, 0.006, cz); pool.scale.setScalar(Math.max(0.01, open) * R); pool.userData.mask.position.set(P.x, 0, P.z);
  U.uT.value = t; U.uCol.value.setHex(TEAMS[0].wet); U.uRip.value = Math.max(0, (I.rip || 0) - 0.016); I.rip = U.uRip.value;
  const u = clamp((t - CR.rise0) / (CR.rise1 - CR.rise0), 0, 1), e = dipEase(u);
  U.uHole.value = u > 0 && u < 1 ? Math.sin(u * Math.PI) : 0;
  I.sink = CR.deep * (1 - Math.min(1, e * 1.15)); I.back = CR.back * (1 - e); // (up and forward together: the head breaks the surface first, the tail last)
  I.pose.pitch = -0.6 * Math.sin(Math.min(1, u * 1.1) * Math.PI) * (1 - 0.5 * e); // (nose up as it climbs, level as it lands)
  if (t >= CR.rise0 && !I.rose) { I.rose = true; AU.pop(); AU.vox('hup', 0.7); I.rip = 1; dipCrown(10, R * 0.45, 2.0, 1.1, 0.5); }
  if (u > 0.45 && !I.mid) { I.mid = true; I.rip = 0.8; dipCrown(8, R * 0.6, 1.4, 1.4, 0.45); }
  if (t >= CR.land && !I.landed) { I.landed = true; I.rip = 0.6; buzz(10); shake = Math.max(shake, 0.03); }
  { const k = Math.max(0, t - CR.land), osc = 0.5 * Math.exp(-k * 6) * Math.cos(k * 15); I.pose.sq = Math.max(0, osc); I.pose.rise = Math.max(0, -osc) * 0.8; }
  const kf = easeOut((t - CR.land - 0.1) / 0.32), kw = clamp((t - CR.land - 0.3) / 0.34, 0, 1);
  introFade(kf, kw);
  const eo = Math.max(0.02, easeOut((t - CR.land - 0.1) / 0.26));
  for (const it of eyes) { it.e.scale.y *= eo; it.pu.scale.multiplyScalar(eo); }
  for (const a of pArcs) if (a.visible) a.scale.y *= eo;
  if (t >= CR.end) endIntro();
}""")
rep("function introFrame() {\n  const I = lookIntro, t = I.t, t2 = IN_T.wait + IN_T.hang;", "function introFrame() {\n  const I = lookIntro, t = I.t, t2 = IN_T.wait + IN_T.hang; if (I.crawl) return crawlFrame(I);")
rep("function endIntro() { if (!lookIntro) return; lookIntro = null; strand.visible = false; introFade(1, 1); }",
    "function endIntro() { if (!lookIntro) return; const cr = lookIntro.crawl; lookIntro = null; strand.visible = false; introFade(1, 1); if (cr && !lkDip) { dipPool.visible = dipPool.userData.mask.visible = false; } }")
# the pose: no hop, drop or shrink for the crawl-out; the nose up comes in through the dip's pitch
rep("    if (D === P && lookIntro) { const I = introPose(lookIntro.t); hop = I.y; sq = I.sq; rise = I.rise; spinY = 0; U.gDrop.value = I.drop; U.gWob.value = I.wob; V.introSc = I.sc; }",
    "    if (D === P && lookIntro) { if (lookIntro.crawl) { const q = lookIntro.pose; hop = 0; sq = q.sq; rise = q.rise; spinY = 0; U.gDrop.value = 0; U.gWob.value = 1; V.introSc = 1; } else { const I = introPose(lookIntro.t); hop = I.y; sq = I.sq; rise = I.rise; spinY = 0; U.gDrop.value = I.drop; U.gWob.value = I.wob; V.introSc = I.sc; } }")
rep("+ (D === P && lkDip && lkDip.pose ? lkDip.pose.pitch : 0), yawD + spinY,", "+ (D === P && lkDip && lkDip.pose ? lkDip.pose.pitch : 0) + (D === P && lookIntro && lookIntro.crawl ? lookIntro.pose.pitch : 0), yawD + spinY,")
# shown from the moment it starts up, not from a landing
rep("!(D === P && lookIntro && lookIntro.t < IN_LAND), was = I.root.visible;", "!(D === P && lookIntro && lookIntro.t < (lookIntro.vis !== undefined ? lookIntro.vis : IN_LAND)), was = I.root.visible;")
# covered in paint while it climbs (then the usual shake-off), down in the pool by its depth and back by its distance, no see-through ghost
rep("  else if (D.introCrawl) { if (V.coatSt !== 'climb') { V.coatSt = 'climb'; I.coatOn(0); } } // (climbing out: covered in paint, in its own shape)",
    "  else if (D.introCrawl || (D === P && lookIntro && lookIntro.crawl && lookIntro.t < lookIntro.land)) { if (V.coatSt !== 'climb') { V.coatSt = 'climb'; I.coatOn(0); } } // (climbing out: covered in paint, in its own shape)")
rep("  else if (D.ip && D.ip.sink !== null) V.sink = D.ip.sink;\n  else V.sink = (V.sink || 0) + (0 - (V.sink || 0)) * Math.min(1, dt * 18);",
    "  else if (D.ip && D.ip.sink !== null) V.sink = D.ip.sink;\n  else if (D === P && lookIntro && lookIntro.crawl) V.sink = lookIntro.sink;\n  else V.sink = (V.sink || 0) + (0 - (V.sink || 0)) * Math.min(1, dt * 18);")
rep("I.noGhost = !!D.introCrawl || inPot || !!(D.ip && D.ip.sink > 0.05); }\n  I.root.position.y = -V.sink;",
    "I.noGhost = !!D.introCrawl || inPot || !!(D.ip && D.ip.sink > 0.05) || !!(D === P && lookIntro && lookIntro.crawl); }\n  I.root.position.y = -V.sink;\n  { const bk = D === P && lookIntro && lookIntro.crawl ? lookIntro.back : 0, yw = V.yawDraw || 0; I.root.position.x = -Math.sin(yw) * bk; I.root.position.z = -Math.cos(yw) * bk; } // (the locker's crawl-out: still back in the pool by this much)")
open(DST, 'w').write(s)
print('ui175 ok', n0, '->', len(s))
