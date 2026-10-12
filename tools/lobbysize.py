"""Lobby shots at a few screen shapes for two builds side by side. usage: lobbysize.py pageA pageB tag"""
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/ui'
A, B, TAG = sys.argv[1], sys.argv[2], sys.argv[3]
SIZES = [(725, 1000), (390, 844), (844, 390)]
async def shot(b, page, w, h, fn):
    ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=True, is_mobile=True)
    await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', runs: 3, seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, tut:{ph:'done'} })); } catch (e) {}")
    pg = await ctx.new_page(); await pg.goto('http://localhost:8765/' + page, timeout=240000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP', timeout=240000, polling=1000)
    await pg.mouse.click(w // 2, h // 2); await pg.wait_for_timeout(5000); await pg.screenshot(path=fn); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for i, (w, h) in enumerate(SIZES):
            ims = []
            for pgn in (A, B):
                fn = f'{OUT}/lob_{TAG}_{i}_{pgn}.png'; await shot(b, pgn, w, h, fn); ims.append(Image.open(fn))
            sh = Image.new('RGB', (w * 2 + 10, h), 'white'); sh.paste(ims[0], (0, 0)); sh.paste(ims[1], (w + 10, 0)); sh.save(f'{OUT}/lob_{TAG}_{i}.png')
        await b.close()
asyncio.run(main())
