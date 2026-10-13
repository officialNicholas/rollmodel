# which way each gill channel turns the ears: constant offsets added to the spring's target, seen from the front and the side
import asyncio, json, sys
sys.argv = ['x', 'pc_h.html', 'none', 'ax']
exec(open('tools/anim252.py').read().split("SCN = {")[0])
exec('CAMF = ' + open('tools/anim252.py').read().split('CAMF = ')[1].split('async def swim')[0])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx, pg, errs = await boot(b, SAVE)
        await pg.evaluate("document.getElementById('lookBtn').click()")
        await pg.wait_for_function("__T.ev('!lookIntro && lookOpen')", timeout=30000, polling=100); await pg.wait_for_timeout(800)
        await pg.evaluate("window.__tscale = 1e-9; window.__idleForce = 'still'")
        frames = []
        await pg.evaluate(CAMF)
        for cam in ['front', 'side', 'top']:
            await pg.evaluate({'front': "__camAx([0, 1.0, 4.2], [0, 0.8, 0])", 'side': "__camAx([4.2, 1.0, 0.3], [0, 0.8, 0.3])", 'top': "__camAx([0, 5, 0.6], [0, 0.6, 0.6])"}[cam])
            for X, Z in [(0, 0), (60, 0), (-60, 0), (0, 60), (0, -60)]:
                await pg.evaluate("__T.ev(`(() => { const A = VP.slime.ax.A; A.gillSpring.addTo = () => { const a = A.gillAdd.slice(); for (let j = 0; j < 6; j++) { a[j * 2] += %d; a[j * 2 + 1] += %d; } return a; }; })()`)" % (X, Z))
                await pg.evaluate("__adv(1/30, 45)")
                cx, cy = await pg.evaluate("__scr(0.8)")
                frames.append((f'{cam} x{X} z{Z}', await grab(pg, cx, cy, 300, 260, 'f')))
        sheet(frames, f'{OUT}/earaxes.png', cols=5)
        print(errs[:3]); await b.close()
asyncio.run(main())
