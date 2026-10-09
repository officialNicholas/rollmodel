# the pictures to hand over: the customize screen on a sunny stage, and a match in play (phone size, 2x)
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'island'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'final'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True, reduced_motion='reduce')
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        await pg.evaluate("(st) => { __T.setStage && __T.setStage(st); __T.freshMap(); }", STAGE)
        await pg.wait_for_timeout(4000)
        await pg.evaluate("() => { __T.openLook(); }"); await pg.wait_for_timeout(7000)
        await pg.screenshot(path=SP + OUT + '_look.png', timeout=180000)
        await pg.evaluate("() => { __T.closeLook(); }"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=SP + OUT + '_menu.png', timeout=180000)
        await pg.evaluate("""() => { const T = __T; T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {}; T.setDiff('hard'); T.start();
          window.__aiP = setInterval(() => { if (T.state === 'play') { T.aiStep(T.P, 1/30); T.steerIn = T.P.steer; T.matchLeft = 99; } }, 33); }""")
        await pg.wait_for_timeout(16000); await pg.screenshot(path=SP + OUT + '_play1.png', timeout=180000)
        await pg.wait_for_timeout(9000); await pg.screenshot(path=SP + OUT + '_play2.png', timeout=180000)
        print('state', await pg.evaluate("() => ({ state: __T.state, form: __T.VP.slime.form, stage: __T.stageSel })"))
        print('errors', errs[:8]); await b.close()
asyncio.run(main())
