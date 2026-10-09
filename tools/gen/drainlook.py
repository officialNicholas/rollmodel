# the customize screen over half a minute: the paint running down, then a hop landing back in the puddle (it washes back up)
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'dl'
TIMES = [2.5, 6.0, 12.0, 20.0, 32.0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("Math.random = (()=>{ let s=4321; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(9000)
        await pg.evaluate("() => { const T = __T; window.__noLoop = true; T.openLook(); const id = T.idle; window.__tick = (n) => { for (let i = 0; i < n; i++) { if (id) { id.t = 99; id.act = null; id.hop = 0; } const I = T.VP.slime; if (I) { I.st.blinkT = 9; I.st.blinkK = 0; } T.visuals(1 / 60, 1 / 60); } T.renderFrame(); }; }")
        shots = []; t = 0.0
        for tt in TIMES:
            n = int(round((tt - t) * 60)); t = tt
            lv = await pg.evaluate("(n) => { window.__tick(n); return +(__T.VP.wade || 0).toFixed(2); }", n)
            fn = SP + 'rx/_dl_%02d.png' % len(shots); await pg.screenshot(path=fn); shots.append((fn, '%.0fs  level %.2f' % (tt, lv)))
        # a hop: up and back down into the puddle
        lv = await pg.evaluate("""() => { const T = __T, id = T.idle; id.act = 'bounce'; id.dur = 0.9; id.u = 0; id.t = 99; const out = [];
          for (let i = 0; i < 70; i++) { if (!id.act) id.t = 99; T.visuals(1 / 60, 1 / 60); if (i % 10 === 0) out.push(+(T.VP.wade || 0).toFixed(2)); } T.renderFrame(); out.push(+(T.VP.wade || 0).toFixed(2)); return out[out.length - 1]; }""")
        fn = SP + 'rx/_dl_hop.png'; await pg.screenshot(path=fn); shots.append((fn, 'hop, landed  level %.2f' % lv))
        ims = []
        for fn, label in shots:
            im = Image.open(fn).convert('RGB'); W, H = im.size; im = im.crop((int(W * 0.16), int(H * 0.14), int(W * 0.84), int(H * 0.48))).resize((360, int(360 * 0.34 * H / (0.68 * W)))); ims.append((im, label))
        w, h = ims[0][0].size; sheet = Image.new('RGB', (w * 3, h * 2), (16, 12, 24)); dr = ImageDraw.Draw(sheet)
        for i, (im, label) in enumerate(ims): sheet.paste(im, ((i % 3) * w, (i // 3) * h)); dr.text(((i % 3) * w + 6, (i // 3) * h + 6), label, fill=(255, 255, 255))
        sheet.save(SP + 'rx/%s_drainlook.png' % TAG); print('saved', sheet.size, errs[:3]); await b.close()
asyncio.run(main())
