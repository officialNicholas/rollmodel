# final showcase shots on a simulated iPhone 15 Pro: python3 gen/finalshots.py [menus] [looks] [play]
import asyncio, sys, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
PARTS = [a for a in sys.argv[1:] if not a.startswith('only=')] or ['menus', 'looks', 'play']
ONLY = next((a[5:].split(',') for a in sys.argv[1:] if a.startswith('only=')), None)
NATIVE = 'window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};'
STORE = "try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}"

async def page(b):
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script(NATIVE); await ctx.add_init_script(STORE)
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:200]))
    pg.set_default_timeout(120000); await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000); await pg.wait_for_timeout(900)
    return ctx, pg, errs

async def settle(pg, n=60):
    await pg.evaluate(f"(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.016, 0.05); __T.renderFrame(); }})()")

async def menus(b):
    ctx, pg, errs = await page(b)
    await pg.evaluate("window.__noLoop = true"); await settle(pg, 120)
    print('gfx', await pg.evaluate("__T.GFX"))
    await pg.screenshot(path='fin/title.png')
    await pg.click('#homePlay'); await pg.wait_for_timeout(700)
    for s in ['garden', 'island', 'blank', 'season']:
        await pg.click(f'.world[data-s="{s}"]'); await pg.wait_for_timeout(1300)
        await pg.screenshot(path=f'fin/world_{s}.png')
    await pg.click('#worldBack'); await pg.wait_for_timeout(500)
    await pg.click('#setBtn'); await pg.wait_for_timeout(600)
    await pg.screenshot(path='fin/settings.png')
    print('menus', errs[:4]); await ctx.close()

async def looks(b):
    ctx, pg, errs = await page(b)
    await pg.evaluate("window.__noLoop = true"); await settle(pg, 120)
    await pg.click('#lookBtn'); await pg.wait_for_timeout(300)
    async def want(color, eyes, head, back):
        for _ in range(4):
            lk = await pg.evaluate("JSON.parse(JSON.stringify(__T.myLook))"); cid = await pg.evaluate("__T.colorId")
            if cid != color: await pg.click(f'.sw[data-c="{color}"]')
            elif lk.get('eyes') != eyes: await pg.click(f'#eyeOpts .lopt[data-e="{eyes}"]')
            elif lk.get('head') != head: await pg.click(f'#wearOpts .lopt[data-w="{head or lk.get("head")}"]')
            elif lk.get('back') != back: await pg.click(f'#wearOpts .lopt[data-w="{back or lk.get("back")}"]')
            else: return lk
            await pg.wait_for_timeout(250)
        return await pg.evaluate("JSON.parse(JSON.stringify(__T.myLook))")
    print('witch', await want('purple', 'happy', 'hat', None), await want('purple', 'happy', 'hat', None))
    await settle(pg, 136); await pg.screenshot(path='fin/look_witch.png')  # the preview sways with sin(spin): this lands it nearly facing you
    print('bat', await want('red', 'round', None, 'wings'), await want('red', 'round', None, 'wings'))
    await settle(pg, 66); await pg.screenshot(path='fin/look_bat.png')  # picking wings swings it a quarter turn to show them; this brings it back round
    print('looks', await pg.evaluate("JSON.stringify(__T.myLook)"), errs[:4]); await ctx.close()

async def play(b):
    ctx, pg, errs = await page(b)
    for k, th, steps in [(k, th, st) for k, th in enumerate(['cathedral', 'garden', 'manor', 'crypt', 'island', 'blank']) for st in (560,) if not ONLY or f'{th}_{st}' in ONLY]:
        r = await pg.evaluate("""([th, seed, steps]) => { const T = __T, P = T.P; window.__noLoop = true;
          T.genWorld(seed, { themes: [th] }); T.mapUsed = false; T.start(); window.__noStep = false;
          // the game's own AI drives you for a bit, so the paint lands the way it does in a real match
          P.cpu = true; T.aiReset(P);
          const run = n => { for (let i = 0; i < n; i++) { T.steerIn = P.steer || 0; T.step(0.016); if (i % 3 === 2) { T.visuals(0.048, 0.048); T.flushTrail(); } } };
          // then wait for a clean moment: rolling on the ground, no power-up, not at a refill
          const clean = () => P.st === 'play' && !P.air && !P.power && !(P.giantT > 0) && T.wx === 'clear' && P.paint > 0.2 && !T.POTS.slice(0, 8).some(q => Math.hypot(q[0] - P.x, q[2] - P.z) < 6.5);
          run(steps); let extra = 0; while (!clean() && extra < 380) { run(10); extra += 10; }
          P.cpu = false; T.steerIn = 0;
          for (let i = 0; i < 24; i++) T.visuals(0.016, 0.016); T.flushTrail(); document.getElementById('banner').style.display = 'none'; T.renderFrame();
          return [T.TH.id, T.state, P.st, extra, Math.round(T.matchLeft), T.wx, clean()]; }""", [th, 4242 + k * 17, steps])
        print(th, r)
        await pg.screenshot(path=f'fin/play_{th}_{steps}.png')
        await pg.evaluate("(() => { document.getElementById('banner').style.display = ''; __T.state = 'menu'; __T.showMenu(); })()")
    print('play', errs[:4]); await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for part in PARTS: await {'menus': menus, 'looks': looks, 'play': play}[part](b)
        await b.close()
asyncio.run(main())
