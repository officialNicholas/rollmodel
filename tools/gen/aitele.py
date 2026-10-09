import asyncio, json, sys
from playwright.async_api import async_playwright
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
CPU = sys.argv[2] if len(sys.argv) > 2 else 'hard'
N = int(sys.argv[3]) if len(sys.argv) > 3 else 4
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + PAGE
JS = r"""([sd, cpu]) => { let s = sd * 7919 + 1; Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  window.__noLoop = true; const T = __T, P = T.P, H = T.H; T.genWorld(500 + sd); T.mapUsed = false; T.showMenu(); T.start(); T.setAI(cpu); T.aiReset(P);
  const tel = { modes: {}, pivot: 0, charging: 0, flips: 0, airT: 0, stuckReplans: 0, dist: 0, unst: 0, closeT: 0, contacts: 0, hFalls: 0 };
  let lastS = 0, lx = H.x, lz = H.z, wasClose = false, prevStuck = 0;
  for (let i = 0; i < 7500 && T.state === 'play'; i++) {
    T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI(cpu); T.step(0.012);
    if (H.st !== 'play') continue; const ai = H.ai;
    tel.modes[ai.mode] = (tel.modes[ai.mode] || 0) + 0.012;
    if (H.charging) { tel.charging += 0.012; if (!ai.plan && !ai.atShelter && !ai.airAim) tel.pivot += 0.012; }
    if (H.air) tel.airT += 0.012;
    if (Math.abs(H.steer) > 0.5 && Math.sign(H.steer) !== Math.sign(lastS) && Math.abs(lastS) > 0.5) tel.flips++;
    if (Math.abs(H.steer) > 0.5) lastS = H.steer;
    tel.dist += Math.hypot(H.x - lx, H.z - lz); lx = H.x; lz = H.z;
    const close = P.st === 'play' && Math.hypot(P.x - H.x, P.z - H.z) < 6; if (close) tel.closeT += 0.012; if (close && !wasClose) tel.contacts++; wasClose = close;
  }
  tel.hOuts = H.outWhy; tel.pOuts = P.outWhy; tel.hKos = H.kos; tel.pKos = P.kos; tel.hFlats = H.flats; tel.pFlats = P.flats; tel.cov = [+T.teamCov(1).toFixed(1), +T.teamCov(0).toFixed(1)];
  for (const k in tel.modes) tel.modes[k] = +tel.modes[k].toFixed(1); for (const k of ['pivot', 'charging', 'airT', 'dist', 'closeT']) tel[k] = +tel[k].toFixed(1);
  return tel; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        for k in range(N):
            r = await pg.evaluate(JS, [k, CPU])
            print(json.dumps(r))
        print(errs[:3]); await b.close()
asyncio.run(main())
