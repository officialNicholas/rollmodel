# paintings for the world select, rendered by the game itself: python3 gen/cardart.py theme seed
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
TH = sys.argv[1]; SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 4242; COL = sys.argv[3] if len(sys.argv) > 3 else 'red'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':1100,'height':760}, device_scale_factor=1.5)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', color: 'orange', look: { eyes: 'round', head: null, back: null, mouth: null }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(800)
        await pg.evaluate("""([th, seed, col]) => { const T = __T; window.__noLoop = true; T.genWorld(seed, { themes: [th] }); T.mapUsed = false; T.resetRun(); T.decorate(); T.menuPose(); T.setColor(col); }""", [TH, SEED, COL])
        await pg.click('#lookBtn'); await pg.wait_for_timeout(200)
        pos = await pg.evaluate("""() => { const T = __T;
          for (const id of ['menu', 'hud', 'look']) document.getElementById(id).style.visibility = 'hidden'; document.querySelector('.corner').style.visibility = 'hidden';
          for (let i = 0; i < 160; i++) T.visuals(0.016, 0.04); T.renderFrame();
          const b = T.body, v = new THREE.Vector3(); b.getWorldPosition(v); v.project(T.camera); return [(v.x + 1) / 2 * innerWidth, (1 - v.y) / 2 * innerHeight]; }""")
        await pg.screenshot(path=f'logo/{TH}_raw.png')
        im = Image.open(f'logo/{TH}_raw.png').convert('RGB'); s = im.width / 1100
        cx, cy = pos[0] * s, pos[1] * s; W = im.width * 0.7; H = W * 220 / 320
        x0 = max(0, min(im.width - W, cx - W * 0.5)); y0 = max(0, min(im.height - H, cy - H * 0.58))
        art = im.crop((int(x0), int(y0), int(x0 + W), int(y0 + H))).resize((720, 495), Image.LANCZOS)
        art.save(f'logo/{TH}_art_prev.png'); art.save(f'logo/{TH}_art.webp', 'WEBP', quality=82, method=6)
        print(TH, pos, errs[:3]); await b.close()
asyncio.run(main())
