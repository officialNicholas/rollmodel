# the customize screen: its idle hops and spins as a contact sheet, close in
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'lookidle'; ACT = sys.argv[2] if len(sys.argv) > 2 else 'spin'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 520}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'solo', look: { head: null }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        await ctx.add_init_script("window.__instant = true; window.__stepN = 7; window.__camA = 0.15; window.__camD = 1.6; window.__camH = 0.55;")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("() => { __T.setStage && __T.setStage('island'); __T.freshMap(); __T.showMenu(); }"); await pg.wait_for_timeout(2500)
        await pg.evaluate("() => { const T = __T; window.__noLoop = true; T.openLook(); for (let i = 0; i < 200; i++) T.visuals(1/60, 1/60); }")
        frames = []
        for k in range(12):
            d = await pg.evaluate("""([k, act]) => { const T = __T, I = T.idle; if (k === 0) { I.act = act; I.dur = act === 'spin' ? 0.85 : act === 'wiggle' ? 1.3 : 0.9; I.u = 0; }
              for (let i = 0; i < (window.__stepN || 4); i++) T.visuals(1/60, 1/60);
              const P = T.P, ca = P.yaw + (window.__camA === undefined ? 0.9 : window.__camA), cd = window.__camD || 2.4, c = [P.x + Math.sin(ca) * cd, window.__camH || 1.0, P.z + Math.cos(ca) * cd]; T.camera.position.set(...c); T.camera.lookAt(P.x, 0.3, P.z); T.camera.updateMatrixWorld(); T.camera.clearViewOffset && T.camera.clearViewOffset(); T.renderFrame();
              const S = T.VP.slime.st; return [T.renderer.domElement.toDataURL('image/png'), { ball: +S.ball.toFixed(2), bend: +S.bend.toFixed(2), ear: S.earL.map(v => +v.toFixed(2)), sway: +(T.idle.sway || 0).toFixed(2), push: +(T.idle.push || 0).toFixed(2), hop: +(T.idle.hop || 0).toFixed(2), act: T.idle.act }]; }""", [k, ACT])
            frames.append(Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB')); print(k, d[1])
        W = frames[0].width; cols = 6; rows = 2; sheet = Image.new('RGB', (W * cols, frames[0].height * rows), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % cols) * W, (i // cols) * f.height))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
