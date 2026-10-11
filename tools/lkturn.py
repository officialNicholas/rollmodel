"""Locker turn filmstrip: drag the character round (in slow motion), shoot it as it turns and settles, from the locker camera and from
above; log the turn speed and the body's bend. usage: lkturn.py [tag] [dx px] [top: 0/1]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'; DX = float(sys.argv[2]) if len(sys.argv) > 2 else 220; TOP = len(sys.argv) > 3 and sys.argv[3] == '1'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 40, runs: 3, tut: { done: true } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100)
        await pg.wait_for_timeout(2500); await ev("__T.openLook()"); await pg.wait_for_timeout(9000)
        if TOP: await ev("(() => { const P = __T.P; window.__cam = [[P.x + 0.01, 6.5, P.z + 0.6], [P.x, 0, P.z]]; })()")
        await ev("window.__tscale = 0.3")
        x0, y0 = 90, 200
        await pg.mouse.move(x0, y0); await pg.mouse.down()
        for i in range(8): await pg.mouse.move(x0 + DX * (i + 1) / 8, y0); await pg.wait_for_timeout(30)
        await pg.mouse.up()
        shots = []
        for i in range(16):
            d = await ev("(() => { const A = __T.AXOC.S.list[0].ax.A, L = A.loco; return { t: +__T.clock.toFixed(2), v: +__T.shim.vel.toFixed(2), bend: +L.bend.toFixed(0), tl: +(L.tlg || 0).toFixed(0) }; })()")
            path = f'{WS}/ui/lkturn_{TAG}_{i:02d}.png'; await pg.screenshot(path=path); shots.append((path, d)); print(i, d)
        print('errors', errs[:3]); await b.close()
        from PIL import Image, ImageDraw
        cw, ch = 180, 200; sel = shots[::2]; sheet = Image.new('RGB', (cw * len(sel), ch), 'white'); dr = ImageDraw.Draw(sheet)
        for k, (pth, d) in enumerate(sel):
            im = Image.open(pth).convert('RGB').crop((0, 30, 360, 430)).resize((cw, ch)); sheet.paste(im, (k * cw, 0)); dr.text((k * cw + 4, 4), f"v {d['v']} b {d['bend']}", fill='black')
        sheet.save(f'{WS}/ui/lkturn_{TAG}_sheet.jpg', quality=85)
asyncio.run(main())
