"""The axolotl in the menus: the lobby (a couple of moments of its idle), then the locker with a few things on. Prints its animator state
and where it's looking. usage: axomenu.py [tag] [items: slot:item,slot:item ...]"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'm'
ITEMS = [tuple(x.split(':')) for x in (sys.argv[2] if len(sys.argv) > 2 else 'head:hat,eye:patch,mouth:fangs,side:flower').split(',')]
DSF = float(os.environ.get('DSF', '1'))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=DSF)
        if os.environ.get('SLIME'): await ctx.add_init_script("window.AXO_PACK = 'no-axo.txt'; Object.defineProperty(window, 'AXO_PACK_BUF', { set() {}, get() { return undefined; } });")
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400])); pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000)
        for i in range(150):
            if await pg.evaluate("typeof __T === 'object' && !!__T.VP && !!__T.VP.slime"): break
            await pg.wait_for_timeout(2000)
        q = "(() => { const I = __T.VP.slime, X = I.ax; if (!X) return { kind: 'slime' }; const A = X.A; return { mesh: A.mesh, state: A.state, look: [+A.look.yaw.toFixed(1), +A.look.pitch.toFixed(1)], lk: [X.lookY && +X.lookY.toFixed(1), X.lookP && +X.lookP.toFixed(1)], wade: +(X.wade || 0).toFixed(2), coat: +X.coat.toFixed(2), uw: +X.look.U.uCoat.value.w.toFixed(3) }; })()"
        await pg.wait_for_timeout(3000); await pg.screenshot(path=f'{OUT}/{TAG}_lobby1.png'); print('lobby', json.dumps(await pg.evaluate(q)))
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{OUT}/{TAG}_lobby2.png')
        await pg.evaluate("(() => { try { __T.openLook(); } catch (e) {} })()"); await pg.wait_for_timeout(3500)
        await pg.screenshot(path=f'{OUT}/{TAG}_locker0.png'); print('locker', json.dumps(await pg.evaluate(q)))
        for slot, item in ITEMS:
            await pg.evaluate(f"(() => {{ const L = __T.myLook; for (const k of ['head','eye','neck','side','lash','mouth','back']) if (k in L) L[k] = null; L['{slot}'] = '{item}'; }})()")
            await pg.wait_for_timeout(1400)
            await pg.screenshot(path=f'{OUT}/{TAG}_{slot}_{item}.png')
        print('after', json.dumps(await pg.evaluate(q)), 'errors', errs[:6])
        await b.close()
asyncio.run(main())
