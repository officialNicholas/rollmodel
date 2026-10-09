import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', color: 'purple', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(800)
        await pg.evaluate("window.__noLoop = true;"); await pg.click('#lookBtn')
        for n in [40, 10, 10]:
            r = await pg.evaluate(f"""(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.016, 0.016); const T=__T, st = T.scene.children.find(o => o.type === 'Group' && o.children.length === 2 && o.children[0].geometry && o.children[0].geometry.type === 'CylinderGeometry');
              return {{ cam: T.camera.position.toArray().map(v => +v.toFixed(2)), drop: T.P ? [+T.P.x.toFixed(2), +T.P.z.toFixed(2)] : 0, strand: st ? {{ vis: st.visible, pos: st.position.toArray().map(v => +v.toFixed(2)), sc: st.scale.toArray().map(v => +v.toFixed(3)) }} : 'none' }}; }})()""")
            print(r)
        await b.close()
asyncio.run(main())
