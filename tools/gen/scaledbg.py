import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 480, 'height': 480}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:400]) if m.type in ('error', 'warning') and 'GPU stall' not in m.text else None)
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T, R = T.renderer, gl = R.getContext(); window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: ['island'] }); T.mapUsed = false; T.start();
          const dt = 1/60; for (let i = 0; i < 30; i++) { T.step(dt); T.visuals(dt, dt); } T.renderFrame();
          const out = { K: T.SLIME.SCALE_K.value.toArray(), tex: !!T.SLIME.S.scales, img: T.SLIME.S.scales && [T.SLIME.S.scales.image.width, T.SLIME.S.scales.image.data[1000], T.SLIME.S.scales.image.data[5000]] };
          const progs = R.info.programs.filter(p => String(p.cacheKey).includes('slime-body'));
          out.progs = progs.length;
          if (progs.length) { const pr = progs[0].program, sh = gl.getAttachedShaders(pr); const fs = sh.map(s => gl.getShaderSource(s)).find(src => src.includes('gl_FragColor') || src.includes('pc_fragColor')) || ''; out.hasScale = fs.includes('sScaleH'); out.hasPerturb = fs.includes('sPerturb(-vViewPosition'); out.hasPaintLit = fs.includes('material.roughness = mix(material.roughness, 0.1, sCoatM)'); out.fsLen = fs.length; }
          const I = T.VP.slime, m = I.mats.slime.body; out.uniformsHasScales = !!(m.userData && m.userData.shader); 
          return out; }""")
        print(json.dumps(r))
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
