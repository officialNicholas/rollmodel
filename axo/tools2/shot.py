# generic headless sheet renderer: open a page, run a js setup per cell, capture; compose a grid with labels
import asyncio, base64, io, json, time
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
async def open_page(p, url, W, H):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    pg = await b.new_page(viewport={'width': W, 'height': H}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:400]))
    await pg.goto(url, timeout=120000); await pg.wait_for_function("window.ready", timeout=120000)
    return b, pg, errs
def grid(cells, ncol, W, H):
    nrow = (len(cells) + ncol - 1) // ncol; sh = Image.new('RGB', (W * ncol, H * nrow), (255, 255, 255))
    for k, (im, label) in enumerate(cells):
        im = im.copy(); ImageDraw.Draw(im).text((6, 6), label, fill=(20, 20, 60)); sh.paste(im, ((k % ncol) * W, (k // ncol) * H))
    return sh
async def capture(pg, js_list, shot_js='shot()'):
    out = []
    for js in js_list:
        await pg.evaluate(js); d = await pg.evaluate(shot_js); out.append(Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB'))
    return out
