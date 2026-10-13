import asyncio, sys
from playwright.async_api import async_playwright
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 195, 'height': 422}, device_scale_factor=1, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'sewer', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_perf.html', timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000); await pg.evaluate("window.__perfAI()")
        await pg.wait_for_timeout(3000)
        await pg.evaluate("""(() => { const gl = __T.renderer.getContext(); window.__ul = {}; for (const f of ['texImage2D', 'texSubImage2D']) { const o = gl[f]; gl[f] = function () { const a = [...arguments]; let sz = ''; const src = a.find(x => x && typeof x === 'object' && ('width' in x)); if (src) sz = src.width + 'x' + src.height + ' ' + (src.constructor && src.constructor.name); else sz = a.filter(x => typeof x === 'number').join(','); const st = new Error().stack.split('\\n').slice(2, 7).map(s => s.trim().replace(/https?:[^)]*?:(\\d+):\\d+/g, 'L$1')).join(' < '); const k = f + ' ' + sz + ' | ' + st; __ul[k] = (__ul[k] || 0) + 1; return o.apply(this, arguments); }; } })()""")
        await pg.wait_for_timeout(4000)
        U = await pg.evaluate("__ul")
        for k, v in sorted(U.items(), key=lambda kv: -kv[1])[:12]: print(v, k[:420])
        await b.close()
asyncio.run(main())
