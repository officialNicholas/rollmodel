"""v213: the Abilities square on the lobby rail (locked at rank 2, the tap's note; at rank 3, coming soon), and the commissions board with
a finished job striped in place (no new job dealt), then all three done; portrait and landscape."""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/abil'
SIZES = [(390, 844, 'p'), (844, 390, 'l')] if len(sys.argv) < 2 else [(390, 844, 'p')] if sys.argv[1] == 'p' else [(844, 390, 'l')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, t in SIZES:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{look:1}, runs: 9, xp: 140, drops: 168, tut: { ph: 'done' }, comm: { day: new Date().toDateString(), active: ['play3', 'cov25', 'solo30'], prog: { play3: 1 }, done: [] } })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' and 'Failed to load' not in m.text and 'ERR_FAILED' not in m.text else None)
            await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(3500)
            await pg.screenshot(path=f'{OUT}/{t}_lobby.png', timeout=120000)
            print(t, 'rank 2:', await pg.evaluate("[document.getElementById('abilBtn').className, document.getElementById('abilTag').textContent, document.getElementById('abilBtn').getAttribute('aria-label'), JSON.stringify(document.getElementById('abilBtn').getBoundingClientRect())]"))
            await pg.evaluate("document.getElementById('abilBtn').click()"); await pg.wait_for_timeout(450)
            print(t, 'tap:', await pg.evaluate("(document.querySelector('#abilBtn .abtoast') || {}).textContent"))
            await pg.screenshot(path=f'{OUT}/{t}_locked_tap.png', timeout=120000)
            await pg.wait_for_timeout(2200)
            await pg.evaluate("__T.store.xp = 260; __T.renderLobbyUI()"); await pg.wait_for_timeout(500)
            await pg.evaluate("document.getElementById('abilBtn').click()"); await pg.wait_for_timeout(450)
            print(t, 'rank 3:', await pg.evaluate("[document.getElementById('abilBtn').className, document.getElementById('abilTag').textContent, document.getElementById('abilBtn').getAttribute('aria-label'), (document.querySelector('#abilBtn .abtoast') || {}).textContent]"))
            await pg.screenshot(path=f'{OUT}/{t}_soon_tap.png', timeout=120000)
            await pg.wait_for_timeout(2200)
            # a job finished in a match: it stays in its place, striped; nothing new is dealt
            r = await pg.evaluate("""(() => { const f1 = __T.commProgress({ you: 26.2, mode: 'duel', win: 0 }).map(k => k.id), c = __T.store.comm, a1 = c.active.slice(), d1 = c.done.slice(), pr = JSON.stringify(c.prog);
              const f2 = __T.commProgress({ you: 41, mode: 'duel', win: 1 }).map(k => k.id); return { f1, a1, d1, pr, f2, a2: c.active.slice(), d2: c.done.slice(), badge: document.getElementById('commBadge').textContent }; })()""")
            print(t, 'progress:', json.dumps(r))
            await pg.evaluate("__T.renderLobbyUI()"); await pg.wait_for_timeout(300)
            await pg.evaluate("document.getElementById('commBtn').click()"); await pg.wait_for_timeout(1400)
            await pg.screenshot(path=f'{OUT}/{t}_comm_one.png', timeout=120000)
            print(t, 'board:', await pg.evaluate("[...document.querySelectorAll('#commList .comm')].map(c => c.className + ' | ' + c.querySelector('.ct b').textContent + ' | ' + c.querySelector('.ring').dataset.n)"), await pg.evaluate("!!document.querySelector('#commList .cnote')"))
            # all three done
            await pg.evaluate("(() => { const c = __T.store.comm; c.done = c.active.slice(); c.prog = {}; __T.renderComms(); })()"); await pg.wait_for_timeout(1200)
            await pg.screenshot(path=f'{OUT}/{t}_comm_all.png', timeout=120000)
            print(t, 'all done note:', await pg.evaluate("(document.querySelector('#commList .cnote') || {}).textContent"))
            print(t, 'errors', errs[:6]); await ctx.close()
        await b.close()
asyncio.run(main())
