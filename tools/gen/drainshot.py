# the paint it's sitting in, draining: driven through its paint, then stopped; frames at times after stopping, then moving again (and a
# landing). One sheet rx/<tag>_drain.png, with the level written on each frame
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'drain'
COLOR = sys.argv[2] if len(sys.argv) > 2 else 'red'
SETUP = open(SP + 'gen/skinshot.py').read().split('SETUP = r"""')[1].split('"""')[0]
TIMES = [0.0, 1.0, 2.5, 5.0, 9.0, 14.0, 20.0, 30.0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=2)
        await ctx.add_init_script("Math.random = (()=>{ let s=777; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: '" + COLOR + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        await pg.evaluate(SETUP, 'island')
        await pg.evaluate("""() => { const T = __T, P = T.P, n0 = window.__n0;
          for (let i = 0; i < 7; i++) { const a = i / 7 * 6.2832, r = i ? 1.6 : 0; T.addSplat(n0.x + Math.sin(a) * r, 0, n0.z + Math.cos(a) * r, a, 1.5, T.clock, false, true, 0, 0); }
          window.__run = (n, spd) => { for (let i = 0; i < n; i++) { T.steerIn = 0; P.paint = 1; P.vy = 0; P.air = false; P.spd = spd; T.step(1 / 60); P.x = n0.x; P.z = n0.z; P.yaw = 0.6; P.spd = spd; const I = T.VP.slime; if (I) { I.st.blinkT = 9; I.st.blinkK = 0; } T.visuals(1 / 60, 1 / 60); } };
          window.__run(180, T.cfg.speed * 0.9); }""")
        shots = []; t = 0.0
        for tt in TIMES:
            n = int(round((tt - t) * 60)); t = tt
            lv = await pg.evaluate("(n) => { window.__run(n, 0); window.__shot(1.35, 0.42, 3.0, 0.1); return [+__T.VP.wade.toFixed(3), +__T.VP.slime.st.res.toFixed(3)]; }", n)
            fn = SP + 'rx/_dr_%02d.png' % len(shots); await pg.screenshot(path=fn); shots.append((fn, 'stopped %.0fs  level %.2f' % (tt, lv[0])))
        # moving again for half a second
        for k, n in enumerate([6, 12, 30]):
            lv = await pg.evaluate("(n) => { window.__run(n, __T.cfg.speed * 0.9); window.__shot(1.35, 0.42, 3.0, 0.1); return [+__T.VP.wade.toFixed(3)]; }", n)
            fn = SP + 'rx/_dr_m%d.png' % k; await pg.screenshot(path=fn); shots.append((fn, 'moving again  level %.2f' % lv[0]))
        ims = []
        for fn, label in shots:
            im = Image.open(fn).convert('RGB'); W, H = im.size; im = im.crop((int(W * 0.08), int(H * 0.38), int(W * 0.92), int(H * 0.72))).resize((420, int(420 * 0.34 * H / (0.84 * W)))); ims.append((im, label))
        w, h = ims[0][0].size; cols = 4; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (w * cols, h * rows), (16, 12, 24)); dr = ImageDraw.Draw(sheet)
        for i, (im, label) in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h)); dr.text(((i % cols) * w + 6, (i // cols) * h + 6), label, fill=(255, 255, 255))
        sheet.save(SP + 'rx/%s_drain.png' % TAG); print('saved', sheet.size, errs[:3]); await b.close()
asyncio.run(main())
