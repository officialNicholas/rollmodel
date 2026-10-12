"""The lesson's first dodge: swipe clear as the rival's pound comes, then log the slow-down from the swipe on (real time): it should hold about
a second, then ease back to full speed within a quarter second, whether or not the pound has landed. usage: dodgeslow.py [page]"""
import asyncio, sys
from playwright.async_api import async_playwright
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=50)
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.tap('#homePlay'); await wait("__T.tut && __T.tut.step === 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'dodge' && n++ < 20) __T.tutNext(); })(); 0")
        await pg.evaluate("""(() => { window.__log = []; let t0 = null, rolled = false; const L = () => { const P = __T.P, H = __T.H, t = __T.tut; if (!t || __T.TUT_STEPS[t.step].id !== 'dodge') { __log.push('step over: ' + (t ? __T.TUT_STEPS[t.step].id : '-')); return; }
          if (P.st === 'hide') __T.exitPot(P, true);
          const eta = H.slam ? H.slamEta - H.slamT : 9;
          if (!rolled && H.slam && eta < 0.5 && P.st === 'play' && !P.air) { rolled = true; __T.dodgeRoll(P); t0 = performance.now(); __log.push('SWIPE at eta ' + eta.toFixed(2)); }
          if (t0 !== null) { const s = (performance.now() - t0) / 1000; if (s < 2.2) __log.push([s.toFixed(2), 'slowK', t.slowK.toFixed(2), 'rollRT', (t.rollRT || 0).toFixed(2), H.slam ? 'pound in air' : 'landed', t.sub].join(' ')); }
          requestAnimationFrame(L); }; requestAnimationFrame(L); })(); 0""")
        await wait("__log.some(l => l.startsWith('step over')) || (__log.length > 5 && parseFloat(__log[__log.length - 1]) > 2.1)", 600000)
        lg = await pg.evaluate("__log"); prev = None
        for l in lg:
            k = l.split(' slowK ')[1][:4] if ' slowK ' in l else l
            if k != prev or l.startswith('SWIPE') or l.startswith('step'): print(l); prev = k
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
