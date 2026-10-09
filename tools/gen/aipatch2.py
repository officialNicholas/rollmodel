f='/home/claude/paint-the-canvas.html'; s=open(f).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n, (a[:90], s.count(a)); s=s.replace(a,b)
# 1) the sunrise check must not wipe out the coffin it's already heading for
rep("""    if (coffin && cd * (D.paint < 0.55 ? 0.45 : D.paint < 0.8 ? 0.8 : 1.05) < sd) { sd = cd; shelter = coffin; }
    ai.goPot = shelter === coffin ? coffinP : null;
  }
  const ttsun = timeToSun();
  if (shelter && (sunny || (AI.sunLead > 0 && ttsun < sd / speed + AI.sunLead))) { const gp = ai.goPot; aiGo(D, shelter, 'shelter'); ai.goPot = gp; return; }""",
"""    if (coffin && cd * (D.paint < 0.55 ? 0.45 : D.paint < 0.8 ? 0.8 : 1.05) < sd) { sd = cd; shelter = coffin; }
  }
  const ttsun = timeToSun();
  if (shelter && (sunny || (AI.sunLead > 0 && ttsun < sd / speed + AI.sunLead))) {
    // already under a deck or beside a tower with the sun out: keep painting, but only where the shadow falls
    if (AI.plan > 0 && wxPhase === 'sun' && shelter !== coffin && src.shade && D.paint > 0.2) {
      for (const n of NAV.nodes) if (!n.shade) nMult[n.id] += 1000;
      dijkstra(src.id);
      let best = null, bv = 0.8;
      for (const n of NAV.nodes) { const d = nDist[n.id]; if (!n.shade || !(d < 500) || d < 1.5) continue; const v = (nAcc[n.id] + 0.5 * nGain[n.id]) / (d + 2); if (v > bv) { bv = v; best = n; } }
      aiGo(D, best || src, best ? 'shadepaint' : 'shelter'); return;
    }
    aiGo(D, shelter, 'shelter'); ai.goPot = shelter === coffin ? coffinP : null; return;
  }""")
rep("  // 2) running low: refill before it's too late", """  // spots right next to boiling water, where a pound splashes it away and fills the tank back up
  const sunNow = wxPhase === 'sun' || wxPhase === 'warn';
  if (AI.plan > 0 && !sunNow) { pudNear.fill(0, 0, NN); for (const r of rivals) if (r.on) NAV.near(r.x, r.z, r.y, SLAM_R * 0.5 + r.rad - 0.6, n => { if (Math.hypot(n.x - r.x, n.z - r.z) > r.hit + 0.35) pudNear[n.id] = 1; }); }
  // 2) running low: refill before it's too late""")
rep("""  ai.need = need;
""", """  ai.need = need;
  // a pound needs more than half a tank, so the smart refill is to pound boiling water while you still can
  if (AI.plan > 0 && !sunNow && D.paint > 0.53 && D.paint < need + 0.22) {
    let best = null, bd = 16;
    for (const n of NAV.nodes) { if (!pudNear[n.id]) continue; const d = nDist[n.id]; if (d >= bd) continue; const tt = d / speed; if (D.slamCD > tt + 0.3 || D.paint - tt * cfg.drain * 1.15 < 0.54) continue; bd = d; best = n; }
    if (best) { aiGo(D, best, 'paint'); ai.poundAt = best.id; return; }
  }
""")
rep("""  const cand = [], sunNow = wxPhase === 'sun' || wxPhase === 'warn';
  const planOK = AI.plan > 0 && !sunNow && (D.paint > SLAM_COST + Math.max(0.12, need + 0.04) || D.paint < 0.6);
  if (planOK) { pudNear.fill(0, 0, NN); for (const r of rivals) if (r.on) NAV.near(r.x, r.z, r.y, SLAM_R * 0.5 + r.rad - 0.6, n => { if (Math.hypot(n.x - r.x, n.z - r.z) > r.hit + 0.35) pudNear[n.id] = 1; }); }
  const refillV = 220 * clamp(1 - D.paint, 0, 1), richOK = D.paint > SLAM_COST + Math.max(0.12, need + 0.04);
  const pv = n => { if (!planOK) return 0; const d = nDist[n.id]; if (D.slamCD > d / speed + 0.25) return 0; const pu = pudNear[n.id]; if (!pu && !richOK) return 0; return (poundVal(n.id) + (pu ? refillV : 0)) * AI.plan; };""",
"""  const cand = [], planOK = AI.plan > 0 && !sunNow && D.paint > 0.53;
  const pv = n => {
    if (!planOK) return 0; const d = nDist[n.id], tt = d / speed; if (D.slamCD > tt + 0.25) return 0;
    const arrive = D.paint - tt * cfg.drain * 1.15; if (arrive < 0.53) return 0;
    const pu = pudNear[n.id]; if (!pu && arrive - SLAM_COST < Math.max(0.3, need)) return 0;
    return (poundVal(n.id) + (pu ? 120 + 220 * (1 - (arrive - SLAM_COST)) : 0)) * AI.plan;
  };""")
