# the winner screen after a real match on a stage full of ivy and splashes: a few moments of it, as the player sees it
import asyncio, sys, json, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'vic'; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        await pg.evaluate("(st) => { __T.setStage && __T.setStage(st); __T.freshMap(); __T.showMenu(); }", STAGE); await pg.wait_for_timeout(2500)
        await pg.evaluate("""() => { const T = __T; T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {}; T.setDiff('easy'); T.start(); }""")
        for i in range(60):
            st = await pg.evaluate("() => __T.state")
            if st == 'play': break
            if st == 'menu': await pg.evaluate("() => { try { __T.start(); } catch (e) {} }")
            await pg.wait_for_timeout(1000)
        print('state', await pg.evaluate("() => __T.state"))
        await pg.evaluate("""() => { const T = __T, dt = 1 / 60; T.aiReset(T.P); for (let i = 0; i < 60 * 20 && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 10 === 0) T.visuals(dt * 10, dt * 10); if (i % 20 === 0) T.flushTrail(); }
          window.__aiP = setInterval(() => { if (T.state === 'play') { T.aiStep(T.P, 1/30); T.steerIn = T.P.steer; } }, 33); T.matchLeft = 0.05; }""")
        await pg.wait_for_function('!!__T.vic', polling=300, timeout=120000)
        frames = []
        for k in range(6):
            await pg.wait_for_timeout(900)
            png = await pg.screenshot(timeout=120000); frames.append(Image.open(io.BytesIO(png)).convert('RGB'))
            print(k, await pg.evaluate("() => { const V = __T.VP, I = V.slime; return { vic: !!__T.vic, wade: +(V.wade || 0).toFixed(2), bend: +I.st.bend.toFixed(2), ball: +I.st.ball.toFixed(2), tuck: +I.st.tuck.toFixed(2), vis: I.root.visible }; }"))
        w, h = frames[0].size; s = 0.5; tw, th = int(w * s), int(h * s); sheet = Image.new('RGB', (tw * 6, th), 'white')
        for i, f in enumerate(frames): sheet.paste(f.resize((tw, th)), (i * tw, 0))
        sheet.save(SP + OUT + '.png'); frames[2].save(SP + OUT + '_one.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
