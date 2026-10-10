import asyncio, json, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
# the stage reveal before the count: the sweep with the name up, then the count
async def run(w, h, tag):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__skipIntro = false; window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type == 'error' and 'Failed to load' not in m.text and errs.append(m.text[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn'); await pg.wait_for_timeout(400)
        await pg.wait_for_function("__T.state === 'reveal'", timeout=90000, polling=200)
        for at, name in [(0.35, 'a'), (1.4, 'b'), (2.45, 'c')]:
            await pg.wait_for_function("__T.state !== 'reveal' || __T.revealT >= %f" % at, timeout=90000, polling=100)
            print(tag, name, await pg.evaluate("[__T.state, +__T.revealT.toFixed(2), document.getElementById('reveal').className, document.getElementById('rvName').textContent, document.getElementById('rvSub').textContent]"))
            await pg.screenshot(path=f'{WS}/ui/reveal_{tag}_{name}.png')
        await pg.wait_for_function("__T.state === 'intro' && __T.introT > 0.7", timeout=90000, polling=200); await pg.screenshot(path=f'{WS}/ui/reveal_{tag}_count.png')
        print(tag, 'count', await pg.evaluate("[__T.state, document.getElementById('countN').textContent, document.getElementById('reveal').hidden]"))
        print(tag, 'errors', errs[:4]); await b.close()
for k in (sys.argv[1:] or ['port', 'land']): asyncio.run(run(*{'port': (390, 780, 'port'), 'land': (844, 390, 'land')}[k]))
