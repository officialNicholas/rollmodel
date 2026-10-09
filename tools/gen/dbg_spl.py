import asyncio
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:500]))
        await pg.goto('file://' + SP + 'pc_t.html'); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(400)
        await pg.evaluate("window.__noLoop = true")
        await pg.evaluate("""() => { const T = __T, P = T.P; T.genWorld(5151, { themes: ['cathedral'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
          let bb = null; for (const b of T.BOXES) { if (b[4] > 0 || b[6] === 'c' || b[6] === 'g' || b[5] - b[4] < 0.9) continue; if (!bb || (b[1] - b[0]) > (bb[1] - bb[0])) bb = b; }
          window.__bb = bb; const cx = (bb[0] + bb[1]) / 2, z = bb[3]; T.clock = 100;
          T.putSplash(cx - 0.3, 0.55, z, 0, 1, 0.7, 0); T.putSplash(cx + 0.2, 0.5, z, 0, 1, 0.7, 1);
          document.getElementById('hud').classList.add('off'); document.getElementById('banner').style.display = 'none'; T.clock = 104; T.visuals(0.001, 0.001); T.clock = 104; }""")
        shots = []
        DBG = "const ob = T.splIM.userData.ob || (T.splIM.userData.ob = m.onBeforeCompile); const mm = m.clone(); mm.onBeforeCompile = sh => { ob(sh); sh.fragmentShader = sh.fragmentShader.replace('#include <dithering_fragment>', '#include <dithering_fragment>\\n' + XX); }; mm.customProgramCacheKey = () => XX; T.splIM.material = mm;"
        for k, js in [('base', ''), ('vcol', DBG.replace('XX', '"gl_FragColor = vec4(vColor.rgb, 1.0);"')), ('alpha', DBG.replace('XX', '"gl_FragColor = vec4(vec3(texture2D(map, vMapUv).a), 1.0);"')), ('uv', DBG.replace('XX', '"gl_FragColor = vec4(fract(vMapUv * 2.0), 0.0, 1.0);"'))]:
            await pg.evaluate("(() => { const T = __T, m = T.splIM.material, c = T.camera, bb = window.__bb, cx = (bb[0] + bb[1]) / 2; " + js + " c.position.set(cx, 0.8, bb[3] + 1.8); c.lookAt(cx, 0.6, bb[3]); T.renderFrame(); })()")
            for q in range(3):
                await pg.wait_for_timeout(300); await pg.evaluate("__T.renderFrame()")
            f = f'{SP}st/dsp_{k}.png'; await pg.screenshot(path=f); shots.append(f)
        print(errs[:3]); await b.close()
    ims = [Image.open(f).convert('RGB').crop((0, 400, 780, 1300)).resize((390, 450)) for f in shots]
    o = Image.new('RGB', (len(ims) * 396, 450)); [o.paste(im, (i * 396, 0)) for i, im in enumerate(ims)]; o.save(f'{SP}st/dsp_sheet.png')
asyncio.run(main())
