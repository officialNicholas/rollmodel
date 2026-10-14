"""v260: the sound starts afresh (app back from the background) in the middle of the intro: the intro's music engine re-wires its stems
on the new context, and the intro carries on through its cards."""
import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tapGate = false; try { localStorage.clear(); localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient: 'port', tut: { ph: 'match' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
        await pg.goto('http://localhost:8773/_intro_test.html', timeout=600000)
        await pg.wait_for_function("typeof __T === 'object'", timeout=600000, polling=500)
        ev = lambda e: pg.evaluate("__T.ev(" + json.dumps(e) + ")")
        await pg.evaluate("window.dispatchEvent(new PointerEvent('pointerdown')); 1")
        await pg.wait_for_function("__T.ev('FL && FL.peek && FL.peek() && FL.peek().ph') === 'iris'", timeout=600000, polling=250)
        await pg.wait_for_timeout(1500)
        await ev("(() => { const f = AU.flm.renew; AU.flm.renew = function () { window.__fr = (window.__fr || 0) + 1; return f.apply(this, arguments); }; return 1; })()")
        before = await ev("JSON.stringify({ ph: FL.peek().ph, lay: AU.flm.lay, sound: AU.state, renews: AU.renews })")
        await pg.evaluate("window.dispatchEvent(new CustomEvent('nativeresume', { detail: { away: true } })); 1"); await pg.wait_for_timeout(1500)
        after = await ev("JSON.stringify({ ph: FL.peek().ph, lay: AU.flm.lay, sound: AU.state, renews: AU.renews, flmRenews: window.__fr || 0, fx: AU.flm.fx('sparkle', 0.01) })")
        await ev("FL.go('paint'); 1"); await pg.wait_for_timeout(2500)
        later = await ev("JSON.stringify({ ph: FL.peek().ph, lay: AU.flm.lay, err: !document.getElementById('errLine').hidden })")
        print('before', before); print('after renew', after); print('later', later); print('errors', errs[:5]); await b.close()
asyncio.run(main())
