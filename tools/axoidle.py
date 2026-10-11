"""The lobby idle on the axolotl: samples what the game's idle asks of it (hops, head bob, hands, sway) and where its body is, over a while."""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 520}, device_scale_factor=1)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000)
        for i in range(150):
            if await pg.evaluate("typeof __T === 'object' && !!__T.VP && !!__T.VP.slime"): break
            await pg.wait_for_timeout(2000)
        await pg.evaluate("""(() => { const I = __T.VP.slime; window.__log = []; const AX = __T.AXOC, up = AX.update; AX.update = (J, o) => { if (J === I) { const v = new THREE.Vector3(); J.root.getWorldPosition(v);
          window.__log.push([+o.dt.toFixed(3), o.inAir ? 1 : 0, +(o.height || 0).toFixed(2), +(o.headPitch || 0).toFixed(2), +(o.headRoll || 0).toFixed(2), +(o.hand || 0).toFixed(2), +(o.shove || 0).toFixed(2), +(o.push || 0).toFixed(2), +(o.squash || 0).toFixed(2), +(o.rise || 0).toFixed(2), +v.y.toFixed(3)]); } return up(J, o); }; })()""")
        await pg.wait_for_timeout(20000)
        L = await pg.evaluate("window.__log")
        print(len(L), 'frames; dt inAir height pitch roll hand shove push squash rise rootY')
        for r in L[::max(1, len(L) // 60)]: print(r)
        print('errors', errs[:5])
        await b.close()
asyncio.run(main())
