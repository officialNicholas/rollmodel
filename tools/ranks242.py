"""The rank gates: rank 1 (Strokes and Commissions locked), rank 2 (the Strokes lesson, Commissions still locked), rank 3 with Strokes done
(the Commissions card). usage: ranks242.py <page> <tag>"""
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE, TAG = sys.argv[1], sys.argv[2]
SEEDS = [('r1', 0, "{ ph: 'done' }"), ('r2', 120, "{ ph: 'done' }"), ('r3', 260, "{ ph: 'done', strokes: 1 }")]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist']); fs = []
        for name, xp, tut in SEEDS:
            ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
            await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ look: 1 }, drops: 120, runs: 9, xp: " + str(xp) + ", owned: [], tut: " + tut + " })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
            await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(4500)
            print(name, 'rank', await ev("document.getElementById('repLvl').textContent"), 'comm', await ev("document.getElementById('commBtn').className + ' / ' + document.getElementById('commTag').textContent"), 'abil', await ev("document.getElementById('abilBtn').className + ' / ' + document.getElementById('abilTag').textContent"), 'card', await ev("document.getElementById('tutGo').hidden ? 'none' : document.getElementById('tgTitle').textContent"))
            if name == 'r1': await ev("document.getElementById('commBtn').click()"); await pg.wait_for_timeout(500)
            f = f'{WS}/ui/rk_{TAG}_{name}.png'; await pg.screenshot(path=f); fs.append(f); print('errors', errs[:2]); await ctx.close()
        await b.close()
    ims = [Image.open(f) for f in fs]; w, h = ims[0].size; sh = Image.new('RGB', (w * 3 + 20, h), 'white'); [sh.paste(im, (i * (w + 10), 0)) for i, im in enumerate(ims)]
    sh.resize((sh.width * 2 // 3, sh.height * 2 // 3)).save(f'{WS}/ui/rk_{TAG}_sheet.png'); print(sh.size)
asyncio.run(main())
