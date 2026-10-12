"""Match 3's script: the orb comes up near you and the CPU leaves it, it makes you a giant (crawling only: the swim share stays 0), then Ol'
Bloop's line on swapping specials, then the slingshot reminder. usage: match3.py [page] [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'
ST = "[+__T.runT.toFixed(1), __T.tut3 && __T.tut3.ph, __T.tutTip && __T.tutTip.key, +__T.P.giantT.toFixed(2), __T.orb.on, __T.H.ai && __T.H.ai.mode, +Math.hypot(__T.orb.x - __T.P.x, __T.orb.z - __T.P.z).toFixed(1), +Math.hypot(__T.orb.x - __T.H.x, __T.orb.z - __T.H.z).toFixed(1)]"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 3, xp: 400, mode: 'duel', tut: { ph: 'done', m3: 1, strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        wait = lambda f, t=400000: pg.wait_for_function(f, timeout=t, polling=100)
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await ev("__T.mode = 'duel'; __T.applyMode(); __T.start()"); await wait("__T.state === 'play' && __T.tut3"); print('tut3', await ev(ST))
        await ev("__T.setDiff('hard'); __T.orb.spawnT = 0.05"); await wait("__T.orb.on"); print('orb up', await ev(ST))
        for i in range(6): await pg.wait_for_timeout(1500); print(' ', await ev(ST))
        await ev("__T.takeOrb(__T.P)"); await wait("__T.tut3.ph === 'giant'"); print('giant', await ev(ST))
        sl = []
        for i in range(14): await pg.wait_for_timeout(250); sl.append(await ev("(() => { const A = __T.VP.slime.ax.A; return [+(A.loco && A.loco.slK || 0).toFixed(2), +__T.P.spd.toFixed(1), A.motion.dry]; })()"))
        print('giant swim share, speed, dry flag', sl)
        await ev("__T.P.giantT = 0.02"); await wait("__T.tutTip && __T.tutTip.key === 'm3swap'"); print('said', await ev(ST)); await pg.wait_for_timeout(700); await pg.screenshot(path=f'{WS}/ui/m3_{TAG}_1.png')
        for i in range(8): await pg.wait_for_timeout(2000); print('  ', await ev("[+__T.runT.toFixed(1), __T.tut3.tipT, __T.tut3.remAt, __T.tut3.rem, __T.tutTip && __T.tutTip.key, __T.P.st]"))
        await ev("__T.tut3.remAt = __T.runT + 0.5"); await wait("__T.tutTip && __T.tutTip.key === 'm3sling'", 120000); print('reminder', await ev(ST)); await pg.wait_for_timeout(700); await pg.screenshot(path=f'{WS}/ui/m3_{TAG}_2.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
