# flings at a floating pad from a few distances and charges, with and without the nudge: where does the blob end up?
import asyncio, json
from playwright.async_api import async_playwright
JS = r"""
(noLedge) => {
  window.__noLedge = noLedge; window.__ledgeDbg = true; const T = __T, P = T.P; const out = [];
  const pads = T.BOXES.filter(b => b[4] > 0.5 && b[4] < 1.6 && b[6] !== 'c'); if (!pads.length) return { none: true, boxes: T.BOXES.filter(b => b[4] > 0).map(b => b.slice(0, 7)) };
  const b = pads[0], cx = (b[0] + b[1]) / 2, cz = (b[2] + b[3]) / 2;
  for (const dist of [2.2, 3.2, 4.4, 5.6]) for (const c of [0.35, 0.5, 0.65, 0.8, 1.0]) {
    // stand south of the pad's face on open floor, aimed at it
    const x = cx, z = b[3] + dist; if (T.surfaceUnder(x, z, 0.5, true) !== 0 || T.blockedAt(x, z, 0)) { out.push({ dist, c, skip: true }); continue; }
    T.matchLeft = 500; for (const R of T.rivals) { R.x = -20; R.z = -20; R.spd = 0; R.st = 'play'; R.air = false; } P.x = x; P.z = z; P.y = 0; P.air = false; P.vy = 0; P.spd = 0; P.yaw = Math.PI; P.st = 'play'; P.pot = null; P.charging = true; P.charge = c; P.kx = P.kz = 0; P.knockT = 0; P.flatT = 0; P.stunT = 0;
    window.__ledgeLast = null; T.flingIt(P, c); let plan = P.ledge ? P.ledge.mode : null, dbg = window.__ledgeLast; let bonk = false, maxY = 0, tAir = 0;
    for (let i = 0; i < 160 && (P.air || i < 3); i++) { const x0 = P.x, z0 = P.z; T.step(1 / 60); maxY = Math.max(maxY, P.y); if (P.air) tAir += 1 / 60; if (!plan && P.ledge) { plan = P.ledge.mode + '*'; dbg = window.__ledgeLast; } if (P.air && Math.hypot(P.x - x0, P.z - z0) < 1e-4) bonk = true; }
    const onTop = Math.abs(P.y - b[5]) < 0.05 && x > b[0] && x < b[1] && P.z > b[2] && P.z < b[3];
    out.push({ dist, c, plan, onTop, under: P.z < b[2], short: P.z > b[3], y: +P.y.toFixed(2), z: +(P.z - b[3]).toFixed(2), bonk, maxY: +maxY.toFixed(2), dbg });
  }
  const decks = T.BOXES.filter(b => b[4] >= 2 && b[6] !== 'c'); const hi = [];
  for (const d of decks.slice(0, 2)) { const cx = (d[0] + d[1]) / 2; for (const dist of [1.5, 2.5, 3.5]) for (const c of [0.8, 1.0]) {
    const x = cx, z = d[3] + dist; if (T.surfaceUnder(x, z, 0.5, true) !== 0 || T.blockedAt(x, z, 0)) continue;
    T.matchLeft = 500; for (const R of T.rivals) { R.x = -20; R.z = -20; R.spd = 0; R.st = 'play'; R.air = false; } P.x = x; P.z = z; P.y = 0; P.air = false; P.vy = 0; P.spd = 0; P.yaw = Math.PI; P.st = 'play'; P.pot = null; P.charging = true; P.charge = c; P.kx = P.kz = 0;
    window.__ledgeLast = null; T.flingIt(P, c); let plan = P.ledge ? P.ledge.mode : null, dbg = window.__ledgeLast; let bump = false, maxHead = 0;
    for (let i = 0; i < 160 && (P.air || i < 3); i++) { const vy0 = P.vy; T.step(1 / 60); maxHead = Math.max(maxHead, P.y + 0.8); if (P.air && vy0 > 0.5 && P.vy === 0) bump = true; if (!plan && P.ledge) { plan = P.ledge.mode + '*'; dbg = window.__ledgeLast; } }
    hi.push({ deck: [d[4], d[5]], dist, c, plan, bump, maxHead: +maxHead.toFixed(2), z: +(P.z - d[3]).toFixed(2), y: +P.y.toFixed(2), dbg }); } }
  return { pad: [b[4], b[5], +(b[1]-b[0]).toFixed(1), +(b[3]-b[2]).toFixed(1)], out, hi };
}
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noLoop = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', stage:'island', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1000)
        for seed in range(6):
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(300)
            r0 = await pg.evaluate(JS, True); r1 = await pg.evaluate(JS, False)
            if r0.get('none'): print('seed', seed, 'no low pad; floating', r0['boxes'][:3]); await pg.evaluate("__T.toMenu()"); await pg.wait_for_timeout(500); continue
            print('seed', seed, 'pad bottom/top/w/d', r0['pad'])
            for a, bb in zip(r0['out'], r1['out']):
                if a.get('skip'): continue
                res = lambda q: 'top' if q['onTop'] else 'under' if q['under'] else ('bonk' if q['bonk'] else 'short') if q['short'] else 'past'
                print(f"  d={a['dist']} c={a['c']}: plain {res(a):5} (y {a['y']}, dz {a['z']})  nudged {res(bb):5} plan={bb['plan']} (y {bb['y']}, dz {bb['z']}, bonk {bb['bonk']})", '' if res(bb) != 'bonk' else bb['dbg'])
            for a, bb in zip(r0.get('hi', []), r1.get('hi', [])): print(f"  deck {a['deck']} d={a['dist']} c={a['c']}: plain bump={a['bump']} head {a['maxHead']} dz {a['z']}  nudged bump={bb['bump']} plan={bb['plan']} head {bb['maxHead']} dz {bb['z']} y {bb['y']}", bb['dbg'] if bb['bump'] else '')
            await pg.evaluate("__T.toMenu()"); await pg.wait_for_timeout(500)
            if seed >= 2: break
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
