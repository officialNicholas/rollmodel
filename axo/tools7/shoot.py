# a labelled sheet of cells from one or more pages: spec = {out, W, H, ncol, title, pages: {name: {url, shot, size}}, cells: [[page, js, label], ...]}
# (each page is opened once; cells run in order; a cell's js runs on its page before the capture)
import asyncio, base64, io, json, sys, time
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
try: FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
except Exception: FONT = None
def label(im, text):
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
        if im.size != (W, H): im = im.resize((W, H))
        if lab: label(im, lab)
        sh.paste(im, ((k % ncol) * W, (k // ncol) * H + th))
    sh.save(out, quality=quality); return sh
async def run(spec):
    t0 = time.time(); W, H = spec.get('W', 400), spec.get('H', 400); errs = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pages = {}
        for name, pg_ in spec['pages'].items():
            pg = await b.new_page(viewport={'width': W, 'height': H}); errs[name] = []
            pg.on('pageerror', lambda e, n=name: errs[n].append(str(e)[:400])); pg.on('console', lambda m, n=name: m.type == 'error' and errs[n].append(m.text[:400]))
            await pg.goto(pg_['url'], timeout=300000); await pg.wait_for_function(pg_.get('ready', 'window.ready'), timeout=300000, polling=200)
            if pg_.get('size'): await pg.evaluate(pg_['size'].replace('$W', str(W)).replace('$H', str(H)))
            if pg_.get('init'): await pg.evaluate(pg_['init'])
            pages[name] = (pg, pg_.get('shot', 'V.shot()'))
        ims = []
        for page, js, lab in spec['cells']:
            if page is None:   # (v10: a picture from disk, cropped: {img, crop [x0, y0, x1, y1]})
                o = json.loads(js); im = Image.open(o['img']).convert('RGB'); im = im.crop(tuple(o['crop'])) if o.get('crop') else im; ims.append((im, lab)); continue
            pg, shot = pages[page]
            if js: await pg.evaluate('(async () => { ' + js + ' })()')
            if shot == 'screenshot': im = Image.open(io.BytesIO(await pg.screenshot())).convert('RGB')
            else: d = await pg.evaluate(shot); im = Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB')
            ims.append((im, lab))
        await b.close()
    compose(ims, spec.get('ncol', 4), W, H, spec['out'], title=spec.get('title'))
    print(spec['out'], len(ims), 'cells', round(time.time() - t0, 1), 's', 'errors:', {k: v[:3] for k, v in errs.items() if v})
if __name__ == '__main__':
    spec = json.load(open(sys.argv[1])) if sys.argv[1].endswith('.json') else json.loads(sys.argv[1])
    asyncio.run(run(spec))
