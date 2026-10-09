# the crawl in motion: the slime driven along at a given speed (straight, or turning), the camera riding beside it; a strip of frames
# across about two strides (rx/<tag>_crawl_<mode>.png)
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'crawl'
MODE = sys.argv[2] if len(sys.argv) > 2 else 'side'   # side | slow | turn | back
PAGE = sys.argv[3] if len(sys.argv) > 3 else 'pc_t.html'
SETUP = open(SP + 'gen/skinshot.py').read().split('SETUP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1.5, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        await pg.evaluate(SETUP, 'island')
        spd = {'side': 0.9, 'slow': 0.35, 'turn': 0.8, 'back': 0.9}[MODE]
        turn = 1.0 if MODE == 'turn' else 0.0
        await pg.evaluate("""([spd, turn]) => { const T = __T, P = T.P, n0 = window.__n0; P.x = n0.x; P.z = n0.z; P.y = 0; P.air = false; P.vy = 0; P.yaw = 0.6; T.camYaw = 0.6;
          window.__drive = (n) => { for (let i = 0; i < n; i++) { T.steerIn = turn; P.spd = T.cfg.speed * spd; P.paint = 1; P.vy = 0; P.air = false; T.step(1 / 60); P.x = n0.x; P.z = n0.z; if (!turn) P.yaw = 0.6; const I = T.VP.slime; if (I) { I.st.blinkT = 9; I.st.blinkK = 0; } T.visuals(1 / 60, 1 / 60); } };
          window.__drive(150); }""", [spd, turn])
        az, el, dist, look = {'side': (1.57, 0.3, 10.5, 0.2), 'slow': (1.57, 0.3, 10.5, 0.2), 'turn': (0.5, 3.2, 8.5, 0.0), 'back': (2.3, 1.6, 7.5, 0.1)}[MODE]
        await pg.evaluate("""() => { window.__shot2 = (az, el, dist, look, back) => { const T = __T, c = T.camera, D = T.P, R = T.VP.root, a = D.yaw + az, fx = Math.sin(D.yaw), fz = Math.cos(D.yaw), cx = R.position.x - fx * back, cz = R.position.z - fz * back;
          c.position.set(cx + Math.sin(a) * dist, R.position.y + el, cz + Math.cos(a) * dist); c.lookAt(cx, R.position.y + look, cz); c.fov = 30; c.updateProjectionMatrix(); T.renderFrame(); c.fov = 40; c.updateProjectionMatrix(); }; }""")
        frames = []
        for k in range(16):
            await pg.evaluate("() => window.__drive(3)")
            await pg.evaluate("() => window.__shot2(%f, %f, %f, %f, 0.35)" % (az, el, dist, look))
            fn = SP + 'rx/_cr_%02d.png' % k; await pg.screenshot(path=fn); frames.append(fn)
        info = await pg.evaluate("() => { const s = __T.VP.slime.st, U = __T.VP.slime.U, R = __T.VP.root, P = __T.P; return { P: [P.x, P.y, P.z, P.st, P.yaw], R: R.position.toArray(), C: __T.camera.position.toArray(), n0: [window.__n0.x, window.__n0.z], gph: s.gph, gamp: s.gamp, crawl: U.sCrawl.value.toArray(), micro: U.sMicro.value.toArray(), bend: s.bend }; }")
        print(info)
        ims = []
        for fn in frames:
            im = Image.open(fn).convert('RGB'); W, H = im.size; im = im.crop((0, int(H * 0.38), W, int(H * 0.62))); ims.append(im)
        w, h = ims[0].size; cols = 4; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (w * cols, h * rows), (16, 12, 24)); dr = ImageDraw.Draw(sheet)
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h)); dr.text(((i % cols) * w + 4, (i // cols) * h + 4), str(i), fill=(255, 255, 255))
        sheet.save(SP + 'rx/%s_crawl_%s.png' % (TAG, MODE)); print('saved', sheet.size)
        ims[0].save(SP + 'rx/%s_crawl_%s.gif' % (TAG, MODE), save_all=True, append_images=ims[1:], duration=50, loop=0)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
