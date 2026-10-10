# render frame sheets of the preview states and transitions (headless, deterministic stepping)
import asyncio, base64, io, sys, json, time, os
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
W = int(os.environ.get('W', '400')); PREFIX = os.environ.get('PREFIX', 'p2_')
# name -> (states with settle seconds, capture times after the last set, cameras (yaw, pitch, dist, ty [, tx, tz, fov]))
SHEETS = {
 'stand':    dict(pre=[('stand', 1.5)], times=[0, 0.7, 1.4, 2.1, 2.8, 3.5], cams=[(0.6, 0.18, 4.2, 0.85), (1.57, 0.1, 4.2, 0.85), (0.0, 0.1, 4.2, 0.85)]),
 'crawl':    dict(pre=[('crawl', 2.0)], times=[0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9], cams=[(2.2, 0.35, 5.0, 0.3), (1.57, 0.12, 5.0, 0.3), (0.0, 1.35, 5.0, 0.0), (0.3, 0.2, 4.6, 0.3)]),
 'crawltail': dict(pre=[('crawl', 2.0)], times=[0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9], cams=[(0.0, 1.4, 3.2, 0.0, 0.3, -0.9), (2.6, 0.3, 3.0, 0.3, 0.3, -0.8)]),
 'crawlhands': dict(pre=[('crawl', 2.0)], times=[0, 0.12, 0.24, 0.36, 0.48, 0.6, 0.72, 0.84], cams=[(0.5, 0.5, 1.6, 0.15, 0.0, 0.9), (1.4, 0.3, 1.6, 0.15, 0.35, 0.85)]),
 'head':     dict(pre=[('stand', 1.5)], times=[0, 0.8, 1.6, 2.4, 3.2], cams=[(0.0, 0.1, 2.0, 1.35), (1.57, 0.1, 2.0, 1.35), (0.0, 1.45, 2.0, 1.3), (0.6, 0.25, 2.0, 1.35)]),
 'headc':    dict(pre=[('crawl', 1.5)], times=[0, 0.3, 0.6, 0.9], cams=[(0.0, 0.1, 2.2, 0.45, 0, 0.6), (1.57, 0.15, 2.2, 0.45, 0, 0.6), (0.0, 1.45, 2.2, 0.3, 0, 0.6)]),
 'lookgill': dict(js='axo.setLook(50,-10)', pre=[('stand', 2.0)], times=[0, 0.6], cams=[(2.2, 0.3, 1.5, {'j': 'gill1.R.1'}), (-1.2, 0.4, 1.5, {'j': 'gill1.R.1'}), (0.3, 1.2, 1.6, {'j': 'head', 'off': [0, 0.3, 0]}), (2.6, 0.2, 1.5, {'j': 'gill1.L.1'})]),
 'lookgill2': dict(js='axo.setLook(-50,-10)', pre=[('stand', 2.0)], times=[0, 0.6], cams=[(2.2, 0.3, 1.5, {'j': 'gill1.R.1'}), (-1.2, 0.4, 1.5, {'j': 'gill1.R.1'}), (0.3, 1.2, 1.6, {'j': 'head', 'off': [0, 0.3, 0]})]),
 'look':     dict(js='axo.setLook(55,-15)', pre=[('stand', 1.5)], times=[0, 0.5], cams=[(0.0, 0.1, 2.0, 1.35), (0.0, 1.45, 2.0, 1.3), (1.57, 0.1, 2.0, 1.35)]),
 'hands':    dict(pre=[('stand', 1.0)], times=[0], probe=True, cams=[(0.3, -0.3, 1.0, 0.62, 0.52, 0.2, 30), (1.3, -0.2, 1.0, 0.62, 0.52, 0.2, 30), (-0.3, -0.3, 1.0, 0.62, -0.5, 0.1, 30), (-1.3, -0.2, 1.0, 0.62, -0.5, 0.1, 30)]),
 'fists':    dict(pre=[('pound', 1.0)], times=[0], probe=True, cams=[(0.3, 0.3, 0.9, {'j': 'hand.L'}), (1.3, 0.3, 0.9, {'j': 'hand.L'}), (-0.3, -0.5, 0.9, {'j': 'hand.L'}), (-0.3, 0.3, 0.9, {'j': 'hand.R'}), (-1.3, 0.3, 0.9, {'j': 'hand.R'}), (0.3, -0.5, 0.9, {'j': 'hand.R'})]),
 'vhands':   dict(pre=[('victory', 1.0)], times=[0, 0.3], probe=True, cams=[(0.3, 0.3, 1.2, {'j': 'hand.L'}), (-0.3, 0.3, 1.2, {'j': 'hand.R'})]),
 'phands':   dict(pre=[('power', 1.0)], times=[0], probe=True, cams=[(0.5, 0.2, 1.1, {'j': 'hand.L'}), (-0.5, 0.2, 1.1, {'j': 'hand.R'}), (1.57, 0.2, 1.1, {'j': 'hand.L'})]),
 'feet':     dict(pre=[('stand', 1.0)], times=[0], cams=[(0.3, 0.4, 1.0, 0.08, 0.3, 0.15, 30), (1.5, 0.3, 1.0, 0.08, 0.3, 0.15, 30), (-0.3, 0.4, 1.0, 0.08, -0.3, 0.1, 30), (-1.5, 0.3, 1.0, 0.08, -0.3, 0.1, 30)]),
 'power':    dict(probe=True, pre=[('power', 1.2)], times=[0, 1.0, 2.0], cams=[(0.5, 0.18, 4.2, 0.85), (1.57, 0.1, 4.2, 0.85), (0.0, 0.1, 4.2, 0.85)]),
 'jetpack':  dict(probe=True, pre=[('jetpack', 1.2)], times=[0, 0.5, 1.0, 1.5], cams=[(0.5, 0.1, 4.6, 1.2), (1.57, 0.05, 4.6, 1.2), (0.0, 0.1, 4.6, 1.2)]),
 'pound':    dict(probe=True, pre=[('pound', 1.2)], times=[0, 0.5, 1.0], cams=[(0.5, 0.15, 4.6, 1.1), (1.57, 0.05, 4.6, 1.1), (0.0, 0.1, 4.6, 1.1)]),
 'victory':  dict(probe=True, pre=[('victory', 1.0)], times=[0, 0.12, 0.24, 0.36, 0.48, 0.6], cams=[(0.5, 0.15, 4.4, 0.95), (1.57, 0.1, 4.4, 0.95)]),
 'stand2crawl': dict(pre=[('stand', 1.0), ('crawl', 0)], times=[0, 0.1, 0.2, 0.28, 0.33, 0.36, 0.4, 0.48, 0.65, 1.0], cams=[(0.9, 0.3, 4.4, 0.6), (1.57, 0.12, 4.4, 0.6)]),
 'crawl2stand': dict(pre=[('crawl', 2.0), ('stand', 0)], times=[0, 0.1, 0.2, 0.27, 0.31, 0.34, 0.38, 0.5, 0.7, 1.0], cams=[(0.9, 0.3, 4.4, 0.6), (1.57, 0.12, 4.4, 0.6)]),
 'crouch':   dict(pre=[('crouch', 1.0)], times=[0], cams=[(1.57, 0.1, 4.6, 0.5), (0.5, 0.3, 4.6, 0.5), (0.0, 0.1, 4.6, 0.5)]),
}
def viewjs(cam, mesh):
    j = cam[3]; off = j.get('off', [0, 0, 0]); fov = cam[4] if len(cam) > 4 else 30
    return f'(()=>{{const p=axo.joint("{mesh}","{j["j"]}"); axo.view({cam[0]},{cam[1]},{cam[2]},p[1]+{off[1]},p[0]+{off[0]},p[2]+{off[2]},{fov});}})()'
