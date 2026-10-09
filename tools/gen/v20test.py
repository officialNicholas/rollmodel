import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
PREP = r"""
(() => { window.__noLoop = true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === 'function') __T.AU[k] = () => {};
  __T.genWorld(5000); __T.mapUsed = false; __T.setDiff('hard'); __T.showMenu(); __T.start(); __T.setWx('clear', 999); __T.matchLeft = 80; })()
"""
# helpers inside page
HELP = r"""
window.__open = (need) => { const T = __T; const N = T.NAVo.nodes; // a ground node with clear floor in a radius
  const ok = (x, z, y, r) => { for (let a = 0; a < 6.28; a += 0.4) for (let d = 0.5; d <= r; d += 0.7) { const g = T.surfaceUnder(x + Math.sin(a) * d, z + Math.cos(a) * d, y + 0.5, true); if (g === -Infinity || Math.abs(g - y) > 0.05 || T.blockedAt(x + Math.sin(a) * d, z + Math.cos(a) * d, y)) return false; } return !T.rivals.some(q => q.on && Math.hypot(q.x - x, q.z - z) < r + q.rad + 0.5); };
  for (const n of N) if (ok(n.x, n.z, n.h, need)) return n; return null; };
window.__place = (D, x, z, y, yaw) => { D.st = 'play'; D.koT = 0; D.x = x; D.z = z; D.y = y; D.air = false; D.vy = 0; D.spd = 0; D.yaw = yaw || 0; D.immuneT = 0; D.flatT = 0; D.slam = false; D.missile = false; D.charging = false; D.paint = 1; D.kx = D.kz = 0; D.knockT = 0; D.flung = false; D.flingC = 0; D.pot = null; D.freeLand = false; };
window.__flat = () => { const T = __T; T.applyLayout({ holes: [], boxes: [], ramps: [], clouds: [] }); T.rebuildSamples(); T.buildNav(); T.rivals.forEach(r => { r.on = false; }); T.pots2.forEach((p, i) => { p.y = 0; p.x = -20 + i * 4; p.z = -22; }); };
window.__freezeAI = () => { const T = __T; if (T.H.ai) window.__hai = T.H.ai; T.H.ai = null; T.H.steer = 0; };
"""
async def page(b):
    pg = await b.new_page(viewport={'width':390,'height':844})
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
    await pg.evaluate(PREP); await pg.evaluate(HELP)
    return pg, errs

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg, errs = await page(b)
        # 1. respawn timers
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, out = {};
          const n = __open(1); __place(P, n.x, n.z, n.h); T.knockOut(P, 'dry'); out.dry = P.koT; __place(P, n.x, n.z, n.h);
          T.knockOut(P, 'sun'); out.sun = P.koT; __place(P, n.x, n.z, n.h);
          T.knockOut(P, 'fall', null); out.fall = P.koT; __place(P, n.x, n.z, n.h);
          T.knockOut(P, 'pound', H); out.pound = P.koT; __place(P, n.x, n.z, n.h);
          P.lastHit = { by: H, t: T.runT }; T.knockOut(P, 'fall', P.lastHit && T.runT - P.lastHit.t < 3.5 ? P.lastHit.by : null); out.knockedOff = P.koT; out.lastHitCleared = P.lastHit === null;
          __place(P, n.x, n.z, n.h); return out; })()""")
        print('respawn', r)
        # 6. CPU uses it
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; let used = 0, tries = 0, ko = 0;
          for (let t = 0; t < 12; t++) { const pots = T.pots2.filter(q => T.potUp(q) && !q.occ); const p = pots[t % pots.length]; if (!p) break;
            __place(P, p.x + 40, p.z + 40, 0); P.st = 'ko'; P.koT = 1e9; __place(H, p.x, p.z, p.y, t); T.aiReset(H); T.enterPot(H, p); H.slamCD = 0; H.paint = 1;
            T.useSlam(H); tries++; let k = 0, u = false; while (H.air && k < 500) { T.step(0.012); k++; if (H.air && !H.airSling) u = true; }
            if (u) used++; if (H.st === 'ko') { ko++; H.st = 'play'; H.koT = 0; } }
          return { tries, used, ko }; })()""")
        print('cpu burst sling', r)
        await pg.evaluate("__flat()")
        await pg.evaluate("window.__noAssist = true")
        # 2. fling splat: radius and push
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, res = [];
          window.__noStep = false;
          for (const [c, off] of [[1, 2.4], [1, 3.4], [0.6, 2.0], [0.3, 1.6], [1, 6]]) {
            const n = __open(9); if (!n) return 'no open';
            const L = T.flightFor(c, 0).d; __place(P, n.x - L * 0.5, n.z, n.h, Math.PI / 2); P.paint = 1;
            // holy water sits beside the landing point (perpendicular, so the fling never touches it)
            __place(H, n.x - L * 0.5 + L, n.z + off, n.h, 0); __freezeAI(); const h0x = H.x, h0z = H.z;
            T.flingIt(P, c); let k = 0; while (P.air && k < 400) { H.x = h0x; H.z = h0z; H.spd = 0; H.yaw = 0; T.step(0.012); k++; }
            const landX = P.x, landZ = P.z; let kk = 0; const kick = Math.hypot(H.kx, H.kz);
            while ((H.air || Math.hypot(H.kx, H.kz) > 0.1) && kk < 300) { H.spd = 0; T.step(0.012); kk++; }
            res.push({ c, off, landDist: +Math.hypot(landX - n.x - L * 0.5, landZ - n.z).toFixed(2), kick: +kick.toFixed(2), moved: +Math.hypot(H.x - h0x, H.z - h0z).toFixed(2), st: H.st });
          }
          return res; })()""")
        print('splash push', json.dumps(r))
        # 3. direct shove: fling right into the holy water
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; const n = __open(9);
          const L = T.flightFor(0.7, 0).d; __place(P, n.x - L, n.z, n.h, Math.PI / 2); __place(H, n.x + 1.0, n.z, n.h, 0); __freezeAI(); const h0x = H.x;
          T.flingIt(P, 0.7); let k = 0, shoved = false; while (k < 300) { if (!shoved) { H.x = h0x; H.z = n.z; H.spd = 0; } T.step(0.012); if (H.knockT > 0.5) shoved = true; k++; if (!P.air && !H.air && k > 40) break; }
          return { shoved, moved: +Math.hypot(H.x - h0x, H.z - n.z).toFixed(2), st: H.st }; })()""")
        print('shove', r)
        await pg.evaluate("window.__noAssist = false")
        # 3b. aim assist: shots aimed a bit off land closer to the holy water
        for na in [True, False]:
            await pg.evaluate(f"window.__noAssist = {'true' if na else 'false'}")
            r = await pg.evaluate(r'''(() => { const T = __T, P = T.P, H = T.H, res = [];
              for (const [off, c, mis] of [[0.25, 0.75, false], [-0.3, 0.9, false], [0.2, 0.55, false], [0.3, 1, true], [-0.4, 1, true], [0.7, 0.8, false]]) {
                const n = __open(9); __place(H, n.x + 4, n.z, n.h, 0); __freezeAI(); H.immuneT = 0;
                const d0 = 9; __place(P, n.x + 4 - d0, n.z, n.h, Math.PI / 2 + off); P.slamCD = 0; P.paint = 1;
                T.flingIt(P, c); let k = 0, used = false; while ((P.air || P.slam) && k < 400) { H.x = n.x + 4; H.z = n.z; H.spd = 0; H.immuneT = 0.2; if (mis && !used && k === 22) { used = true; T.useSlam(P); } T.step(0.012); k++; }
                res.push({ off, c, mis, miss: +Math.hypot(P.x - H.x, P.z - H.z).toFixed(2) }); if (H.st === 'ko') { H.st = 'play'; H.koT = 0; } if (P.st === 'ko') { P.st = 'play'; P.koT = 0; } }
              return res; })()''')
            print('assist' if not na else 'no assist', json.dumps(r))
        await pg.evaluate("window.__noAssist = false")
        # 4. missile: pound mid-fling, KO at 6 from landing
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, res = [];
          for (const [c, side] of [[1, 6.2], [1, 7.5]]) { const n = __open(9); const L = T.flightFor(c, 0).d;
            __place(P, n.x - L * 0.5, n.z, n.h, Math.PI / 2); P.slamCD = 0;
            __place(H, n.x, n.z + side, n.h, 0); __freezeAI(); H.immuneT = 0;
            T.flingIt(P, c); for (let i = 0; i < 12; i++) T.step(0.012); const ok = T.useSlam(P); const mis = P.missile;
            let k = 0; while ((P.air || P.slam) && k < 300) { H.spd = 0; H.x = n.x; H.z = n.z + side; T.step(0.012); k++; }
            res.push({ side, missile: mis, ok, sep: +Math.hypot(H.x - P.x, H.z - P.z).toFixed(2), out: H.st === 'ko' });
            if (H.st === 'ko') { H.st = 'play'; H.koT = 0; } }
          return res; })()""")
        print('missile', r)
        # 5. burst sling distances
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, res = [];
          for (const [c, when] of [[1, 'apex'], [0.5, 'apex'], [1, 'late'], [0, 'none']]) {
            const p = T.pots2.find(q => T.potUp(q) && !q.occ); if (!p) return 'no pot';
            __place(P, p.x, p.z, p.y, 0); __place(H, p.x + 30, p.z + 30, 0); H.st = 'ko'; H.koT = 1e9; T.enterPot(P, p); P.slamCD = 0; P.paint = 1;
            T.useSlam(P); let k = 0, rel = null, used = false;
            while (P.air && k < 500) { T.step(0.012); k++;
              const go = when === 'apex' ? P.vy < 0.2 : when === 'late' ? P.vy < -6 : false;
              if (go && !used) { used = true; T.startCharge(P); const ch = P.charging; for (let i = 0; i < 20; i++) T.step(0.012); rel = { x: P.x, z: P.z, y: P.y, ch }; const s = T.airShot(P, c, P.yaw); rel.pred = +s.dist.toFixed(2); rel.spd = +s.spd.toFixed(2); T.fling(P, c); }
            }
            res.push({ c, when, charged: rel && rel.ch, pred: rel && rel.pred, spd: rel && rel.spd, flew: rel ? +Math.hypot(P.x - rel.x, P.z - rel.z).toFixed(2) : null, normal: +T.flightFor(Math.max(c, 0.08), 0).d.toFixed(2), slingLeft: P.airSling, st: P.st });
            if (P.st === 'ko') { P.st = 'play'; P.koT = 0; }
          }
          return res; })()""")
        print('burst sling', json.dumps(r))
        print('errors', errs)
        await b.close()
asyncio.run(main())
