import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ xp: 720, streak: 2, bestStreak: 3, diff: 'hard', seen: {}, wins: { hard: 4 }, played: { hard: 9 } })); } catch (e) {}")
        pg = await ctx.new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.wait_for_timeout(800); await pg.screenshot(path='gen/f_menu.png')
        # under a deck
        await pg.evaluate("(()=>{ let s=1; for(;s<400;s++){ __T.genWorld(s); if (__T.BOXES.some(b=>b[4]>2 && (b[1]-b[0])>6)) break; } __T.mapUsed=false; __T.showMenu(); })()")
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__noStep=true")
        r = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; for(let i=0;i<150;i++) T.step(0.012); const b=T.BOXES.find(b=>b[4]>2 && (b[1]-b[0])>6);
          P.st='play'; P.x=(b[0]+b[1])/2; P.z=b[2]+0.8; P.y=0; P.air=false; P.spd=0; P.yaw=0; H.ai=null; H.st='ko'; H.koT=99; return b; })()""")
        print('deck', r)
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(900); await pg.evaluate("window.__noStep=true")
        await pg.screenshot(path='gen/f_under.png')
        # a tie at the buzzer goes to overtime
        r = await pg.evaluate("""(()=>{ const T=__T; T.teamN[1]=T.teamN[2]=0; T.matchLeft=0.05; for(let i=0;i<10;i++) T.step(0.012); return {state:T.state, left:+T.matchLeft.toFixed(1)}; })()""")
        print('tie ->', r)
        await pg.evaluate("window.__noStep=false"); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/f_ot.png')
        # finish with a win and watch the blood bar fill to a rank up
        await pg.evaluate("(()=>{ const T=__T; T.H.st='ko'; T.H.koT=99; for(let i=0;i<600;i++){ T.addSplat(-20+Math.random()*40, 0, -20+Math.random()*40, 0, 1.5, 0, false, true, 0); if (T.teamCov(0)>18) break; } T.matchLeft=0.05; })()")
        await pg.wait_for_timeout(4200)
        await pg.screenshot(path='gen/f_end1.png')
        await pg.wait_for_timeout(1600)
        await pg.screenshot(path='gen/f_end2.png')
        st = await pg.evaluate("JSON.parse(localStorage.getItem('paint-world-red.v1'))")
        print('store', {k: st.get(k) for k in ['xp','streak','bestStreak','bestCov']})
        # back to the menu, then tonight's canvas
        await pg.click('#menuBtn'); await pg.wait_for_timeout(600)
        print('menu rank:', await pg.evaluate("document.getElementById('rkName').textContent + ' | ' + document.getElementById('rkInfo').textContent"))
        await pg.click('#dailyBtn'); await pg.wait_for_timeout(900)
        s1 = await pg.evaluate("__T.GEN.seed"); print('daily state', await pg.evaluate("__T.state"))
        await pg.evaluate("__T.matchLeft=0.05"); await pg.wait_for_timeout(3600)
        print('end eyebrow:', await pg.evaluate("document.getElementById('endEyebrow').textContent"))
        await pg.click('#endBtn'); await pg.wait_for_timeout(900)
        print('rematch same daily canvas:', s1 == await pg.evaluate("__T.GEN.seed"))
        print('errors', errs)
        await b.close()
asyncio.run(main())
