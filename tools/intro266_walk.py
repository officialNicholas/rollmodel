#!/usr/bin/env python3
"""The whole first-launch intro stepped at 30 frames a second of game time, every frame saved, the cards answered as a player would.
Usage: p266.py <out dir> [port|land]   (env FROM=<phase> saves frames only from that phase on; ENDAT=<phase> stops there)"""
import asyncio, json, os, sys, time
from playwright.async_api import async_playwright
SHIM = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'intro264_ending.py')).read().split('SHIM = """')[1].split('"""')[0]
OUT = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'port'; VP = (390, 780) if MODE == 'port' else (780, 390)
FROM = os.environ.get('FROM', 'barrel'); ENDAT = os.environ.get('ENDAT', '')
ORDER = ['sky', 'barrel', 'iris', 'style', 'paint', 'form', 'name', 'confirm', 'wink']
FR = os.path.join(OUT, 'all_' + MODE); os.makedirs(FR, exist_ok=True)
LOG = open(os.path.join(OUT, 'log_all_' + MODE + '.txt'), 'w')
def log(*a): print(*a, flush=True); LOG.write(' '.join(str(x) for x in a) + '\n'); LOG.flush()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': VP[0], 'height': VP[1]}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tapGate = false; try { localStorage.clear(); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:400]))
        pg.on('console', lambda m: errs.append(m.type + ' ' + m.text[:300]) if m.type == 'error' else None)
        await pg.goto('http://localhost:8773/_intro_test.html', timeout=600000)
        await pg.wait_for_function('typeof __T === "object"', timeout=600000, polling=500)
        await pg.wait_for_timeout(1500)
        if await pg.evaluate("!document.getElementById('orient').hidden"):
            await pg.evaluate("document.querySelector('#orient .ocard[data-o=\"%s\"]').click(); document.getElementById('orientOk').click()" % MODE); await pg.wait_for_timeout(800)
        for i in range(200):
            if await pg.evaluate("__T.ev('!!(FL && FL.live)')"): break
            await pg.wait_for_timeout(200)
        await pg.evaluate(SHIM); await pg.wait_for_timeout(200)
        n = 0; done = set(); saving = False; ended = None
        CLICK = {'iris': [".flopt[data-i='blue']", '#flIrisGo'], 'style': [".flopt[data-s='edgy']", '#flStyleGo'], 'paint': [".flopt[data-c='red']", '#flPaintGo'],
                 'name': ['#flNameGo'], 'confirm': ['#flYes']}
        while n < 2400:
            await pg.evaluate('__step(1000 / 30)'); n += 1
            s = json.loads(await pg.evaluate("__T.ev('JSON.stringify({ p: FL.peek(), live: FL.live, jin: FL.jin ? FL.jin.ph : null })')"))
            ph = s['p']['ph'] if s['p'] else None; pt = s['p']['pt'] if s['p'] else 0
            if ph == FROM: saving = True
            if ENDAT and ph == ENDAT: break
            if saving: await pg.screenshot(path=f'{FR}/f{n:04d}.jpg', type='jpeg', quality=82)
            if n % 15 == 0: log(n, ph, round(pt, 2), s['jin'])
            if ph in CLICK and pt > 1.1 and ph not in done:
                done.add(ph)
                for sel in CLICK[ph]:
                    if ph == 'name' and sel == '#flNameGo': await pg.fill('#flNameIn', 'Pip')
                    await pg.evaluate("document.querySelector(%s).click()" % json.dumps(sel))
                    for _ in range(12):
                        await pg.evaluate('__step(1000 / 30)'); n += 1
                        if saving: await pg.screenshot(path=f'{FR}/f{n:04d}.jpg', type='jpeg', quality=82)
                log('clicked', ph, n)
            if not s['live'] and not s['jin'] and ph is None:
                if ended is None: ended = n
                if n > ended + 20: break
        log('frames', n); log('ERRORS', [e for e in errs if 'PAGEERR' in e or e.startswith('error')][:10]); await b.close()
asyncio.run(main())
