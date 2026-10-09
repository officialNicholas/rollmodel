import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
        print(await pg.evaluate("""(()=>{ const T=__T; const out=[]; for (const c of T.scene.children) if (c.isMesh && c.geometry.type==='SphereGeometry' && c.material.type==='MeshToonMaterial') out.push([c.id, c.geometry.parameters.radius, c.geometry.parameters.widthSegments, c.material.color.getHexString(), c.visible, c.position.toArray().map(v=>+v.toFixed(1)), c.scale.x.toFixed(2)]); return [out.length, out.slice(0,6)]; })()"""))
        await b.close()
asyncio.run(main())
