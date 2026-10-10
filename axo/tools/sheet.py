# render frame sheets of the preview states and transitions (headless, deterministic stepping)
import asyncio, base64, io, sys, json, time
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/'
W = int(__import__('os').environ.get('W', '360'))
# name -> (setup states with settle seconds, capture times (s) after the last set, camera (yaw, pitch, dist, ty))
SHEETS = {
 'stand':    dict(pre=[('stand', 1.5)], times=[0, 0.7, 1.4, 2.1, 2.8, 3.5], cams=[(0.6, 0.18, 4.2, 0.85), (1.57, 0.1, 4.2, 0.85)]),
 'crawl':    dict(pre=[('crawl', 2.0)], times=[0, 0.16, 0.32, 0.48, 0.64, 0.8], cams=[(2.2, 0.35, 5.6, 0.35), (1.57, 0.12, 5.4, 0.35), (0.0, 1.35, 5.6, 0.1)]),
 'closeup':  dict(pre=[('stand', 1.5)], times=[0, 0.8, 1.6], cams=[(0.5, 0.2, 2.3, 1.35), (2.4, 0.2, 2.3, 1.35)]),
 'closeupc': dict(pre=[('crawl', 1.5)], times=[0, 0.3, 0.6], cams=[(2.0, 0.3, 2.6, 0.5), (0.6, 0.5, 2.6, 0.5)]),
 'arm': dict(js='axo.skel(true); axo.A.P.m.crawl.mesh.material.wireframe=false', pre=[('crawl', 1.5)], times=[0.1, 0.2, 0.3, 0.4], cams=[(2.6, 0.25, 2.0, 0.35)], off=(0.1, 0, 0.9)),
 'limbs': dict(js='axo.skel(true)', pre=[('crawl', 1.5)], times=[0, 0.2, 0.4, 0.6, 0.8], cams=[(2.3, 0.5, 3.2, 0.3), (0.0, 1.45, 3.4, 0.2)]),
 'power':    dict(pre=[('power', 1.2)], times=[0, 1.0, 2.0], cams=[(0.5, 0.18, 4.2, 0.85), (1.57, 0.1, 4.2, 0.85)]),
 'jetpack':  dict(pre=[('jetpack', 1.2)], times=[0, 0.5, 1.0, 1.5], cams=[(0.5, 0.1, 4.6, 1.2), (1.57, 0.05, 4.6, 1.2)]),
 'pound':    dict(pre=[('pound', 1.2)], times=[0, 0.5, 1.0], cams=[(0.5, 0.15, 4.6, 1.1), (1.57, 0.05, 4.6, 1.1)]),
 'victory':  dict(pre=[('victory', 1.0)], times=[0, 0.12, 0.24, 0.36, 0.48, 0.6], cams=[(0.5, 0.15, 4.4, 0.95)]),
 'stand2crawl': dict(pre=[('stand', 1.0), ('crawl', 0)], times=[0, 0.15, 0.3, 0.45, 0.55, 0.62, 0.69, 0.8, 1.0, 1.3], cams=[(0.9, 0.3, 4.4, 0.6), (1.57, 0.12, 4.4, 0.6)]),
 'crawl2stand': dict(pre=[('crawl', 2.0), ('stand', 0)], times=[0, 0.15, 0.3, 0.37, 0.44, 0.5, 0.65, 0.85, 1.1, 1.4], cams=[(0.9, 0.3, 4.4, 0.6), (1.57, 0.12, 4.4, 0.6)]),
 'wtest': dict(pre=[('power', 0.6), ('victory', 0.0)], times=[0, 0.3, 0.6], cams=[(0.6, 0.15, 3.0, 1.0), (2.3, 0.15, 3.0, 1.0)]),
 'crouch': dict(pre=[('crouch', 1.0)], times=[0], cams=[(1.57, 0.1, 5.0, 0.5), (0.5, 0.3, 5.0, 0.5)]),
 'restcheck': dict(js='axo.A.mesh="crawl"; axo.A.blend=1; axo.A.blendDur=0.01', pre=[('prone', 0.3), ('sym', 0.0)], times=[0, 0.5], cams=[(2.2, 0.35, 5.5, 0.4), (0.0, 1.4, 5.5, 0.2)]),
 'restcheck2': dict(js='axo.A.mesh="stand"; axo.A.blend=1; axo.A.blendDur=0.01', pre=[('rest', 0.3), ('prone', 0.0)], times=[0, 0.5], cams=[(2.2, 0.35, 5.5, 0.4), (0.0, 1.4, 5.5, 0.2)]),
}
async def main(which):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': W, 'height': W}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto('http://localhost:8765/axo/preview.html?manual&stand=' + __import__('os').environ.get('STAND', 'axo_stand'), timeout=300000); await pg.wait_for_function('window.ready', timeout=300000)
        await pg.evaluate(f'axo.size({W},{W})')
        for name in which:
            cfg = SHEETS[name]; t0 = time.time()
            rows = []
            for ci, cam in enumerate(cfg['cams']):
                await pg.evaluate(f'axo.view({cam[0]},{cam[1]},{cam[2]},{cam[3]})')
                if cfg.get('js'): await pg.evaluate(cfg['js'])
                for st, settle in cfg['pre']:
                    await pg.evaluate(f'axo.setState("{st}")'); n = int(settle * 60)
                    if n: await pg.evaluate(f'axo.step(1/60,{n})')
                ims = []; last = 0
                for tt in cfg['times']:
                    n = int(round((tt - last) * 60)); last = tt
                    if n: await pg.evaluate(f'axo.step(1/60,{n})')
                    await pg.evaluate(f'axo.view({cam[0]},{cam[1]},{cam[2]},{cam[3]})')
                    if cfg.get('off'): o = cfg['off']; await pg.evaluate(f'axo.A.P.m.crawl.mesh.position.set({-o[0]},{-o[1]},{-o[2]}); axo.A.P.m.stand.mesh.position.set({-o[0]},{-o[1]},{-o[2]})')
                    d = await pg.evaluate('axo.shot()'); im = Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')
                    info = await pg.evaluate('JSON.stringify({s: axo.A.state, m: axo.A.mesh, f: axo.A.fade.toFixed(2)})'); j = json.loads(info)
                    ImageDraw.Draw(im).text((6, 6), f'{name} t={tt:.2f} {j["s"]}/{j["m"]} fade {j["f"]}', fill=(30, 30, 60)); ims.append(im)
                rows.append(ims)
            sh = Image.new('RGB', (W * len(cfg['times']), W * len(rows)), (255, 255, 255))
            for r, ims in enumerate(rows):
                for i, im in enumerate(ims): sh.paste(im, (i * W, r * W))
            sh.save(D + f'preview_{name}.jpg', quality=85); print(name, 'done', round(time.time() - t0, 1), 's', 'errors', errs[:3]); errs.clear()
        await b.close()
asyncio.run(main(sys.argv[1:] or list(SHEETS)))
