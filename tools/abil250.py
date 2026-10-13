"""The Strokes (abilities) lesson, the first time it shows: Ol' Bloop's two cards in the lobby, then the Strokes page with its tips.
Samples where the UI pieces sit every frame for a few seconds at each step (after their entrance animations) and reports anything that
keeps moving, plus shots. usage: abil250.py [WxH]"""
import asyncio, os, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; PAGE = os.environ.get('PAGE', 'pc_h.html')
W, H = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else '390x844').split('x')]
SAMPLE = r"""(ms) => new Promise(res => { const sel = ['#tutGo .tgcard', '#tut', '#tutHand', '.coach', '#coach', '#abilBtn', '#stSpecialRail', '.stopt[data-st="giant"]', '#stSkip', '.stslot', '#mStrokes .stwrap', '.tutdim', '#tutDim b', '.lobby', '#mHome', '.pbar', '#logo'];
  const els = []; for (const s of sel) document.querySelectorAll(s).forEach((e, i) => els.push([s + (i ? '#' + i : ''), e]));
  const hist = {}, t0 = performance.now(); let frames = 0;
  const step = () => { frames++; for (const [k, e] of els) { const r = e.getBoundingClientRect(), cs = getComputedStyle(e); const v = [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height), cs.opacity, cs.visibility === 'hidden' || cs.display === 'none' || !r.width ? 0 : 1, e.className.baseVal === undefined ? e.className : '', e.hidden ? 1 : 0, e.dataset && (e.dataset.pos || e.dataset.style || e.dataset.mode || '')].join('|'); (hist[k] = hist[k] || []).push(v); }
    if (performance.now() - t0 < ms) requestAnimationFrame(step); else { const out = {}; for (const k in hist) { const h = hist[k]; let ch = 0; for (let i = 1; i < h.length; i++) if (h[i] !== h[i - 1]) ch++; const uniq = [...new Set(h)]; if (ch) out[k] = { changes: ch, frames: h.length, distinct: uniq.length, sample: uniq.slice(0, 4) }; } res({ frames, moving: out }); } };
  requestAnimationFrame(step); })"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if W > H else 'port') + "', name:'Dusk', seen:{ jump: 1, hold: 1 }, drops: 300, runs: 6, xp: 400, tut: { ph: 'done', m3: 1 }, owned: ['flower', 'fangs'], bought: ['flower', 'fangs'] })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000, polling=100)
        print('rank', await ev("__T.ev('repOf(store.xp || 0).lv')"), 'strokes due', await ev("__T.ev('[strokesDue(), store.tut.strokes, tutPh()]')"))
        if os.environ.get('FAST'): await ev("(() => { const r = __T.renderer; r.render = () => {}; })(); 0")
        await pg.wait_for_function("!document.getElementById('tutGo').hidden", timeout=120000, polling=100); await pg.wait_for_timeout(1500)
        print('card 1', await ev("document.getElementById('tutGo').dataset.mode")); await pg.screenshot(path=f'{WS}/ui/abil_{W}x{H}_card1.png')
        r = await ev(SAMPLE, 2500); print('  card 1 moving:', json.dumps(r)[:3000])
        await ev("document.getElementById('tgGo').click()"); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{WS}/ui/abil_{W}x{H}_card2.png')
        r = await ev(SAMPLE, 2500); print('  card 2 moving:', json.dumps(r)[:3000])
        await ev("document.getElementById('tgGo').click()"); await pg.wait_for_timeout(600); await pg.screenshot(path=f'{WS}/ui/abil_{W}x{H}_open0.png')
        await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/abil_{W}x{H}_open1.png')
        print('page', await ev("[__T.ev('menuPage'), __T.tutTip && __T.tutTip.key]"))
        r = await ev(SAMPLE, 3000); print('  strokes page moving:', json.dumps(r)[:4000])
        await pg.screenshot(path=f'{WS}/ui/abil_{W}x{H}_open2.png')
        for step, js in [('craft', "document.querySelector('.stopt[data-st=\"giant\"]').click()"), ('skip', "document.getElementById('stSkip').click()"), ('equip', "document.querySelector('.stopt[data-st=\"giant\"]').click()")]:
            await ev(js); await pg.wait_for_timeout(700); print(step, await ev("[__T.tutTip && __T.tutTip.key, __T.ev('JSON.stringify(strokesOf())')]"))
            r = await ev(SAMPLE, 2500); print('  ' + step + ' moving:', json.dumps(r)[:3000]); await pg.screenshot(path=f'{WS}/ui/abil_{W}x{H}_{step}.png')
        await pg.wait_for_timeout(6000); print('after', await ev("[__T.tutTip && __T.tutTip.key, __T.ev('tutPh()'), document.querySelector('.menu').className]"))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
