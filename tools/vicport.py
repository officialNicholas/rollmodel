"""The winner screen in portrait, won and lost: where the featured character sits against the bottom block (place, cards, tap line).
Prints the character's on-screen box (its posed mesh projected through the victory camera) and the top of the bottom block, and saves
shots at the landing and at the top of the big jump. Usage: vicport.py <page> <tag>"""
import asyncio, sys, json
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'cur'
MEASURE = r"""(() => { const T = __T, THREE = T.THREE, v = T.vic; if (!v) return null; const cam = T.ev('vicCam'), out = [];
  for (const D of v.feat) { const root = T.ev('lookRoot')(D); root.updateWorldMatrix(true, true); const b = new THREE.Box3().setFromObject(root, true);
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; for (let i = 0; i < 8; i++) { const p = new THREE.Vector3(i & 1 ? b.max.x : b.min.x, i & 2 ? b.max.y : b.min.y, i & 4 ? b.max.z : b.min.z).project(cam);
      const sx = (p.x + 1) / 2 * innerWidth, sy = (1 - p.y) / 2 * innerHeight; x0 = Math.min(x0, sx); x1 = Math.max(x1, sx); y0 = Math.min(y0, sy); y1 = Math.max(y1, sy); }
    out.push({ top: Math.round(y0), bottom: Math.round(y1), left: Math.round(x0), right: Math.round(x1) }); }
  const r = s => document.querySelector(s).getBoundingClientRect(), foot = r('#victory .vfoot'), top = r('#victory .vtop'), place = r('#vPlace'), cards = r('#vCards'), tap = r('#vTap');
  return { t: +v.t.toFixed(2), cy: +(v.cy || 0).toFixed(3), room: +(v.room || 0).toFixed(3), H: innerHeight, topBottom: Math.round(top.bottom), footTop: Math.round(foot.top), placeTop: Math.round(place.top), cardsTop: Math.round(cards.top), tapTop: Math.round(tap.top), chars: out }; })()"""
async def run(b, w, h, pad, lose):
    ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, has_touch=True, is_mobile=True)
    await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', runs: 3, tut: { ph: 'done' }, seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
    if pad: await pg.evaluate("(() => { const st = document.createElement('style'); st.textContent = ':root{padding-bottom:34px!important}.victory{padding-bottom:34px!important}'; document.head.appendChild(st); })(); 0")
    await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
    await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000); await pg.wait_for_timeout(1500)
    await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, TEAMCODE); } __T.flushTrail(); __T.matchLeft = 0.4; })()".replace('TEAMCODE', '1' if lose else '0'))
    await pg.wait_for_function("!!__T.vic", timeout=120000, polling=200)
    await pg.evaluate("__T.renderer.render = window.__o; 0")
    tag = f"{TAG}_{w}x{h}{'p' if pad else ''}_{'lose' if lose else 'win'}"
    async def at(t):
        await pg.evaluate("__T.vic.t = %f; 0" % t); await pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => requestAnimationFrame(r))))")
        await pg.evaluate("__T.vic.t = %f; 0" % t); await pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
    await pg.wait_for_timeout(1500); await at(1.6); m0 = await pg.evaluate(MEASURE); await pg.screenshot(path=f'{WS}/ui/vp_{tag}_a.png')
    await at(2.57); m1 = await pg.evaluate(MEASURE); await pg.screenshot(path=f'{WS}/ui/vp_{tag}_b.png')
    print(tag, json.dumps(m0), json.dumps(m1), 'errors', errs[:3], flush=True); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, pad in [(390, 780, False), (430, 932, True)]:
            for lose in (False, True): await run(b, w, h, pad, lose)
        await b.close()
asyncio.run(main())
