import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
JS = """(() => { const P = __T.P, root = __T.scene.children.find(o => o.children && o.children[0] && o.children[0].children && o.children[0].children.length > 20);
  const body = root.children[0], out = [];
  body.children.forEach((m, i) => { if (!m.isMesh && !m.isGroup) return; const mat = m.material; out.push([i, m.type, m.visible, m.scale.toArray().map(v => +v.toFixed(2)).join(','), mat ? (mat.opacity != null ? +mat.opacity.toFixed(2) : '-') : 'grp', m.layers.mask]); });
  return out; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(800)
        await pg.click('#lookBtn'); await pg.wait_for_timeout(2600)
        print('in look', json.dumps(await pg.evaluate(JS)))
        await pg.click('#lookDone'); await pg.wait_for_timeout(300)
        await pg.click('#homePlay'); await pg.wait_for_timeout(300); await pg.click('#startBtn'); await pg.wait_for_function("__T.state === 'play'", polling=100, timeout=20000); await pg.wait_for_timeout(1500)
        print('in play', json.dumps(await pg.evaluate(JS)))
        await b.close()
asyncio.run(main())
