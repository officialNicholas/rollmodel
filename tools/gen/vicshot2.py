# the winner screen after a match on a stage full of ivy and splashes, stepped by hand (fast): frames of the 3D view
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'vic'; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""(stage) => { const T = __T; window.__noLoop = true; T.mode = 'trio'; T.applyMode(); T.genWorld(4242, { themes: [stage] }); T.mapUsed = false; T.setDiff('easy'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          const dt = 1 / 60; T.aiReset(T.P); for (let i = 0; i < 60 * 20 && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 10 === 0) { T.visuals(dt * 10, dt * 10); T.flushTrail(); } T.matchLeft = Math.max(T.matchLeft, 5); }
          T.matchLeft = 0.01; let n = 0; while (!T.vic && n++ < 2000) { T.step(dt); T.visuals(dt, dt); } if (!T.vic) { try { T.startVictory(); } catch (e) { return 'noVic ' + e; } }
          return { vic: !!T.vic, state: T.state, n }; }""", STAGE)
        print('to victory', r)
        frames = []
        for k in range(8):
            d = await pg.evaluate("""() => { const T = __T, dt = 1 / 60; for (let i = 0; i < 18; i++) T.visuals(dt, dt); T.renderFrame(); const V = T.VP, I = V.slime;
              return [T.renderer.domElement.toDataURL('image/png'), { wade: +(V.wade || 0).toFixed(2), bend: +I.st.bend.toFixed(2), ball: +I.st.ball.toFixed(2), tuck: +I.st.tuck.toFixed(2), vis: I.root.visible, t: T.vic ? +T.vic.t.toFixed(2) : null }]; }""")
            frames.append(Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB')); print(k, d[1])
        w, h = frames[0].size; s = 0.5; tw, th = int(w * s), int(h * s); sheet = Image.new('RGB', (tw * 4, th * 2), 'white')
        for i, f in enumerate(frames): sheet.paste(f.resize((tw, th)), ((i % 4) * tw, (i // 4) * th))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
