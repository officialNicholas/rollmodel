"""The five new pieces: each worn in the locker, close; then the shop grid with their rendered pictures. usage: wear238.py [page] [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
from PIL import Image
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'; FITS = sys.argv[3] if len(sys.argv) > 3 else '{}' # (json: {beanie:{..},party:{..},mono:{..},stache:{..},scarf:{..}} sets window.__*Fit)
LOOKS = [{'head': 'beanie'}, {'head': 'party'}, {'eye': 'monocle'}, {'mouth': 'stache'}, {'neck': 'scarf'}]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 800}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 2000, runs: 3, owned: [], bought: [], tut: { ph: 'done' } })); } catch (e) {}")
        await ctx.add_init_script("(() => { const F = " + FITS + "; for (const k in F) window['__' + k + 'Fit'] = F[k]; })()")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100)
        await pg.wait_for_timeout(2500); await ev("__T.openLook()"); await pg.wait_for_timeout(8000)
        fs = []
        for i, look in enumerate(LOOKS):
            await ev("(l) => { const L = __T.myLook; for (const k of ['head','side','mouth','eye','neck','lash']) L[k] = l[k] || null; __T.renderLook(); }", look); await pg.wait_for_timeout(2500)
            fn = f'{WS}/ui/wear_{TAG}_{i}.png'; await pg.screenshot(path=fn); fs.append(fn); print(i, look, await ev("(() => { const W = __T.VP.wear || (__T.VP.W) || null; return W ? Object.keys(W).filter(k => W[k] && W[k].visible === true) : 'no W'; })()"))
        await ev("__T.myLook.head = null; __T.myLook.eye = null; __T.myLook.mouth = null; __T.myLook.neck = null; __T.renderLook(); __T.closeLook && __T.closeLook();"); await pg.wait_for_timeout(1200)
        await ev("document.getElementById('dabsBtn') ? document.getElementById('dabsBtn').click() : __T.openShop()"); await pg.wait_for_timeout(2500)
        await ev("(() => { const g = document.getElementById('shopGrid'); const c = g.querySelector('.shitem[data-w=\"beanie\"]'); if (c) c.scrollIntoView(); })()"); await pg.wait_for_timeout(600)
        fn = f'{WS}/ui/wear_{TAG}_shop.png'; await pg.screenshot(path=fn); fs.append(fn)
        for j, w in enumerate(['stache', 'scarf']):
            await ev("(w) => { const c = document.querySelector('#shopGrid .shitem[data-w=\"' + w + '\"]'); if (c) c.scrollIntoView(); }", w); await pg.wait_for_timeout(600); await pg.screenshot(path=f'{WS}/ui/wear_{TAG}_shop{j + 1}.png')
        print('shop cards', await ev("[...document.querySelectorAll('#shopGrid .shitem')].map(e => e.dataset.w + (e.querySelector('img') ? ':img' : ':svg'))"))
        print('errors', errs[:3]); await b.close()
    ims = [Image.open(f).crop((0, 0, 390, 520)) for f in fs[:5]]; w, h = ims[0].size; sh = Image.new('RGB', (w * 5, h), 'white'); [sh.paste(im, (i * w, 0)) for i, im in enumerate(ims)]; sh.save(f'{WS}/ui/wear_{TAG}_sheet.png')
asyncio.run(main())
