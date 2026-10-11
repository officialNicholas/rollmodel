"""v200: the first real match after the lesson: the sun in three steps (find shade with the way shown, hold to stay put, or a coffin), the rain
in one plain line with no slow-down, the zombie eyes' box and the orb near you, then: bought in the shop, Back goes to the locker to wear them"""
import asyncio, os, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main(w, h, tag):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', runs: 1, drops: 120, stage: 'crypt', tut: { ph: 'match2' }, owned: ['flower', 'fangs'], bought: ['flower', 'fangs'], look: { mouth: 'fangs', side: 'flower' }, seen: { steer:1, jump:1, hold:1, burst:1, roll:1, pound:1, missile:1, item:1, orb:1, rocket:1, airdash:1, look:1 } })); } catch (e) {}")
        await ctx.add_init_script('window.__starts = []; const _st = AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start = function (w, off, dur) { try { window.__starts.push([+(off || 0).toFixed(3), dur ? +dur.toFixed(3) : 0, performance.now()]); } catch (e) {} return _st.apply(this, arguments); };')
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=240000): await pg.wait_for_function(js, timeout=t, polling=100)
        async def shot(name): await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(800); await pg.screenshot(path=f'{WS}/ui/t2_{tag}_{name}.png'); await pg.evaluate("__T.renderer.render = () => {}; 0")
        st = "(() => { const t = __T.tut2, P = __T.P, el = document.getElementById('tut'), ar = document.getElementById('tutArrow'), pin = document.querySelector('.tuthand:not(#tutHand)'), g = document.querySelector('.tutgest'); return { tip: __T.tutTip && __T.tutTip.key, text: __T.tutTip && __T.tutTip.text, ph: t && t.ph, sub: t && t.sub, wx: __T.wxPhase, slow: document.getElementById('tutSlow').className, arrow: !ar.hidden, pin: pin ? !pin.hidden : null, gest: g && !g.hidden ? g.dataset.g : null, shade: t && t.shade ? +Math.hypot(t.shade[0] - P.x, t.shade[1] - P.z).toFixed(1) : null, inShade: __T.inShadow(P.x, P.z, P.y), pst: P.st, paint: +P.paint.toFixed(2) }; })()"
        await pg.goto('http://localhost:8765/' + os.environ.get('PAGE', 'pc_h.html'), timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.evaluate("__T.stageSel = 'crypt'; document.getElementById('homePlay').click()"); await wait("__T.state === 'play'"); await wait("!!__T.tut2")
        print('match2', await pg.evaluate("[__T.tutPh(), __T.TH && __T.TH.id, __T.tut2.ph]"))
        p0 = await pg.evaluate("[__T.P.paint, __T.runT]"); await pg.wait_for_timeout(2500); p1 = await pg.evaluate("[__T.P.paint, __T.runT]"); print('paint use per s (this match)', round((p0[0] - p1[0]) / max(0.01, p1[1] - p0[1]), 4))
        await pg.evaluate("__T.matchLeft = 44; 0"); await wait("__T.tutTip && __T.tutTip.key === 'wxsun'"); await pg.wait_for_timeout(200)
        print('sun', await pg.evaluate(st)); await shot('sun')
        print('voice takes started so far', await pg.evaluate('(() => { const tk = [[72.20627, 0.66067], [72.92694, 0.60242], [73.58935, 0.48762], [74.13698, 0.45177], [74.64875, 0.89765], [75.6064, 0.47129], [76.13769, 0.65838]]; return window.__starts.filter(s => tk.some(t => Math.abs(s[0] - t[0]) < 0.08 && Math.abs(s[1] - t[1]) < 0.05)).map(s => s[0]); })()'))
        await pg.evaluate("(() => { const t = __T.tut2, P = __T.P; if (t.shade) { P.x = t.shade[0]; P.z = t.shade[1]; } })(); 0")
        await wait("__T.tutTip && (__T.tutTip.key === 'wxhold' || __T.tutTip.key === 'wxpot')", 60000); await pg.wait_for_timeout(300); k = await pg.evaluate("__T.tutTip.key"); print('next', await pg.evaluate(st)); await shot('hold' if k == 'wxhold' else 'pot')
        if k == 'wxhold':
            await pg.evaluate("__T.startCharge(__T.P); 0"); await wait("__T.tutTip && __T.tutTip.key === 'wxpot'", 60000); await pg.wait_for_timeout(300); print('pot', await pg.evaluate(st)); await shot('pot')
        await pg.evaluate("__T.P.charging = false; __T.P.charge = 0; 0")
        await wait("__T.tutTip && __T.tutTip.key === 'wxrain'", 180000); await pg.wait_for_timeout(300); print('rain', await pg.evaluate(st), await pg.evaluate("__T.tut2.slowK")); await shot('rain')
        await wait("__T.gift && __T.gift.on", 180000); await pg.wait_for_timeout(300); print('gift', await pg.evaluate("[__T.gift.id, +Math.hypot(__T.gift.x - __T.P.x, __T.gift.z - __T.P.z).toFixed(1), __T.tutTip && __T.tutTip.key, !document.getElementById('tutArrow').hidden]")); await shot('gift')
        await pg.evaluate("__T.orb.on = false; __T.orb.spawnT = 0; 0"); await wait("__T.orb.on", 60000); print('orb', await pg.evaluate("[+Math.hypot(__T.orb.x - __T.P.x, __T.orb.z - __T.P.z).toFixed(1), +Math.hypot(__T.orb.x - __T.H.x, __T.orb.z - __T.H.z).toFixed(1)]"))
        await pg.evaluate("(() => { const P = __T.P, g = __T.gift; if (P.st === 'hide') __T.exitPot(P, true); P.x = g.x; P.z = g.z; })(); 0"); await wait("__T.gift.got", 60000); print('got', await pg.evaluate("[__T.newItemV, __T.store.zombieDeal]"))
        await pg.evaluate("__T.matchLeft = 0.05; 0"); await wait("!document.getElementById('victory').hidden", 180000); await wait("__T.vic && __T.vic.t >= 1", 90000); await pg.evaluate("document.getElementById('victory').click()")
        await wait("!document.getElementById('newItem').hidden", 90000); await pg.wait_for_timeout(1800); print('newitem', await pg.evaluate("[document.getElementById('niName').textContent, document.getElementById('niTry').textContent, __T.store.drops]"))
        await pg.evaluate("document.getElementById('niTry').click()"); await wait("__T.shopOpen", 60000); await pg.wait_for_timeout(1200)
        await pg.evaluate("document.getElementById('shopGrid').querySelector('.shitem[data-w=\"zombie\"]').click()"); await pg.wait_for_timeout(900); print('bought', await pg.evaluate("[__T.store.bought && __T.store.bought.includes('zombie'), __T.store.drops]"))
        await pg.evaluate("document.getElementById('shopBack').click()"); await wait("__T.lookOpen", 30000); await pg.wait_for_timeout(1500)
        print('locker', await pg.evaluate("[__T.lookOpen, __T.lookCat, __T.tutTip && __T.tutTip.key, __T.tutTip && __T.tutTip.text, __T.shopOpen]")); await shot('locker')
        await pg.evaluate("document.getElementById('eyeStyles').querySelector('[data-es=\"zombie\"]').click()"); await pg.wait_for_timeout(1200); print('worn', await pg.evaluate("[__T.myLook.eyes, __T.tutTip && __T.tutTip.key]")); await shot('worn')
        await pg.evaluate("document.getElementById('lookDone').click()"); await wait("!document.getElementById('tutGo').hidden", 60000); await pg.wait_for_timeout(900); print('welcome', await pg.evaluate("document.getElementById('tgTitle').textContent"))
        print('voice takes started in all', await pg.evaluate('(() => { const tk = [[72.20627, 0.66067], [72.92694, 0.60242], [73.58935, 0.48762], [74.13698, 0.45177], [74.64875, 0.89765], [75.6064, 0.47129], [76.13769, 0.65838]]; return window.__starts.filter(s => tk.some(t => Math.abs(s[0] - t[0]) < 0.08 && Math.abs(s[1] - t[1]) < 0.05)).map(s => s[0]); })()'))
        print('errors', errs); await b.close()
k = sys.argv[1] if len(sys.argv) > 1 else 'port'
asyncio.run(main(*{'port': (390, 780, 'port'), 'land': (844, 390, 'land')}[k]))
