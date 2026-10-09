# splashes up the nearest block wall, then looks at them as the drips run: python3 gen/splashtest.py TAG [theme]
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1]; TH = sys.argv[2] if len(sys.argv) > 2 else 'cathedral'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + SP + 'pc_t.html'); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(400)
        await pg.evaluate("window.__noLoop = true")
        await pg.evaluate("""(th) => { const T = __T, P = T.P; T.genWorld(5151, { themes: [th] }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
          let bb = null; for (const b of T.BOXES) { if (b[4] > 0 || b[6] === 'c' || b[6] === 'g' || b[5] - b[4] < 0.9) continue; if (!bb || (b[1] - b[0]) > (bb[1] - bb[0])) bb = b; }
          window.__bb = bb; const cx = (bb[0] + bb[1]) / 2, z = bb[3];
          T.clock = 100; for (let i = 0; i < 9; i++) T.putSplash(cx - 1.2 + i * 0.3, 0.35 + (i % 3) * 0.22, z, 0, 1, 0.55 + (i % 4) * 0.12, i % 2);
          const c = T.camera; document.getElementById('hud').classList.add('off'); document.getElementById('banner').style.display = 'none';
          P.x = cx; P.z = z + 4; T.camYaw = Math.PI; }""", TH)
        shots = []
        for t in [100.05, 100.7, 101.4, 103]:
            await pg.evaluate("""(t) => { const T = __T, c = T.camera, bb = window.__bb, cx = (bb[0] + bb[1]) / 2; T.clock = t; T.visuals(0.001, 0.001); T.clock = t; c.position.set(cx + 0.6, 1.1, bb[3] + 2.6); c.lookAt(cx, 0.6, bb[3]); T.renderFrame(); }""", t)
            f = f'{SP}st/{TAG}_{t}.png'; await pg.screenshot(path=f); shots.append(f)
        print(errs[:3]); await b.close()
    W, H = 390, 844; ims = [Image.open(f).convert('RGB').resize((W, H)) for f in shots]
    o = Image.new('RGB', (len(ims) * W + (len(ims) - 1) * 6, H), (16, 16, 16))
    for i, im in enumerate(ims): o.paste(im, (i * (W + 6), 0))
    o.save(f'{SP}st/{TAG}_sheet.png'); print('sheet', o.size)
asyncio.run(main())
