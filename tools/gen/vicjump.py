# the winner's jumps on the victory screen, frame by frame: a contact sheet rx/<tag>_vic.png (crops round the winner)
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'vic'
PAGE = sys.argv[2] if len(sys.argv) > 2 else 'pc_t.html'
TIMES = [float(x) for x in (sys.argv[3] if len(sys.argv) > 3 else '0.95,1.05,1.12,1.18,1.26,1.36,1.48,1.6,1.7,1.76,1.84,1.96').split(',')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1.5, has_touch=True, is_mobile=True)
        await ctx.add_init_script("Math.random = (()=>{ let s=2468; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(600)
        await pg.evaluate(r"""(()=>{ const T=__T, P=T.P; window.__noLoop = true; T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {}; T.start(); T.setWx('clear', 999); T.aiReset(P);
          for (let i=0;i<600;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); if (P.st==='ko') { P.st='play'; P.koT=0; } }
          for (const n of T.NAVo.nodes) if (n.h === 0 && Math.random() < 0.12) T.addSplat(n.x, 0, n.z, 0, 1.2, T.dryClock, false, true, 0);
          for (let k=0;k<3 && T.state==='play';k++) { T.matchLeft = 0.01; for (let i=0;i<60 && T.state==='play';i++) T.step(0.012); }
          T.startVictory(); T.vic.happy = true; })()""")
        shots = []; t = 0.0
        for tt in TIMES:
            n = int(round((tt - t) / 0.016)); t += n * 0.016
            r = await pg.evaluate("(n) => { for (let i = 0; i < n; i++) __T.visuals(0.016, 0.016); __T.renderFrame(); const v = __T.vic, D = v.feat[0], vp = D.vicPose; return [+v.t.toFixed(2), +vp.hop.toFixed(2), +vp.sq.toFixed(2), +vp.coil.toFixed(2), vp.kick, vp.leap]; }", n)
            fn = SP + 'rx/_vj_%02d.png' % len(shots); await pg.screenshot(path=fn); shots.append((fn, r)); print(tt, r)
        ims = []
        for fn, r in shots:
            im = Image.open(fn).convert('RGB'); W, H = im.size; im = im.crop((0, int(H * 0.04), W, int(H * 0.66))).resize((300, int(300 * 0.62 * H / W))); ims.append((im, '%.2f' % r[0]))
        w, h = ims[0][0].size; cols = 6; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (w * cols, h * rows), (16, 12, 24)); dr = ImageDraw.Draw(sheet)
        for i, (im, lab) in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h)); dr.text(((i % cols) * w + 4, (i // cols) * h + 4), lab, fill=(255, 255, 255))
        sheet.save(SP + 'rx/%s_vic.png' % TAG); print('saved', sheet.size, errs[:3]); await b.close()
asyncio.run(main())
