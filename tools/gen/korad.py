import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100)
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__noStep=true")
        for d, hide in [(5.0,True),(5.25,True),(5.7,True)]:
            r = await pg.evaluate("""([d, hide])=>{ const T=__T, P=T.P, H=T.H; T.setWx('clear', 60);
              // open ground for both: find a ground node with room
              const n = T.NAVo.nodes.find(m => m.h===0 && m.edge===0 && T.NAVo.nodes.some(k=>k.h===0 && Math.abs(Math.hypot(k.x-m.x,k.z-m.z)-d)<0.3 && !T.blockedAt(k.x,k.z,0)) && !T.BOXES.some(b=>b[4]>0 && Math.abs(b[0]+b[1])/2-m.x<9 && false));
              let x0 = n.x, z0 = n.z, tgt;
              if (hide) { const p = T.pots2.find(q=>T.potUp(q)&&!q.occ); x0 = p.x + d; z0 = p.z; tgt = p; H.st='play'; H.koT=0; H.immuneT=0; H.x=p.x; H.z=p.z; H.y=p.y; H.air=false; H.spd=0; H.paint=1; T.step(0.012); H.immuneT=0; window.__ai=H.ai; H.ai=null; }
              else { H.st='play'; H.koT=0; H.immuneT=0; H.x=x0+d; H.z=z0; H.y=0; H.air=false; H.spd=0; H.ai.thinkT=99; }
              const hid = H.st; P.st='play'; P.x=x0; P.z=z0; P.y=hide?tgt.y:0; P.air=false; P.spd=0; P.paint=1; P.slamCD=0; P.immuneT=0;
              const hx=H.x, hz=H.z; T.useSlam(P); let k=0; while((P.air||P.slam)&&k<300){ H.x=hx; H.z=hz; H.spd=0; T.step(0.012); k++; }
              const res = {d, hid, out: H.st==='ko', reason: H.reason, sep: +Math.hypot(H.x-P.x,H.z-P.z).toFixed(2)};
              if (!H.ai) T.aiReset(H); H.st='play'; H.koT=0; return res; }""", [d, hide])
            print(r)
        # the warning ring under a slamming holy water matches the splat
        await pg.evaluate("""(()=>{ const T=__T, P=T.P, H=T.H; H.st='play'; H.immuneT=0; H.slamCD=0; H.paint=1; H.air=false; H.y=0; P.x=H.x-4.2; P.z=H.z; P.y=0; P.air=false; P.st='play'; P.yaw=Math.atan2(H.x-P.x,H.z-P.z); T.useSlam(H); for(let i=0;i<30;i++){ T.step(0.012); } })()""")
        await pg.wait_for_timeout(250); await pg.screenshot(path='gen/korad.png')
        print('errors', errs)
        await b.close()
asyncio.run(main())
