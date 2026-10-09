import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate(r"""(()=>{ const T=__T, P=T.P, H=T.H; window.__noLoop=true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.setWx('clear', 99);
          const out=[];
          for (const [roller, sitter] of [[P, H], [H, P]]) {
            const pt = T.pots.find(p => p.y === 0 && p.g.visible && !p.occ); pt.ink = 0.8; pt.cool = 0;
            const ai = H.ai; H.ai = null;
            sitter.st='play'; sitter.x=pt.x; sitter.z=pt.z; sitter.y=pt.y; sitter.spawnImm=false; sitter.immuneT=0; T.enterPot2(sitter, pt);
            // roller lined up 2.6 units away, rolling at the coffin
            let a=0; for (let k=0;k<16;k++){ const aa=k/16*6.283, x=pt.x-Math.sin(aa)*2.6, z=pt.z-Math.cos(aa)*2.6; if (T.surfaceUnder(x,z,0.3)===0 && !T.blockedAt(x,z,0)) { a=aa; break; } }
            roller.st='play'; roller.air=false; roller.y=pt.y; roller.x=pt.x-Math.sin(a)*2.6; roller.z=pt.z-Math.cos(a)*2.6; roller.yaw=a; roller.spd=T.cfg.speed; roller.rollCD=0; roller.paint=0.5; roller.giantT=0; roller.charging=false;
            T.dodgeRoll(roller); let t=0; while (t < 0.6 && roller.st === 'play') { T.steerIn = 0; T.step(0.012); t += 0.012; }
            out.push({ roller: roller===P?'P':'H', rollerSt: roller.st, inPot: roller.pot === pt, sitterSt: sitter.st, sitterAir: sitter.air, sitterOut: Math.hypot(sitter.x-pt.x, sitter.z-pt.z).toFixed(2), pop: document.getElementById('pop').textContent, banner: document.getElementById('bannerBig').textContent });
            // reset for the next case
            if (roller.st === 'hide') { roller.st='play'; roller.pot=null; pt.occ=null; }
            for (let i=0;i<80;i++) T.step(0.012); H.ai = ai;
          }
          return out; })()""")
        for x in r: print(x)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