# shade painting ends with the sun
rep("  if (ai.mode === 'shelter' && wxPhase !== 'warn' && wxPhase !== 'sun' && !(AI.sunLead > 0 && timeToSun() < 1)) {", "  if ((ai.mode === 'shelter' || ai.mode === 'shadepaint') && wxPhase !== 'warn' && wxPhase !== 'sun' && !(AI.sunLead > 0 && timeToSun() < 1)) {")
# 2) a safe way out of the coffin: never hop out over a drop into nothing
rep("// inside a coffin: wait out the sun, top up, don't hop out into your pound, then leave toward the next target", """// the hop out of a coffin carries you about four units: pick a heading where that lands on something
function exitYaw(D, want) {
  const p = D.pot, ok = a => { for (let d = 0.5; d <= 4.8; d += 0.35) { const x = p.x + Math.sin(a) * d, z = p.z + Math.cos(a) * d; if (surfaceUnder(x, z, p.y + 1.2) === -Infinity) return false; if (d > 2.4 && rivals.some(r => r.on && Math.abs(r.y - p.y) < 0.4 && Math.hypot(x - r.x, z - r.z) < r.hit)) return false; } return true; };
  if (ok(want)) return want;
  for (let k = 1; k <= 8; k++) for (const sg of [1, -1]) { const a = want + sg * k * 0.393; if (ok(a)) return a; }
  return want;
}
// inside a coffin: wait out the sun, top up, don't hop out into your pound, then leave toward the next target""")
rep("if (!ai.exitPlan || !ai.exitPlan.flee) ai.exitPlan = { yaw: Math.atan2(D.x - O.x, D.z - O.z), t: 0, flee: true };", "if (!ai.exitPlan || !ai.exitPlan.flee) ai.exitPlan = { yaw: exitYaw(D, Math.atan2(D.x - O.x, D.z - O.z)), t: 0, flee: true };")
rep("""    const w = ai.plan ? null : aiFollow(D), t = ai.path && ai.path.length ? NAV.nodes[ai.path[Math.min(ai.path.length - 1, 5)]] : null;
    ai.plan = null; ai.exitPlan = { yaw: t ? Math.atan2(t.x - D.x, t.z - D.z) : D.yaw, t: 0 };""",
"""    // head for the first point on the new route that's clear of the coffin itself
    let t = null; if (ai.path) for (const id of ai.path) { const n = NAV.nodes[id]; t = n; if (Math.hypot(n.x - D.x, n.z - D.z) > 2.5) break; }
    if (t && Math.hypot(t.x - D.x, t.z - D.z) < 1 && ai.tgt >= 0) t = NAV.nodes[ai.tgt];
    ai.plan = null; ai.exitPlan = { yaw: exitYaw(D, t && Math.hypot(t.x - D.x, t.z - D.z) > 0.5 ? Math.atan2(t.x - D.x, t.z - D.z) : D.yaw), t: 0 };""")
open(f,'w').write(s)
print('patched')
