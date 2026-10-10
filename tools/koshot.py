import asyncio, json, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
# knocked out by the rival: the flood, the badge, the parting, the comeback
async def run(w, h, tag):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type == 'error' and 'Failed to load' not in m.text and errs.append(m.text[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn'); await pg.wait_for_timeout(400)
        await pg.wait_for_function("__T.state === 'play'", timeout=40000); await pg.wait_for_function("!__T.P.air", timeout=90000, polling=300); await pg.wait_for_timeout(500)
        await pg.evaluate("__T.matchLeft = 400; __T.knockOut(__T.P, 'pound', __T.H);")
        shots = [(0.25, 'flood'), (0.9, 'badge'), (3.2, 'count')]
        for at, name in shots:
            await pg.wait_for_function("!document.getElementById('kof').hidden && __T.P.st === 'ko' && (%f - (__T.RESPAWN_T || 3.5) + __T.P.koT) <= 0" % at, timeout=90000, polling=200)
            print(tag, name, await pg.evaluate("[__T.P.st, +__T.P.koT.toFixed(2), document.getElementById('kof').className, document.getElementById('kofSmall').textContent, document.getElementById('kofBy').textContent, document.getElementById('kofN').textContent]"))
            await pg.screenshot(path=f'{WS}/ui/ko_{tag}_{name}.png')
        await pg.wait_for_function("document.getElementById('kof').classList.contains('out')", timeout=90000, polling=100); await pg.wait_for_timeout(250)
        await pg.screenshot(path=f'{WS}/ui/ko_{tag}_part.png'); print(tag, 'part', await pg.evaluate("[__T.P.st, document.getElementById('kof').className]"))
        await pg.wait_for_function("document.getElementById('kof').hidden", timeout=60000, polling=200); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{WS}/ui/ko_{tag}_back.png'); print(tag, 'back', await pg.evaluate("[__T.P.st, !!__T.P.pot]"))
        print(tag, 'errors', errs[:4]); await b.close()
for k in (sys.argv[1:] or ['port']): asyncio.run(run(*{'port': (390, 780, 'port'), 'land': (844, 390, 'land')}[k]))
