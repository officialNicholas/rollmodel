import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
JS = """(sd)=>{ __T.genWorld(404); __T.mapUsed=false; __T.showMenu(); __T.clock=0; window.__rc=0; Math.random = (()=>{ let s = sd; return () => { window.__rc++; if (window.__trace) window.__st.push((new Error().stack.split(String.fromCharCode(10))[2]||'').trim().slice(0,90)); s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })(); __T.start(); const T=__T, P=T.P, H=T.H; T.setAI('hard'); P.st='ko'; P.koT=1e9; const out=[];
  out.push(['init', T.wxLeft.toFixed(3), H.x, H.z, H.yaw.toFixed(3), JSON.stringify(T.MOVERS.map(m=>m.cx.toFixed(2)))]);
  window.__st=[]; for (let i=0;i<3725 && T.state==="play";i++){ window.__trace = i===3720; T.step(0.012); out.push([i, window.__rc, H.x.toFixed(4), H.z.toFixed(4), H.yaw.toFixed(4), H.spd.toFixed(4), H.ai.mode, H.paint.toFixed(4), H.ai.tgt, T.wx, H.slowK.toFixed(4), H.ai.thinkT.toFixed(4), T.hard]); } return [window.__st]; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_timeout(1500)
        await pg.evaluate('window.__noLoop=true; window.__fixedPR=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === "function") __T.AU[k] = () => {};')
        a = await pg.evaluate(JS, 99); b2 = await pg.evaluate(JS, 99)
        A=a[0]; B=b2[0]; print(len(A), len(B))
        from collections import Counter
        print('only run1', Counter(A)-Counter(B)); print('only run2', Counter(B)-Counter(A))
        await b.close()
asyncio.run(main())
