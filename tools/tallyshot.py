import asyncio, json, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
# a duel ended with you ahead on paint but behind on eliminations, so the tally turns it round
async def run(w, h, tag, kos_p, kos_h, splats):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, look:{head:'flower', eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn'); await pg.wait_for_timeout(400)
        await pg.wait_for_function("__T.state === 'play'", timeout=40000); await pg.wait_for_function("!__T.P.air && !__T.H.air", timeout=90000, polling=300); await pg.wait_for_timeout(500)
        await pg.evaluate("window.__instant = false; window.__tallyAt = 1.3; window.__log = []; new MutationObserver(() => __log.push(['tally', Math.round(performance.now()), document.getElementById('tally').hidden])).observe(document.getElementById('tally'), { attributes: true }); new MutationObserver(() => __log.push(['vic', Math.round(performance.now()), document.getElementById('victory').hidden])).observe(document.getElementById('victory'), { attributes: true })"); await pg.evaluate("(() => { const P = __T.P, H = __T.H; for (let i = 0; i < %d; i++) { const x = P.x + (i %% 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } for (let i = 0; i < 6; i++) { const x = H.x + (i %% 3 - 1) * 3.2, z = H.z + (i / 3 | 0) * 3.2 - 1.6; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, H.y + 3, true)), z, 1, 3, __T.clock, false, true, 0); } __T.flushTrail(); P.kos = %d; H.kos = %d; __T.matchLeft = 0.05; })()" % (splats, kos_p, kos_h))
        try:
          await pg.wait_for_function("!document.getElementById('tally').hidden", timeout=120000, polling=100)
        except Exception as ex:
          print('FAIL', tag, await pg.evaluate("JSON.stringify(window.__log)"), await pg.evaluate("[__T.state, document.getElementById('tally').hidden, !!__T.vic, __T.matchLeft, JSON.stringify(__T.endInfo && {tot: __T.endInfo.tot, kos: __T.endInfo.kos, win: __T.endInfo.win}), window.__instant]"), errs[:4]); await pg.screenshot(path=f'{WS}/ui/tally_{tag}_fail.png'); await b.close(); return
        T = await pg.evaluate("[__T.tal.KO0, __T.tal.KOD, __T.tal.koq.length, __T.tal.KOEND, __T.tal.END]"); print(tag, 'times', T)
        shots = [(1.3, 'paint'), (T[0] + T[1] * 1.5, 'elims'), (T[0] + T[1] * T[2] + 0.2, 'elims2'), (T[3] + 0.9, 'winner')]
        for at, name in shots:
            await pg.evaluate("window.__tallyAt = %f" % at); await pg.wait_for_function("__T.tal && Math.abs(__T.tal.t - %f) < 0.3" % at, timeout=20000, polling=100); await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'{WS}/ui/tally_{tag}_{name}.png')
            print(tag, name, await pg.evaluate("['L', 'M', 'R'].filter(k => !document.getElementById('tyNum' + k).hidden).map(k => [document.getElementById('tyName' + k).textContent, document.getElementById('tyNum' + k).firstChild.textContent, document.querySelectorAll('#tyNum' + k + ' .tyko').length, document.getElementById('tyNum' + k).classList.contains('win')]).concat([document.getElementById('tyWord').textContent, document.getElementById('tySub').textContent, +__T.tal.t.toFixed(2)])"))
        await pg.evaluate("window.__tallyAt = 99"); await pg.wait_for_function("!!__T.vic", timeout=20000, polling=100); await pg.evaluate("window.__tallyAt = null"); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{WS}/ui/tally_{tag}_victory.png')
        print(tag, 'victory', await pg.evaluate("[document.getElementById('vName').getAttribute('aria-label'), document.getElementById('vSub').textContent, document.getElementById('vTagTxt').textContent, JSON.stringify(__T.endInfo.tot), JSON.stringify(__T.endInfo.kos), __T.endInfo.win]"))
        await pg.tap('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=20000); await pg.wait_for_timeout(3500)
        await pg.screenshot(path=f'{WS}/ui/tally_{tag}_results.png')
        print(tag, 'bar', await pg.evaluate("(() => { const r = e => { const q = e.getBoundingClientRect(); return [Math.round(q.left), Math.round(q.top), Math.round(q.width), Math.round(q.height)]; }; return { bar: r(document.getElementById('jBar')), lab: r(document.getElementById('jLab')), ls: [...document.querySelectorAll('#jLab .jl')].map(r), nums: [...document.querySelectorAll('#jNums b')].map(b => [b.textContent, ...r(b)]) }; })()"))
        print(tag, 'results', await pg.evaluate("[document.getElementById('endWord').textContent, [...document.querySelectorAll('#board .brow')].map(r => r.getAttribute('aria-label'))]"))
        print(tag, 'log', await pg.evaluate("JSON.stringify(window.__log)")); print(tag, 'errors', errs[:4]); await ctx.close(); await b.close()
RUNS = {'port': (390, 780, 'port', 1, 4, 14), 'land': (844, 390, 'land', 3, 0, 10), 'flip': (390, 780, 'flip', 0, 5, 14)}
for k in (sys.argv[1:] or ['port', 'land']): asyncio.run(run(*RUNS[k]))
