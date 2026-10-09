import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
W, H, TAG = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
async def settle(pg, n=160):
    await pg.evaluate(f"(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.0001, 0.05); __T.renderFrame(); }})()")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        mobile = W < 600
        ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=2 if mobile else 1, has_touch=mobile, is_mobile=mobile)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ diff: 'medium', seen: {}, wins: { medium: 4 }, played: { medium: 9 }, bestCov: { medium: 31 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and 'ERR_' not in m.text and errs.append(m.text))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(900)
        await settle(pg); await pg.screenshot(path=f'ui/{TAG}_1menu.png')
        # pick a color
        await pg.click('.sw[data-c="green"]'); await pg.wait_for_timeout(250); await settle(pg, 40)
        info = await pg.evaluate("({title: document.title, word: document.getElementById('logoWord').textContent, ink: getComputedStyle(document.documentElement).getPropertyValue('--ink'), pressed: [...document.querySelectorAll('.sw')].map(b=>b.getAttribute('aria-pressed')).join(','), stored: JSON.parse(localStorage.getItem('paint-world-red.v1')).color})")
        print('color', info)
        await pg.wait_for_timeout(700); await settle(pg, 60); await pg.screenshot(path=f'ui/{TAG}_2green.png')
        # how to play
        await pg.click('#howBtn'); await pg.wait_for_timeout(400)
        await pg.screenshot(path=f'ui/{TAG}_3how.png')
        print('how open', await pg.evaluate("!document.getElementById('howModal').hidden"), 'focus', await pg.evaluate("document.activeElement.id"))
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
        print('how closed by Esc', await pg.evaluate("document.getElementById('howModal').hidden"), 'state', await pg.evaluate("__T.state"))
        # difficulty and shuffle
        await pg.click('#stages button[data-d="hard"]'); await pg.wait_for_timeout(150)
        print('diff', await pg.evaluate("[__T.diff, [...document.querySelectorAll('#stages button')].map(b=>b.getAttribute('aria-pressed')).join(',')]"))
        names = []
        for i in range(2):
            await pg.click('#shuffleBtn'); await pg.wait_for_timeout(300)
            names.append(await pg.evaluate("document.getElementById('cvName').textContent"))
        print('shuffle', names)
        await settle(pg); await pg.screenshot(path=f'ui/{TAG}_4shuffle.png')
        # play
        await pg.click('#startBtn'); await pg.wait_for_timeout(2500)
        print('banner', await pg.evaluate("document.getElementById('bannerBig').textContent"), 'state', await pg.evaluate("__T.state"))
        await pg.screenshot(path=f'ui/{TAG}_5play.png')
        # roll
        if mobile:
            r = await pg.evaluate("""(async()=>{ const P=__T.P; await new Promise(r=>setTimeout(r,300)); const cv=document.getElementById('cv'); const x=195, y=600; const ev=(t,yy)=>cv.dispatchEvent(new PointerEvent(t,{pointerId:7,pointerType:'touch',clientX:x,clientY:yy,bubbles:true,isPrimary:true}));
              const before={air:P.air, st:P.st, spd:P.spd}; ev('pointerdown',y); await new Promise(r=>setTimeout(r,30)); ev('pointermove',y-20); await new Promise(r=>setTimeout(r,30)); ev('pointermove',y-70); const rolled=P.rollT>0; await new Promise(r=>setTimeout(r,30)); ev('pointerup',y-70); return {before, rolled, rollT:P.rollT, spd:P.spd.toFixed(2), cd:P.rollCD.toFixed(2)}; })()""")
        else:
            await pg.wait_for_timeout(300)
            await pg.keyboard.press('Shift')
            r = await pg.evaluate("({rolled: __T.P.rollT > 0, rollT: __T.P.rollT, spd: __T.P.spd.toFixed(2), cd: __T.P.rollCD.toFixed(2), air: __T.P.air})")
        print('roll', r)
        await pg.wait_for_timeout(120); await pg.screenshot(path=f'ui/{TAG}_6roll.png')
        await pg.wait_for_timeout(1200)
        print('hint', await pg.evaluate("document.getElementById('hintText').textContent"))
        # pause
        await pg.click('#pauseBtn'); await pg.wait_for_timeout(350)
        print('pause', await pg.evaluate("[document.getElementById('pauseYou').textContent, document.getElementById('pauseClock').textContent, document.getElementById('pauseCpu').textContent, document.activeElement.id]"))
        await pg.screenshot(path=f'ui/{TAG}_7pause.png')
        await pg.click('#resumeBtn'); await pg.wait_for_timeout(300)
        # end
        await pg.evaluate("(()=>{ const T=__T, P=T.P; for (let i=0;i<8;i++) T.addSplat(P.x+i*0.5, T.surfaceUnder(P.x+i*0.5,P.z,99), P.z, 0, 2.2, 0, false, true, 0); P.kos = 2; T.H.kos = 1; T.H.flats = 1; T.matchLeft = 0.05; })()"); await pg.wait_for_function("!document.getElementById('end').hidden", polling=200, timeout=90000); await pg.wait_for_timeout(900)
        await pg.screenshot(path=f'ui/{TAG}_8end.png')
        print('end', await pg.evaluate("({title: document.getElementById('endTitle').textContent, cls: document.getElementById('endTitle').className, you: document.getElementById('endPct').textContent, cpu: document.getElementById('endPctC').textContent, winYou: document.getElementById('chipYou').classList.contains('win'), stats: document.getElementById('endStats').innerText.replace(/\\n/g,' | '), placard: document.getElementById('pTitle').textContent + ' / ' + document.getElementById('pMeta').textContent})"))
        await pg.click('#menuBtn'); await pg.wait_for_timeout(600); await settle(pg)
        print('back to menu', await pg.evaluate("[__T.state, document.getElementById('logoWord').textContent]"))
        await pg.screenshot(path=f'ui/{TAG}_9menu.png')
        print(TAG, 'errors', errs[:6]); await b.close()
asyncio.run(main())
