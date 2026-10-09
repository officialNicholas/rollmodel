# the same close view in the dark crypt for two builds, side by side (how the skin holds up in low light)
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGES = sys.argv[1].split(',')
STAGE = sys.argv[2] if len(sys.argv) > 2 else 'crypt'
SETUP = open(SP + 'gen/skinshot.py').read().split('SETUP = r"""')[1].split('"""')[0]
async def one(p, page):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
    pg = await ctx.new_page()
    await pg.goto('file://' + SP + page, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1000)
    await pg.evaluate(SETUP, STAGE)
    await pg.evaluate("() => { const T = __T, P = T.P; for (let i = 0; i < 200; i++) { T.steerIn = 0; P.spd = 0; P.vy = 0; P.air = false; T.VP.wade = 0; T.step(1 / 60); P.x = window.__n0.x; P.z = window.__n0.z; P.yaw = 0.6; T.camYaw = 0.6; const I = T.VP.slime; if (I) { I.st.blinkT = 9; I.st.blinkK = 0; } T.visuals(1 / 60, 1 / 60); } }")
    await pg.evaluate("() => window.__shot(0.5, 0.45, 2.8, 0.18)")
    fn = SP + 'rx/_cc_%s.png' % page.replace('.html', ''); await pg.screenshot(path=fn); await b.close(); return fn
async def main():
    async with async_playwright() as p:
        fns = [await one(p, pg) for pg in PAGES]
    ims = [Image.open(f).convert('RGB') for f in fns]; W, H = ims[0].size
    s = Image.new('RGB', (W * len(ims), int(H * 0.5)))
    for i, im in enumerate(ims): s.paste(im.crop((0, int(H * 0.25), W, int(H * 0.75))), (i * W, 0))
    s.save(SP + 'rx/cryptcmp_%s.png' % STAGE); print('saved', s.size)
asyncio.run(main())
