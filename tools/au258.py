"""v258 audio probe: the app goes to the background and comes back (fresh context, song carries on); a resume that hangs gets caught by the
clock check and a touch starts the sound afresh; the app's plain 'back' signal with a hanging resume retries by itself."""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE = sys.argv[1]
ST = "JSON.stringify({ state: AU.state, trk: AU._trk && AU._trk.key, pos: AU._ctx && AU._trk ? +AU._pos().toFixed(2) : -1, clock: AU._ctx && +AU._ctx.currentTime.toFixed(2), renews: AU.renews })"
HIDE = "Object.defineProperty(document, 'hidden', { configurable: true, get: () => %s }); document.dispatchEvent(new Event('visibilitychange')); true"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx, pg, errs = await boot(b, PAGE, SAVE, init='window.__tapGate = false; window.__skipIntro = true; window.__noReveal = true;')
        await pg.evaluate("window.dispatchEvent(new PointerEvent('pointerdown')); __T.ev(\"AU.music('menu')\"); true")
        st = lambda: pg.evaluate("__T.ev(" + json.dumps(ST) + ")")
        for _ in range(30):
            s = json.loads(await st())
            if s['trk']: break
            await pg.wait_for_timeout(500)
        print('menu', s, flush=True)
        # A: to the background and back, the app saying it was away
        await pg.evaluate(HIDE % 'true'); await pg.wait_for_timeout(600); print('A hidden', await st(), flush=True)
        await pg.evaluate(HIDE % 'false'); await pg.evaluate("window.dispatchEvent(new CustomEvent('nativeresume', { detail: { away: true } })); true")
        await pg.wait_for_timeout(300); print('A back', await st(), flush=True)
        await pg.wait_for_timeout(1500); print('A settled', await st(), flush=True)
        # B: a browser whose resume hangs after the background: the check catches it, a touch starts afresh
        await pg.evaluate("window.__res = AudioContext.prototype.resume; AudioContext.prototype.resume = function () { return new Promise(() => {}); }; true")
        await pg.evaluate(HIDE % 'true'); await pg.wait_for_timeout(600); await pg.evaluate(HIDE % 'false'); await pg.wait_for_timeout(1300)
        print('B stuck', await st(), flush=True)
        await pg.evaluate("window.dispatchEvent(new PointerEvent('pointerdown')); true"); await pg.wait_for_timeout(1200); print('B touched', await st(), flush=True)
        # C: the app's plain 'back' (Control Center) with the resume still hanging: stop-and-start fails, it retries afresh by itself
        await pg.evaluate("window.dispatchEvent(new Event('nativeresume')); true"); await pg.wait_for_timeout(400); print('C kick', await st(), flush=True)
        await pg.wait_for_timeout(1600); print('C settled', await st(), flush=True)
        # D: a match: background and back mid-match, then pause muffle kept
        await pg.evaluate("AudioContext.prototype.resume = window.__res; true")
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=120000, polling=100); await pg.wait_for_timeout(2500)
        print('D play', await st(), flush=True)
        await pg.evaluate("window.dispatchEvent(new Event('blur')); true"); await pg.evaluate(HIDE % 'true'); await pg.wait_for_timeout(500)
        await pg.evaluate(HIDE % 'false'); await pg.evaluate("window.dispatchEvent(new CustomEvent('nativeresume', { detail: { away: true } })); true"); await pg.wait_for_timeout(1500)
        print('D back', await st(), await pg.evaluate("__T.ev('state')"), flush=True)
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
