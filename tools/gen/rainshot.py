# a live match in the rain (ripples, puddles) and a clear one (shadows), as screenshots
import asyncio, sys
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'island'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'rain'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.evaluate("""([stage]) => { const T = __T; T.mode = 'trio'; T.applyMode(); T.genWorld(4242, { themes: [stage] }); T.mapUsed = false; T.setDiff('hard'); T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {}; T.aiReset(T.P); T.setWx('clear', 999); window.__aiP = setInterval(() => { if (T.state === 'play') { T.aiStep(T.P, 1/30); T.steerIn = T.P.steer; T.matchLeft = 99; } }, 33); }""", [STAGE])
        await pg.wait_for_timeout(25000)
        await pg.screenshot(path=SP + OUT + '_clear.png')
        await pg.evaluate("() => __T.setWx('rain', 999)")
        await pg.wait_for_timeout(12000)
        await pg.screenshot(path=SP + OUT + '_rain.png')
        sc = await pg.evaluate("() => JSON.stringify(__T.shadowCache)")
        print('cache', sc); print('errors', errs[:3]); await b.close()
asyncio.run(main())
