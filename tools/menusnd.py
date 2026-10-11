"""Log every sound call in the first seconds after the main menu loads (to find a stray chime)."""
import asyncio, sys
from playwright.async_api import async_playwright
async def run(p, store, tag):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
    ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
    await ctx.add_init_script("window.__tut = true; window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify(" + store + ")); } catch (e) {}")
    await ctx.add_init_script("""(() => { const t0 = performance.now(); window.__snd = []; const hook = () => { const A = window.__T && window.__T.AU; if (!A) return setTimeout(hook, 5); for (const k of Object.keys(A)) if (typeof A[k] === 'function' && !['init','muted','suspend','wake','at','beat','mood','_trk','prep'].includes(k)) { const f = A[k]; A[k] = function (...a) { __snd.push([Math.round(performance.now() - t0), k, JSON.stringify(a).slice(0, 40)]); return f.apply(this, a); }; } }; hook(); })()""")
    pg = await ctx.new_page()
    await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
    r0 = await pg.evaluate('Math.round(performance.now())'); await pg.wait_for_timeout(15000)
    print(tag, 'menu at', r0, await pg.evaluate("JSON.stringify(__snd.filter(e => !['sizzle','rain','roll','pre','chargeSet','music'].includes(e[1]) || e[1] === 'music'))")); await b.close()
async def main():
    async with async_playwright() as p:
        await run(p, "{ orient:'port', name:'Dusk', seen:{look:1}, drops: 50, runs: 3, tut: { ph: 'done' } }", 'returning')
        await run(p, "{ orient:'port', name:'Dusk', seen:{}, drops: 0 }", 'firstrun')
asyncio.run(main())
