"""v259 app probe: the iOS build served the way the app serves it, with the internet cut off and the app's message handlers stubbed.
Save copy restored on a fresh start, kept when the web view's copy is newer, restored when it's older; saves sent to the app throttled
and flushed when the app is put away; graphics lost and restored (keeps going), lost for good (starts over); the memory signal; a match."""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/a259'
import os; os.makedirs(OUT, exist_ok=True)
BASE = 'http://127.0.0.1:8771/'
INIT = """window.__posts = window.__posts || []; const sink = n => ({ postMessage: m => { if (n === 'save') window.__posts.push(JSON.parse(JSON.stringify(m))); } });
window.webkit = { messageHandlers: { save: sink('save'), haptic: sink('haptic'), device: sink('device'), orient: sink('orient') } };
window.__NATIVE = { platform: 'ios', model: 'iPhone15,2', tier: 3, memGB: 6, lowPower: false, thermal: 0, maxFPS: 60, scale: 3 };"""
ev = lambda pg, e: pg.evaluate("__T.ev(" + json.dumps(e) + ")")
STORE = "JSON.stringify({ name: store.name, xp: store.xp, t: localStorage.getItem(KEY + '.t') })"
async def booted(pg):
    await pg.wait_for_function("typeof __T === 'object'", timeout=300000, polling=500); await pg.wait_for_timeout(1500)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True, service_workers='block')
        outside = []
        async def route(r):
            if r.request.url.startswith(BASE) or r.request.url.startswith('data:') or r.request.url.startswith('blob:'): await r.continue_()
            else: outside.append(r.request.url); await r.abort()
        await ctx.route('**/*', route)
        await ctx.add_init_script(INIT)
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
        await pg.goto(BASE + 'index.html', timeout=300000); await booted(pg)
        print('1 fresh start, app copy restored', await ev(pg, STORE), flush=True)
        await ev(pg, "store.name = 'Local'; save(); 1"); await pg.wait_for_timeout(700)
        await pg.reload(); await booted(pg); print('1b web view copy newer, kept', await ev(pg, STORE), flush=True)
        await pg.evaluate("localStorage.setItem('paint-world-red.v1', JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('paint-world-red.v1')), { name: 'Old' }))); localStorage.setItem('paint-world-red.v1.t', '5'); 1")
        await pg.reload(); await booted(pg); print('1c web view copy older, app copy wins', await ev(pg, STORE), flush=True)
        # saves to the app: a burst goes over once, put away goes at once
        await pg.evaluate("window.__posts.length = 0")
        await ev(pg, "for (let i = 0; i < 5; i++) save(); 1"); await pg.wait_for_timeout(100); n1 = await pg.evaluate("__posts.length")
        await pg.wait_for_timeout(600); n2 = await pg.evaluate("__posts.length")
        await ev(pg, "store.drops = 1234; save(); Object.defineProperty(document, 'hidden', { configurable: true, get: () => true }); document.dispatchEvent(new Event('visibilitychange')); Object.defineProperty(document, 'hidden', { configurable: true, get: () => false }); 1")
        n3 = await pg.evaluate("__posts.length"); last = await pg.evaluate("(() => { const p = __posts[__posts.length - 1]; return { t: typeof p.t, drops: JSON.parse(p.save).drops }; })()")
        print('2 posts after a burst: at 100ms', n1, 'at 700ms', n2, 'after put away', n3, last, flush=True)
        # graphics lost and given back
        await pg.evaluate("window.__marker = 1")
        await ev(pg, "window.__lc = renderer.getContext().getExtension('WEBGL_lose_context'); __lc.loseContext(); 1"); await pg.wait_for_timeout(1500)
        f0 = await ev(pg, "renderer.info.render.frame"); await ev(pg, "__lc.restoreContext(); 1"); await pg.wait_for_timeout(3000)
        f1 = await ev(pg, "renderer.info.render.frame"); lost = await ev(pg, "renderer.getContext().isContextLost()")
        await pg.screenshot(path=OUT + '/restored.png'); print('3 restored: lost', lost, 'frames', f0, '->', f1, 'same page', await pg.evaluate("window.__marker === 1"), flush=True)
        # lost for good: starts over
        await ev(pg, "window.__lc = renderer.getContext().getExtension('WEBGL_lose_context'); __lc.loseContext(); 1")
        await pg.wait_for_timeout(7000); same = await pg.evaluate("window.__marker === 1")
        await booted(pg); await pg.screenshot(path=OUT + '/restarted.png'); print('3b lost for good: same page', same, 'after restart', await ev(pg, STORE), flush=True)
        # memory signal, then a match
        await pg.evaluate("window.dispatchEvent(new PointerEvent('pointerdown')); 1"); await pg.wait_for_timeout(1500)
        b0 = await ev(pg, "AU.beat() && AU.beat().t"); await pg.evaluate("window.dispatchEvent(new Event('nativememory')); 1"); await pg.wait_for_timeout(1000)
        print('4 memory signal: sound', await ev(pg, "AU.state"), 'song clock', b0, '->', await ev(pg, "AU.beat() && AU.beat().t"), flush=True)
        await ev(pg, "start(); 1")
        await pg.wait_for_function("__T.ev('state') === 'play'", timeout=180000, polling=250); await pg.wait_for_timeout(4000)
        await pg.screenshot(path=OUT + '/match.png'); print('5 match', await ev(pg, "state"), await ev(pg, "JSON.stringify({ sound: AU.state, stage: TH && TH.id })"), flush=True)
        print('outside requests', outside); print('errors', errs[:8]); await b.close()
asyncio.run(main())
