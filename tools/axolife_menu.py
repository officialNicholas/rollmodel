"""v214 on the home screen: the axolotl idles and dances (its hops go through the new air logic); frames over a few seconds, its
animator state, any errors."""
import asyncio
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/lab'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, xp: 140, drops: 168, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400])); pg.on('console', lambda m: errs.append(m.text[:300]) if m.type == 'error' and 'Failed to load' not in m.text and 'ERR_FAILED' not in m.text else None)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000)
        for i in range(8):
            await pg.wait_for_timeout(700); await pg.screenshot(path=f'{OUT}/menu_{i}.png', clip={'x': 60, 'y': 380, 'width': 270, 'height': 280})
            print(i, await pg.evaluate("(() => { const A = __T.VP.slime.ax.A, L = A.loco; return [A.state, A.mesh, L ? L.limbs.map(l => l.st[0]).join('') : '-', L ? +L.v.toFixed(2) : 0, L ? L.air : null, +A.breath.toFixed(2)]; })()"))
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
