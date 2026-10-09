# the match's opening, frame by frame: the countdown from the basins (eyes peeking out of the paint, then out onto the floor) to Go and a
# moment after; a contact sheet rx/<tag>_intro.png with the time on each frame
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'intro'
PAGE = sys.argv[2] if len(sys.argv) > 2 else 'pc_t.html'
STAGE = sys.argv[4] if len(sys.argv) > 4 else 'island'
CAM = sys.argv[5] if len(sys.argv) > 5 else ''
KIND = sys.argv[6] if len(sys.argv) > 6 else ''
TIMES = [float(x) for x in (sys.argv[3] if len(sys.argv) > 3 else '0.3,0.7,1.1,1.4,1.7,2.0,2.3,2.6,2.9,3.2,3.5,3.9').split(',')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1.5, has_touch=True, is_mobile=True)
        await ctx.add_init_script("Math.random = (()=>{ let s=97531; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); window.__skipIntro = false; window.__introKind = '" + KIND + "'; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        await pg.evaluate("""(stage) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(stage === 'crypt' ? 4242 : 88, { themes: [stage] }); T.mapUsed = false;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          document.getElementById('menu').hidden = true; T.beginMatch(); window.__it = 0; }""", STAGE)
        shots = []; t = 0.0
        for tt in TIMES:
            n = int(round((tt - t) * 60)); t = tt
            info = await pg.evaluate("""([n, cam]) => { const T = __T, P = T.P; for (let i = 0; i < n; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } window.__dbg = [P.ip ? P.ip.expr : null, P.introAct ? +P.introAct.tLand.toFixed(2) : null, T.H.introKind];
              if (cam === 'rv') { const R = T.H, c = T.camera, bx = window.__rvx = window.__rvx !== undefined ? window.__rvx : R.x, bz = window.__rvz = window.__rvz !== undefined ? window.__rvz : R.z, fx = Math.sin(R.yaw), fz = Math.cos(R.yaw);
                c.position.set(bx + fx * 4.5 + fz * 1.5, R.y + 2.2, bz + fz * 4.5 - fx * 1.5); c.lookAt(bx + fx * 1.2, R.y + 0.6, bz + fz * 1.2); c.fov = 40; c.updateProjectionMatrix(); c.updateMatrixWorld(); window.__rvInfo = [R.introKind, R.st]; }
              else if (cam) { const C = P.introCrawl, b = window.__bas || (window.__bas = C ? { x: C.cx, z: C.cz, fx: C.fx, fz: C.fz } : null); if (b) { const c = T.camera, rx = b.fz, rz = -b.fx, sd = cam === 'side' ? 1 : -1;
                c.position.set(b.x + b.fx * 1.4 + rx * 7.5 * sd, P.y + 1.3, b.z + b.fz * 1.4 + rz * 7.5 * sd); c.lookAt(b.x + b.fx * 1.4, P.y + 0.5, b.z + b.fz * 1.4); c.fov = 26; c.updateProjectionMatrix(); c.updateMatrixWorld(); } }
              T.renderFrame();
              return [T.state, P.st, +P.y.toFixed(2), +T.VP.root.position.y.toFixed(2), !!P.introLeap, !!P.introOut, document.getElementById('countN').textContent, +T.introT.toFixed(2), window.__dbg]; }""", [n, CAM])
            fn = SP + 'rx/_in_%02d.png' % len(shots); await pg.screenshot(path=fn); shots.append((fn, '%.1fs %s' % (tt, info)))
            print(tt, info)
        ims = []
        for fn, label in shots:
            im = Image.open(fn).convert('RGB'); W, H = im.size; im = im.crop((0, int(H * 0.12), W, int(H * 0.8))).resize((270, int(270 * 0.68 * H / W))) if not CAM else im.crop((0, int(H * 0.36), W, int(H * 0.64))).resize((540, int(540 * 0.28 * H / W))); ims.append((im, label))
        w, h = ims[0][0].size; cols = 6 if not CAM else 3; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (w * cols, h * rows), (16, 12, 24)); dr = ImageDraw.Draw(sheet)
        for i, (im, label) in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h)); dr.text(((i % cols) * w + 4, (i // cols) * h + 4), label.split(' ')[0], fill=(255, 255, 255))
        sheet.save(SP + 'rx/%s_intro.png' % TAG); print('saved', sheet.size)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