async def main(which):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': W, 'height': W}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto('http://localhost:8765/axo2/preview.html?manual', timeout=600000); await pg.wait_for_function('window.ready', timeout=600000)
        await pg.evaluate(f'axo.size({W},{W})')
        for name in which:
            cfg = SHEETS[name]; t0 = time.time(); rows = []
            for ci, cam in enumerate(cfg['cams']):
                if not isinstance(cam[3], dict): await pg.evaluate(f'axo.view({",".join(str(x) for x in cam)})')
                await pg.evaluate('axo.setLook(0,0)')
                if cfg.get('js'): await pg.evaluate(cfg['js'])
                for st, settle in cfg['pre']:
                    await pg.evaluate(f'axo.setState("{st}")'); n = int(settle * 60)
                    if n: await pg.evaluate(f'axo.step(1/60,{n})')
                ims = []; last = 0
                for tt in cfg['times']:
                    n = int(round((tt - last) * 60)); last = tt
                    if n: await pg.evaluate(f'axo.step(1/60,{n})')
                    await pg.evaluate(viewjs(cam, await pg.evaluate('axo.A.mesh')) if isinstance(cam[3], dict) else f'axo.view({",".join(str(x) for x in cam)})')
                    d = await pg.evaluate('axo.shot()'); im = Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')
                    if cfg.get('probe'): print(name, tt, await pg.evaluate('JSON.stringify(axo.probe())')); im = Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')
                    j = json.loads(await pg.evaluate('JSON.stringify({s: axo.A.state, m: axo.A.mesh, f: axo.A.fade.toFixed(2)})'))
                    ImageDraw.Draw(im).text((6, 6), f'{name} t={tt:.2f} {j["s"]}/{j["m"]} fade {j["f"]}', fill=(30, 30, 60)); ims.append(im)
                rows.append(ims)
            sh = Image.new('RGB', (W * len(cfg['times']), W * len(rows)), (255, 255, 255))
            for r, ims in enumerate(rows):
                for i, im in enumerate(ims): sh.paste(im, (i * W, r * W))
            sh.save(D + f'{PREFIX}{name}.jpg', quality=85); print(name, 'done', round(time.time() - t0, 1), 's', 'errors', errs[:3]); errs.clear()
        await b.close()
asyncio.run(main(sys.argv[1:] or list(SHEETS)))
