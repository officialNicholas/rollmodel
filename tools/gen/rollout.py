# out of a basin in play: swiping up (a roll out) and tapping (a hop out), frame by frame from the side
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'ro'
SETUP = open(SP + 'gen/skinshot.py').read().split('SETUP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1.5)
        await ctx.add_init_script("Math.random = (()=>{ let s=4242; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        await pg.evaluate(SETUP, 'island')
        rows = []
        for mode in ['roll', 'hop']:
            await pg.evaluate("""(mode) => { const T = __T, P = T.P, p = T.pots.filter(q => T.potUp(q) && !q.occ).sort((a, b) => Math.hypot(a.x - P.x, a.z - P.z) - Math.hypot(b.x - P.x, b.z - P.z))[0];
              P.x = p.x; P.z = p.z; P.y = p.y; P.air = false; P.vy = 0; P.spd = 0; T.enterPot2(P, p); P.yaw = Math.atan2(-p.x, -p.z); for (let i = 0; i < 90; i++) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
              window.__b = { x: p.x, z: p.z, y: p.y, yaw: P.yaw };
              if (mode === 'roll') T.dodgeRoll(P); else T.jump(P); }""", mode)
            for k in range(10):
                await pg.evaluate("""() => { const T = __T; for (let i = 0; i < 4; i++) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } const b = window.__b, c = T.camera, rx = Math.cos(b.yaw), rz = -Math.sin(b.yaw), fx = Math.sin(b.yaw), fz = Math.cos(b.yaw);
                  c.position.set(b.x + fx * 1.3 + rx * 8.5, b.y + 1.6, b.z + fz * 1.3 + rz * 8.5); c.lookAt(b.x + fx * 1.3, b.y + 0.55, b.z + fz * 1.3); c.fov = 62; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); }""")
                fn = SP + 'rx/_ro_%s_%d.png' % (mode, k); await pg.screenshot(path=fn); rows.append((mode, k, fn))
        ims = [Image.open(fn).convert('RGB') for _, _, fn in rows]; W, H = ims[0].size
        crops = [im.crop((0, int(H * 0.3), W, int(H * 0.62))).resize((270, int(270 * 0.32 * H / W))) for im in ims]
        w, h = crops[0].size; sheet = Image.new('RGB', (w * 10, h * 2)); dr = ImageDraw.Draw(sheet)
        for i, im in enumerate(crops): sheet.paste(im, ((i % 10) * w, (i // 10) * h))
        sheet.save(SP + 'rx/%s_rollout.png' % TAG); print('saved', sheet.size, errs[:3]); await b.close()
asyncio.run(main())
