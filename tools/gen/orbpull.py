# roll up beside the orb with an empty tank and no jump: it should be drawn in and you go giant; out of reach, nothing happens
import asyncio, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'perf', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T, P = T.P, O = T.orb, out = {}; window.__noLoop = true; T.genWorld(77, { themes: ['cathedral'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
          for (let i = 0; i < 200; i++) T.step(0.016);
          const trial = (dist, frames) => { T.orbSpawn(); for (let i = 0; i < 40; i++) T.step(0.016); if (!O.on) return 'no orb';
            const ox = O.x, oz = O.z, gy = T.surfaceUnder(ox, oz, O.base + 0.5, true); let res = null;
            for (let i = 0; i < frames; i++) { P.x = ox + dist; P.z = oz; P.y = gy; P.vy = 0; P.air = false; P.paint = 0; P.giantT = P.giantT || 0; T.step(0.016); if (P.giantT > 0) { res = i; break; } }
            const r = { took: res, pull: +(O.pull || 0).toFixed(2), giant: P.giantT > 0 }; P.giantT = 0; if (O.on) { O.on = false; O.g.visible = false; } return r; };
          out.near = trial(1.9, 90); out.far = trial(3.6, 90); return out; }""")
        print(json.dumps(r), errs[:3]); await b.close()
asyncio.run(main())
