"""The bottom of the screen in a portrait match, at the user's size inside the Claude app (430x754): idle, and mid slingshot pull"""
import asyncio, json
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
INFO = """(() => { const R = e => { if (!e || e.hidden) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; };
  const out = {}; for (const id of ['slamBtn', 'itemBtn', 'tutHand', 'tutGest', 'stick', 'knob']) { const e = document.getElementById(id); out[id] = e ? [R(e), e.className] : 'none'; }
  out.big = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(), cs = getComputedStyle(e); return r.bottom > innerHeight - 260 && r.width > 40 && r.height > 40 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0.05 && !e.closest('[hidden]') && e.tagName !== 'CANVAS'; }).map(e => [e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ').join('.') : ''), R(e)]).slice(0, 40);
  return out; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, drops: 50, runs: 5, flings: 50, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
        await pg.evaluate("document.getElementById('homePlay').click()")
        await pg.wait_for_function("__T.state === 'play'", timeout=300000); await pg.wait_for_timeout(5000)
        print('idle', json.dumps(await pg.evaluate(INFO)))
        await pg.screenshot(path=f'{WS}/ui/btn_idle.png')
        # a slingshot pull: touch the middle and drag down, hold
        cdp = await ctx.new_cdp_session(pg)
        async def touch(t, x, y): await cdp.send('Input.dispatchTouchEvent', {'type': t, 'touchPoints': [] if t == 'touchEnd' else [{'x': x, 'y': y}]})
        await touch('touchStart', 215, 420)
        for i in range(1, 12): await touch('touchMove', 215 - i * 4, 420 + i * 22); await pg.wait_for_timeout(40)
        await pg.wait_for_timeout(500)
        print('pull', json.dumps(await pg.evaluate(INFO)))
        await pg.screenshot(path=f'{WS}/ui/btn_pull.png')
        await touch('touchEnd', 0, 0)
        print('errors', errs)
        await b.close()
asyncio.run(main())
