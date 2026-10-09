# the winner screen when the match ends mid-turret (and mid-rocket for the CPU): both should be their plain selves
import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Sprinkle', gfx: 'hi', mode: 'duel', color: 'pink', owned: ['lashes'], look: { lash: 'lashes' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('blank'); T.genWorld(77, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          for (let i = 0; i < 60; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          for (let i = 0; i < 16; i++) { const P = T.P; T.addSplat(P.x + (i % 4 - 1.5) * 3, 0, P.z + ((i / 4) | 0) * 3 - 4, 0, 1.6, T.dryClock, false, false, 0); }
          T.startTurret(T.P); for (let i = 0; i < 40; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          const form0 = T.VP.slime.form; for (let k = 0; k < 4 && T.state === 'play'; k++) { T.matchLeft = 0.01; for (let i = 0; i < 3; i++) T.step(1 / 60); }
          return { form0, state: T.state, turret: !!T.P.turret }; }""")
        print('before', json.dumps(r)); await pg.wait_for_timeout(1700)
        r = await pg.evaluate("() => { const T = __T; for (let i = 0; i < 64; i++) T.visuals(1 / 60, 1 / 60); T.renderFrame(); return { vic: !!T.vic, form: T.VP.slime.form, next: T.VP.slime.st.formNext, turret: T.P.turret }; }")
        print('victory', json.dumps(r)); await pg.screenshot(path=SP + 'st/vic_tur.png'); print('errors', errs[:4]); await b.close()
asyncio.run(main())
