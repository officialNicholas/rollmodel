# the other forms in the new skin: the giant (still, and rolling as the ball) and the turret, close; Graphics mode or the plain mode
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'forms'
PAGE = sys.argv[2] if len(sys.argv) > 2 else 'pc_t.html'
GFX = sys.argv[3] if len(sys.argv) > 3 else 'hi'
SETUP = open(SP + 'gen/skinshot.py').read().split('SETUP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1000)
        await pg.evaluate(SETUP, 'island')
        await pg.evaluate("""() => { const T = __T, P = T.P; window.__still = (n, spd) => { for (let i = 0; i < n; i++) { T.steerIn = 0; P.spd = spd; P.vy = 0; P.air = false; T.step(1 / 60); P.x = window.__n0.x; P.z = window.__n0.z; P.yaw = 0.6; T.camYaw = 0.6; { const I = T.VP.slime; I.st.blinkT = 9; I.st.blinkK = 0; } T.visuals(1 / 60, 1 / 60); } }; }""")
        shots = []
        # plain slime first (for the plain mode check)
        await pg.evaluate("() => window.__still(120, __T.cfg.speed * 0.9)")
        await pg.evaluate("() => window.__shot(0.7, 0.5, 3.0, 0.15)"); fn = SP + 'rx/_f_slime.png'; await pg.screenshot(path=fn); shots.append((fn, 'slime moving'))
        await pg.evaluate("() => { __T.P.giantT = 99; window.__still(150, 0); }")
        await pg.evaluate("() => window.__shot(0.7, 2.2, 10.5, 1.2)"); fn = SP + 'rx/_f_giant.png'; await pg.screenshot(path=fn); shots.append((fn, 'giant'))
        await pg.evaluate("() => { window.__still(90, __T.cfg.speed * 1.4); }")
        await pg.evaluate("() => window.__shot(0.7, 2.2, 10.5, 1.2)"); fn = SP + 'rx/_f_ball.png'; await pg.screenshot(path=fn); shots.append((fn, 'giant moving'))
        await pg.evaluate("() => { __T.P.giantT = 0; __T.P.turret = { t: 99, cd: 0.45, kick: 0, ph: 0 }; window.__still(150, 0); }")
        await pg.evaluate("() => window.__shot(0.7, 0.6, 3.4, 0.3)"); fn = SP + 'rx/_f_turret.png'; await pg.screenshot(path=fn); shots.append((fn, 'turret'))
        ims = []
        for fn, label in shots:
            im = Image.open(fn).convert('RGB'); W, H = im.size; im = im.crop((0, int(H * 0.2), W, int(H * 0.8))); im = im.resize((int(im.size[0] * 520 / im.size[1]), 520)); ims.append((im, label))
        Wt = sum(im.size[0] for im, _ in ims) + 6 * (len(ims) - 1); sheet = Image.new('RGB', (Wt, 520), (16, 12, 24)); x = 0; dr = ImageDraw.Draw(sheet)
        for im, label in ims: sheet.paste(im, (x, 0)); dr.text((x + 6, 6), label, fill=(255, 255, 255)); x += im.size[0] + 6
        sheet.save(SP + 'rx/%s_forms.png' % TAG); print('saved', sheet.size)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
