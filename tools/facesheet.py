import asyncio, base64, sys
sys.argv = ['x', sys.argv[1] if len(sys.argv) > 1 else 'pc_252.html', 'none', 'fs']
exec(open('tools/anim252.py').read().split("SCN = {")[0])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx, pg, errs = await boot(b, SAVE)
        for k in ['col', 'msk']:
            d = await pg.evaluate(f"__T.ev(`(() => {{ const sh = AXO.makeFaceSheets(200), c = document.createElement('canvas'); c.width = sh.col.width; c.height = sh.col.height; const g = c.getContext('2d'); g.fillStyle = '#e8a0a8'; g.fillRect(0, 0, c.width, c.height); g.drawImage(sh.{k}, 0, 0); g.strokeStyle = '#333'; for (let i = 0; i <= 4; i++) {{ g.beginPath(); g.moveTo(i * 200, 0); g.lineTo(i * 200, c.height); g.stroke(); }} for (let j = 0; j <= 8; j++) {{ g.beginPath(); g.moveTo(0, j * 200); g.lineTo(800, j * 200); g.stroke(); }} g.fillStyle = '#000'; g.font = '16px sans-serif'; for (let i = 0; i < 32; i++) g.fillText(String(i), (i % 4) * 200 + 6, Math.floor(i / 4) * 200 + 18); return c.toDataURL(); }})()`)")
            open(f'{OUT}/facesheet_{k}.png', 'wb').write(base64.b64decode(d.split(',')[1]))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
