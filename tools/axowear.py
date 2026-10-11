"""What the axolotl wears: the locker open, each item put on in turn (hats, masks, glasses, the bow tie and pearls, the flower, lashes,
fangs, wings), a shot of each. usage: axowear.py [tag]"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'w'
ONLY = os.environ.get('ONLY')
ITEMS = [('head', 'hat'), ('head', 'tophat'), ('head', 'pirate'), ('head', 'tiara'), ('head', 'bunny'), ('head', 'halo'), ('head', 'skull'), ('head', 'horns'),
         ('eye', 'glasses'), ('eye', 'hockey'), ('eye', 'patch'), ('neck', 'bowtie'), ('neck', 'pearls'), ('side', 'flower'), ('lash', 'lashes'), ('mouth', 'fangs'), ('back', 'wings')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=1)
        if os.environ.get('SLIME'): await ctx.add_init_script("window.AXO_PACK = 'no-axo.txt'; Object.defineProperty(window, 'AXO_PACK_BUF', { set() {}, get() { return undefined; } });")
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000)
        for i in range(150):
            if await pg.evaluate("typeof __T === 'object' && !!__T.VP && !!__T.VP.slime"): break
            await pg.wait_for_timeout(2000)
        await pg.wait_for_timeout(2000)
        await pg.evaluate("(() => { try { __T.openLook(); } catch (e) {} })()"); await pg.wait_for_timeout(3500)
        print('look keys', await pg.evaluate("Object.keys(__T.myLook)"), 'kind', await pg.evaluate("__T.VP.slime && __T.VP.slime.kind"))
        for slot, item in [x for x in ITEMS if not ONLY or x[1] in ONLY.split(',')]:
            await pg.evaluate(f"(() => {{ const L = __T.myLook; for (const k of ['head','eye','neck','side','lash','mouth','back']) if (k in L) L[k] = null; L['{slot}'] = '{item}'; }})()")
            await pg.wait_for_timeout(1300)
            await pg.screenshot(path=f'{OUT}/{TAG}_{slot}_{item}.png')
        print('errors', errs[:5])
        await b.close()
asyncio.run(main())
