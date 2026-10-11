"""The canvas page during onboarding (vote step): layout measurements and screenshots in portrait and landscape."""
import asyncio, sys
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
R = "(() => { const q = s => { const e = document.querySelector(s); if (!e || !e.getClientRects().length) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; }; return { head: q('.mworld .whead'), tip: q('#tut'), gal: q('#stagePick'), world: q('#stagePick .world[aria-pressed=\"true\"] .frame') || q('#stagePick .world .frame'), plaque: q('#stagePick .world[aria-pressed=\"true\"] .plaque'), prev: q('#gPrev'), dots: q('#gDots'), note: q('#soloNote'), go: q('#startBtn'), hand: q('#tutHand'), vh: innerHeight, err: document.getElementById('errLine').textContent.slice(0, 80), g: (() => { const g = document.getElementById('stagePick'), on = [...g.children].find(b => b.getAttribute('aria-pressed') === 'true'); return [g.scrollLeft, g.scrollWidth, g.clientWidth, g.style.paddingLeft, getComputedStyle(g).paddingLeft, on && on.dataset.s, on && on.offsetLeft, on && on.offsetWidth, [...g.children].map(b => b.dataset.s + ':' + b.offsetLeft + '/' + b.offsetWidth).join(' ')]; })() }; })()"
async def run(p, W, H, tag):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if W > H else 'port') + "', name:'Dusk', seen:{}, drops: 0, tut: { ph: 'vote' } })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
    await pg.evaluate("document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(2500)
    print(tag, await pg.evaluate(R)); await pg.screenshot(path=S + '/ws/ui/vote_' + tag + '.png'); print('errors', errs); await b.close()
async def main():
    async with async_playwright() as p:
        for k in (sys.argv[1:] or ['port', 'land']): await run(p, *{'port': (390, 780, 'port'), 'land': (844, 390, 'land'), 'tall': (430, 932, 'tall')}[k])
asyncio.run(main())
