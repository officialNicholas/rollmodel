# every color the slime comes in (and the rivals' blue): a close front three-quarter view of each, moving (paint on its lower half) and
# standing still, in one sheet rx/<tag>_colors.png
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'col'
PAGE = sys.argv[2] if len(sys.argv) > 2 else 'pc_t.html'
SETUP = open(SP + 'gen/skinshot.py').read().split('SETUP = r"""')[1].split('"""')[0]
COLS = ['red', 'orange', 'gold', 'green', 'purple', 'pink', 'blue']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1000)
        await pg.evaluate(SETUP, 'island')
        await pg.evaluate("""() => { const T = __T, P = T.P; window.__still = (n, spd) => { for (let i = 0; i < n; i++) { T.steerIn = 0; P.spd = spd; P.vy = 0; P.air = false; if (!spd) T.VP.wade = 0; T.step(1 / 60); P.x = window.__n0.x; P.z = window.__n0.z; P.yaw = 0.6; T.camYaw = 0.6; { const I = T.VP.slime; I.st.blinkT = 9; I.st.blinkK = 0; } T.visuals(1 / 60, 1 / 60); } }; }""")
        rows = []
        for c in COLS:
            if c == 'blue': await pg.evaluate("() => { const T = __T; T.setColor('red'); T.TEAMS = null; }")
            js = "() => { const T = __T; T.setColor('%s'); }" % c if c != 'blue' else "() => { const T = __T; T.setColor('red'); const h = 0x2E9BFF; T.paintUniforms.uWetA.value[0].setHex(h); T.VP.mat.color.setHex(h); window.__blue = h; }"
            await pg.evaluate(js)
            ims = []
            for spd, lab in [(1, 'moving'), (0, 'still')]:
                await pg.evaluate("() => window.__still(%d, %s)" % (90 if spd else 260, '__T.cfg.speed * 0.9' if spd else '0'))
                if c == 'blue': await pg.evaluate("() => { const I = __T.VP.slime; I.setColor(new __T.THREE.Color(0x2E9BFF)); I.setPaint(new __T.THREE.Color(0x2E9BFF)); }")
                await pg.evaluate("() => window.__shot(0.7, 0.5, 3.0, 0.15)"); fn = SP + 'rx/_c_%s_%s.png' % (c, lab); await pg.screenshot(path=fn)
                im = Image.open(fn).convert('RGB'); W, H = im.size; im = im.crop((0, int(H * 0.27), W, int(H * 0.73))).resize((360, int(360 * 0.46 * H / W))); ims.append(im)
            rows.append((c, ims))
        h = rows[0][1][0].size[1]; sheet = Image.new('RGB', (len(rows) * 366, h * 2 + 6), (16, 12, 24)); dr = ImageDraw.Draw(sheet)
        for i, (c, ims) in enumerate(rows):
            for j, im in enumerate(ims): sheet.paste(im, (i * 366, j * (h + 6)))
            dr.text((i * 366 + 6, 6), c, fill=(255, 255, 255))
        sheet.save(SP + 'rx/%s_colors.png' % TAG); print('saved', sheet.size)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
