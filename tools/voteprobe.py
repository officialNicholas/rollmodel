import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1}, mode:'trio', runs: 3, stage:'island' })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        print('mode', await pg.evaluate("[__T.mode, __T.tutPh()]"))
        await pg.evaluate("window.__instant = false; window.__noVote = false; document.getElementById('homePlay').click()")
        await pg.wait_for_function("!document.getElementById('vvote').hidden", timeout=60000); await pg.wait_for_timeout(3600)
        await pg.evaluate("const vs = __T.voteState; vs.votes.set(__T.P, 'island'); vs.votes.set(__T.H, 'manor'); vs.votes.set(__T.H2, 'manor');")
        await pg.wait_for_function("document.querySelector('#vts .vt.win')", timeout=60000)
        print('win', await pg.evaluate("[document.querySelector('#vts .vt.win').dataset.s, document.getElementById('vvWin').textContent, document.getElementById('vvLbl').textContent]"))
        await pg.screenshot(path=f'{WS}/ui/vote_major.png'); print('errors', errs[:3]); await b.close()
asyncio.run(main())
