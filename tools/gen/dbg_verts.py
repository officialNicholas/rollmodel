import asyncio, json, sys
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SEED = "(() => { let s = 12345; Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for gfx in ['perf', 'hi']:
            ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + gfx + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
            r = await pg.evaluate("""(seed) => { const T = __T, P = T.P; window.__noLoop = true; eval(seed);
              T.genWorld(4242, { themes: ['island'] }); T.mapUsed = false; T.start(); window.__noStep = false;
              P.cpu = true; T.aiReset(P); for (let i = 0; i < 375; i++) { T.steerIn = P.steer || 0; T.step(0.016); T.visuals(0.016, 0.016); T.flushTrail(); }
              const g = T.paintMesh.geometry, pos = g.attributes.position.array, tm = g.attributes.team.array, ed = g.attributes.edge.array, bi = g.attributes.birth.array, n = g.drawRange.count;
              let red = 0, nan = 0, ymin = 1e9, ymax = -1e9, edMin = 9, edMax = -9, sample = [];
              for (let v = 0; v < n; v++) { if (tm[v] !== 0) continue; red++; const x = pos[v*3], y = pos[v*3+1], z = pos[v*3+2]; if (!isFinite(x) || !isFinite(y) || !isFinite(z)) { nan++; continue; } ymin = Math.min(ymin, y); ymax = Math.max(ymax, y); edMin = Math.min(edMin, ed[v]); edMax = Math.max(edMax, ed[v]); if (v % 600 === 0) sample.push([x.toFixed(2), y.toFixed(3), z.toFixed(2), ed[v], bi[v].toFixed(2)]); }
              return { n, red, nan, ymin, ymax, edMin, edMax, sample, P: [P.x.toFixed(1), P.y.toFixed(2), P.z.toFixed(1)] }; }""", SEED)
            print(gfx, json.dumps(r))
            await ctx.close()
        await b.close()
asyncio.run(main())
