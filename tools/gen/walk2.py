import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
W, H, TAG = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        mobile = W < 600
        ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=2 if mobile else 1, has_touch=mobile, is_mobile=mobile)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ xp: 4417, streak: 2, lastDay: 1, daily: {date:1,best:3}, diff: 'medium', seen: {}, wins: { medium: 4 }, played: { medium: 9 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and 'ERR_' not in m.text and errs.append(m.text))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(700)
        st = await pg.evaluate("JSON.parse(localStorage.getItem('paint-world-red.v1'))")
        print('store keys', sorted(st.keys()))
        print('menu canvas', await pg.evaluate("document.getElementById('cvName').textContent"), 'how', (await pg.evaluate("document.getElementById('howCtl').textContent"))[:40])
        await pg.screenshot(path=f'qol/{TAG}_1menu.png')
        names = []
        for i in range(3):
            await pg.click('#shuffleBtn'); await pg.wait_for_timeout(250)
            names.append(await pg.evaluate("[document.getElementById('cvName').textContent, __T.GEN.seed]"))
        print('shuffle', names)
        await pg.screenshot(path=f'qol/{TAG}_2shuffle.png')
        seed0 = await pg.evaluate("__T.GEN.seed")
        await pg.click('#startBtn'); await pg.wait_for_timeout(600)
        print('played seed same as menu', seed0 == await pg.evaluate("__T.GEN.seed"))
        await pg.screenshot(path=f'qol/{TAG}_3start.png')
        if not mobile:
            await pg.keyboard.down('a'); await pg.wait_for_timeout(300); await pg.keyboard.up('a')
        await pg.wait_for_timeout(1500)
        print('hint', await pg.evaluate("document.getElementById('hintText').textContent"), '| keysUI how', (await pg.evaluate("document.getElementById('howCtl').textContent"))[:30])
        # pause, restart on the same canvas
        await pg.click('#pauseBtn'); await pg.wait_for_timeout(300)
        await pg.screenshot(path=f'qol/{TAG}_4pause.png')
        s1 = await pg.evaluate("[__T.GEN.seed, __T.BOXES.length, __T.state]")
        await pg.click('#restartBtn'); await pg.wait_for_timeout(900)
        s2 = await pg.evaluate("[__T.GEN.seed, __T.BOXES.length, __T.state, __T.matchLeft.toFixed(1)]")
        print('restart same canvas', s1, s2)
        # end of match
        await pg.evaluate("(()=>{ const T=__T, P=T.P; for (let i=0;i<6;i++) T.addSplat(P.x+i*0.5, T.surfaceUnder(P.x+i*0.5,P.z,99), P.z, 0, 2, 0, false, true, 0); T.matchLeft = 0.05; })()"); await pg.wait_for_timeout(4800)
        await pg.screenshot(path=f'qol/{TAG}_5end.png')
        print('end', await pg.evaluate("({btn: document.getElementById('endBtn').innerText.replace(/\\n/g,' | '), menu: document.getElementById('menuBtn').textContent, replay: document.getElementById('replayBtn').textContent, replayHidden: document.getElementById('replayBtn').hidden, meta: document.getElementById('pMeta').textContent, note: document.getElementById('endNote').textContent, pill: !document.getElementById('endPill').hidden})"))
        s3 = await pg.evaluate("__T.GEN.seed")
        await pg.click('#replayBtn'); await pg.wait_for_timeout(900)
        print('same canvas button', s3 == await pg.evaluate("__T.GEN.seed"), await pg.evaluate("__T.state"))
        if not mobile:
            await pg.keyboard.press('p'); await pg.wait_for_timeout(200)
            await pg.keyboard.press('r'); await pg.wait_for_timeout(900)
            print('R from pause ->', await pg.evaluate("[__T.state, __T.GEN.seed === %d]" % s3))
            await pg.evaluate("(()=>{ const T=__T, P=T.P; for (let i=0;i<6;i++) T.addSplat(P.x+i*0.5, T.surfaceUnder(P.x+i*0.5,P.z,99), P.z, 0, 2, 0, false, true, 0); T.matchLeft = 0.05; })()"); await pg.wait_for_timeout(4800)
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
            print('Esc on end ->', await pg.evaluate("__T.state"))
        else:
            await pg.evaluate("(()=>{ const T=__T, P=T.P; for (let i=0;i<6;i++) T.addSplat(P.x+i*0.5, T.surfaceUnder(P.x+i*0.5,P.z,99), P.z, 0, 2, 0, false, true, 0); T.matchLeft = 0.05; })()"); await pg.wait_for_timeout(4800)
            s4 = await pg.evaluate("__T.GEN.seed")
            await pg.click('#endBtn'); await pg.wait_for_timeout(900)
            print('rematch new canvas', s4 != await pg.evaluate("__T.GEN.seed"), await pg.evaluate("__T.state"))
            await pg.click('#pauseBtn'); await pg.wait_for_timeout(200); await pg.click('#quitBtn'); await pg.wait_for_timeout(500)
            print('menu after quit', await pg.evaluate("[__T.state, document.getElementById('cvName').textContent]"))
        await pg.click('#how summary'); await pg.wait_for_timeout(300)
        await pg.evaluate("document.getElementById('menu').scrollTop = 99999"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=f'qol/{TAG}_6how.png')
        print(TAG, 'errors', errs[:4]); await b.close()
asyncio.run(main())
