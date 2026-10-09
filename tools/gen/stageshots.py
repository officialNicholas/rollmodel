# per theme: a seeded mid-match frame and a wide look over the stage, on one sheet: python3 gen/stageshots.py TAG [gfx=hi] [dsf=1] themes...
import asyncio, sys, json
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1]
GFX = next((a[4:] for a in sys.argv[2:] if a.startswith('gfx=')), 'hi')
DSF = int(next((a[4:] for a in sys.argv[2:] if a.startswith('dsf=')), '1'))
STEPS = int(next((a[6:] for a in sys.argv[2:] if a.startswith('steps=')), '560'))
THEMES = [a for a in sys.argv[2:] if '=' not in a] or ['garden', 'cathedral', 'crypt', 'manor', 'island', 'blank']
SEED = "(() => { let s = 777; Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=DSF, has_touch=True, is_mobile=True)
        await ctx.add_init_script(SEED)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', look: { back: 'wings' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html'); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(700)
        await pg.evaluate("window.__noLoop = true"); await pg.evaluate("(() => { for (let i = 0; i < 40; i++) __T.visuals(0.016, 0.05); __T.renderFrame(); })()")
        await pg.screenshot(path=f'{SP}st/{TAG}_menu.png')
        for th in THEMES:
            r = await pg.evaluate("""([th, steps]) => { const T = __T, P = T.P; T.genWorld(5151, { themes: [th] }); T.mapUsed = false; T.start(); window.__noStep = false;
              P.cpu = true; T.aiReset(P);
              const run = n => { for (let i = 0; i < n; i++) { T.steerIn = P.steer || 0; T.step(0.016); if (i % 3 === 2) { T.visuals(0.048, 0.048); T.flushTrail(); } } };
              const clean = () => P.st === 'play' && !P.air && !P.power && !(P.giantT > 0) && T.wx === 'clear' && !T.POTS.slice(0, 8).some(q => Math.hypot(q[0] - P.x, q[2] - P.z) < 6.5) && Math.hypot(P.x, P.z) < T.ARENA * 0.62 && (Math.sin(P.yaw) * -P.x + Math.cos(P.yaw) * -P.z) > 0.2 * Math.hypot(P.x, P.z);
              run(steps); let extra = 0; while (!clean() && extra < 900) { run(10); extra += 10; }
              P.cpu = false; T.steerIn = 0; for (let i = 0; i < 20; i++) T.visuals(0.016, 0.016); T.flushTrail(); document.getElementById('banner').style.display = 'none'; T.renderFrame();
              return [T.TH.id, Math.round(T.matchLeft), extra]; }""", [th, STEPS])
            await pg.screenshot(path=f'{SP}st/{TAG}_{th}_play.png')
            await pg.evaluate("""() => { const T = __T, c = T.camera; document.getElementById('hud').classList.add('off'); c.position.set(-15, 21, -23); c.lookAt(2, 0, 4); T.renderFrame(); }""")
            await pg.screenshot(path=f'{SP}st/{TAG}_{th}_wide.png')
            await pg.evaluate("(() => { document.getElementById('hud').classList.remove('off'); document.getElementById('banner').style.display = ''; __T.state = 'menu'; __T.showMenu(); })()")
        print(TAG, errs[:4]); await b.close()
    W, H = 300, 649; ims = [Image.open(f'{SP}st/{TAG}_menu.png').convert('RGB').resize((W, H))]
    for th in THEMES:
        for v in ['play', 'wide']: ims.append(Image.open(f'{SP}st/{TAG}_{th}_{v}.png').convert('RGB').resize((W, H)))
    cols = 7 if len(ims) > 7 else len(ims); rows = (len(ims) + cols - 1) // cols
    o = Image.new('RGB', (cols * W + (cols - 1) * 6, rows * H + (rows - 1) * 6), (16, 16, 16))
    for i, im in enumerate(ims): o.paste(im, ((i % cols) * (W + 6), (i // cols) * (H + 6)))
    o.save(f'{SP}st/{TAG}_sheet.png'); print('sheet', o.size)
asyncio.run(main())
