"""The v208 home screen: the lobby (power bar, dabs, friends, the spots beside you), the menu slid open, Settings, a page of words, the
stats behind the power bar, friends (soon); portrait and landscape. Checks the sound switches drive the audio graph's gates."""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
SIZES = [(390, 844, 'p'), (844, 390, 'l')] if len(sys.argv) < 2 else [(390, 844, 'p')] if sys.argv[1] == 'p' else [(844, 390, 'l')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, t in SIZES:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{look:1}, runs: 9, xp: 140, drops: 168, wins: { fair: 4, trio: 1 }, played: { fair: 7, trio: 2, solo: 1 }, bestCov: { fair: 41, solo: 52 }, tut: { ph: 'done' } })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' and 'Failed to load' not in m.text and 'ERR_FAILED' not in m.text else None)
            await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(3500)
            await pg.screenshot(path=f'{OUT}/hu_{t}_lobby.png')
            print(t, 'lobby', await pg.evaluate("[document.getElementById('pbar').hidden, document.getElementById('pbLvl').textContent, document.getElementById('pbNext').textContent, document.getElementById('pbXp').textContent, document.getElementById('statDrops').textContent, getComputedStyle(document.querySelector('.corner')).display, document.body.classList.contains('homeon')]"))
            await pg.evaluate("document.getElementById('hamBtn').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{OUT}/hu_{t}_menu.png')
            await pg.evaluate("document.getElementById('smSet').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{OUT}/hu_{t}_set.png')
            print(t, 'settings', await pg.evaluate("[document.getElementById('setModal').hidden, document.getElementById('sideMenu').hidden, document.getElementById('setVer').textContent]"))
            # the switches: music off, then effects off (both off is the old mute), then both back on
            await pg.evaluate("document.querySelector('#musPick [data-v=off]').click()"); await pg.wait_for_timeout(300)
            print(t, 'music off', await pg.evaluate("[__T.store.musicOff, __T.store.sfxOff, __T.store.muted, document.querySelector('#musPick [data-v=off]').getAttribute('aria-pressed')]"))
            await pg.screenshot(path=f'{OUT}/hu_{t}_set2.png')
            await pg.evaluate("document.querySelector('#sfxPick [data-v=off]').click()"); await pg.wait_for_timeout(300)
            print(t, 'both off', await pg.evaluate("[__T.store.musicOff, __T.store.sfxOff, __T.store.muted]"))
            await pg.evaluate("document.querySelector('#sfxPick [data-v=on]').click(); document.querySelector('#musPick [data-v=on]').click()"); await pg.wait_for_timeout(300)
            await pg.evaluate("document.getElementById('credBtn').click()"); await pg.wait_for_timeout(700); await pg.screenshot(path=f'{OUT}/hu_{t}_doc.png')
            await pg.evaluate("document.getElementById('docClose').click()"); await pg.wait_for_timeout(500)
            print(t, 'doc closed', await pg.evaluate("[document.getElementById('docModal').hidden, document.getElementById('setModal').hidden, document.activeElement && document.activeElement.id]"))
            await pg.evaluate("document.getElementById('setBack').click()"); await pg.wait_for_timeout(600)
            await pg.evaluate("document.getElementById('pbar').click()"); await pg.wait_for_timeout(800); await pg.screenshot(path=f'{OUT}/hu_{t}_stats.png')
            print(t, 'stats', await pg.evaluate("[document.getElementById('stWins').textContent, document.getElementById('stPlayed').textContent, document.getElementById('stRate').textContent, document.getElementById('stBest').textContent, document.getElementById('stXp').textContent]"))
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
            await pg.evaluate("document.getElementById('friendsBtn').click()"); await pg.wait_for_timeout(800); await pg.screenshot(path=f'{OUT}/hu_{t}_friends.png')
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
            await pg.evaluate("document.getElementById('slotL').click()"); await pg.wait_for_timeout(500)
            print(t, 'slot opens friends', await pg.evaluate("!document.getElementById('friendsModal').hidden"))
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
            # a rank up: the paint runs to the end, the rank pops, then on to the new XP
            await pg.evaluate("__T.store.xp = 260; __T.renderLobbyUI && __T.renderLobbyUI()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{OUT}/hu_{t}_lvup.png', clip={'x': 0, 'y': 0, 'width': w, 'height': h // 2 + 120})
            await pg.wait_for_timeout(2500)
            print(t, 'rank up', await pg.evaluate("[document.getElementById('pbLvl').textContent, document.getElementById('pbNext').textContent, document.getElementById('pbXp').textContent]"))
            print(t, 'errors', errs[:6]); await ctx.close()
        await b.close()
asyncio.run(main())
