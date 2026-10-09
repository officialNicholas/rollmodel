import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100)
        await pg.evaluate("(()=>{ __T.genWorld(5131); __T.mapUsed=false; __T.showMenu(); })()")
        await pg.wait_for_timeout(600)
        await pg.screenshot(path='gen/s_menu.png')
        await pg.click('#startBtn'); await pg.wait_for_timeout(200)
        await pg.evaluate("window.__noStep=true")
        # sink: put P in a coffin, drain it, step until mid-sink with a fixed camera on it
        info = await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; H.st='ko'; H.koT=999; for(let i=0;i<200;i++) T.step(0.012);
            const p=T.pots2.find(q=>q.y===0); P.x=p.x; P.z=p.z; P.y=p.y; P.air=false; P.spd=0; P.paint=0.6; T.step(0.012); p.ink=0.03; T.setWx('clear', 40);
            let n=0; while(p.st==='up' && n<400){ T.step(0.012); n++; } for(let i=0;i<40;i++) T.step(0.012);
            window.__cam=[[p.x+3.2, p.y+3.2, p.z+3.6],[p.x, p.y+0.2, p.z]]; return {x:p.x,z:p.z,st:p.st,t:p.t, Pst:P.st}; })()""")
        print('sink', info)
        await pg.wait_for_timeout(300); await pg.screenshot(path='gen/s_sink.png')
        info = await pg.evaluate("""(()=>{ const T=__T; const p=T.pots2.find(q=>q.st!=='up'); let n=0; while(!(p.st==='down' && p.tele.visible && p.t > 3.2) && n<800){ T.step(0.012); n++; }
            window.__cam=[[p.next[0]+3.4, p.next[1]+3.4, p.next[2]+3.8],[p.next[0], p.next[1]+0.2, p.next[2]]]; window.__pp=p; return {st:p.st, t:p.t, next:p.next}; })()""")
        print('tele', info)
        await pg.wait_for_timeout(300); await pg.screenshot(path='gen/s_tele.png')
        info = await pg.evaluate("""(()=>{ const T=__T, p=window.__pp; let n=0; while(!(p.st==='rise' && p.t>0.22) && n<400){ T.step(0.012); n++; } return {st:p.st,t:p.t}; })()""")
        print('rise', info)
        await pg.wait_for_timeout(300); await pg.screenshot(path='gen/s_rise.png')
        await pg.evaluate("""(()=>{ const T=__T, p=window.__pp; let n=0; while(p.st!=='up' && n<400){ T.step(0.012); n++; } for(let i=0;i<30;i++) T.step(0.012); })()""")
        await pg.wait_for_timeout(300); await pg.screenshot(path='gen/s_up.png')
        # sprinkler: P pounds a puddle, camera on it
        info = await pg.evaluate("""(()=>{ const T=__T, P=T.P; const r=T.rivals.find(q=>q.on&&q.y===0); P.st='play'; P.x=r.x+1.4; P.z=r.z; P.y=0; P.air=false; P.spd=0; P.paint=1; P.slamCD=0; P.immuneT=0;
            window.__cam=[[r.x+4.5, 4.8, r.z+5.2],[r.x, 0.2, r.z]]; T.useSlam(P); let n=0; while((P.air||P.slam)&&n<300){ T.step(0.012); n++; } for(let i=0;i<14;i++) T.step(0.012); return {on:r.on, drops:T.sprDrops.length}; })()""")
        print('sprinkle', info)
        await pg.wait_for_timeout(300); await pg.screenshot(path='gen/s_spr.png')
        print('errors', errs)
        await b.close()
asyncio.run(main())
