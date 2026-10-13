"""v256 gameplay probes. usage: p256.py PAGE TAG SCENARIO
  play   (duel, hard) the freeze and tapping out of it, a CPU tapping out, the orb in the slot and its clock, Deep Pockets, a CPU's orb,
         the darker bigger trap, the turret draining paint and knocking out on empty
  zone   (Showdown) the warning curtain and countdown, the close, burning outside, the knock-out; the colours
  duo    (2v2) the team colours
  gate   (duel at rank 3, commissions lesson waiting) the results offer only Main menu"""
import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG, SC = sys.argv[1], sys.argv[2], sys.argv[3]
async def shot(pg, n): await pg.screenshot(path=f'{OUT}/{TAG}_{SC}_{n}.png', timeout=120000); print('shot', n, flush=True)
async def adv(pg, secs, dt=1/30):
    n = max(1, round(secs / dt))
    while n > 0: k = min(n, 15); await pg.evaluate(f"__adv({dt}, {k})"); n -= k
ev = lambda pg, e: pg.evaluate("__T.ev(" + json.dumps(e) + ")")
async def intro(pg):
    await pg.evaluate("__T.start()")
    await pg.wait_for_function("__T.state === 'intro' || __T.state === 'play'", timeout=240000, polling=50)
    await pg.evaluate("window.__tscale = 1e-9"); await pg.wait_for_timeout(300)
    for _ in range(500):
        if await pg.evaluate("__T.state === 'play'"): break
        await pg.evaluate("__adv(1/30, 6)")
    await adv(pg, 1.5)
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        mode = {'play': 'duel', 'zone': 'ffa', 'zone2': 'ffa', 'duo': 'duo', 'gate': 'duel'}[SC]
        save = dict(SAVE, mode=mode, diff='hard')
        if SC == 'gate': save = dict(save, xp=250, tut={'ph': 'done', 'strokes': 1, 'm3': 2})
        ctx, pg, errs = await boot(b, PAGE, save, vp=(390, 780), dpr=1, init='window.__skipIntro = false; window.__noReveal = true;')
        await intro(pg)
        if SC == 'play':
            # the freeze: H casts it on you
            await ev(pg, "(H.x = P.x + Math.sin(P.yaw) * 6, H.z = P.z + Math.cos(P.yaw) * 6, H.y = P.y, startFreeze(H), 0)"); await adv(pg, 1.0)
            print('frozen', await ev(pg, "JSON.stringify({ f: +P.frozenT.toFixed(2), s: +P.stunT.toFixed(2) })")); await shot(pg, 'frozen')
            for i in range(14): await pg.evaluate("document.getElementById('cv').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 7, clientX: 200, clientY: 400 })); document.getElementById('cv').dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 7, clientX: 200, clientY: 400 }))")
            print('after 14 taps', await ev(pg, "JSON.stringify({ f: +P.frozenT.toFixed(2), s: +P.stunT.toFixed(2), tap: P.iceTap })")); await adv(pg, 0.05); await shot(pg, 'shake')
            t = 0
            while await ev(pg, "P.frozenT > 0") and t < 8: await adv(pg, 0.25); t += 0.25
            print('you thawed after', t, 's more')
            # you freeze H (hard: it taps its way out)
            await ev(pg, "(P.frozenT = 0, P.stunT = 0, startFreeze(P), 0)"); await adv(pg, 1.0)
            print('H frozen', await ev(pg, "JSON.stringify({ f: +H.frozenT.toFixed(2), mash: H.iceMash })"))
            t = 0
            while await ev(pg, "H.frozenT > 0") and t < 8: await adv(pg, 0.25); t += 0.25
            print('H thawed after', t, 's (5 s less a second of tapping ~ 4)')
            # the orb in your slot and its clock (out in the open: the slot hides while you're down in a basin)
            await ev(pg, "(P.stunT = 0, P.frozenT = 0, P.st === 'hide' && exitPot(P), 0)"); await adv(pg, 0.6)
            await ev(pg, "(window.__orbKind = 'giant', takeOrb(P), 0)"); await adv(pg, 0.2)
            print('orb', await ev(pg, "JSON.stringify({ g: P.orbSaved, t: +P.orbT.toFixed(2), btn: !$('orbBtn').hidden, keep: $('orbBtn').classList.contains('keep') })"))
            await shot(pg, 'orb0'); await ev(pg, "(P.orbT = 6.1, 0)"); await adv(pg, 0.1); await shot(pg, 'orb4s')
            print('orb at ~6 s left', await ev(pg, "JSON.stringify({ t: +P.orbT.toFixed(2), of: $('orbBtn').style.getPropertyValue('--of') })"))
            await ev(pg, "(P.orbT = 2.1, 0)"); await adv(pg, 0.1); await shot(pg, 'orb85s')
            await adv(pg, 2.2); print('after 10 s', await ev(pg, "JSON.stringify({ g: P.orbSaved, btn: !$('orbBtn').hidden })"))
            await ev(pg, "(P.skill = 'pockets', takeOrb(P), 0)"); await adv(pg, 0.3)
            print('pockets', await ev(pg, "JSON.stringify({ g: P.orbSaved, t: P.orbT, keep: $('orbBtn').classList.contains('keep') })")); await shot(pg, 'orbkeep')
            await ev(pg, "(P.orbSaved = null, P.skill = 'swim', window.__orbKind = 'giant', takeOrb(H), 0)")
            print('H orb', await ev(pg, "JSON.stringify({ g: H.orbSaved, w: +H.ai.orbWait.toFixed(2) })")); t = 0
            while await ev(pg, "!!H.orbSaved") and t < 5: await adv(pg, 0.25); t += 0.25
            print('H used its orb after', t, 's; giant', await ev(pg, "H.giantT > 0"))
            # the trap, in front of you
            await ev(pg, "(H.giantT = 0, P.st === 'hide' && exitPot(P), H.x = P.x + Math.sin(P.yaw) * 3.2, H.z = P.z + Math.cos(P.yaw) * 3.2, H.y = P.y, dropTrap(H), H.x += Math.sin(P.yaw) * 5, H.z += Math.cos(P.yaw) * 5, P.spd = 0, 0)"); await adv(pg, 0.15); await shot(pg, 'trap')
            print('trap', await ev(pg, "JSON.stringify({ r: TRAP_R, sc: trapList[0] && trapList[0].g.scale.x, col: trapList[0] && trapList[0].g.children[1].material.color.getHexString(), team: TEAMS[1].css })"))
            # the turret's shots on you: paint drains, then empty knocks you out
            r = []
            for k in range(4):
                r.append(await ev(pg, "(P.immuneT = 0, P.paint = Math.min(P.paint, 0.1), shotHit(P, { by: H, vx: 10, vz: 0, vy: 0, x: P.x, y: P.y, z: P.z }), JSON.stringify({ p: +P.paint.toFixed(2), dry: !!P.dry, st: P.st, why: P.reason || null }))"))
                await adv(pg, 0.05)
            print('turret hits', r)
        elif SC == 'zone':
            print('colours', await ev(pg, "JSON.stringify({ mine: colorOf().id, show: TEAMS.map(t => t.css), own: rivalCol.map(c => c && c.id) })"))
            await ev(pg, "(runT = 44.6, 0)"); await adv(pg, 0.6)
            print('warn', await ev(pg, "JSON.stringify({ warn: zone.warn, next: zone.next, chip: !$('zChip').hidden, n: $('zChipN').textContent, cut: zoneCut(), pOut: zoneLost(P.x, P.z), P: [+P.x.toFixed(1), +P.z.toFixed(1)] })"))
            await ev(pg, "(camYaw = P.yaw, camSnap = true, 0)"); await adv(pg, 0.5); await shot(pg, 'warn')
            # keep you outside for the close: put you just past the line
            await ev(pg, "(P.x = 29, P.z = 0, P.y = surfaceUnder(29, 0, 8, true), P.yaw = -Math.PI / 2, P.air = false, runT = 59.9, camSnap = true, 0)"); await adv(pg, 0.6)
            print('closed', await ev(pg, "JSON.stringify({ cur: zone.cur, warn: zone.warn, lid: !!zone.mNow, out: zoneLost(P.x, P.z), vig: $('zVig').classList.contains('on'), paint: +P.paint.toFixed(2) })")); await shot(pg, 'outside')
            await ev(pg, "(P.yaw = Math.PI / 2, camYaw = P.yaw, camSnap = true, 0)"); await adv(pg, 0.4); await shot(pg, 'lookin')
            t = 0
            while await ev(pg, "P.st === 'play'") and t < 8: await adv(pg, 0.25); t += 0.25
            print('outside: knocked out after', t, 's', await ev(pg, "JSON.stringify({ st: P.st, why: P.reason, hearts: P.hearts, self: P.selfOuts })"))
        elif SC == 'zone2':
            # the curtain ahead of you while it's warned
            await ev(pg, "(P.st === 'hide' && exitPot(P), P.x = 21.5, P.z = 0, P.y = Math.max(0, surfaceUnder(21.5, 0, 8, true)), P.yaw = Math.PI / 2, P.air = false, P.stunT = 30, runT = 46, camYaw = P.yaw, camSnap = true, 0)"); await adv(pg, 0.8)
            print('warned', await ev(pg, "JSON.stringify({ warn: zone.warn, next: zone.next, n: $('zChipN').textContent })")); await shot(pg, 'curtain')
            # closed, and you held still out past it: the paint burns off, then you're out
            await ev(pg, "(P.x = 29.5, P.z = 0, P.y = Math.max(0, surfaceUnder(29.5, 0, 8, true)), P.yaw = -Math.PI / 2, P.stunT = 30, runT = 59.95, camYaw = P.yaw, camSnap = true, 0)"); await adv(pg, 0.4)
            print('closed', await ev(pg, "JSON.stringify({ cur: zone.cur, out: zoneLost(P.x, P.z), vig: $('zVig').classList.contains('on'), paint: +P.paint.toFixed(2), x: +P.x.toFixed(1), y: +P.y.toFixed(2), st: P.st })")); await shot(pg, 'burning')
            t = 0; trace = []
            while await ev(pg, "P.st === 'play'") and t < 8: await adv(pg, 0.5); t += 0.5; trace.append(await ev(pg, "+P.paint.toFixed(2)"))
            print('burn trace', trace, 'out after', t, await ev(pg, "JSON.stringify({ st: P.st, why: P.reason, hearts: P.hearts, self: P.selfOuts, kofBy: $('kofBy').textContent })"))
            await adv(pg, 0.3); await shot(pg, 'zoneko')
        elif SC == 'duo':
            print('team colours', await ev(pg, "JSON.stringify({ mine: colorOf().id, own: rivalCol.map(c => c && c.id), show: TEAMS.map(t => t.css), apart: +colDist(TEAMS[0].wet, TEAMS[1].wet).toFixed(3) })"))
            await shot(pg, 'hud')
        elif SC == 'gate':
            await ev(pg, "(() => { for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; addSplat(x, Math.max(0, surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, clock, false, true, 0); } flushTrail(); matchLeft = 0.3; return 0; })()")
            await pg.evaluate("window.__tscale = 1")
            for _ in range(400):
                if await pg.evaluate("!document.getElementById('end').hidden"): break
                if await pg.evaluate("!!__T.vic && !window.vk"): await pg.wait_for_timeout(2500); await pg.evaluate("window.vk = 1; document.getElementById('victory').click()")
                await pg.wait_for_timeout(750)
            await pg.wait_for_timeout(2500)
            print('gate', await ev(pg, "JSON.stringify({ gate: end.classList.contains('gate'), btn: $('endBtn').innerText, row: $('replayBtn').closest('.row').hidden })")); await shot(pg, 'end')
            await pg.evaluate("document.getElementById('endBtn').click()")
            await pg.wait_for_function("__T.ev('state') === 'menu' && !__T.ev('irisBusy')", timeout=60000, polling=200); print('menu', await ev(pg, "menuPage"))
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
