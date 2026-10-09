# Shader programs compiled mid-match = hitches on a phone. Counts programs after boot, after the match settles, then after each
# event that brings in something new (power-ups, the orb, giant slams, rain, floaters fading, a knockout, the victory screen).
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t'
THEME = sys.argv[2] if len(sys.argv) > 2 else 'cathedral'
JS = """(theme) => { const T = __T, R = T.renderer, P = T.P, out = []; window.__noLoop = true;
  const n = () => R.info.programs.length, run = (k) => { for (let i = 0; i < k; i++) { T.step(0.016); T.visuals(0.016, 0.016); if (i % 4 === 0) T.renderFrame(); } T.renderFrame(); };
  const names = () => R.info.programs.map(p => p.id + '|' + p.name + '|' + (String(p.cacheKey).match(/slime-[a-z]+|jelly[a-z-]*|[A-Za-z]+Material/) || [''])[0] + '|' + String(p.cacheKey).length + '|' + String(p.cacheKey).slice(0, 160).split(String.fromCharCode(10)).join(' ')); let seen = new Set(names()); const diff = (label) => { const now = names(); const nw = now.filter(x => !seen.has(x)); seen = new Set(now); if (nw.length) out.push([label + ' NEW', nw]); };
  const mark = (label, f) => { const a = n(); try { f(); } catch (e) { out.push([label, 'ERR ' + String(e).slice(0, 80)]); return; } run(30); out.push([label, n() - a]); diff(label); };
  out.push(['boot', n()]);
  out.push(['stage built (warmed)', n()]);
  diff('pre'); T.start(); run(120); out.push(['match +2s', n()]); diff('match');
  mark('more play', () => run(120));
  mark('power-up taken', () => { const pw = T.POWER_SPOTS.find(s => s[3]); if (pw) { P.x = pw[0]; P.z = pw[2]; } run(40); });
  mark('orb + giant', () => { T.orbSpawn && T.orbSpawn(); run(10); T.takeOrb && T.takeOrb(P); });
  mark('giant slam', () => { P.air = true; P.vy = 2; P.y = 2; T.useSlam && T.useSlam(P); run(60); });
  mark('rain', () => T.setWx('rain', 10));
  mark('sun', () => T.setWx('clear', 10));
  mark('under a floater', () => { const fb = T.BOXES.find(b => b[4] > 0.5); if (fb) { P.x = (fb[0] + fb[1]) / 2; P.z = (fb[2] + fb[3]) / 2; P.y = 0; for (let i = 0; i < 60; i++) { T.step(0.016); P.x = (fb[0] + fb[1]) / 2; P.z = (fb[2] + fb[3]) / 2; T.visuals(0.016, 0.016); T.renderFrame(); } } });
  mark('knockout', () => { T.knockOut && T.knockOut(T.H2 || T.H, P); });
  mark('fling', () => { T.flingIt(P, 0.9); run(60); });
  mark('into a refill and out (paint bursts off)', () => { const pot = T.pots3.find(p => p.st === 'up' || p.st === undefined) || T.pots3[0]; T.enterPot2(P, pot); run(30); T.jump(P); run(50); });
  mark('wading through paint', () => { run(60); });
  mark('roller', () => { P.power = { type: 'roller', t: 3 }; run(60); P.power = null; run(30); });
  mark('turret', () => { T.startTurret(P); run(40); const sh = T.shots; T.fireShot && T.fireShot(P); run(40); });
  mark('giant rolling', () => { P.turret = null; P.giantT = 6; P.spd = 6; run(60); });
  mark('slime forms', () => { const I = T.VP.slime; if (I) out.push(['form', I.form, I.giant.rolling]); });
  mark('victory', () => { T.matchLeft = 0.01; run(30); });
  mark('victory frames', () => run(60));
  out.push(['total', n()]);
  return out; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 240, 'height': 520}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(SP + PAGE + '.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.wait_for_function('!__T.SLIME || (__T.SLIME.S.ready && __T.VP.slime)', polling=200, timeout=60000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(theme) => { __T.setStage && __T.setStage(theme === 'island' || theme === 'blank' ? theme : 'season'); __T.freshMap(); }", THEME)
        await pg.wait_for_timeout(3000)
        r = await pg.evaluate(JS, THEME)
        for row in r: print(PAGE, THEME, row)
        print('errors', errs[:3])
        await b.close()
asyncio.run(main())
