"""v256 Showdown top bar: faces and hearts only, the time in the middle. usage: sdhud256.py PAGE TAG [duo,ffa,narrow,mini,wide]
Shoots 2v2 and free-for-all upright (390 wide and a narrow 320), and 2v2 wide (844 x 390): the start, a lost heart and a fighter out,
the zone warning chip under the bar, and the last ten seconds."""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG = sys.argv[1], sys.argv[2]
ev = lambda pg, e: pg.evaluate("__T.ev(" + json.dumps(e) + ")")
async def adv(pg, secs, dt=1/30):
    n = max(1, round(secs / dt))
    while n > 0: k = min(n, 15); await pg.evaluate(f"__adv({dt}, {k})"); n -= k
async def run(b, mode, vp, orient, name):
    save = dict(SAVE, mode=mode, diff='medium', orient=orient)
    ctx, pg, errs = await boot(b, PAGE, save, vp=vp, dpr=2, init='window.__skipIntro = false; window.__noReveal = true;')
    await pg.evaluate("__T.start()")
    await pg.wait_for_function("__T.state === 'intro' || __T.state === 'play'", timeout=240000, polling=50)
    await pg.evaluate("window.__tscale = 1e-9"); await pg.wait_for_timeout(300)
    for _ in range(500):
        if await pg.evaluate("__T.state === 'play'"): break
        await pg.evaluate("__adv(1/30, 6)")
    await adv(pg, 1.2)
    top = vp[1] * 0.3 if vp[0] < vp[1] else vp[1] * 0.42
    async def shot(n):
        await pg.screenshot(path=f'{OUT}/{TAG}_{name}_{n}.png', clip={'x': 0, 'y': 0, 'width': vp[0], 'height': top}, timeout=120000); print('shot', name, n, flush=True)
    print(name, await ev(pg, "JSON.stringify({ mode, sd: hud.classList.contains('sdmode'), bar: !$('sdBar').hidden, html: $('sdBar').children.length, clock: $('clock').textContent, r: (() => { const a = $('clock').getBoundingClientRect(), m = document.querySelector('.sdmid'), q = m && m.getBoundingClientRect(), f = document.querySelector('.sdc .bico').getBoundingClientRect(); return { clockX: +(a.left + a.width / 2).toFixed(1), midX: q && +(q.left + q.width / 2).toFixed(1), clockY: +(a.top + a.height / 2).toFixed(1), faceY: +(f.top + f.height / 2).toFixed(1), barW: +$('sdBar').getBoundingClientRect().width.toFixed(1), barH: +$('sdBar').getBoundingClientRect().height.toFixed(1) }; })() })"))
    await shot('start')
    # a heart down for a rival, and one fighter out (free-for-all) or your teammate down to one (2v2)
    await ev(pg, "(H.hearts = 1, mode === 'ffa' ? (H3.hearts = 0, sdOut(H3)) : (H2.hearts = 1), sdHud(true), 0)"); await adv(pg, 0.8); await shot('hurt')
    # the zone's warning under the bar
    await ev(pg, "(runT = 44.6, 0)"); await adv(pg, 0.6); await shot('zone')
    # the last ten seconds
    await ev(pg, "(matchLeft = 8.2, 0)"); await adv(pg, 0.3)
    print(name, 'hurry', await ev(pg, "JSON.stringify({ t: $('clock').textContent, hurry: $('clock').classList.contains('hurry'), col: getComputedStyle($('clock')).color })"))
    await shot('hurry')
    await pg.screenshot(path=f'{OUT}/{TAG}_{name}_full.png', timeout=120000)
    print(name, 'errors', errs[:5]); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        CF = {'duo': ('duo', (390, 780), 'port'), 'ffa': ('ffa', (390, 780), 'port'), 'narrow': ('ffa', (320, 640), 'port'), 'mini': ('duo', (375, 667), 'port'), 'wide': ('duo', (844, 390), 'land')}
        for k in (sys.argv[3].split(',') if len(sys.argv) > 3 else ['duo', 'ffa', 'narrow', 'wide']): await run(b, CF[k][0], CF[k][1], CF[k][2], k)
        await b.close()
asyncio.run(main())
