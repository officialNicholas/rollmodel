# Which materials make three.js re-derive their shader every frame (a costly lookup that churns memory): count calls to each
# material's customProgramCacheKey (three calls it on every program lookup) over steady play frames
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 120, 'height': 260}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(SP + PAGE + '.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.genWorld(77, { themes: ['cathedral'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
          for (let i = 0; i < 200; i++) { T.step(0.016); T.visuals(0.016, 0.016); if (i % 5 === 0) T.renderFrame(); }
          const mats = new Map(); T.scene.traverse(o => { const ms = Array.isArray(o.material) ? o.material : o.material ? [o.material] : []; for (const m of ms) { let e = mats.get(m); if (!e) { e = { m, n: 0, users: new Set() }; mats.set(m, e); const f = m.customProgramCacheKey; m.customProgramCacheKey = function () { e.n++; return f.call(this); }; } e.users.add((o.isInstancedMesh ? 'I:' : o.isPoints ? 'P:' : o.isSprite ? 'S:' : 'M:') + (o.name || o.geometry && o.geometry.type || '?')); } });
          const N = 10; for (let i = 0; i < N; i++) { T.step(0.016); T.visuals(0.016, 0.016); T.renderFrame(); }
          const out = []; for (const e of mats.values()) if (e.n) out.push([+(e.n / N).toFixed(1), e.m.type, e.m.name || '', e.m.transparent, [...e.users].slice(0, 6).join(' ')]);
          out.sort((a, b) => b[0] - a[0]); return out.slice(0, 30); }""")
        for row in r: print(row)
        await b.close()
asyncio.run(main())
