import asyncio, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 400, 'height': 400}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: ['island'] }); T.mapUsed = false; T.start(); for (let i = 0; i < 20; i++) T.step(0.016);
          const pot = T.pots[0], out = []; pot.g.updateMatrixWorld(true); const box = new THREE.Box3(), c = new THREE.Vector3(), sz = new THREE.Vector3();
          pot.inner.traverse(o => { if (!o.isMesh) return; box.setFromObject(o); box.getCenter(c); box.getSize(sz); const lc = pot.g.worldToLocal(c.clone()); out.push([o.material.type + (o.material === T.scene ? '' : ''), o.geometry.type, lc.toArray().map(v => +v.toFixed(2)), sz.toArray().map(v => +v.toFixed(2)), !!o.geometry.attributes.color]); });
          return out; }""")
        for row in r: print(row)
        await b.close()
asyncio.run(main())
