"""The lab filmed to a video: a scenario at 30 frames a second from a camera following the axolotl at a fixed offset.
usage: labvid.py <scen> '<json>' <seconds> <out.mp4> [warm] [offx offy offz] [atdz]"""
import asyncio, sys, os, json, subprocess, shutil
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
SC, OPT, SECS, OUT = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
WARM = int(sys.argv[5]) if len(sys.argv) > 5 else 10
OFF = [float(x) for x in sys.argv[6:9]] if len(sys.argv) > 8 else [2.3, 1.05, 1.5]
ATDZ = float(sys.argv[9]) if len(sys.argv) > 9 else -0.3
W, H = int(os.environ.get('LW', 480)), int(os.environ.get('LH', 320))
async def main():
    tmp = f'{S}/lab/vid_{os.getpid()}'; os.makedirs(tmp, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': W, 'height': H}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/lab/index.html?v=' + str(os.getpid()), timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        await pg.evaluate("(() => { const h = document.getElementById('hud'); if (h) h.style.display = 'none'; })()")
        await pg.evaluate(f"LAB.cam = 'fixed'; LAB.set('{SC}', {OPT}); LAB.step({WARM})")
        n = int(SECS * 30)
        for i in range(n):
            await pg.evaluate(f"(() => {{ LAB.step(2); const D = LAB.D, c = Math.cos(D.yaw), s = Math.sin(D.yaw), o = {json.dumps(OFF)}; LAB.camPos = [D.x + o[0] * c + o[2] * s, o[1], D.z - o[0] * s + o[2] * c]; LAB.camAt = [D.x + {ATDZ} * s, 0.3, D.z + {ATDZ} * c]; LAB.render(); }})()")
            await pg.screenshot(path=f'{tmp}/f{i:04d}.png')
        print('frames', n, 'errors', errs[:3]); await b.close()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', f'{tmp}/f%04d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', OUT], check=True)
    shutil.rmtree(tmp); print('wrote', OUT, os.path.getsize(OUT))
asyncio.run(main())
