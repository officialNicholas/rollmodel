"""v251 soak: whole matches with the AI playing (drawing off, so at speed), traps in the item mix and CPUs' orbs forced to Flash Freeze; counts
traps dropped, set off and rolled through, freezes cast and who got frozen, your skill; collects every error.
usage: soak251.py [duel|trio] [seconds] [skill]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'duel'; SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 80; SK = sys.argv[3] if len(sys.argv) > 3 else 'pockets'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noReveal = true; window.__orbKind = null; window.__allTraps = %s; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1, roll: 1, pound: 1, missile: 1, burst: 1 }, drops: 0, runs: 9, xp: 900, tut: { ph: 'done', strokes: 1, comms: 1, m3: 2 }, strokes: { special: 'freeze', skill: '%s', own: ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets'] } })); } catch (e) {}" % ('true' if __import__('os').environ.get('TRAPS') else 'false', SK))
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append('console: ' + m.text[:200])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_252f.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=400000); await pg.wait_for_timeout(800)
        await ev("(() => { const r = __T.renderer; r.render = () => {}; })(); 0")
        await ev(f"window.__orbKind = undefined; __T.mode = '{MODE}'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000)
        # count what happens: wrap the trap and freeze functions, CPUs' orbs always Flash Freeze, items often traps
        await ev("""(() => { const T = __T, c = window.__cnt = { drop: 0, hit: 0, rolled: 0, fizz: 0, cast: 0, frozen: {}, spared: 0, useHeld2: 0, saved: 0, skill: T.P.skill };
          T.ev(`(() => { const d = dropTrap, pp = trapPop, sf = startFreeze, ff = freezeFlash, u2 = useHeld2;
            dropTrap = D => { window.__cnt.drop++; return d(D); };
            trapPop = (Tr, B, h) => { if (!B && h) window.__cnt.fizz++; else if (B && h) window.__cnt.rolled++; else if (B) window.__cnt.hit++; return pp(Tr, B, h); };
            startFreeze = D => { window.__cnt.cast++; return sf(D); };
            freezeFlash = F => { const r = ff(F); for (const B of ACTIVE) if (B.frozenT > 2.9) window.__cnt.frozen[nameOf(B)] = (window.__cnt.frozen[nameOf(B)] || 0) + 1; return r; };
            cpuGift = () => 'freeze'; const si = spawnItem; spawnItem = () => { const n = powers.length; si(); if (powers.length > n) { const pw = powers[powers.length - 1]; if (window.__allTraps) { placePower(pw, 'trap', [pw.x, pw.y, pw.z]); itemSpawn.t = 3; } (window.__cnt.items = window.__cnt.items || []).push(pw.type); } };
            const ff2 = freezeFlash; freezeFlash = F => { (window.__cnt.flashes = window.__cnt.flashes || []).push(nameOf(F.by) + ': ' + ACTIVE.filter(B => B !== F.by).map(B => nameOf(B) + '/' + B.st + (B.rollT > 0 ? '/roll' : '')).join(' ')); return ff2(F); }; })()`); })()""")
        await ev("""(() => { let a = 0; window.__drv = setInterval(() => { if (__T.state !== 'play') return; a += 0.25; __T.steerIn = Math.sin(a) * 0.8; const P = __T.P; if (P.st === 'hide') { P.__hid = (P.__hid || 0) + 1; if (P.__hid > 25) { P.__hid = 0; __T.ev('exitPot(P)'); } } else P.__hid = 0; if (P.held && Math.random() < 0.02) __T.ev('useHeld(P)'); if (P.held2 && Math.random() < 0.02) __T.ev('useHeld2(P)'); if (P.orbSaved && Math.random() < 0.01) __T.ev('useOrb(P)'); }, 100); })()""")
        t0 = await ev("__T.runT"); n = 0; mx = {'held2': 0, 'saved': 0}
        while True:
            r = await ev("[__T.state, __T.runT, __T.P.held2 ? 1 : 0, __T.P.orbSaved ? 1 : 0, __T.ev('trapList.length'), __T.ev('frzList.length')]")
            if r[0] != 'play': break
            mx['held2'] = max(mx['held2'], r[2]); mx['saved'] = max(mx['saved'], r[3]); n += 1
            if r[1] - t0 > SECS: break
            await pg.wait_for_timeout(150)
        print(MODE, SK, 'game secs', round(r[1] - t0, 1), 'samples', n, 'counts', await ev("window.__cnt"), 'P held two / saved an orb at some point', mx)
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
