# world-select paintings rendered by the game: a blob near the edge, looking back at the camera, the world's horizon behind it
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
TH = sys.argv[1]; SEED = int(sys.argv[2]); COL = sys.argv[3]; WEAR = sys.argv[4] if len(sys.argv) > 4 else ''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':1100,'height':756}, device_scale_factor=1.4)
        look = "{ eyes: 'round', head: " + ("'hat'" if WEAR == 'hat' else 'null') + ", back: " + ("'wings'" if WEAR == 'wings' else 'null') + ", mouth: null }"
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', color: '" + COL + "', look: " + look + ", seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""([th, seed]) => { const T = __T; window.__noLoop = true; T.genWorld(seed, { themes: [th] }); T.mapUsed = false; T.start(); window.__noStep = false;
          for (let i = 0; i < 120; i++) T.step(0.016);
          const A = T.ARENA; let best = null;
          for (let k = 0; k < 24 && !best; k++) { const a = k / 24 * 6.283 + 0.3, R = A - 4.5, x = Math.cos(a) * R, z = Math.sin(a) * R;
            if (T.surfaceUnder(x, z, 0.3) !== 0 || T.blockedAt(x, z, 0) || T.BOXES.some(bx => bx[4] > 0 && Math.hypot((bx[0] + bx[1]) / 2 - x, (bx[2] + bx[3]) / 2 - z) < 9) || T.HOLES.some(h => Math.hypot((h[0] + h[1]) / 2 - x, (h[2] + h[3]) / 2 - z) < 5)) continue; const cx = Math.cos(a) * (R - 5.5), cz = Math.sin(a) * (R - 5.5); if (T.surfaceUnder(cx, cz, 0.3) !== 0) continue; best = { x, z, cx, cz, a }; }
          if (!best) return null;
          const P = T.P; P.x = best.x; P.z = best.z; P.y = 0; P.air = false; P.vy = 0; P.spd = 0; P.yaw = Math.atan2(best.cx - best.x, best.cz - best.z);
          // a little paint round its feet
          for (let i = 0; i < (th === 'garden' ? 2 : 3); i++) { const aa = i * 1.6 + 2.4, d = 1.9 + i * 0.5, x = P.x + Math.sin(aa) * d, z = P.z + Math.cos(aa) * d; T.addSplat(x, 0, z, aa, 0.9 + (i % 2) * 0.3, T.clock, false, true, 0); }
          T.flushTrail(); window.__noStep = true;
          for (const id of ['menu', 'hud', 'foePtr', 'foePtr2', 'orbPtr', 'soundBtn']) { const el = document.getElementById(id); if (el) el.style.visibility = 'hidden'; } document.querySelector('.corner').style.visibility = 'hidden'; document.getElementById('banner').style.display = 'none';
          for (let i = 0; i < 60; i++) T.visuals(0.016, 0.016);
          const c = T.camera, dx = Math.cos(best.a), dz = Math.sin(best.a); c.position.set(P.x - dx * 2.5, 1.35, P.z - dz * 2.5); c.lookAt(P.x + dx * 4, 0.55, P.z + dz * 4); T.post.dofK.set(0.62, 0.95, 0.9, 0.06);
          T.post.render(); return [best.a, P.x, P.z]; }""", [TH, SEED])
        await pg.screenshot(path=f'logo/{TH}_raw2.png')
        im = Image.open(f'logo/{TH}_raw2.png').convert('RGB'); W = im.width; H = round(W * 220 / 320); y0 = (im.height - H) // 2
        art = im.crop((0, y0, W, y0 + H)).resize((720, 495), Image.LANCZOS); art.save(f'logo/{TH}_art_prev.png'); art.save(f'logo/{TH}_art.webp', 'WEBP', quality=82, method=6)
        print(TH, r, errs[:3]); await b.close()
asyncio.run(main())
