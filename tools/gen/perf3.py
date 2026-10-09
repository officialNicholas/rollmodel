import asyncio, json, sys
from collections import defaultdict
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
MODE = sys.argv[1] if len(sys.argv) > 1 else 'trio'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':200,'height':400}, device_scale_factor=1)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        info = await pg.evaluate(r"""(m)=>{ const T=__T; window.__noLoop=true; window.__fixedPR=true; T.mode=m; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
          for (let i=0;i<1500;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); }
          let n=0, vis=0, meshes=0; T.scene.traverse(o => { n++; if (o.visible) vis++; if (o.isMesh) meshes++; }); return { objects: n, visibleFlag: vis, meshes }; }""", MODE)
        print(info)
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 100}); await cdp.send('Profiler.start')
        t = await pg.evaluate(r"""(()=>{ const T=__T, P=T.P; const a=performance.now(); for (let f=0; f<200; f++){ for (let k=0;k<2;k++){ T.aiStep(P,0.008); T.steerIn=P.steer; T.step(0.008);} T.visuals(0.016,0.016); T.flushTrail(); T.renderFrame(); } return (performance.now()-a)/200; })()""")
        prof = (await cdp.send('Profiler.stop'))['profile']
        print('ms/frame', t)
        nodes = {n['id']: n for n in prof['nodes']}; self_t = defaultdict(int)
        parent = {}
        for n in prof['nodes']:
            for c in n.get('children', []): parent[c] = n['id']
        for s in prof['samples']: n = nodes[s]; self_t[(n['callFrame']['functionName'] or '(anon)') + ':' + str(n['callFrame']['lineNumber']) + ':' + n['callFrame']['url'][-12:]] += 1
        tot = sum(self_t.values())
        for k, v in sorted(self_t.items(), key=lambda kv: -kv[1])[:45]: print(f'{v/tot*100:5.1f}%  {k}')
        # inclusive time for top-level game functions
        incl = defaultdict(int)
        for s in prof['samples']:
            seen = set(); nid = s
            while nid is not None:
                n = nodes[nid]; key = n['callFrame']['functionName']
                if key and key not in seen: incl[key] += 1; seen.add(key)
                nid = parent.get(nid)
        print('--- inclusive')
        for k in ['step', 'visuals', 'renderFrame', 'flushTrail', 'aiStep', 'aiThink', 'dijkstra', 'stepBlob', 'render', 'updateMatrixWorld', 'renderObjects', 'projectObject', 'foePointer', 'renderBufferDirect', 'setProgram', 'render$1']:
            if k in incl: print(f'{incl[k]/tot*100:5.1f}%  {k}')
        print(errs[:3]); await b.close()
asyncio.run(main())
