"""v251 features, each checked by stepping the game by hand: skills (pace in clear and rain, Weather Repel's immunities), Deep Pockets (two
items, the saved orb), the Paint Trap (a hit, a roll through, your own), Flash Freeze (a hit, a basin, a perfect roll, a CPU's at you), and
the Strokes page. usage: feat251.py section [section ...]  (strokes speed weather pockets trap freeze vote)"""
import asyncio, os, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; SEC = sys.argv[1:]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': int(os.environ.get('VW', 390)), 'height': int(os.environ.get('VH', 844))}, device_scale_factor=float(os.environ.get('DSF', 2)), has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1, roll: 1, pound: 1, missile: 1, burst: 1 }, drops: 0, runs: 9, xp: 900, mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1, m3: 2 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append('console: ' + m.text[:200])); ev = pg.evaluate
        async def wait(js, t=400000): await pg.wait_for_function(js, timeout=t, polling=100)
        async def shot(n): await pg.screenshot(path=f'{WS}/ui/f251_{n}.png')
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(800)
        E = lambda js: ev("(() => { const T = __T; return T.ev(" + json.dumps(js) + "); })()")
        if 'strokes' in SEC:
            await E("openStrokes()"); await pg.wait_for_timeout(900); await shot('strokes_0')
            print('specials', await ev("[...document.querySelectorAll('#stSpecialRail .stopt')].map(b => b.textContent)"))
            print('skills', await ev("[...document.querySelectorAll('#stSkillRail .stopt')].map(b => b.textContent)"))
            await ev("document.querySelector('#stSkillRail [data-sk=repel]').click()"); await pg.wait_for_timeout(500)
            print('card', await ev("document.getElementById('stSkillNow').innerText.replace(/\\n+/g, ' | ')"), 'skill', await E("strokeSkill()"))
            await ev("document.getElementById('stWrap').scrollTop = 9999"); await pg.wait_for_timeout(300); await shot('strokes_repel')
            await ev("document.querySelector('#stSkillNow .stequip').click()"); await pg.wait_for_timeout(500); print('after Equip', await E("strokeSkill()"), await ev("document.querySelector('#stSkillRail .stopt.on').textContent"))
            await ev("document.querySelector('#stSkillRail [data-sk=pockets]').click()"); await pg.wait_for_timeout(300); await ev("document.querySelector('#stSkillRail [data-sk=pockets]').click()"); await pg.wait_for_timeout(400)
            print('second tap equips', await E("strokeSkill()")); await ev("document.getElementById('stWrap').scrollTop = 9999"); await pg.wait_for_timeout(300); await shot('strokes_pockets')
            await E("equipSkill('swim'); closeStrokes()"); await pg.wait_for_timeout(500)
        if set(SEC) & {'speed', 'weather', 'pockets', 'trap', 'freeze', 'shots', 'cputrap'}:
            if os.environ.get('FAST'): await ev("(() => { const r = __T.renderer; r.render = () => {}; })(); 0")
            await ev("__T.mode = 'duel'; __T.applyMode(); __T.start()"); await wait("__T.state === 'play'"); await pg.wait_for_timeout(1500)
            await ev("window.__noStep = true")
            spot = await ev("""(() => { const T = __T, A = T.ARENA - 3, ok = (x, z) => Math.abs(x) < A && Math.abs(z) < A && T.surfaceUnder(x, z, 0.3) === 0 && !T.blockedAt(x, z, 0) && !T.pots.some(p => Math.hypot(p.x - x, p.z - z) < 2.5);
              let best = null; for (let gx = -A; gx <= A; gx += 1.5) for (let gz = -A; gz <= A; gz += 1.5) { if (!ok(gx, gz)) continue; for (let k = 0; k < 16; k++) { const a = k * Math.PI / 8; let run = 0; for (let d = 0.5; d <= 22; d += 0.5) { let c = true; for (const s of [-2, 0, 2]) if (!ok(gx + Math.sin(a) * d + Math.cos(a) * s, gz + Math.cos(a) * d - Math.sin(a) * s)) c = false; if (!c) break; run = d; }
                if (!best || run > best[3]) best = [gx, gz, a, run]; } } return best; })()""")
            put = lambda d, side=0: ev(f"""(() => {{ const T = __T, P = T.P, H = T.H, [gx, gz, a] = {json.dumps(spot[:3])}; P.x = gx; P.z = gz; P.y = 0; P.yaw = a; P.air = false; P.vy = 0; P.st = 'play'; P.spd = 0; P.stunT = 0; P.frozenT = 0; P.rollT = 0; P.flatT = 0; P.dry = false; P.paint = 1; P.dilT = 0; T.camYaw = a; T.camSnap = true;
                H.x = gx + Math.sin(a) * {d} + Math.cos(a) * {side}; H.z = gz + Math.cos(a) * {d} - Math.sin(a) * {side}; H.y = 0; H.yaw = a + Math.PI; H.st = 'play'; H.air = false; H.vy = 0; H.spd = 0; H.stunT = 0; H.frozenT = 0; H.rollT = 0; H.spawnGuard = 0; H.immuneT = 0; H.flatT = 0; }})()""")
            steps = lambda n, dt=1/60: ev(f"(() => {{ for (let i = 0; i < {n}; i++) __T.step({dt}); }})()")
        if 'speed' in SEC:
            for sk in ['swim', 'repel', 'pockets']:
                for wx in ['clear', 'rain']:
                    await put(30); await E(f"P.skill = '{sk}'; P.swimBoost = 1; setWx('{wx}', 30); speedMul = '{wx}' === 'rain' ? 2 : 1")
                    await E("H.ai = H.ai || null"); hs = []
                    for i in range(8): await steps(15); hs.append(await E("+P.spd.toFixed(2)"))
                    print(f'  {sk:8s} {wx:5s} spdK', await E("+spdK(P).toFixed(3)"), 'cfg.speed', await E("+cfg.speed.toFixed(2)"), 'P.spd over 2 s', hs)
            await E("setWx('clear', 30); speedMul = 1")
        if 'weather' in SEC:
            for sk in ['swim', 'repel']:
                await put(30); await E(f"P.skill = '{sk}'; setWx('rain', 30)"); await steps(60)
                r = await E("[+P.dilT.toFixed(2), P.exposed]"); await E("setWx('sun', 30)"); await steps(30)
                print(f'  {sk:6s} after rain: dilT', r[0], '| in the sun: exposed', await E("P.exposed"), 'paint', await E("+P.paint.toFixed(2)"))
            await E("setWx('clear', 30); P.skill = 'swim'")
        if 'pockets' in SEC:
            await put(30); await E("P.skill = 'pockets'; P.held = null; P.held2 = null; P.orbSaved = null")
            give = "(t => { const pw = { phase: 0, pop: 1, grace: 0, owner: null }; placePower(pw, t, [P.x, P.y, P.z]); powers.push(pw); collectPower(P, pw); })"
            await E(give + "('roller')"); await E(give + "('trap')"); print('two items', await E("[P.held, P.held2]"))
            await E("window.__orbKind = 'giant'; takeOrb(P)"); print('orb saved', await E("[P.orbSaved, P.giantT]"))
            await ev("window.__noStep = false"); await pg.wait_for_timeout(1200); await shot('pockets_hud'); await ev("window.__noStep = true")
            print('buttons', await ev("['itemBtn', 'itemBtn2', 'orbBtn'].map(id => { const b = document.getElementById(id), r = b.getBoundingClientRect(); return [id, b.hidden, b.textContent, Math.round(r.left), Math.round(r.top), Math.round(r.width)]; })"))
            print('use second (trap)', await E("useHeld2(P)"), await E("[P.held, P.held2, trapList.length]"))
            await E(give + "('turret')"); print('third pickup', await E("[P.held, P.held2]"))
            print('use saved orb', await E("useOrb(P)"), await E("[P.orbSaved, +P.giantT.toFixed(1)]")); await E("P.giantT = 0")
            await E("P.orbSaved = 'rocket'; window.__orbKind = 'giant'; takeOrb(P)"); print('one saved, the next goes off', await E("[P.orbSaved, +P.giantT.toFixed(1)]")); await E("P.giantT = 0; P.orbSaved = null; P.held = P.held2 = null; P.skill = 'swim'; clearTraps()")
        if 'trap' in SEC:
            await put(30); await E("P.skill = 'swim'; P.held = 'trap'"); print('drop', await E("useHeld(P)"), await E("trapList.map(T => [+T.x.toFixed(1), +T.z.toFixed(1), +T.arm.toFixed(2)])"))
            await steps(45); print('armed; you over your own:', await E("(() => { const T = trapList[0]; P.x = T.x; P.z = T.z; P.y = T.y; P.air = false; step(1/60); return [trapList.length, P.stunT]; })()"))
            await E("(() => { const T = trapList[0]; P.x = T.x + 6; H.x = T.x; H.z = T.z; H.y = T.y; H.air = false; H.rollT = 0; H.spd = 1; })()"); await steps(1)
            print('rival walks on:', await E("[trapList.length, +H.stunT.toFixed(2), +H.vy.toFixed(1), H.air]"))
            await ev("window.__noStep = false"); await pg.wait_for_timeout(200); await shot('trap_hit'); await ev("window.__noStep = true")
            await put(30); await E("P.held = 'trap'; useHeld(P)"); await steps(45)
            print('rival rolls through:', await E("(() => { const T = trapList[0]; P.x = T.x + 6; H.x = T.x; H.z = T.z; H.y = T.y; H.air = false; H.stunT = 0; H.rollT = ROLL_T; step(1/60); return [trapList.length, +H.stunT.toFixed(2)]; })()"))
            await put(30); await E("P.held = 'trap'; useHeld(P)"); await steps(45); await E("(() => { const T = trapList[0]; P.x = T.x + 6; P.z = T.z + 1; })()")
            await ev("window.__noStep = false"); await pg.wait_for_timeout(1500); await shot('trap_set'); await ev("window.__noStep = true"); await E("clearTraps()")
        if 'freeze' in SEC:
            await put(7); await E("orbGift(P, 'freeze')"); await steps(50); r1 = await E("[+H.frozenT.toFixed(2), frzList.length]"); await steps(6)
            print('you cast it: before the flash', r1, '| after', await E("[+H.frozenT.toFixed(2), +H.stunT.toFixed(2)]"))
            await ev("window.__noStep = false"); await pg.wait_for_timeout(700); await shot('freeze_hit'); await ev("window.__noStep = true")
            await steps(200); print('thawed after 3 s:', await E("[+H.frozenT.toFixed(2), +H.stunT.toFixed(2)]"))
            await put(7); await E("(() => { const p = pots.find(p => potUp(p) && !p.occ); enterPot(H, p); })()"); await E("orbGift(P, 'freeze')"); await steps(60)
            print('rival in a basin:', await E("[H.st, +H.frozenT.toFixed(2)]")); await E("H.st === 'hide' && exitPot(H)"); await steps(30)
            await put(7); await E("orbGift(P, 'freeze')"); await steps(50); await E("H.rollT = 0; dodgeRoll(H)"); await steps(6)
            print('rival rolls 0.1 s before the flash:', await E("[+H.frozenT.toFixed(2), +H.rollT.toFixed(2)]")); await steps(60)
            await put(7); await E("orbGift(P, 'freeze')"); await steps(20); await E("H.rollT = 0; dodgeRoll(H)"); await steps(36)
            print('rival rolls 0.37 s before:', await E("[+H.frozenT.toFixed(2)]")); await steps(200)
            await put(7); await E("orbGift(H, 'freeze')"); await steps(56); print('a CPU casts at you, no roll:', await E("[+P.frozenT.toFixed(2), document.getElementById('frost').className]"))
            await ev("window.__noStep = false"); await pg.wait_for_timeout(500); await shot('freeze_you'); await ev("window.__noStep = true"); await steps(200)
            await put(7); await E("orbGift(H, 'freeze')"); await steps(49); await E("P.rollT = 0; dodgeRoll(P)"); await steps(7)
            print('a CPU casts, you roll at the flash:', await E("[+P.frozenT.toFixed(2)]"))
        if 'shots' in SEC:
            # a trap 3 m ahead, armed, the rival off to the side
            await put(10, 3); await E("(() => { P.held = 'trap'; const sx = P.x, sz = P.z; P.x += Math.sin(P.yaw) * 3.2; P.z += Math.cos(P.yaw) * 3.2; useHeld(P); P.x = sx; P.z = sz; T.camSnap = true; })()".replace('T.camSnap', '__T.camSnap'))
            await steps(45); await pg.wait_for_timeout(2500); await shot('v_trap')
            # the rival onto it: the burst
            await E("(() => { const T = trapList[0]; H.x = T.x; H.z = T.z; H.y = T.y; H.air = false; H.rollT = 0; H.stunT = 0; H.tGuard = 0; })()"); await steps(1); await steps(8); await pg.wait_for_timeout(1500); await shot('v_trap_hit')
            await steps(120)
            # Flash Freeze: the wind-up, then the rival frozen up close
            await put(4.5, 0.6); await pg.wait_for_timeout(1500); await E("orbGift(P, 'freeze')"); await steps(30); await pg.wait_for_timeout(1200); await shot('v_frz_wind')
            await steps(26); await pg.wait_for_timeout(250); await shot('v_frz_flash'); await pg.wait_for_timeout(2200); await shot('v_frz_iced')
            await steps(200); await pg.wait_for_timeout(800)
            # a rival frozen up close (its AI held still so it stays put)
            await put(4, 0.4); await E("H.yaw = P.yaw + Math.PI * 0.6; window.__hai = H.ai; H.ai = null"); await pg.wait_for_timeout(1200); await E("H.stunT = 0.98; H.spd = 0; orbGift(P, 'freeze')"); await steps(56); await pg.wait_for_timeout(900); await shot('v_frz_rival'); await E("H.ai = window.__hai"); await steps(200)
            # a CPU's at you: your view frozen
            await put(5, 1); await pg.wait_for_timeout(1200); await E("orbGift(H, 'freeze')"); await steps(56); await pg.wait_for_timeout(1500); await shot('v_frz_you'); await steps(200)
            # you in a basin when it goes off
            await put(6, 1); await E("(() => { const p = pots.filter(p => potUp(p) && !p.occ).sort((a, b) => Math.hypot(a.x - P.x, a.z - P.z) - Math.hypot(b.x - P.x, b.z - P.z))[0]; enterPot(P, p); })()"); await steps(20)
            await E("orbGift(H, 'freeze')"); await steps(58); print('you in a basin:', await E("[P.st, +P.frozenT.toFixed(2)]"))
        if 'cputrap' in SEC:
            # a CPU holding a trap with you close: it drops it
            await put(5); await E("H.held = 'trap'; H.heldT = 0; clearTraps()"); used = None
            for i in range(40):
                await steps(6)
                if await E("!H.held"): used = await E("[+runT.toFixed(2), trapList.length, trapList[0] && trapList[0].owner === H]"); break
            print('CPU with a trap, you 5 m away: dropped', used)
            # CPUs heading straight for your trap: how often they roll through it (Fair critics: about half)
            rolls = 0; tries = 12
            for i in range(tries):
                await put(30); await E("clearTraps(); P.held = 'trap'; useHeld(P)"); await steps(40)
                r = await E("(() => { const T = trapList[0]; if (!T) return 'none'; P.x = T.x + 8; P.z = T.z + 8; const a = Math.random() * 6.283; H.x = T.x - Math.sin(a) * 1.4; H.z = T.z - Math.cos(a) * 1.4; H.y = T.y; H.yaw = a; H.spd = 4; H.air = false; H.rollT = 0; H.stunT = 0; H.tGuard = 0; H.stunGuard = 0; const ai = H.ai; H.ai = null; trapTick(0); H.ai = ai; const rolled = H.rollT > 0; H.ai = ai; for (let k = 0; k < 30 && trapList.length; k++) step(1/60); return [rolled, trapList.length, +H.stunT.toFixed(2)]; })()")
                if r != 'none' and r[0]: rolls += 1
                print('   ', r)
            print('CPU rolled through', rolls, 'of', tries, 'at', await E("diff"))
        if 'vote' in SEC:
            await E("tutSet('vote')"); await E("openVote(runId, () => {})"); await pg.wait_for_timeout(9000)
            print('vote lands on', await ev("document.getElementById('vvWin').textContent"))
        print('errors', errs[:6]); await b.close()
asyncio.run(main())
