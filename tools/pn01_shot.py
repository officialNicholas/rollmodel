"""pn01 check: the readout on a phone-shaped page. Turns it on, shoots the lobby, opens the tally, plays a match with the
readout up, comes back and shoots the tally, and checks the online line against a stand-in connection.
usage: pn01_shot.py <test build in game/> <out dir>"""
import asyncio, os, sys, json
from playwright.async_api import async_playwright
PAGE, OUT = sys.argv[1], sys.argv[2]
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
SAVE = "localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient: 'port', name: 'Dusk', introDone: 1, seen: { look: 1, steer: 1, jump: 1, hold: 1, roll: 1, missile: 1, pound: 1, burst: 1, orb: 1 }, drops: 50, runs: 30, flings: 50, xp: 99999, tut: { ph: 'done' } }))"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.route('**/*supabase.co/**', lambda r: r.abort()); await ctx.route('**/*fly.dev/**', lambda r: r.abort())
        await ctx.add_init_script("window.__tapGate = false; try { if (!sessionStorage.getItem('s')) { sessionStorage.setItem('s', 1); %s; } } catch (e) {}" % SAVE)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://127.0.0.1:8766/' + PAGE, timeout=600000)
        await pg.wait_for_function("typeof __T === 'object' && __T.ev('state') === 'menu' && document.getElementById('boot').classList.contains('gone')", timeout=600000, polling=250)
        await pg.evaluate("__T.ev('perfHudSet(true)')"); await pg.wait_for_timeout(3500)
        print('lobby readout:\n' + await pg.evaluate("document.querySelector('.perfhud').textContent"))
        await pg.screenshot(path=OUT + '/pn01_lobby.png')
        await pg.evaluate("__T.ev(\"stageSel = 'sewer'; setMode('duel');\")"); await pg.evaluate("window.__skipIntro = true; __T.ev('start()')")
        await pg.wait_for_function("__T.ev('state') === 'play'", timeout=600000, polling=250); await pg.wait_for_timeout(6000)
        print('match readout:\n' + await pg.evaluate("document.querySelector('.perfhud').textContent"))
        print('tappable in the match:', await pg.evaluate("getComputedStyle(document.querySelector('.perfhud')).pointerEvents"))
        await pg.screenshot(path=OUT + '/pn01_match.png')
        # the online line, against a stand-in connection
        line = await pg.evaluate("__T.ev(\"(() => { const nm0 = NM; NM = { net: { connected: true, stats: () => ({ rtt: 84.2, jitter: 6.1, interpDelay: 112, corrections: 0, bytesIn: 9000, bytesOut: 5000 }) } }; phxLines(); NM.net.stats = () => ({ rtt: 84.2, jitter: 6.1, interpDelay: 112, corrections: 0, bytesIn: 10850, bytesOut: 6100 }); const s = phxLines(); NM = nm0; return s; })()\")")
        print('online line (stand-in):' + line)
        await pg.evaluate("__T.ev('showMenu(); irisBusy = false;')"); await pg.wait_for_timeout(2500)
        await pg.click('.perfhud'); await pg.wait_for_timeout(300)
        print('tally:\n' + await pg.evaluate("document.querySelector('.perfhud').textContent"))
        await pg.screenshot(path=OUT + '/pn01_tally.png')
        print('errors', errs[:5])
        await b.close()
asyncio.run(main())
