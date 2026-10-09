import asyncio, sys, json, statistics as st
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
# usage: bench.py solo hard 6   |   bench.py duel hard hardOld 6   (first is the holy water CPU, second drives the player)
SIM = r"""
(([mode, cpu, bot, sd]) => {
  __T.clock = 0; Math.random = (() => { let s = sd; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })(); __T.start();
  const T = __T, P = T.P, H = T.H; T.setAI(cpu); if (mode === 'duel') T.aiReset(P); else { P.st = 'ko'; P.koT = 1e9; }
  const modes = {}; let i = 0;
  for (; i < 9000 && T.state === 'play'; i++) {
    if (mode === 'duel') { T.setAI(bot); T.aiStep(P, 0.012); T.steerIn = P.steer; T.setAI(cpu); }
    T.step(0.012);
    if (H.ai) modes[H.ai.mode] = (modes[H.ai.mode] || 0) + 1;
  }
  return { you: T.teamCov(0), cpu: T.teamCov(1), H: { kos: H.kos, outs: H.outWhy, flats: H.flats, slams: H.slams }, P: { kos: P.kos, outs: P.outWhy, flats: P.flats, slams: P.slams }, modes, gen: { ...T.GEN }, steps: i };
})
"""
async def main():
    mode = sys.argv[1]
    cpu = sys.argv[2]; bot = sys.argv[3] if mode == 'duel' else cpu; n = int(sys.argv[-1])
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        errs=[]; res = []
        k0 = int(sys.argv[-2]) if len(sys.argv) > 4 and sys.argv[-2].isdigit() else 0
        for k in range(k0, k0 + n):
            for attempt in range(3):
                pg = await b.new_page(viewport={'width':390,'height':844})
                pg.on('pageerror', lambda e: errs.append(str(e)))
                try:
                    await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); break
                except Exception as e:
                    print('   (page load retry)', flush=True); await pg.close()
            await pg.evaluate(f"(()=>{{ __T.genWorld({5000 + k * 131}); __T.mapUsed=false; __T.setDiff('{cpu if cpu in ('easy','medium','hard') else 'hard'}'); __T.showMenu(); }})()")
            await pg.evaluate("__T.AI_LV.hardNM = Object.assign({}, __T.AI_LV.hard, { model: 0 }); window.__noLoop=true; window.__fixedPR=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === 'function') __T.AU[k] = () => {};")
            r = await pg.evaluate(SIM, [mode, cpu, bot, 1234 + k * 977])
            res.append(r)
            hs = sum(r['modes'].values()) or 1; print(f"  hunt {100*r['modes'].get('hunt',0)/hs:.0f}% map {r['gen']['sym']}/{r['gen']['arch']}: cpu {r['cpu']:.1f}%  you {r['you']:.1f}%  H{r['H']}  P{r['P']}", flush=True)
            await pg.close()
        cw = sum(1 for r in res if round(r['cpu']) > round(r['you'])); bw = sum(1 for r in res if round(r['you']) > round(r['cpu']))
        print(f"{mode} {cpu} vs {bot}: cpu avg {st.mean(r['cpu'] for r in res):.1f}  you avg {st.mean(r['you'] for r in res):.1f}  cpu wins {cw} bot wins {bw} draws {n-cw-bw}")
        print('errors', errs[:3])
        await b.close()
asyncio.run(main())
