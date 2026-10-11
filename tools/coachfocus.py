"""v199: Ol' Bloop up close: the lobby plate, the match bubble over the corner coach (pound with its hand, dodge), hidden while you are
knocked out, and the lesson's last card (over its top edge upright, in the corner on a short sideways screen)"""
import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main(w, h, tag):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=240000): await pg.wait_for_function(js, timeout=t, polling=100)
        async def shot(name): await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(800); await pg.screenshot(path=f'{WS}/ui/cf_{tag}_{name}.png'); await pg.evaluate("__T.renderer.render = () => {}; 0")
        st = "(() => { const t = document.getElementById('tut'), c = document.querySelector('.coachpop'), q = e => { if (!e || e.hidden) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; }; return { tip: __T.tutTip && __T.tutTip.key, pos: t.dataset.pos, coach: t.dataset.coach, side: t.dataset.side, wait: t.classList.contains('wait'), plate: q(t.querySelector('.tplate')), corner: c ? [c.className, c.dataset.side, q(c)] : null, hand: q(document.getElementById('tutHand')), slam: q(document.getElementById('slamBtn')), name: t.querySelector('.tname').textContent, card: document.getElementById('tutGo').className }; })()"
        step = "__T.TUT_STEPS[__T.tut.step].id"
        async def goto(sid): await pg.evaluate("(() => { let n = 0; while (__T.tut && __T.TUT_STEPS[__T.tut.step].id !== '" + sid + "' && n++ < 30) __T.tutNext(); })(); 0")
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await wait("__T.tutTip && __T.tutTip.key === 'first'"); print('lobby', await pg.evaluate(st)); await shot('lobby')
        await pg.evaluate("document.getElementById('homePlay').click()"); await wait("__T.tut && __T.tut.step === 0")
        await goto('pound'); await pg.evaluate("__T.tut.st = 13; 0"); await wait("__T.tutTip && __T.tutTip.key === 'pound'"); await pg.wait_for_timeout(600)
        print('pound', await pg.evaluate(st)); await shot('pound')
        await goto('dodge'); await wait("__T.tutTip && __T.tutTip.key === 'dodge'"); await pg.wait_for_timeout(600); print('dodge', await pg.evaluate(st)); await shot('dodge')
        await pg.evaluate("__T.knockOut(__T.P, 'fall'); 0"); await pg.wait_for_timeout(500); print('ko', await pg.evaluate(st)); await shot('ko')
        try: await wait("__T.P.st === 'play'", 120000); await pg.wait_for_timeout(900); print('back', await pg.evaluate(st))
        except Exception: print('no respawn yet', await pg.evaluate("[__T.P.st, __T.state, " + step + ", __T.tut.st]"))
        await goto('rest'); await wait("!document.getElementById('tutGo').hidden", 60000); await pg.wait_for_timeout(900); print('card', await pg.evaluate(st)); await shot('card')
        print('errors', errs); await b.close()
k = sys.argv[1] if len(sys.argv) > 1 else 'port'
asyncio.run(main(*{'port': (390, 780, 'port'), 'iph': (430, 932, 'iph'), 'land': (844, 390, 'land')}[k]))
