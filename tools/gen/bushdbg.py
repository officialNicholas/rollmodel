import asyncio, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 400}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'perf', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T, P = T.P, out = []; window.__noLoop = true; T.genWorld(5151, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
          for (let i = 0; i < 160; i++) { T.step(0.016); T.visuals(0.016, 0.016); }
          const bi = T.swayItems.findIndex(q => q.kind === 'bush'), it = T.swayItems[bi];
          for (let k = 0; k < 12; k++) { P.x = it.x - 0.6 + k * 0.12; P.z = it.z; P.y = it.y0; P.yaw = Math.PI / 2; P.spd = 5; P.air = false; T.step(0.016); out.push([+P.x.toFixed(2), +P.z.toFixed(2), +P.y.toFixed(2), +P.spd.toFixed(2), P.st, T.state, +Math.hypot(P.x - it.x, P.z - it.z).toFixed(2)]); T.visuals(0.016, 0.016); out.push(['b', +it.vx.toFixed(2), +it.bx.toFixed(3)]); }
          return out; }""")
        for row in r: print(row)
        await b.close()
asyncio.run(main())
