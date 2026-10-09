# the gameplay camera's view of the player slime, cropped in on it, a few moments of a match (moving through its paint and not)
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'playclose'; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'; GFX = sys.argv[3] if len(sys.argv) > 3 else 'hi'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'trio', look: { head: null }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        await pg.evaluate("""(stage) => { const T = __T; window.__noLoop = true; T.mode = 'trio'; T.applyMode(); T.genWorld(4242, { themes: [stage] }); T.mapUsed = false; T.setDiff('hard'); T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.aiReset(T.P); T.setWx('clear', 999); const dt = 1 / 60; for (let i = 0; i < 60 * 14 && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 10 === 0) { T.visuals(dt * 10, dt * 10); T.flushTrail(); } T.matchLeft = 99; } }""", STAGE)
        frames = []
        for k in range(6):
            d = await pg.evaluate("""(k) => { const T = __T, dt = 1 / 60; for (let i = 0; i < 25; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); T.visuals(dt, dt); T.matchLeft = 99; } T.flushTrail(); T.renderFrame();
              const v = new T.THREE.Vector3(T.P.x, T.P.y + 0.4, T.P.z).project(T.camera); return [T.renderer.domElement.toDataURL('image/png'), [(v.x + 1) / 2, (1 - v.y) / 2], +(T.VP.wade || 0).toFixed(2)]; }""", k)
            im = Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB'); W, H = im.size; cx, cy = d[1][0] * W, d[1][1] * H; r = W * 0.24
            frames.append(im.crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r))).resize((360, 360))); print(k, 'wade', d[2])
        sheet = Image.new('RGB', (360 * 3, 360 * 2), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % 3) * 360, (i // 3) * 360))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
