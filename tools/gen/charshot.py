# character close-ups in the customizer: python3 gen/charshot.py TAG [gfx]
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
TAG = sys.argv[1]; GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
LOOKS = [('red', 'round', 'wings'), ('purple', 'happy', 'hat'), ('green', 'googly', 'halo')]
async def settle(pg, n=60, dt=0.05):
    await pg.evaluate(f"(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.016, {dt}); __T.renderFrame(); }})()")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(900)
        await pg.evaluate("window.__noLoop = true"); await settle(pg, 60)
        await pg.screenshot(path=f'char/{TAG}_menu.png')
        await pg.click('#lookBtn'); await pg.wait_for_timeout(200); await settle(pg, 120)
        ims = []
        for i, (col, eye, wear) in enumerate(LOOKS):
            await pg.click(f'.sw[data-c="{col}"]'); await pg.click(f'#eyeOpts .lopt[data-e="{eye}"]')
            on = await pg.evaluate(f"document.querySelector('#wearOpts .lopt[data-w=\"{wear}\"]').getAttribute('aria-pressed')")
            if on != 'true': await pg.click(f'#wearOpts .lopt[data-w="{wear}"]')
            await settle(pg, 70)
            f = f'char/{TAG}_look{i}.png'; await pg.screenshot(path=f); ims.append(f)
            await pg.click(f'#wearOpts .lopt[data-w="{wear}"]')
        # side by side crops of the upper half where the blob stands
        crops = [Image.open(f).convert('RGB') for f in ims]
        crops = [c.crop((0, 0, c.width, int(c.height * 0.5))) for c in crops]
        W = sum(c.width for c in crops); H = max(c.height for c in crops); sheet = Image.new('RGB', (W, H))
        x = 0
        for c in crops: sheet.paste(c, (x, 0)); x += c.width
        sheet = sheet.resize((W // 2, H // 2)); sheet.save(f'char/{TAG}_sheet.png')
        print(TAG, errs[:4]); await b.close()
asyncio.run(main())
