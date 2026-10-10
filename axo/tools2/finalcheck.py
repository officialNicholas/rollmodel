import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 400, 'height': 400}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto('http://localhost:8765/axo/preview.html?manual', timeout=600000); await pg.wait_for_function('window.ready', timeout=600000)
        r = await pg.evaluate('''() => { const out = {}; for (const st of ['stand','crawl','power','victory','pound','jetpack','stand']) { axo.setState(st); axo.step(1/60, 90); out[st] = axo.A.state + '/' + axo.A.mesh; } return out; }''')
        d = await pg.evaluate('axo.shot()'); import base64; open('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/v2_final_preview_shot.jpg', 'wb').write(base64.b64decode(d.split(',')[1]))
        print('final preview states:', r, 'errors:', errs[:5]); await b.close()
asyncio.run(main())
