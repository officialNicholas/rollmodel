"""Boot timing: the loading screen's steps and the last step's parts (the character pack, attaching it, the shader warm-up), with an
optional network throttle (kbps) to stand in for a phone's connection. usage: loadprobe.py URL [kbps] [latency_ms]"""
import asyncio, sys, json, time
from playwright.async_api import async_playwright
URL = sys.argv[1]; KBPS = float(sys.argv[2]) if len(sys.argv) > 2 else 0; LAT = float(sys.argv[3]) if len(sys.argv) > 3 else 0
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient: 'port', name: 'Dusk', tut: { ph: 'done' }, runs: 5, xp: 300, seen: { look: 1 } })); } catch (e) {} window.__steps = []; const T0 = performance.now(); new MutationObserver(() => { const m = document.getElementById('bootMsg'); if (m && (!__steps.length || __steps[__steps.length - 1][0] !== m.textContent)) __steps.push([m.textContent, Math.round(performance.now())]); }).observe(document, { subtree: true, childList: true, characterData: true });")
        pg = await ctx.new_page()
        if KBPS:
            cdp = await ctx.new_cdp_session(pg); await cdp.send('Network.enable')
            await cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': LAT, 'downloadThroughput': KBPS * 1000 / 8, 'uploadThroughput': 750 * 1000 / 8})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.text[:300]) if m.type in ('error', 'warning') else None)
        t0 = time.time(); await pg.goto(URL, timeout=600000, wait_until='commit')
        for k in range(120):
            await pg.wait_for_timeout(5000)
            st = await pg.evaluate("({ steps: window.__steps, bt: window.__bt ? Object.fromEntries(Object.entries(window.__bt).map(([k, v]) => [k, typeof v === 'number' ? Math.round(v) : v])) : null })")
            print(round(time.time() - t0), json.dumps(st)[:600], errs[:3], flush=True)
            if st['bt'] and st['bt'].get('warmed'): break
        r = await pg.evaluate("({ steps: window.__steps, bt: Object.fromEntries(Object.entries(window.__bt).map(([k, v]) => [k, typeof v === 'number' ? Math.round(v) : v])) })")
        print(json.dumps(r)); print('wall', round(time.time() - t0, 1)); await b.close()
asyncio.run(main())
