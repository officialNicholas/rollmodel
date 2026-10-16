#!/usr/bin/env python3
"""v257 intro: how smoothly the camera moves. Plays the whole intro (portrait) at a fixed 30 frames a second of game time, as
r257_intro.py does, records the intro camera's place and the way it faces every frame, and prints the biggest changes from one frame to
the next in its velocity (m/s) and in how fast it turns, with the stage and the time in it where they happen.
Usage: cam257_intro.py <page, e.g. _intro_test.html> <out.json>"""
import asyncio, json, math, os, sys
from playwright.async_api import async_playwright
PAGE = sys.argv[1]; OUT = sys.argv[2]; VP = (390, 780); FPS = 30
SHIM = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'r257_intro.py')).read().split('SHIM = """')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--mute-audio'])
        ctx = await b.new_context(viewport={'width': VP[0], 'height': VP[1]}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tapGate = false; try { localStorage.clear(); localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient: 'port' })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('http://localhost:8765/' + PAGE, timeout=600000)
        await pg.wait_for_function('typeof __T === "object"', timeout=600000, polling=500)
        # (v312) a first launch ends on "Tap to start", __tapGate or not: tap it as a player would (a no-op for anyone else)
        await pg.evaluate("(() => { const b = document.getElementById('boot'); if (b && b.classList.contains('tap') && !b.classList.contains('gone')) b.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true })); })()")
        await pg.wait_for_timeout(800); await pg.evaluate(SHIM); await pg.wait_for_timeout(300)
        rec = []; acts = {}; last = None; n = 0
        while n < 3000:
            await pg.evaluate(f'__step({1000 / FPS})'); n += 1
            s = json.loads(await pg.evaluate("__T.ev('(() => { const X = FL._x(); if (!X) return \"null\"; const c = X.pc, e = c.matrixWorld.elements; return JSON.stringify({ ph: X.ph, pt: X.pt, p: [c.position.x, c.position.y, c.position.z], f: [-e[8], -e[9], -e[10]] }); })()')"))
            if not s: break
            rec.append(s); ph, pt = s['ph'], s['pt']
            if ph != last: last = ph; acts = {}
            async def once(k, js):
                if not acts.get(k): acts[k] = True; await pg.evaluate(js)
            if ph == 'iris' and pt > 2.0: await once('a', "document.getElementById('flIrisGo').click()")
            if ph == 'style' and pt > 2.0: await once('a', "document.getElementById('flStyleGo').click()")
            if ph == 'paint':
                if pt > 1.0: await once('p', "document.querySelector('.flopt[data-c=\"purple\"]').click()")
                if pt > 2.0: await once('a', "document.getElementById('flPaintGo').click()")
            if ph == 'name' and pt > 2.0: await once('a', "document.getElementById('flName').requestSubmit()")
            if ph == 'confirm' and pt > 2.0: await once('a', "document.getElementById('flYes').click()")
        json.dump(rec, open(OUT, 'w')); await b.close()
        dt = 1 / FPS; jumps = []
        for i in range(2, len(rec)):
            a, b_, c = rec[i - 2], rec[i - 1], rec[i]
            v1 = [(b_['p'][k] - a['p'][k]) / dt for k in range(3)]; v2 = [(c['p'][k] - b_['p'][k]) / dt for k in range(3)]
            w1 = [(b_['f'][k] - a['f'][k]) / dt for k in range(3)]; w2 = [(c['f'][k] - b_['f'][k]) / dt for k in range(3)]
            jumps.append((math.dist(v1, v2), math.dist(w1, w2), c['ph'], round(c['pt'], 2)))
        print('frames', len(rec))
        print('biggest jumps in speed (m/s per frame):', [(round(j[0], 3), j[2], j[3]) for j in sorted(jumps, key=lambda j: -j[0])[:8]])
        print('biggest jumps in turn (1/s per frame):', [(round(j[1], 3), j[2], j[3]) for j in sorted(jumps, key=lambda j: -j[1])[:8]])
asyncio.run(main())
