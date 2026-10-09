import asyncio, json
from playwright.async_api import async_playwright
JS = r"""
() => { const T = __T, P = T.P, out = {}; const steps = n => { for (let i = 0; i < n; i++) T.step(1 / 60); };
  for (const R of T.rivals) { R.x = -20; R.z = -20; R.spd = 0; } T.matchLeft = 500;
  P.held = 'roller'; out.useRoller = [T.useHeld(P), P.power && P.power.type, +P.paint.toFixed(2), P.held];
  P.power = null; P.held = 'turret'; P.air = true; out.turretInAir = T.useHeld(P); P.air = false; out.turretGround = [T.useHeld(P), !!P.turret]; P.turret = null;
  // holding one, picking up another: the first goes back on the floor behind us, and we cannot re-grab it for a moment
  P.held = 'roller'; T.spawnItem(); const q = T.powers[0]; P.x = q.x; P.z = q.z; P.y = q.y; P.vy = 0; P.air = false; steps(1);
  out.swap = [P.held, T.powers.map(p => [p.type, p.owner === P, +p.grace.toFixed(1), +Math.hypot(p.x - P.x, p.z - P.z).toFixed(2)])];
  steps(30); out.after05 = [P.held, T.powers.length];
  // pacing: with one in hand and one on the floor in a duel, nothing more spawns
  T.itemSpawn.t = 0; steps(5); out.capped = T.powers.length;
  return out; }
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noLoop = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', mode:'duel', stage:'blank', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(800)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(400)
        print(json.dumps(await pg.evaluate(JS))); print('errors', errs[:3]); await b.close()
asyncio.run(main())
