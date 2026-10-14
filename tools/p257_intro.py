#!/usr/bin/env python3
"""v257 intro probe: boots the test build (q257_intro.py --test) as a brand-new player, plays the whole intro through its cards, and
grabs a frame at each stage, then checks the lobby, the coach and the errors. Also: an existing player boots straight to the lobby.
Usage: p257_intro.py <out dir> [port|land] [inset]   (inset: the app's top bar and home bar, 59 and 34 px)"""
import asyncio, json, os, sys, time
from playwright.async_api import async_playwright
OUT = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'port'; INSET = len(sys.argv) > 3 and sys.argv[3] == 'inset'
VP = (390, 780) if MODE == 'port' else (780, 390)
PAGE = os.environ.get('PAGE', '_intro_test.html')
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(OUT, f'log_{MODE}{"_inset" if INSET else ""}.txt'), 'w')
def log(*a):
    print(*a, flush=True); LOG.write(' '.join(str(x) for x in a) + '\n'); LOG.flush()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': VP[0], 'height': VP[1]}, device_scale_factor=1, has_touch=True, is_mobile=True)
        save = os.environ.get('SAVE')
        await ctx.add_init_script("window.__tapGate = false; try { localStorage.clear(); " + (f"localStorage.setItem('paint-world-red.v1', {json.dumps(save)});" if save else "") + " } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:400]))
        pg.on('console', lambda m: errs.append(m.type + ' ' + m.text[:300]) if m.type in ('error', 'warning') and 'Failed to load' not in m.text else None)
        if INSET:
            cdp = await ctx.new_cdp_session(pg)
            try: await cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': {'top': 59, 'bottom': 34, 'left': 0, 'right': 0}})
            except Exception as e: log('inset override failed', e)
        t0 = time.time()
        await pg.goto(f'http://localhost:8765/{PAGE}', timeout=600000)
        await pg.wait_for_function('typeof __T === "object"', timeout=600000, polling=500)
        log('booted', round(time.time() - t0, 1), 's')
        tag = MODE + ('_inset' if INSET else '')
        async def shot(name):
            path = os.path.join(OUT, f'{tag}_{name}.png'); await pg.screenshot(path=path); log('shot', name, await peek())
        async def peek():
            return await pg.evaluate("__T.ev('FL && FL.peek && FL.peek()')")
        if save:
            await pg.wait_for_timeout(4000); live = await pg.evaluate("__T.ev('!!(FL && FL.live)')")
            log('existing player: intro live =', live, 'state', await pg.evaluate("__T.ev('state')")); await shot('existing'); log('ERRORS', errs); return
        if await pg.evaluate("__T.ev('!!(FL && FL.due)')") is not True:
            log('intro not due!'); return
        # the orientation chooser comes first for a new player: pick the one that fits
        await pg.wait_for_timeout(1500)
        if await pg.evaluate("!document.getElementById('orient').hidden"):
            await shot('orient'); await pg.evaluate("document.querySelector('#orient .ocard[data-o=\"%s\"]').click(); document.getElementById('orientOk').click()" % MODE)
            await pg.wait_for_timeout(800)
            if await pg.evaluate("!document.getElementById('orient').hidden"):
                btn = await pg.evaluate("[...document.querySelectorAll('#orient button')].map(b => b.id + ':' + b.textContent.trim()).join(' | ')"); log('orient buttons', btn)
        async def until(cond, to=240):
            t = time.time()
            while time.time() - t < to:
                v = await peek()
                if v and eval(cond, {}, {'v': v}): return v
                if not v and 'None' in cond: return v
                await pg.wait_for_timeout(120)
            log('timeout waiting for', cond); return None
        # (the sky: the stars, the title, the pan down; then the drum, its thumps first: v257_intro.js SKY and BAR0)
        for k, at in [('a0_sky', 0.8), ('a1_title', 3.6), ('a2_pan', 7.4)]:
            await until(f"v['ph'] == 'sky' and v['pt'] >= {at}"); await shot(k)
        for k, at in [('a_barrel', 0.2), ('a3_thump', 0.75), ('b_wobble', 2.45), ('c_tip', 3.95), ('d_pour', 4.95), ('e_pour2', 6.25), ('f_eyes', 7.85), ('g_look', 8.95)]:
            await until(f"v['ph'] == 'barrel' and v['pt'] >= {at}"); await shot(k)
        await until("v['ph'] == 'iris' and v['pt'] > 1.2"); await shot('h_iris')
        await pg.click('.flopt[data-i="blue"]'); await pg.wait_for_timeout(900); await shot('h2_blue')
        await pg.click('#flIrisGo'); await until("v['ph'] == 'style' and v['pt'] > 1.0")
        await pg.click('.flopt[data-s="edgy"]'); await pg.wait_for_timeout(900); await shot('i_style')
        await pg.click('#flStyleGo'); await until("v['ph'] == 'paint' and v['pt'] > 1.4"); await shot('j_paintcard')
        await pg.click('.flopt[data-c="purple"]'); await pg.wait_for_timeout(1500); await shot('k_purple')
        await pg.click('#flPaintGo')
        for k, at in [('l_rise', 0.6), ('m_jump', 1.55), ('n_land', 2.1), ('o_shake', 2.45)]:
            await until(f"v['ph'] == 'form' and v['pt'] >= {at}"); await shot(k)
        await until("v['ph'] == 'name' and v['pt'] > 1.0"); await shot('p_namecard')
        await pg.fill('#flNameIn', 'Pip'); await pg.click('#flNameGo')
        await until("v['ph'] == 'confirm' and v['pt'] > 0.9"); await shot('p2_confirm')
        await pg.click('#flYes')
        await until("v['ph'] == 'wink' and v['pt'] >= 0.9"); await shot('q_wink')
        await until("v['ph'] == 'wink' and v['pt'] >= 1.8"); await shot('r_jumpoff')
        t = time.time()
        while await pg.evaluate("__T.ev('!!FL.live')") and time.time() - t < 120: await pg.wait_for_timeout(100)
        await pg.wait_for_timeout(250); await shot('s_reveal')
        await pg.wait_for_timeout(700); await shot('t_jumpin')
        t = time.time()
        while await pg.evaluate("__T.ev('!!FL.jin')") and time.time() - t < 60: await pg.wait_for_timeout(150)
        await pg.wait_for_timeout(600); await shot('u_lobby')
        t = time.time()
        while await pg.evaluate("document.getElementById('tut').hidden") and time.time() - t < 60: await pg.wait_for_timeout(200)
        await pg.wait_for_timeout(500); await shot('v_coach')
        st = await pg.evaluate("__T.ev('JSON.stringify({ name: store.name, color: store.color, look: store.look, introDone: store.introDone, tut: store.tut, music: AU._trk(), state })')")
        log('store after', st); log('coach', await pg.evaluate("document.getElementById('tutText') && document.getElementById('tutText').textContent"))
        log('ERRORS', errs)
        await b.close()
asyncio.run(main())
