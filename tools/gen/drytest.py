# wet to dry: the slime standing still (no paint on it), soaked, then a frame every 0.6 s as it dries; plus the dry gloss map from the
# front and the side. One sheet rx/<tag>_dry.png
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'dry'
PAGE = sys.argv[2] if len(sys.argv) > 2 else 'pc_t.html'
COLOR = sys.argv[3] if len(sys.argv) > 3 else 'red'
SETUP = open(SP + 'gen/skinshot.py').read().split('SETUP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: '" + COLOR + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1000)
        await pg.evaluate(SETUP, 'island')
        # still, no paint on it
        await pg.evaluate("""() => { const T = __T, P = T.P; window.__still = (n) => { for (let i = 0; i < n; i++) { T.steerIn = 0; P.spd = 0; P.vy = 0; P.air = false; T.VP.wade = 0; T.step(1 / 60); P.x = window.__n0.x; P.z = window.__n0.z; P.yaw = 0.6; { const I = T.VP.slime; I.st.blinkT = 9; I.st.blinkK = 0; } T.visuals(1 / 60, 1 / 60); } }; window.__still(400); }""")
        shots = []
        for az, el, d, lk, lab in [(0.7, 0.5, 3.2, 0.15, 'dry front'), (1.6, 0.45, 3.4, 0.1, 'dry side'), (2.7, 0.8, 3.3, 0.1, 'dry back')]:
            await pg.evaluate("() => window.__shot(%f, %f, %f, %f)" % (az, el, d, lk)); fn = SP + 'rx/_d_%s.png' % lab.replace(' ', '_'); await pg.screenshot(path=fn); shots.append((fn, lab, (0, 120, 360, 520)))
        await pg.evaluate("() => { __T.VP.slime.soak(1); window.__still(1); }")
        for k in range(6):
            await pg.evaluate("() => window.__shot(2.7, 0.8, 3.3, 0.1)"); fn = SP + 'rx/_d_w%d.png' % k; await pg.screenshot(path=fn); shots.append((fn, 'soaked +%.1fs' % (k * 0.6), (0, 120, 360, 520)))
            await pg.evaluate("() => window.__still(36)")
        ims = []
        for fn, label, box in shots:
            im = Image.open(fn).convert('RGB'); s = im.size[0] / 360; im = im.crop(tuple(int(v * s) for v in box)); im = im.resize((int(im.size[0] * 500 / im.size[1]), 500)); ims.append((im, label))
        W = sum(im.size[0] for im, _ in ims) + 8 * (len(ims) - 1); sheet = Image.new('RGB', (W, 500), (16, 12, 24)); x = 0; dr = ImageDraw.Draw(sheet)
        for im, label in ims: sheet.paste(im, (x, 0)); dr.text((x + 6, 6), label, fill=(255, 255, 255)); x += im.size[0] + 8
        sheet.save(SP + 'rx/%s_dry.png' % TAG); print('saved', sheet.size)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
