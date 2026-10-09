import asyncio, sys
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', look: { eyes: 'round', head: 'hat', back: null, mouth: null }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.evaluate("() => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); for (let i = 0; i < 150; i++) { T.step(0.016); T.visuals(0.016, 0.016); } }")
        await pg.evaluate("() => { const T = __T; T.renderFrame(); }"); await pg.screenshot(path='st/dbg0.png')
        info = await pg.evaluate("() => { const T = __T, P = T.P; const near = []; T.scene.traverse(o => { if (o.isMesh && o.visible && o.geometry && o.geometry.boundingSphere !== undefined) { const w = new THREE.Vector3(); o.getWorldPosition(w); if (Math.hypot(w.x - P.x, w.z - P.z) < 2.5 && w.y < 3 && w.y > -1) near.push((o.name || o.geometry.type) + ' ' + (o.material && o.material.color ? o.material.color.getHexString() : '') + ' y' + w.y.toFixed(2)); } }); return { P: [P.x, P.y, P.z].map(v => +v.toFixed(2)), near: near.slice(0, 30) }; }")
        print(info)
        await pg.evaluate("() => { const T = __T; T.startRocket(T.P); for (let i = 0; i < 20; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.rocketMark.m.visible = false; T.rocketMark.fill.visible = false; T.renderFrame(); }"); await pg.screenshot(path='st/dbg1.png')
        print(errs[:3]); await b.close()
asyncio.run(main())
