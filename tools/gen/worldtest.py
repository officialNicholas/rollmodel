import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and 'ERR_' not in m.text and errs.append(m.text))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(800)
        info = lambda: pg.evaluate("({ page: document.getElementById('menu').dataset.page, home: !document.getElementById('mHome').hidden, world: !document.getElementById('mWorld').hidden, stage: [...document.querySelectorAll('.world')].filter(b => b.getAttribute('aria-pressed') === 'true').map(b => b.dataset.s).join(), go: document.getElementById('startBtn').innerText.replace(/\\n/g, ' / '), disabled: document.getElementById('startBtn').disabled, shuffle: !document.getElementById('shuffleBtn').hidden, dots: [...document.querySelectorAll('#gDots i')].map(i => i.classList.contains('on') ? 1 : 0).join(''), focus: document.activeElement && document.activeElement.id, state: __T.state, key: __T.GEN.key })")
        # keyboard: Enter opens the gallery, arrows walk it, Escape steps back
        await pg.keyboard.press('Enter'); await pg.wait_for_timeout(400); print('enter', await info())
        await pg.keyboard.press('ArrowLeft'); await pg.wait_for_timeout(700); print('left', await info())
        await pg.keyboard.press('ArrowRight'); await pg.wait_for_timeout(700); print('right', await info())
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300); print('esc', await info())
        # swipe: centre each painting by scrolling, let it settle
        await pg.click('#homePlay'); await pg.wait_for_timeout(400)
        for i, nm in [(0, 'studio'), (2, 'locked'), (1, 'season')]:
            await pg.evaluate(f"(() => {{ const g = document.getElementById('stagePick'), b = g.children[{i}]; g.scrollLeft = b.offsetLeft + b.offsetWidth / 2 - g.clientWidth / 2; }})()")
            await pg.wait_for_timeout(700); print('swipe', nm, await info())
            if nm == 'locked':
                await pg.screenshot(path='ui/world_locked.png')
                await pg.evaluate("document.querySelector('.world.locked').click()"); await pg.wait_for_timeout(120); print('locked tap', await pg.evaluate("document.querySelector('.world.locked').className"))
        # tap the studio card, then play a quick match there and check its plaque
        await pg.click('.world[data-s="standard"]'); await pg.wait_for_timeout(800); print('tap studio', await info())
        await pg.click('#startBtn'); await pg.wait_for_function("__T.state === 'play'", polling=100, timeout=20000); await pg.wait_for_timeout(800)
        print('playing std', await pg.evaluate("[__T.GEN.std, __T.GEN.key]"))
        await pg.evaluate("(()=>{ const T=__T, P=T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; T.addSplat(x, Math.max(0, T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, T.clock, false, true, 0); } T.flushTrail(); T.matchLeft = 0.05; })()")
        await pg.wait_for_function("__T.state === 'dead'", polling=200, timeout=60000)
        print('stored', await pg.evaluate("JSON.parse(localStorage.getItem('paint-world-red.v1')).world"))
        await pg.evaluate("__T.endVictory && __T.vic && __T.endVictory()"); await pg.wait_for_function("!document.getElementById('end').hidden", polling=200, timeout=60000)
        await pg.click('#menuBtn'); await pg.wait_for_timeout(600); print('menu', await info())
        await pg.click('#homePlay'); await pg.wait_for_timeout(500)
        print('plaques', await pg.evaluate("[...document.querySelectorAll('.plaque')].map(p => p.innerText.replace(/\\n/g, ' | '))"))
        await pg.screenshot(path='ui/world_after.png')
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
