import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
JS = r"""(m)=>{ const T=__T; window.__noLoop=true; window.__fixedPR=true; Math.random = (()=>{ let s=12345; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })();
  T.mode=m; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(T.P); const P=T.P;
  for (let i=0;i<600;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); }
  const S=[], V=[], F=[]; for (let f=0; f<900; f++){ const a=performance.now(); for (let k=0;k<2;k++){ T.aiStep(P,0.008); T.steerIn=P.steer; T.step(0.008);} const b=performance.now(); T.visuals(0.016,0.016); T.flushTrail(); const c=performance.now(); S.push(b-a); V.push(c-b); F.push(c-a); if (P.st==='ko') { P.st='play'; P.koT=0; } if (T.state!=='play') T.state='play'; }
  const st = A => { const s=A.slice().sort((x,y)=>x-y); return { mean: +(A.reduce((x,y)=>x+y,0)/A.length).toFixed(3), p95: +s[Math.floor(s.length*0.95)].toFixed(2), max: +s[s.length-1].toFixed(2) }; };
  return { mode: m, step: st(S), vis: st(V), frame: st(F) }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        for m in ['duel','trio','trio']:
            print(json.dumps(await pg.evaluate(JS, m)))
        print(errs[:3]); await b.close()
asyncio.run(main())
