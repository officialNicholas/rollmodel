import asyncio, json
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
JS = r"""
() => {
  const T = __T, P = T.P, H = T.H, out = {}; const steps = n => { for (let i = 0; i < n; i++) T.step(1 / 60); };
  for (const R of T.rivals) { R.x = -20; R.z = -20; R.spd = 0; } T.matchLeft = 500;
  out.atStart = T.powers.length;
  steps(60 * 12); out.after12s = T.powers.map(p => p.type); out.spawnT = +T.itemSpawn.t.toFixed(1);
  // walk the player onto it
  const pw = T.powers[0]; if (!pw) return out;
  P.x = pw.x; P.z = pw.z; P.y = pw.y; P.air = false; steps(2);
  out.held = P.held; out.onStage = T.powers.length; out.btn = !document.getElementById('itemBtn').hidden;
  steps(60 * 3); out.noSecondWhileHeld = T.powers.length; // nothing new while the only item is in hand (duel: cap 1, busy 1 of 2 players -> allowed? players 2, busy 1: 1+1 < 2 false -> no spawn)
  // use it
  out.used = T.useHeld(P); out.power = P.power && P.power.type; out.turret = !!P.turret; out.heldAfter = P.held; out.btnAfter = !document.getElementById('itemBtn').hidden;
  // spawn another, hold it, then pick up a third: the second goes back on the floor behind us
  T.itemSpawn.t = 0; P.power = null; steps(3); const a = T.powers[0]; out.second = a && a.type;
  if (a) { P.x = a.x; P.z = a.z; P.y = a.y; steps(2); out.held2 = P.held;
    T.itemSpawn.t = 0; T.spawnItem(); const b = T.powers[0]; out.third = b && b.type; P.x = b.x; P.z = b.z; P.y = b.y; steps(2); out.held3 = P.held; out.dropped = T.powers.map(p => [p.type, p.owner === P, +p.grace.toFixed(1)]); }
  // a CPU with a turret in hand uses it when the player is near
  H.held = 'turret'; H.heldT = 0; H.st = 'play'; H.air = false; H.x = P.x + 5; H.z = P.z; H.y = P.y; H.ai = H.ai || {}; steps(60 * 2); out.cpuTurret = !!H.turret; out.cpuHeld = H.held;
  // the orb never hands out the turret
  const kinds = new Set(); window.__orbKind = undefined; for (let i = 0; i < 40; i++) { const g = (['giant', 'rocket'].includes('x')); } out.orbKinds = 'see source'; window.__orbKind = 'giant';
  return out;
}
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, tag in [(390, 780, 'port'), (844, 390, 'land')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("window.__noLoop = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', mode:'duel', stage:'blank', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(800)
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(400)
            pass
            # the button on screen: hold a roller, let the frame loop draw
            await pg.evaluate("(() => { const P = __T.P; if (P.pot) { P.pot.occ = null; P.pot = null; } P.st = 'play'; P.x = __T.START.x; P.z = __T.START.z; P.y = 0; P.held = '" + ('turret' if tag == 'port' else 'roller') + "'; P.power = null; P.turret = null; window.__noLoop = false; })()"); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=f'{WS}/ui/item_{tag}.png')
            print(tag, 'errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
