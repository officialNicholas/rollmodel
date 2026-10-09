# the match intro with the real loop: the countdown drop forming, Go, the fall and the landing (screenshots over time)
import asyncio, sys, json, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'intro'; N = int(sys.argv[3]) if len(sys.argv) > 3 else 18; WHAT = sys.argv[4] if len(sys.argv) > 4 else 'match'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3}; window.__skipIntro = false; window.__instant = true;')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'trio', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: errs.append(m.type + ' ' + m.text[:200]) if m.type in ('error', 'warning') and 'GPU stall' not in m.text else None)
        await pg.goto('file://' + SP + (sys.argv[5] if len(sys.argv) > 5 else 'pc_t.html'), timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && (!__T.SLIME || __T.VP.slime)', polling=200, timeout=240000)
        await pg.wait_for_timeout(1500)
        if WHAT == 'match':
            await pg.evaluate("() => { const T = __T; T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {}; T.start(); }")
        else:
            await pg.evaluate("() => { const T = __T; T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {}; T.openLook(); }")
        frames = []
        for k in range(N):
            await pg.wait_for_timeout(700)
            st = await pg.evaluate("() => { const T = __T, V = T.VP; return { state: T.state, introT: +T.introT.toFixed(2), slime: V.slime ? V.slime.root.visible : null, old: V.oldBlob ? V.oldBlob.visible : null, y: +T.P.y.toFixed(2), air: T.P.air, formK: T.P.formK !== undefined ? +T.P.formK.toFixed(2) : null, lost: T.renderer.getContext().isContextLost(), cam: [T.camera.position.x, T.camera.position.y, T.camera.position.z].map(v => +v.toFixed(2)), px: [T.P.x, T.P.z].map(v => +v.toFixed(2)), st: T.P.st, stage: T.TH && T.TH.key, nan: window.__nanInfo || null, nanCam: window.__nanCam || null, nanCam2: window.__nanCam2 || null }; }")
            png = await pg.screenshot(timeout=120000)
            im = Image.open(io.BytesIO(png)).convert('RGB'); frames.append(im); print(k, st)
        w, h = frames[0].size; s = 0.5; tw, th = int(w * s), int(h * s)
        cols = 6; rows = (len(frames) + cols - 1) // cols; sheet = Image.new('RGB', (tw * cols, th * rows), 'white')
        for i, f in enumerate(frames): sheet.paste(f.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
