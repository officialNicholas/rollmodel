"""Locker paint dip probe: open the locker, tap a new color, and film the dip (screenshots with the dip's own clock), then contact sheet.
usage: lkdip.py [tag] [color index] [w h]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'; CI = int(sys.argv[2]) if len(sys.argv) > 2 else 3
W, H = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (360, 640)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1, has_touch=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 40, runs: 3, tut: { done: true } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100)
        await pg.wait_for_timeout(2500); await ev("__T.openLook()"); await pg.wait_for_timeout(9000)
        await ev("window.__tscale = " + str(float(__import__("os").environ.get("TS", "0.18"))))
        for k in range(12):  # (the locker's opening drop must be over before a pick dips)
            await ev(f"document.querySelectorAll('#swatches .sw')[{(CI + k) % 6}].click()")
            await pg.wait_for_timeout(300)
            if await ev("!!__T.lkDip"): break
            await pg.wait_for_timeout(2000)
        shots = []
        for i in range(140):
            d = await ev("(() => { const D = __T.lkDip; return D ? { t: +D.t.toFixed(3), y: +D.pose.y.toFixed(2), p: +D.pose.pitch.toFixed(2), s: +D.pose.spin.toFixed(2), sw: D.swapped, col: __T.AXOC.S.list[0].ax.look.U.uPaint.value.getHexString() } : null; })()")
            if d is None and i > 2: break
            path = f'{WS}/ui/lkdip_{TAG}_{i:02d}.png'; await pg.screenshot(path=path); shots.append((path, d)); print(i, d)
        print('errors', errs[:3]); await b.close()
        # contact sheet
        from PIL import Image, ImageDraw
        if not any(d for _, d in shots): print('no dip'); return
        ims = [(Image.open(pth), d) for pth, d in shots if d]
        sel = ims[::max(1, len(ims) // 16)][:16]; cw, ch = W // 2, H // 2; cols = 8; rows = (len(sel) + cols - 1) // cols
        sheet = Image.new('RGB', (cw * cols, ch * rows), 'white'); dr = ImageDraw.Draw(sheet)
        for k, (im, d) in enumerate(sel):
            x, y = (k % cols) * cw, (k // cols) * ch; sheet.paste(im.convert('RGB').resize((cw, ch)), (x, y)); dr.text((x + 4, y + 4), f"t {d['t']}", fill='black')
        sheet.save(f'{WS}/ui/lkdip_{TAG}_sheet.jpg', quality=85); print('sheet', len(sel))
asyncio.run(main())
