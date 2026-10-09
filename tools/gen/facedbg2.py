import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
JS = """(() => { const root = __T.scene.children.find(o => o.children && o.children[0] && o.children[0].children && o.children[0].children.length > 20);
  const body = root.children[0], out = [];
  body.children.forEach((m, i) => { if (i < 3 || i > 12) return; const mat = m.material; out.push([i, m.visible, m.scale.toArray().map(v => +v.toFixed(2)).join(','), mat ? +mat.opacity.toFixed(2) : 'grp', m.layers.mask, mat ? mat.transparent : '-', mat ? mat.uuid.slice(0, 4) : '']); });
  return { rootVis: root.visible, out }; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(800)
        await pg.click('#lookBtn'); await pg.evaluate("(()=>{ for (let i=0;i<60;i++) __T.visuals(0.0001, 0.05); })()")
        print('after intro', json.dumps(await pg.evaluate(JS)))
        await pg.click('#lookDone'); await pg.wait_for_timeout(300)
        await pg.click('#homePlay'); await pg.wait_for_timeout(300); await pg.click('#startBtn'); await pg.wait_for_function("__T.state === 'play'", polling=100, timeout=20000); await pg.wait_for_timeout(1200)
        await pg.evaluate("(()=>{ const T=__T, P=T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; T.addSplat(x, Math.max(0, T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, T.clock, false, true, 0); } T.flushTrail(); T.matchLeft = 0.05; })()")
        await pg.wait_for_function("!!__T.vic", polling=200, timeout=90000); await pg.wait_for_timeout(1500)
        print('victory', json.dumps(await pg.evaluate(JS)))
        await pg.screenshot(path='ui/facedbg_vic.png'); print(errs[:3])
        await b.close()
asyncio.run(main())
