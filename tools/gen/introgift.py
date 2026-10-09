# the real start (basin intro, no skipping) with an item due: the plan's made, the intro plays out into the match, the item turns up
import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', stage: 'crypt', itemIn: 0, owned: ['hat'], seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.start(); const g = T.gift; const plan = { id: g.id, at: +g.at.toFixed(1), state: T.state };
          const seq = []; for (let i = 0; i < 60 * 6; i++) { T.step(1 / 60); if (i % 30 === 0) { T.visuals(1 / 2, 1 / 2); seq.push(T.state); } }
          g.at = Math.min(g.at, T.runT + 0.5); for (let i = 0; i < 120 && !g.on; i++) { T.aiStep(T.P, 1 / 60); T.steerIn = T.P.steer; T.step(1 / 60); }
          return { plan, seq: seq.join(','), on: g.on, runT: +T.runT.toFixed(1), set: g.id }; }""")
        print(json.dumps(r)); print('errors', errs[:5]); await b.close()
asyncio.run(main())
