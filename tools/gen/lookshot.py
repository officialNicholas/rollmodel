# the customize screen with the hero settled in it (run the intro through by hand), and a close crop of the hero
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'look'
PAGE = sys.argv[2] if len(sys.argv) > 2 else 'pc_t.html'
COLOR = sys.argv[3] if len(sys.argv) > 3 else 'red'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: '" + COLOR + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(9000)
        await pg.evaluate("() => { const T = __T; window.__noLoop = true; T.openLook(); for (let i = 0; i < 150; i++) { T.visuals(1 / 60, 1 / 60); } const I = T.VP.slime; for (let i = 0; i < 20; i++) { if (I) { I.st.blinkT = 9; I.st.blinkK = 0; } T.visuals(1 / 60, 1 / 60); } T.renderFrame(); }")
        await pg.wait_for_timeout(300)
        fn = SP + 'rx/%s_look.png' % TAG; await pg.screenshot(path=fn)
        im = Image.open(fn); print(im.size)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
