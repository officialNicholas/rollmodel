import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("Math.random = (()=>{ let s=777; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ mode: 'duel', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text[:300]))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        r = await pg.evaluate(r"""(()=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); H.ai=null; H.x=P.x+30; T.setWx('clear', 99);
          // the coffins nearest a clear spot, at different levels
          const ps = T.pots.filter(p => p.y === 0 && p.g.visible); const p0 = ps[0]; const others = ps.slice().sort((a,b)=>Math.hypot(a.x-p0.x,a.z-p0.z)-Math.hypot(b.x-p0.x,b.z-p0.z));
          const lv = [0.6, 1, 0.3, 0.85]; others.forEach((p, i) => { p.ink = lv[i % lv.length]; });
          const x = p0.x, z = p0.z - 2.6; P.x=x; P.z=z; P.y=0; P.yaw=0; P.spd=0; P.st='play'; P.paint = 0.9;
          for (let i=0;i<60;i++) { T.step(0.012); P.spd=0; P.x=x; P.z=z; P.yaw=0; others.forEach((p, k) => { p.ink = lv[k % lv.length]; }); T.visuals(0.016, 0.05); } T.renderFrame(); return others.slice(0,4).map(p=>[p.x.toFixed(1), p.z.toFixed(1), p.ink]); })()""")
        print(r); await pg.wait_for_timeout(6000); await pg.evaluate("(()=>{ for (let i=0;i<5;i++) __T.visuals(0.016,0.016); __T.renderFrame(); })()"); await pg.screenshot(path='ui/ringfill.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
