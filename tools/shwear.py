"""Every wearable on the character in the locker, close up: front and turned. usage: shwear.py page.html outdir [ids,comma] [w h]"""
import asyncio, sys, json
from playwright.async_api import async_playwright
PAGE, OUT = sys.argv[1], sys.argv[2]
SLOTS = {'pirate': 'head', 'tophat': 'head', 'tiara': 'head', 'beanie': 'head', 'party': 'head', 'antennae': 'head', 'propcap': 'head', 'hat': 'head', 'halo': 'head', 'bunny': 'head', 'skull': 'head',
  'patch': 'eye', 'glasses': 'eye', 'monocle': 'eye', 'snorkel': 'eye', 'hockey': 'eye', 'flower': 'side', 'bowtie': 'neck', 'pearls': 'neck', 'scarf': 'neck', 'lashes': 'lash',
  'stache': 'mouth', 'fangs': 'mouth', 'floaties': 'arms', 'cape': 'back'}
IDS = sys.argv[3].split(',') if len(sys.argv) > 3 and sys.argv[3] else list(SLOTS)
W, H = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (430, 754)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2)
        await ctx.route('**/*supabase.co/**', lambda r: r.abort()); await ctx.route('**/*fly.dev/**', lambda r: r.abort())
        allx = list(SLOTS)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'%s', name:'Dusk', seen:{look:1}, runs: 9, owned:%s, bought:%s, tut: { ph: 'done' } })); } catch (e) {}" % ('port' if H > W else 'land', json.dumps(allx), json.dumps(allx)))
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.ev("!!(typeof VP === \'object\' && VP && VP.slime)")', timeout=300000, polling=1000); await pg.wait_for_timeout(2000)
        await ev("__T.ev('openLook()')"); await pg.wait_for_timeout(16000); await ev("window.__idleForce = 'still'")
        clip = {'x': W / 2 - 130, 'y': 90, 'width': 260, 'height': 240} if H > W else {'x': W * 0.3 - 140, 'y': H * 0.12, 'width': 280, 'height': 260}
        for i in IDS:
            await ev("(() => { const L = __T.ev('myLook'); for (const k of ['head','eye','mouth','neck','side','lash','arms','back']) L[k] = null; L['%s'] = '%s'; })()" % (SLOTS[i], i))
            await pg.wait_for_timeout(6500)
            for k in range(5): await pg.screenshot(path=f'{OUT}/{i}_front.png' if k == 0 else f'{OUT}/{i}_f{k}.png', clip=clip); await pg.wait_for_timeout(1100)
            await pg.mouse.move(W / 2 - 60, 230); await pg.mouse.down()
            for k in range(8): await pg.mouse.move(W / 2 - 60 + 70 * (k + 1) / 8, 230); await pg.wait_for_timeout(30)
            await pg.mouse.up(); await pg.wait_for_timeout(500); await pg.screenshot(path=f'{OUT}/{i}_turn.png', clip=clip); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{OUT}/_full.png')
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
