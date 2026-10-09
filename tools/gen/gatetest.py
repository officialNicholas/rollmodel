# sound at load: allowed (as in the app) the menu opens with sound running and no tap; blocked (a browser) the loading screen asks for a tap,
# and that tap starts the sound and opens the menu
import asyncio
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
Q = "() => ({ boot: document.getElementById('boot').className, msg: document.getElementById('bootMsg').textContent, snd: typeof __T === 'object' ? __T.AU.state : null, st: typeof __T === 'object' ? __T.state : null })"
POLICY = """(() => { const A = window.AudioContext; if (!A) return; let gest = false;
  for (const ev of ['pointerdown','pointerup','touchend','keydown','click']) addEventListener(ev, () => { gest = true; setTimeout(() => gest = false, 1000); }, true);
  window.AudioContext = class extends A {
    constructor(o) { super(o); this.__ok = gest; if (!gest) super.suspend(); }
    get state() { return this.__ok ? super.state : (super.state === 'closed' ? 'closed' : 'suspended'); }
    resume() { if (gest) { this.__ok = true; return super.resume(); } return Promise.resolve(); }
  }; window.webkitAudioContext = window.AudioContext; })();"""
async def run(p, allowed):
    args = ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] + (['--autoplay-policy=no-user-gesture-required'] if allowed else ['--autoplay-policy=user-gesture-required'])
    b = await p.chromium.launch(args=args); ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script("window.__tapGate = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'lo', seen: {look:1} })); } catch (e) {}")
    if not allowed: await ctx.add_init_script(POLICY)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function("typeof __T === 'object'", polling=200, timeout=240000); await asyncio.sleep(2.5)
    r1 = await pg.evaluate(Q); print('allowed' if allowed else 'blocked', 'after load', r1)
    if 'tap' in r1['boot']:
        await pg.screenshot(path='st/gate_tap.png', timeout=120000)
        await pg.evaluate('window.__noLoop = true'); await pg.tap('#boot', timeout=180000); await asyncio.sleep(1.5); print('  after tap', await pg.evaluate(Q))
    print('  errors', errs[:3]); await b.close()
async def main():
    async with async_playwright() as p:
        await run(p, False)
        await run(p, True)
asyncio.run(main())
