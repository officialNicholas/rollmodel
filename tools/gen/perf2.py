import asyncio, json, sys
from collections import defaultdict
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
DPR = float(sys.argv[1]) if len(sys.argv) > 1 else 2
PROF = 'prof' in sys.argv
JS = r"""(m)=>{ const T=__T; window.__noLoop=true; window.__fixedPR=true; T.mode=m; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
  for (let i=0;i<1500;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); }
  const gl = T.renderer.getContext(); const r=T.renderer.info; let ts=0, tv=0, tf=0, tr=0, trs=0, N=40;
  for (let f=0; f<N; f++){ const a=performance.now(); for (let k=0;k<2;k++){ T.aiStep(P,0.008); T.steerIn=P.steer; T.step(0.008);} const b=performance.now(); T.visuals(0.016,0.016); const c=performance.now(); T.flushTrail(); const d=performance.now(); T.renderFrame(); gl.finish(); const e=performance.now(); ts+=b-a; tv+=c-b; tf+=d-c; tr+=e-d; }
  const calls=r.render.calls, tris=r.render.triangles;
  T.renderer.shadowMap.autoUpdate=false; for (let f=0; f<N; f++){ const d=performance.now(); T.renderFrame(); gl.finish(); trs+=performance.now()-d; } T.renderer.shadowMap.autoUpdate=true;
  const callsNS=r.render.calls;
  return { mode: m, arena: T.ARENA, stepMs: +(ts/N).toFixed(2), visMs: +(tv/N).toFixed(2), flushMs: +(tf/N).toFixed(2), renderMs: +(tr/N).toFixed(2), renderNoShadowMs: +(trs/N).toFixed(2), calls, callsNoShadow: callsNS, tris, progs: r.programs.length, geos: r.memory.geometries, tex: r.memory.textures, samples: T.NSv, pr: T.renderer.getPixelRatio() }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=DPR)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        for m in ['duel','trio']:
            print(json.dumps(await pg.evaluate(JS, m)))
        if PROF:
            cdp = await ctx.new_cdp_session(pg); await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 100}); await cdp.send('Profiler.start')
            await pg.evaluate(r"""(()=>{ const T=__T, P=T.P; for (let f=0; f<300; f++){ for (let k=0;k<2;k++){ T.aiStep(P,0.008); T.steerIn=P.steer; T.step(0.008);} T.visuals(0.016,0.016); T.flushTrail(); } })()""")
            prof = (await cdp.send('Profiler.stop'))['profile']
            nodes = {n['id']: n for n in prof['nodes']}; self_t = defaultdict(int)
            for s in prof['samples']: n = nodes[s]; self_t[(n['callFrame']['functionName'] or '(anon)') + ':' + str(n['callFrame']['lineNumber'])] += 1
            tot = sum(self_t.values())
            for k, v in sorted(self_t.items(), key=lambda kv: -kv[1])[:40]: print(f'{v/tot*100:5.1f}%  {k}')
        print(errs[:3]); await b.close()
asyncio.run(main())
