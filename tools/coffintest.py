"""CPU coffin exits near the edge of the canvas: on fresh canvases, put the CPU in every coffin within 4 units of the edge, facing the edge
(the worst case: it rolled in from the middle), with a full tank so it leaves straight away, and see where the hop out lands.
Also the drained case (the coffin runs dry and pops it out). usage: coffintest.py [canvases]"""
import asyncio, os, json, sys, time
from playwright.async_api import async_playwright
N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
TEST = """((drained) => { const T = __T, D = T.ACTIVE.find(E => E.cpu && E !== T.P) || T.H, out = [], A = T.ARENA;
  const pots = T.pots.filter(p => T.potUp(p) && (A - Math.abs(p.x) < 4 || A - Math.abs(p.z) < 4));
  for (const p of pots) {
    const O = T.ACTIVE.find(E => E !== D); O.x = 0; O.z = 0; O.y = T.surfaceUnder(0, 0, 9); O.st = 'play';
    if (D.pot) { D.pot.occ = null; D.pot = null; } D.st = 'play'; D.air = false; D.slam = false; D.charging = false; D.flatT = 0; D.stunT = 0; D.rocket = null; D.turret = null; D.giantT = 0;
    p.occ = null; p.cool = 0; p.ink = drained ? 0.01 : 1;
    // face the nearest edge
    const ex = A - Math.abs(p.x) < A - Math.abs(p.z) ? Math.sign(p.x) : 0, ez = ex ? 0 : Math.sign(p.z); D.yaw = Math.atan2(ex, ez);
    T.aiReset(D); D.ai.thinkT = 9; D.paint = drained ? 0.5 : 0.97; T.enterPot2(D, p);
    let exitT = -1, exitYaw = null, fell = false, landed = null, t = 0;
    for (let i = 0; i < 360; i++) { T.step(1 / 120); t += 1 / 120;
      if (exitT < 0 && D.st === 'play') { exitT = t; exitYaw = D.yaw; }
      if (exitT >= 0 && !D.air && D.st === 'play' && !landed) landed = [+D.x.toFixed(2), +D.z.toFixed(2)];
      if (D.st === 'ko') { fell = D.reason; break; }
      if (exitT >= 0 && t - exitT > 1.6) break; }
    out.push({ p: [+p.x.toFixed(1), +p.y.toFixed(1), +p.z.toFixed(1)], faceEdge: [ex, ez], exitT: +exitT.toFixed(2), exitYaw: exitYaw === null ? null : +exitYaw.toFixed(2), dirOut: exitYaw === null ? null : [+Math.sin(exitYaw).toFixed(2), +Math.cos(exitYaw).toFixed(2)], landed, fell, now: [+D.x.toFixed(1), +D.z.toFixed(1)] });
  }
  return out; })"""
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754})
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, flings: 99, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + os.environ.get('PAGE', 'pc_perf.html'), timeout=300000)
        for i in range(200):
            if await pg.evaluate("typeof __T === 'object' && !!window.__pf"): break
            await pg.wait_for_timeout(2500)
        await pg.evaluate("(() => { __T.renderer.render = () => {}; })()")
        tot = {'exits': 0, 'falls': 0}
        for k in range(N):
            st = ['studio', 'crypt', 'cathedral', 'manor', 'island', 'blank'][k % 6]
            await pg.evaluate(f"(() => {{ window.__noStep = false; __T.setStage('{st}'); __T.setDiff('medium'); __T.setAI('medium'); __T.start(); }})()")
            t0 = time.time()
            while time.time() - t0 < 240 and await pg.evaluate("__T.state") != 'play': await pg.wait_for_timeout(500)
            await pg.evaluate("(() => { window.__noStep = true; window.__perfAI(); __T.setAI('medium'); })()")
            for drained in (0, 1):
                res = await pg.evaluate(TEST + f"({drained})")
                for r in res:
                    tot['exits'] += 1; tot['falls'] += 1 if r['fell'] == 'fall' else 0
                    print(st, 'drained' if drained else 'full', json.dumps(r))
            await pg.evaluate("window.__noStep = false")
            await pg.evaluate("(() => { try { __T.toMenu(); } catch (e) {} })()"); await pg.wait_for_timeout(3000)
        print('TOTAL', tot, 'errors', errs[:3])
        await b.close()
asyncio.run(main())
