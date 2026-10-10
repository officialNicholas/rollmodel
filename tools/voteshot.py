import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 393, 'height': 852}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, owned:[], bought:[], drops:300, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2000)
        await pg.screenshot(path=f'{WS}/ui/vote_lobby.png', clip={'x': 0, 'y': 700, 'width': 393, 'height': 152})
        await pg.evaluate("document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{WS}/ui/vote_world.png')
        print('note', await pg.evaluate("[document.getElementById('soloNote').textContent, document.getElementById('cvName').textContent, document.getElementById('lobbyPickLbl').textContent]"))
        await pg.evaluate("const b = [...document.querySelectorAll('#modes button')].find(x => /solo/i.test(x.textContent)); b && b.click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/vote_world_solo.png')
        print('solo', await pg.evaluate("[document.getElementById('soloNote').textContent, document.getElementById('cvName').textContent]"))
        await pg.evaluate("const b = [...document.querySelectorAll('#modes button')].find(x => /1v1/i.test(x.textContent)); b && b.click()"); await pg.wait_for_timeout(600)
        await pg.evaluate("window.__noVote = false; window.__instant = false"); await pg.tap('#startBtn')
        await pg.wait_for_function("!document.getElementById('vvote').hidden", timeout=30000); await pg.wait_for_timeout(2800); await pg.screenshot(path=f'{WS}/ui/vote_strip.png')
        print('vote', await pg.evaluate("[document.getElementById('vvLbl').textContent, !!document.querySelector('.vt.mine')]"), errs[:2]); await b.close()
asyncio.run(main())
