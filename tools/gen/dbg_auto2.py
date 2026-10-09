import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'perf', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
        r = await pg.evaluate("""() => { const T = __T, P = T.P, H = T.H; window.__noLoop = true; const path = [];
          T.genWorld(4242, { themes: ['island'] }); T.mapUsed = false; T.start(); window.__noStep = false;
          P.cpu = true; T.aiReset(P);
          for (let i = 0; i < 640; i++) { T.steerIn = P.steer || 0; T.step(0.016); if (i % 3 === 2) { T.visuals(0.048, 0.048); T.flushTrail(); } if (i % 40 === 0) path.push([+P.x.toFixed(1), +P.z.toFixed(1)]); }
          const g = T.paintMesh.geometry, pos = g.attributes.position.array, tm = g.attributes.team.array, n = g.drawRange.count;
          const cells = {}; let red = 0;
          for (let v = 0; v < n; v++) { if (tm[v] !== 0) continue; red++; const k = Math.round(pos[v*3] / 4) * 4 + ',' + Math.round(pos[v*3+2] / 4) * 4; cells[k] = (cells[k] || 0) + 1; }
          return { n, red, drawCount: g.drawRange.count, path, cells, meshVis: T.paintMesh.visible, parent: T.paintMesh.parent && T.paintMesh.parent.type, pmPos: T.paintMesh.position.toArray(), pmScale: T.paintMesh.scale.toArray(), fc: T.paintMesh.frustumCulled }; }""")
        print(json.dumps(r)[:3000])
        print(errs[:3]); await b.close()
asyncio.run(main())
