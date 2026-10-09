# the customize screen's reactions: a new hat (a head tilt, eyes up) and a new thing on its body (a shimmy), frame by frame
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'lr'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1.5, has_touch=True, is_mobile=True)
        await ctx.add_init_script("Math.random = (()=>{ let s=4321; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', unlockAll: 1, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(9000)
        await pg.evaluate("() => { const T = __T; window.__noLoop = true; T.openLook(); for (let i = 0; i < 200; i++) { const id = T.idle; id.t = 99; T.visuals(1 / 60, 1 / 60); } }")
        rows = []
        for kind, slot, item, dur in [('tilt', 'head', 'tophat', 1.25), ('show', 'neck', 'bowtie', 1.15)]:
            await pg.evaluate("""([kind, slot, item, dur]) => { const T = __T, id = T.idle, L = T.myLook; L[slot] = item; try { T.renderLook(); } catch (e) {}
              for (let i = 0; i < 30; i++) { id.t = 99; id.act = null; T.visuals(1 / 60, 1 / 60); }
              id.act = kind; id.dur = dur; id.u = 0; id.t = 99; id.side = -1; }""", [kind, slot, item, dur])
            for k in range(8):
                await pg.evaluate("(n) => { const T = __T; for (let i = 0; i < n; i++) { T.idle.t = 99; const I = T.VP.slime; if (I) { I.st.blinkT = 9; I.st.blinkK = 0; } T.visuals(1 / 60, 1 / 60); } T.renderFrame(); }", 10)
                fn = SP + 'rx/_lr_%s_%d.png' % (kind, k); await pg.screenshot(path=fn); rows.append((fn, '%s %.2fs' % (kind, (k + 1) * 10 / 60)))
        ims = []
        for fn, label in rows:
            im = Image.open(fn).convert('RGB'); W, H = im.size; im = im.crop((int(W * 0.15), int(H * 0.1), int(W * 0.85), int(H * 0.46))).resize((240, int(240 * 0.36 * H / (0.7 * W)))); ims.append((im, label))
        w, h = ims[0][0].size; sheet = Image.new('RGB', (w * 8, h * 2), (16, 12, 24)); dr = ImageDraw.Draw(sheet)
        for i, (im, label) in enumerate(ims): sheet.paste(im, ((i % 8) * w, (i // 8) * h)); dr.text(((i % 8) * w + 4, (i // 8) * h + 4), label, fill=(255, 255, 255))
        sheet.save(SP + 'rx/%s_lookreact.png' % TAG); print('saved', sheet.size, errs[:3]); await b.close()
asyncio.run(main())
