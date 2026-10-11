"""v205: the pound button recharging, ready and locked, and the item button: crops, and the styles that broke on iPhones (none left)"""
import asyncio, json
from PIL import Image
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
STY = """(() => { const o = {}; for (const sel of ['#slamBtn', '#slamBtn .sdisc', '#slamBtn svg', '#itemBtn', '#itemBtn .sdisc', '#itemBtn svg']) { const e = document.querySelector(sel); if (!e) continue; const c = getComputedStyle(e);
  o[sel] = [c.filter, c.webkitMaskImage || c.maskImage, c.backgroundBlendMode, c.backgroundImage.slice(0, 60), e.className && e.className.baseVal === undefined ? e.className : '']; } return o; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, drops: 50, runs: 5, flings: 50, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
        await pg.evaluate("document.getElementById('homePlay').click()")
        await pg.wait_for_function("__T.state === 'play'", timeout=300000); await pg.wait_for_timeout(2500)
        crops = []
        async def shot(tag):
            await pg.screenshot(path=f'{WS}/ui/bs_{tag}.png'); im = Image.open(f'{WS}/ui/bs_{tag}.png'); crops.append((tag, im.crop((0, 1080, 860, 1508))))
        print('recharging', json.dumps(await pg.evaluate(STY))); await shot('off')
        await pg.evaluate("__T.P.slamCD = 0; __T.P.paint = 1"); await pg.wait_for_function("document.getElementById('slamBtn').classList.contains('ready')", timeout=30000); await pg.wait_for_timeout(700)
        print('ready', json.dumps(await pg.evaluate(STY))); await shot('ready')
        await pg.evaluate("__T.P.held = 'roller'"); await pg.wait_for_function("!document.getElementById('itemBtn').hidden", timeout=30000); await pg.wait_for_timeout(700)
        print('item', json.dumps(await pg.evaluate(STY))); await shot('item')
        await pg.evaluate("document.getElementById('slamBtn').classList.add('locked')"); await pg.wait_for_timeout(300); await shot('locked')
        out = Image.new('RGB', (860, 428 * len(crops) + 10 * len(crops)), 'white'); y = 0
        for tag, c in crops: out.paste(c, (0, y)); y += 438
        out.resize((430, out.height // 2)).save(f'{WS}/ui/bs_states.png'); print('errors', errs)
        await b.close()
asyncio.run(main())
