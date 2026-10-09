import asyncio, json, sys
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SEED = "(() => { let s = 12345; Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
        await pg.evaluate("""(seed) => { const T = __T, P = T.P; window.__noLoop = true; eval(seed);
              T.genWorld(4242, { themes: ['island'] }); T.mapUsed = false; T.start(); window.__noStep = false;
              P.cpu = true; T.aiReset(P); for (let i = 0; i < 375; i++) { T.steerIn = P.steer || 0; T.step(0.016); T.visuals(0.016, 0.016); T.flushTrail(); }
              document.getElementById('banner').style.display = 'none'; document.getElementById('hud').classList.add('off'); T.renderFrame(); }""", SEED)
        await pg.screenshot(path='fin/b2_0normal.png')
        await pg.evaluate("(() => { const T = __T, c = T.camera; c.position.set(30, 16, 12); c.lookAt(18, 0, -8); T.renderFrame(); })()")
        await pg.screenshot(path='fin/b2_3trailview.png')
        await pg.evaluate("(() => { const T = __T, c = T.camera; c.position.set(30, 16, 12); c.lookAt(18, 0, -8); const keep = new Set(); for (let q = T.paintMesh; q; q = q.parent) keep.add(q); const hid = []; T.scene.children.forEach(ch => { if (!keep.has(ch) && ch.visible) { ch.visible = false; hid.push(ch); } }); const bg = T.scene.background; T.scene.background = new THREE.Color(0x202020); T.renderer.setRenderTarget(null); T.renderer.render(T.scene, c); hid.forEach(ch => ch.visible = true); T.scene.background = bg; })()")
        await pg.screenshot(path='fin/b2_4trailonly.png')
        # only the paint, nothing else
        await pg.evaluate("""(() => { const T = __T, keep = new Set(); for (let q = T.paintMesh; q; q = q.parent) keep.add(q); const hid = [];
            T.scene.children.forEach(c => { if (!keep.has(c) && c.visible) { c.visible = false; hid.push(c); } }); window.__hid = hid;
            const bg = T.scene.background; window.__bg = bg; T.scene.background = new THREE.Color(0x202020); T.renderer.setRenderTarget(null); T.renderer.render(T.scene, T.camera); })()""")
        await pg.screenshot(path='fin/b2_1paintonly.png')
        await pg.evaluate("(() => { __hid.forEach(c => c.visible = true); __T.scene.background = __bg; })()")
        # flat magenta paint inside the full scene
        await pg.evaluate("""(() => { const T = __T; window.__pm = T.paintMesh.material; T.paintMesh.material = new THREE.MeshBasicMaterial({ color: 0xff00ff, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }); T.renderFrame(); })()""")
        await pg.screenshot(path='fin/b2_2magenta.png')
        await pg.evaluate("(() => { __T.paintMesh.material = __pm; })()")
        info = await pg.evaluate("""(() => { const T = __T, m = T.paintMesh.material; const g = T.paintMesh.geometry; return { defines: m.defines, lights: m.lights, fog: m.fog, side: m.side, vis: T.paintMesh.visible, layers: T.paintMesh.layers.mask, camLayers: T.camera.layers.mask, dr: g.drawRange, bs: g.boundingSphere ? [g.boundingSphere.center.toArray(), g.boundingSphere.radius] : null, fc: T.paintMesh.frustumCulled, prog: !!(T.renderer.properties.get(m).program) }; })()""")
        print(json.dumps(info))
        print(errs[:5]); await b.close()
asyncio.run(main())
