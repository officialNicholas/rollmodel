# the preview strip for V66: close-ups of the new reactions, each staged and caught at its moment (HUD hidden): tumbling head over heels
# after a ram, bracing for the ground, tucked into a ball mid-roll, and jolted by a bump
import asyncio, sys, json
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
SETUP = r"""(stage) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage(stage); T.genWorld(88, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  document.querySelectorAll('#stage > *:not(#cv)').forEach(e => e.style.visibility = 'hidden');
  const H = T.H; H.st = 'out'; H.x = 99; H.z = 99; T.LH.drop.visible = false;
  for (let i = 0; i < 60; i++) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
  const P = T.P, open = n => { for (let a = 0; a < 16; a++) for (let r = 1; r <= 6; r += 1) { const x = n.x + Math.sin(a / 16 * 6.2832) * r, z = n.z + Math.cos(a / 16 * 6.2832) * r; if (T.surfaceUnder(x, z, 1) !== 0 || T.blockedAt(x, z, 0.3)) return false; } return true; }, nodes = T.NAVo.nodes.filter(n => n.h === 0 && n.edge === 0 && open(n));
  const n0 = nodes.sort((a, b) => Math.hypot(a.x, a.z) - Math.hypot(b.x, b.z))[0]; window.__n0 = n0;
  window.__adv = (dt) => { let n = Math.round(dt * 60); while (n-- > 0) { T.steerIn = 0; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } };
  window.__place = (yaw, spd) => { for (let i = 0; i < 50; i++) { T.steerIn = 0; P.x = n0.x; P.z = n0.z; P.y = 0; P.yaw = yaw; P.air = false; P.spd = spd; P.vy = 0; T.step(1 / 60); P.x = n0.x; P.z = n0.z; T.visuals(1 / 60, 1 / 60); } };
  window.__shot = (az, el, dist, look) => { const c = T.camera, D = T.P, R = T.VP.root, a = D.yaw + az; c.position.set(R.position.x + Math.sin(a) * dist, R.position.y + el, R.position.z + Math.cos(a) * dist); c.lookAt(R.position.x, R.position.y + (look || 0), R.position.z); c.fov = 30; c.updateProjectionMatrix(); T.renderFrame(); c.fov = 40; c.updateProjectionMatrix(); };
  return n0; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 520}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
        shots = []
        # 1) rammed: tumbling head over heels
        await pg.evaluate(SETUP, 'island')
        await pg.evaluate("""() => { const T = __T, P = T.P, H = T.H; window.__place(0, 0); H.st = 'play'; H.x = P.x; H.z = P.z - 0.75; H.y = 0; H.yaw = 0; H.spd = 11; H.flung = true; H.air = false; T.shove(H, P); P.yaw = 0; }""")
        await pg.evaluate("() => window.__adv(0.17)"); await pg.evaluate("() => window.__shot(1.35, 0.7, 4.6, 0.2)")
        await pg.screenshot(path=SP + 'rx/v66s_1.png'); shots.append(SP + 'rx/v66s_1.png')
        # 2) a jump coming down: bracing for the ground
        await pg.evaluate(SETUP, 'island')
        await pg.evaluate("() => { const T = __T; window.__place(0, T.cfg.speed * 0.8); T.jump(T.P); }")
        await pg.evaluate("() => window.__adv(0.6)"); await pg.evaluate("() => window.__shot(0.8, 0.35, 3.6, 0.2)")
        await pg.screenshot(path=SP + 'rx/v66s_2.png'); shots.append(SP + 'rx/v66s_2.png')
        # 3) a dodge roll: tucked into a ball
        await pg.evaluate(SETUP, 'island')
        await pg.evaluate("() => { const T = __T, P = T.P; window.__place(0, T.cfg.speed); P.rollCD = 0; T.dodgeRoll(P); }")
        await pg.evaluate("() => window.__adv(0.13)"); await pg.evaluate("() => window.__shot(1.3, 0.6, 3.8, 0.1)")
        await pg.screenshot(path=SP + 'rx/v66s_3.png'); shots.append(SP + 'rx/v66s_3.png')
        # 4) touching down from a jump: stubs planted out wide, the top carrying on over
        await pg.evaluate(SETUP, 'island')
        await pg.evaluate("() => { const T = __T; window.__place(0, T.cfg.speed * 0.8); T.jump(T.P); }")
        info = None
        for k in range(90):
            await pg.evaluate("() => window.__adv(1 / 60)")
            st = await pg.evaluate("() => ({ air: __T.P.air, splat: __T.VP.slime.st.splat, bp: __T.VP.slime.st.bp })")
            if not st['air']: info = st; break
        await pg.evaluate("() => window.__adv(2 / 60)"); await pg.evaluate("() => window.__shot(0.7, 0.4, 3.6, 0.15)")
        await pg.screenshot(path=SP + 'rx/v66s_4.png'); shots.append(SP + 'rx/v66s_4.png')
        ims = [Image.open(f).convert('RGB') for f in shots]; W, H = ims[0].size; gap = 12
        strip = Image.new('RGB', (len(ims) * W + (len(ims) - 1) * gap, H), (18, 14, 28))
        for i, im in enumerate(ims): strip.paste(im, (i * (W + gap), 0))
        strip.save(SP + 'out/RollModel-V66.jpg', quality=88); print('saved', strip.size, info)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
