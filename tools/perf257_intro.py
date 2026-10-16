#!/usr/bin/env python3
"""v257 intro cost: the game's own measure of each frame's main-thread time (lastCpu: everything the frame does, the GL calls
included) and the draw calls, averaged over each stage of the intro, then over the lobby that follows, in the same browser.
Usage: perf257_intro.py [port|land]"""
import asyncio, json, sys
from playwright.async_api import async_playwright
MODE = sys.argv[1] if len(sys.argv) > 1 else 'port'; VP = (390, 780) if MODE == 'port' else (780, 390)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--mute-audio'])
        ctx = await b.new_context(viewport={'width': VP[0], 'height': VP[1]}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tapGate = false; try { localStorage.clear(); localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient: '%s' })); } catch (e) {}" % MODE)
        pg = await ctx.new_page(); await pg.goto('http://localhost:8765/_intro_test.html', timeout=600000)
        await pg.wait_for_function('typeof __T === "object"', timeout=600000, polling=500)
        # (v312) a first launch ends on "Tap to start", __tapGate or not: tap it as a player would (a no-op for anyone else)
        await pg.evaluate("(() => { const b = document.getElementById('boot'); if (b && b.classList.contains('tap') && !b.classList.contains('gone')) b.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true })); })()")
        # sample every frame from the page itself: the stage, the frame's cpu time, the wall time between frames, the draw calls
        await pg.evaluate("""window.__S = []; (function tick(){ try { const p = __T.ev('FL.peek()'); window.__S.push({ ph: p ? p.ph : (__T.ev('FL.jin') ? 'jin' : 'lobby'), cpu: __T.ev('lastCpu') * 1000, calls: __T.ev('renderer.info.render.calls'), tris: __T.ev('renderer.info.render.triangles'), t: performance.now() }); } catch (e) {} requestAnimationFrame(tick); })();""")
        async def ph(): return await pg.evaluate("(() => { const p = __T.ev('FL.peek()'); return p ? p.ph : 'lobby'; })()")
        while await ph() != 'iris': await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(3000); await pg.click('#flIrisGo')
        while await ph() != 'style': await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(1500); await pg.click('#flStyleGo')
        while await ph() != 'paint': await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(1500); await pg.click('.flopt[data-c="gold"]'); await pg.wait_for_timeout(2500); await pg.click('#flPaintGo')
        while await ph() != 'name': await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(3000); await pg.click('#flNameGo')
        while await ph() != 'confirm': await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(1500); await pg.click('#flYes')
        while await ph() != 'lobby': await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(15000)
        S = await pg.evaluate('window.__S')
        out = {}
        for i, s in enumerate(S[1:], 1):
            o = out.setdefault(s['ph'], {'n': 0, 'cpu': 0, 'gap': 0, 'calls': 0, 'tris': 0}); o['n'] += 1; o['cpu'] += s['cpu']; o['gap'] += s['t'] - S[i - 1]['t']; o['calls'] = max(o['calls'], s['calls']); o['tris'] = max(o['tris'], s['tris'])
        print(f'{"stage":8} {"frames":>6} {"cpu ms":>7} {"frame ms":>9} {"draws":>6} {"tris":>7}')
        for k, o in out.items(): print(f"{k:8} {o['n']:6d} {o['cpu'] / o['n']:7.2f} {o['gap'] / o['n']:9.1f} {o['calls']:6d} {o['tris']:7d}")
        await b.close()
asyncio.run(main())
