"""Gallery photos: a stage on its own (no characters, no HUD), the whole arena from a high corner, rendered large and scaled down to the
frame's 720x495 (or a custom size). usage: stagephoto.py stageId tag [az el dist fov]  (az, el in degrees; dist in units of ARENA)
env: W, H (render size, default 1440x990), OUT (final size, default 720x495)"""
import asyncio, os, sys, functools, json, math
from playwright.async_api import async_playwright
from PIL import Image
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; PAGE = os.environ.get('PAGE', 'pc_h.html')
SID, TAG = sys.argv[1], sys.argv[2]; AZ, EL, DIST, FOV = [float(x) for x in (sys.argv[3:7] if len(sys.argv) >= 7 else ['40', '38', '1.9', '34'])]
W, H = int(os.environ.get('W', 1440)), int(os.environ.get('H', 990)); OW, OH = [int(x) for x in os.environ.get('OUT', '720x495').split('x')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1, roll: 1, pound: 1, missile: 1, burst: 1 }, drops: 0, runs: 5, stage: '" + SID + "', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000, polling=100); await pg.wait_for_timeout(1000)
        await ev("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=600000, polling=100); await pg.wait_for_timeout(1500)
        print('stage', await ev("[__T.TH.id, __T.ARENA]"))
        await ev("""(() => { __T.state = 'paused'; document.getElementById('hud').classList.add('off'); for (const id of ['banner', 'pop', 'hint']) { const e = document.getElementById(id); if (e) e.style.display = 'none'; }
          __T.ev(`for (const D of [P, H, H2]) { try { koHide(D); lookRoot(D).visible = false; } catch (e) {} } try { orb.g.visible = false; orb.ring.visible = false; } catch (e) {} try { potCue.visible = false; } catch (e) {} try { for (const q of powers) if (q.g) q.g.visible = false; } catch (e) {}`); })()""")
        az, el, fov = math.radians(AZ), math.radians(EL), FOV
        await ev("""(() => { const A = __T.ARENA, d = A * %f, az = %f, el = %f; __T.camera.fov = %f; __T.camera.updateProjectionMatrix();
          __T.dPos.set(Math.sin(az) * Math.cos(el) * d, Math.sin(el) * d, Math.cos(az) * Math.cos(el) * d); __T.dLook.set(0, 0, 0); __T.camSnap = true; })()""" % (DIST, az, el, fov))
        await pg.wait_for_timeout(2500)
        raw = f'{WS}/ui/photo_{TAG}_raw.png'; await pg.screenshot(path=raw)
        im = Image.open(raw).convert('RGB'); k = max(OW / im.size[0], OH / im.size[1]); im = im.resize((round(im.size[0] * k), round(im.size[1] * k)), Image.LANCZOS)
        l = (im.size[0] - OW) // 2; t = (im.size[1] - OH) // 2; im = im.crop((l, t, l + OW, t + OH)); im.save(f'{WS}/ui/photo_{TAG}.png'); print('saved', f'photo_{TAG}.png', im.size, 'errors', errs[:3])
        await b.close()
asyncio.run(main())
