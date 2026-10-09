import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SIM = r"""(([sd]) => { Math.random = (() => { let s = sd; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
  const T = __T, P = T.P, H = T.H; T.start(); T.setAI('hard'); T.aiReset(P); const ev = []; let spawnAt = -1, exitAt = -1, wasSt = P.st;
  for (let i = 0; i < 7500 && T.state === 'play'; i++) {
    T.setAI('medium'); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI('hard'); T.step(0.012);
    if (wasSt === 'ko' && P.st !== 'ko') spawnAt = T.runT;
    if (wasSt === 'hide' && P.st === 'play' && spawnAt >= 0 && exitAt < 0) exitAt = T.runT;
    if (wasSt !== 'ko' && P.st === 'ko' && spawnAt >= 0) { ev.push({ sinceSpawn: +(T.runT - spawnAt).toFixed(2), sinceExit: exitAt >= 0 ? +(T.runT - exitAt).toFixed(2) : null, why: P.reason }); spawnAt = -1; exitAt = -1; }
    wasSt = P.st;
  }
  return ev; })"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        allev = []
        for k in range(6):
            pg = await b.new_page(viewport={'width':390,'height':844})
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
            await pg.evaluate(f"(()=>{{ __T.genWorld({7000 + k * 131}); __T.mapUsed=false; __T.setDiff('hard'); __T.showMenu(); window.__noLoop=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === 'function') __T.AU[k] = () => {{}}; }})()")
            ev = await pg.evaluate(SIM, [99 + k * 31]); allev += ev; print(k, ev, flush=True); await pg.close()
        await b.close()
asyncio.run(main())
