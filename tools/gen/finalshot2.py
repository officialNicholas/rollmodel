# the pictures to hand over: the customize screen and a match well under way (phone size, 2x); the match is simulated ahead in big steps
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'island'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'final'; WHAT = sys.argv[3] if len(sys.argv) > 3 else 'look,play'; SEC = float(sys.argv[4]) if len(sys.argv) > 4 else 22
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True, reduced_motion='reduce')
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        await pg.evaluate("(st) => { __T.setStage && __T.setStage(st); __T.freshMap(); __T.showMenu(); }", STAGE)
        await pg.wait_for_timeout(3000)
        if 'look' in WHAT:
            await pg.evaluate("() => { __T.openLook(); }")
            # let the camera settle and the face and hat fade in (game time runs slowly here, so step the visuals along)
            await pg.evaluate("() => { const T = __T; for (let i = 0; i < 90; i++) { T.visuals(1 / 30, 1 / 30); } }")
            await pg.wait_for_timeout(2500)
            await pg.screenshot(path=SP + OUT + '_look.png', timeout=180000)
            await pg.evaluate("() => { __T.closeLook(); }"); await pg.wait_for_timeout(1500)
        if 'play' in WHAT:
            await pg.evaluate("""(sec) => { const T = __T; T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {}; T.setDiff('hard'); T.start(); }""", SEC)
            await pg.wait_for_timeout(1500)
            await pg.evaluate("""(sec) => { const T = __T, dt = 1 / 60, n = Math.round(sec / dt); T.aiReset(T.P);
              for (let i = 0; i < n && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 10 === 0 || i > n - 40) T.visuals(i > n - 40 ? dt : dt * 10, i > n - 40 ? dt : dt * 10); if (i % 20 === 0) T.flushTrail(); }
              T.flushTrail(); window.__aiP = setInterval(() => { if (T.state === 'play') { T.aiStep(T.P, 1/30); T.steerIn = T.P.steer; } }, 33); }""", SEC)
            await pg.wait_for_timeout(2500); await pg.screenshot(path=SP + OUT + '_play1.png', timeout=180000)
            await pg.wait_for_timeout(2500); await pg.screenshot(path=SP + OUT + '_play2.png', timeout=180000)
        print('state', await pg.evaluate("() => ({ state: __T.state, form: __T.VP.slime.form, stage: __T.stageSel, left: __T.matchLeft })"))
        print('errors', errs[:8]); await b.close()
asyncio.run(main())
