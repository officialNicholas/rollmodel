#!/usr/bin/env python3
"""v257 intro recorder: plays the intro at a fixed 30 frames a second of game time (requestAnimationFrame, performance.now and the
page's CSS animations all stepped together), saves every frame and a log of when each stage began, for r257_mix.py to cut a video with
the music laid in. Usage: r257_intro.py <frames dir> [port|land]"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'port'; VP = (390, 780) if MODE == 'port' else (780, 390); FPS = 30
os.makedirs(OUT, exist_ok=True)
SHIM = """window.__simT = performance.now(); { const pn = performance.now.bind(performance); window.__realNow = pn; }
performance.now = () => window.__simT; window.__rq = []; window.requestAnimationFrame = cb => (window.__rq.push(cb), 1);
window.__step = dt => { window.__simT += dt; for (const a of document.getAnimations()) { try { a.pause(); a.currentTime = (a.__t = (a.__t === undefined ? (a.currentTime || 0) : a.__t) + dt); } catch (e) {} }
  const q = window.__rq; window.__rq = []; for (const cb of q) { try { cb(window.__simT); } catch (e) { console.error(e); } } };"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--mute-audio'])
        ctx = await b.new_context(viewport={'width': VP[0], 'height': VP[1]}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tapGate = false; try { localStorage.clear(); localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient: '%s' })); } catch (e) {}" % MODE)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/_intro_test.html', timeout=600000)
        await pg.wait_for_function('typeof __T === "object" && FLready()' if False else 'typeof __T === "object"', timeout=600000, polling=500)
        await pg.wait_for_timeout(800); await pg.evaluate(SHIM); await pg.wait_for_timeout(300)
        log = []; last = None; n = 0; acts = {}; T = 0.0; after = None
        async def st(): return await pg.evaluate("__T.ev('JSON.stringify({ p: FL.peek(), live: FL.live, jin: !!FL.jin, tut: !document.getElementById(\"tut\").hidden })')")
        while True:
            await pg.evaluate(f'__step({1000 / FPS})'); T += 1 / FPS; n += 1
            await pg.screenshot(path=f'{OUT}/f{n:05d}.jpg', type='jpeg', quality=88)
            s = json.loads(await st()); ph = s['p']['ph'] if s['p'] else ('jin' if s['jin'] else 'lobby')
            if ph != last: log.append({'ph': ph, 't': round(T, 4), 'hit': s['p']['hit'] if s['p'] else 0}); last = ph; print(n, ph, flush=True); acts = {}
            pt = s['p']['pt'] if s['p'] else 0
            if s['p'] and s['p']['ph'] == 'wink' and not log[-1].get('hit'): log[-1]['hit'] = s['p']['hit']
            async def once(k, js):
                if not acts.get(k): acts[k] = True; await pg.evaluate(js); log.append({'act': k, 't': round(T, 4)})
            if ph == 'iris':
                if pt > 1.6: await once('iris', "document.querySelector('.flopt[data-i=\"blue\"]').click()")
                if pt > 2.8: await once('next1', "document.getElementById('flIrisGo').click()")
            if ph == 'style':
                if pt > 1.2: await once('style', "document.querySelector('.flopt[data-s=\"edgy\"]').click()")
                if pt > 2.4: await once('next2', "document.getElementById('flStyleGo').click()")
            if ph == 'paint':
                if pt > 1.4: await once('paint', "document.querySelector('.flopt[data-c=\"purple\"]').click()")
                if pt > 2.8: await once('next3', "document.getElementById('flPaintGo').click()")
            if ph == 'name':
                if pt > 1.4: await once('type', "document.getElementById('flNameIn').value = 'Pip'")
                if pt > 2.4: await once('go', "document.getElementById('flName').requestSubmit()")
            if ph == 'confirm':
                if pt > 1.4: await once('yes', "document.getElementById('flYes').click()")
            if ph == 'lobby' and after is None: after = T
            if after is not None and T - after > (4.5 if s['tut'] else 6.0): break
            if n > 3000: break
        json.dump({'fps': FPS, 'log': log}, open(f'{OUT}/log.json', 'w'), indent=1); print('frames', n, 'errors', errs)
        await b.close()
asyncio.run(main())
