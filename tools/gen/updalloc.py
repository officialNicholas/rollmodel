# does the slime's per-frame update make garbage? Its state object's mode (fast or dictionary properties), and the heap used across 2000
# calls with a fixed set of options (no collection allowed in between: the growth is what it made)
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--js-flags=--allow-natives-syntax', '--enable-precise-memory-info'])
        ctx = await b.new_context(viewport={'width': 200, 'height': 300}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""() => { const T = __T, I = T.VP.slime, S = T.SLIME; window.__noLoop = true;
          const o = { dt: 1 / 60, spd: 0.8, lean: 0.2, air: 0, inAir: false, vy: 0, height: 0, grav: 15, pos: [0, 0, 0], shove: 0, push: 0, drop: 0, squash: 0.1, rise: 0, wob: 0.6, yaw: 0, aimPitch: 0, speed: 5, rad: 0.34, look: null, leap: false, hover: false, maxBall: 1, brace: 0, wall: 0, flail: 0, curl: 0, glance: 0, grip: 0, dizzy: 0, tired: 0, watch: null };
          for (let i = 0; i < 300; i++) { o.pos[2] += 0.1; o.yaw = Math.sin(i / 30); S.update(I, o); }
          const fast = %HasFastProperties(I.st), fastU = %HasFastProperties(I.U);
          const h0 = performance.memory.usedJSHeapSize; for (let i = 0; i < 2000; i++) { o.pos[2] += 0.1; o.yaw = Math.sin(i / 30); o.flail = i % 200 < 50 ? 1 : 0; S.update(I, o); } const h1 = performance.memory.usedJSHeapSize;
          const keys = Object.keys(I.st).length;
          return { fastSt: fast, fastU, keys, bytesPerCall: (h1 - h0) / 2000 }; }""")
        print(PAGE, json.dumps(r)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
