import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(900)
        await pg.evaluate("window.__noLoop = true")
        await pg.click('#lookBtn'); await pg.wait_for_timeout(200)
        r = await pg.evaluate("""(() => { for (let i=0;i<120;i++) __T.visuals(0.016, 0.05); const M = __T.pMouth; const o = { vis: M.visible, smile: M.smile.visible, oh: M.oh.visible, pos: M.position.toArray().map(v=>+v.toFixed(3)), sc: M.smile.scale.x, parent: M.parent === __T.body,
          kids: M.smile.children.map(m => [m.visible, m.material.opacity, m.material.transparent, m.renderOrder, m.material.type]), q: M.quaternion.toArray().map(v=>+v.toFixed(3)),
          eye: __T.eyes[0].e.position.toArray().map(v=>+v.toFixed(3)), cheek: __T.cheeks[0].m.position.toArray().map(v=>+v.toFixed(3)), cheekVis: __T.cheeks[0].m.visible, cheekOp: __T.cheeks[0].m.material.opacity,
          face: __T.pFade.face.map(f => +f.mat.opacity.toFixed(2)) }; return o; })()""")
        print(r, errs[:3]); await b.close()
asyncio.run(main())
