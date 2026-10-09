import asyncio, json, sys
from collections import defaultdict
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
MODE = sys.argv[1] if len(sys.argv) > 1 else 'trio'
FR = int(sys.argv[2]) if len(sys.argv) > 2 else 600
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        await pg.evaluate(r"""(m)=>{ const T=__T; window.__noLoop=true; window.__fixedPR=true; T.mode=m; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
          for (let i=0;i<1200;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); } }""", MODE)
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 50}); await cdp.send('Profiler.start')
        t = await pg.evaluate("""(FR)=>{ const T=__T, P=T.P; let ts=0, tv=0; for (let f=0; f<FR; f++){ const a=performance.now(); for (let k=0;k<2;k++){ T.aiStep(P,0.008); T.steerIn=P.steer; T.step(0.008);} const b=performance.now(); T.visuals(0.016,0.016); T.flushTrail(); tv+=performance.now()-b; ts+=b-a; if (T.state!=='play' || P.st==='ko') { P.st='play'; P.koT=0; } } return [ts/FR, tv/FR]; }""", FR)
        prof = (await cdp.send('Profiler.stop'))['profile']
        print('step/vis ms', t)
        nodes = {n['id']: n for n in prof['nodes']}; self_t = defaultdict(int); lines = defaultdict(lambda: defaultdict(int))
        for n in prof['nodes']:
            fn = n['callFrame']['functionName'] or '(anon)'
            for pt in n.get('positionTicks', []): lines[fn][pt['line']] += pt['ticks']
        for s in prof['samples']: n = nodes[s]; self_t[(n['callFrame']['functionName'] or '(anon)')] += 1
        tot = sum(self_t.values())
        for k, v in sorted(self_t.items(), key=lambda kv: -kv[1])[:30]:
            ls = sorted(lines[k].items(), key=lambda kv: -kv[1])[:(14 if k in ('aiThink','aiStep','(anon)') else 5)]
            print(f'{v/tot*100:5.1f}%  {k}   ' + ' '.join(f'L{l}:{c}' for l, c in ls))
        print(errs[:3]); await b.close()
asyncio.run(main())
