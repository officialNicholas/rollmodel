import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
THEME = sys.argv[1] if len(sys.argv) > 1 else 'island'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 240, 'height': 520}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.wait_for_function('!__T.SLIME || (__T.SLIME.S.ready && __T.VP.slime)', polling=200, timeout=60000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(theme) => { __T.setStage && __T.setStage(theme === 'island' || theme === 'blank' ? theme : 'season'); __T.freshMap(); }", THEME)
        await pg.wait_for_timeout(3000)
        r = await pg.evaluate("""() => { const T = __T, R = T.renderer; const cnt = () => R.info.programs.filter(p => String(p.cacheKey).includes('paint-stream')).length;
          const streams = []; T.scene.traverse(o => { if (o.material && o.material.customProgramCacheKey && String(o.material.customProgramCacheKey()).includes('paint-stream')) { let v = true, q = o; while (q) { if (!q.visible) v = false; q = q.parent; } streams.push({ vis: o.visible, chainVis: v, inScene: true, layers: o.layers.mask }); } });
          const a = cnt(); return { programsWithStream: a, streams, pots: T.pots.length, kinds: T.pots.map(p => p.kind).join(','), theme: T.TH && T.TH.id }; }""")
        print(json.dumps(r))
        r = await pg.evaluate("""() => { const T = __T, R = T.renderer; window.__noLoop = true; T.start(); for (let i = 0; i < 30; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame();
          const streams = []; T.scene.traverse(o => { if (o.material && o.material.customProgramCacheKey && String(o.material.customProgramCacheKey()).includes('paint-stream')) { let v = true, q = o; while (q) { if (!q.visible) v = false; q = q.parent; } streams.push({ vis: o.visible, chainVis: v, id: o.id }); } });
          return { programsWithStream: R.info.programs.filter(p => String(p.cacheKey).includes('paint-stream')).length, streams, pots: T.pots.length, kinds: T.pots.map(p => p.kind).join(',') }; }""")
        print(json.dumps(r))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
