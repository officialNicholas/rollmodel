# a slingshot, frame by frame from the side: a long pull (it balls up, then opens out as it slows) and a short one (its plain jump);
# the player wearing a crown so the hat's float shows
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'fl'
CS = [float(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '1.0,0.25').split(',')]
SETUP = open(SP + 'gen/skinshot.py').read().split('SETUP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1.5)
        await ctx.add_init_script("Math.random = (()=>{ let s=99; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', look: { head: 'tiara' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        await pg.evaluate(SETUP, 'island')
        await pg.evaluate("() => { const T = __T; try { T.myLook.head = 'tiara'; } catch (e) {} }")
        rows = []
        for c in CS:
            await pg.evaluate("""(c) => { const T = __T, P = T.P, n0 = window.__n0; P.x = n0.x; P.z = n0.z; P.y = 0; P.air = false; P.vy = 0; P.yaw = 0.6; P.spd = 0;
              for (let i = 0; i < 30; i++) { T.steerIn = 0; T.step(1 / 60); P.x = n0.x; P.z = n0.z; P.yaw = 0.6; T.visuals(1 / 60, 1 / 60); }
              window.__b = { x: P.x, z: P.z, y: P.y, yaw: P.yaw }; T.flingIt(P, c); }""", c)
            for k in range(12):
                info = await pg.evaluate("""() => { const T = __T, P = T.P; for (let i = 0; i < 4; i++) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
                  const b = window.__b, c = T.camera, fx = Math.sin(b.yaw), fz = Math.cos(b.yaw), rx = Math.cos(b.yaw), rz = -Math.sin(b.yaw), m = 3.6;
                  c.position.set(b.x + fx * m + rx * 12, b.y + 2.0, b.z + fz * m + rz * 12); c.lookAt(b.x + fx * m, b.y + 1.3, b.z + fz * m); c.fov = 58; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame();
                  const U = T.VP.slime.U; return [+P.y.toFixed(2), +U.sBlob.value.x.toFixed(2), +U.sBlob.value.y.toFixed(2), P.air]; }""")
                fn = SP + 'rx/_fl_%d_%d.png' % (len(rows), k); await pg.screenshot(path=fn); rows.append((fn, 'c%.2f  %s' % (c, info)))
            print(c, 'done')
        ims = [Image.open(fn).convert('RGB') for fn, _ in rows]; W, H = ims[0].size
        crops = [im.crop((0, int(H * 0.28), W, int(H * 0.66))).resize((300, int(300 * 0.38 * H / W))) for im in ims]
        w, h = crops[0].size; cols = 12; nr = (len(crops) + cols - 1) // cols
        sheet = Image.new('RGB', (w * 6, h * nr * 2), (16, 12, 24)); dr = ImageDraw.Draw(sheet)
        for i, im in enumerate(crops): r = i // 12; k = i % 12; sheet.paste(im, ((k % 6) * w, (r * 2 + k // 6) * h)); dr.text(((k % 6) * w + 4, (r * 2 + k // 6) * h + 4), rows[i][1], fill=(255, 255, 255))
        sheet.save(SP + 'rx/%s_fling.png' % TAG); print('saved', sheet.size, errs[:3]); await b.close()
asyncio.run(main())
