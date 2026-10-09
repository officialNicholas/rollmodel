import asyncio, json, sys
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SEED = "(() => { let s = 12345; Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for gfx in ['perf', 'hi']:
            ctx = await b.new_context(viewport={'width': 600, 'height': 600}, device_scale_factor=1)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + gfx + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
            r = await pg.evaluate("""(seed) => { const T = __T, P = T.P; window.__noLoop = true; eval(seed);
              T.genWorld(4242, { themes: ['island'] }); T.mapUsed = false; T.start(); window.__noStep = false;
              P.cpu = true; T.aiReset(P); const path = [];
              for (let i = 0; i < 375; i++) { T.steerIn = P.steer || 0; T.step(0.016); T.visuals(0.016, 0.016); T.flushTrail(); if (i % 75 === 0) path.push([P.x, P.z]); }
              path.push([P.x, P.z]);
              const mk = new THREE.MeshBasicMaterial({ color: 0x00ff00, depthTest: false }); const g = new THREE.SphereGeometry(0.6, 8, 6);
              path.forEach(([x, z]) => { const m = new THREE.Mesh(g, mk); m.position.set(x, 3, z); m.renderOrder = 999; T.scene.add(m); });
              document.getElementById('hud').classList.add('off'); document.getElementById('banner').style.display = 'none';
              const cam = new THREE.OrthographicCamera(-30, 30, 30, -30, 0.1, 200); cam.position.set(0, 60, 0); cam.up.set(0, 0, -1); cam.lookAt(0, 0, 0); cam.updateProjectionMatrix();
              const R = T.renderer; R.setRenderTarget(null); R.render(T.scene, cam);
              return path.map(([x, z]) => x.toFixed(1) + ',' + z.toFixed(1)).join(' '); }""", SEED)
            print(gfx, r); await pg.screenshot(path=f'fin/or_{gfx}.png'); print(errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
