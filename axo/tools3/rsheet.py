# reusable sheet renderer: open a page once, run each cell's setup JS, capture with shotJS, compose a labelled grid
import asyncio, base64, io, json, sys, time
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
try: FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
except Exception: FONT = None
async def open_page(p, url, W, H):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    pg = await b.new_page(viewport={'width': W, 'height': H}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:400])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:400]))
    await pg.goto(url, timeout=300000); await pg.wait_for_function('window.ready', timeout=300000)
    return b, pg, errs
def label(im, text, scale=1):
    d = ImageDraw.Draw(im); x, y = 5, 4
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1): d.text((x + dx, y + dy), text, fill=(255, 255, 255), font=FONT)
    d.text((x, y), text, fill=(20, 20, 60), font=FONT)
def compose(cells, ncol, W, H, out, quality=88, title=None):
    nrow = (len(cells) + ncol - 1) // ncol; th = 22 if title else 0
    sh = Image.new('RGB', (W * ncol, H * nrow + th), (255, 255, 255))
    if title: ImageDraw.Draw(sh).text((6, 4), title, fill=(10, 10, 10), font=FONT)
    for k, (im, lab) in enumerate(cells):
        im = im.copy()
        if lab: label(im, lab)
        sh.paste(im, ((k % ncol) * W, (k // ncol) * H + th))
    sh.save(out, quality=quality); return sh
async def grab(pg, shot_js='axo.shot()'):
    d = await pg.evaluate(shot_js); return Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')
async def render(url, cells, ncol, W, H, out, shot_js='axo.shot()', init_js=None, size_js=None, title=None, verbose=True):
    """cells: list of (js, label); js runs before each capture (it can step the animation, move the camera, ...)"""
    t0 = time.time()
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, url, W, H)
        if size_js: await pg.evaluate(size_js)
        if init_js: await pg.evaluate(init_js)
        ims = []
        for js, lab in cells:
            if js: r = await pg.evaluate(js)
            ims.append((await grab(pg, shot_js), lab))
        await b.close()
    compose(ims, ncol, W, H, out, title=title)
    if verbose: print(out, len(cells), 'cells', round(time.time() - t0, 1), 's', 'errors:', errs[:3])
    return errs
if __name__ == '__main__':
    spec = json.load(open(sys.argv[1]))
    asyncio.run(render(spec['url'], [tuple(c) for c in spec['cells']], spec.get('ncol', 4), spec.get('W', 400), spec.get('H', 400), spec['out'], spec.get('shot', 'axo.shot()'), spec.get('init'), spec.get('size'), spec.get('title')))
