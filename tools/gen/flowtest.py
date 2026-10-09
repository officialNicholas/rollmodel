# the real-time flow through the wipes: menu -> start (wipe, intro, play) -> pause -> quit (wipe to menu) -> start -> time up -> results -> replay (wipe) -> menu
import asyncio, time
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__instant = false; window.__skipIntro = false;')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', mode: 'duo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        st = lambda: pg.evaluate("() => ({ st: __T.state, iris: !document.getElementById('iris').hidden, busy: __T.irisBusy, it: +__T.introT.toFixed(2), menu: !document.getElementById('menu').hidden, end: !document.getElementById('end').hidden, hudOff: document.querySelector('.hud').classList.contains('off') })")
        async def until(cond, tmo=40):
            t0 = time.time()
            while time.time() - t0 < tmo:
                s = await st()
                if eval(cond, {}, {'s': s}): return s, round(time.time() - t0, 2)
                await asyncio.sleep(0.1)
            return await st(), 'TIMEOUT'
        print('boot', await st())
        await pg.evaluate("() => __T.start()"); print('start ->', await st())
        print('intro', await until("s['st'] == 'intro' and not s['busy']"))
        print('play', await until("s['st'] == 'play'", 60))
        await pg.evaluate("() => document.getElementById('pauseBtn') ? document.getElementById('pauseBtn').click() : null"); await asyncio.sleep(0.3); print('pause', await st())
        await pg.evaluate("() => document.getElementById('quitBtn').click()"); await asyncio.sleep(0.1); print('quit ->', await st())
        print('menu', await until("s['st'] == 'menu' and not s['iris']"))
        await pg.evaluate("() => __T.start()"); print('play2', await until("s['st'] == 'play'", 60))
        await pg.evaluate("() => { __T.matchLeft = 0.05; }"); print('dead', await until("s['st'] == 'dead'", 30))
        print('results', await until("s['end']", 40))
        await pg.evaluate("() => document.getElementById('menuBtn').click()"); print('menu2', await until("s['st'] == 'menu' and not s['iris']"))
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
