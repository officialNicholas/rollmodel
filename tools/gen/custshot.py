# the compact Customize: nothing found yet (and a tap on a locked one), then everything (each category, the slider moved along),
# one-headgear-at-a-time, facial mix and match, the name button opening the name card
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'cu'
GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
W, H = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (390, 844)
SEEN = "{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1}"
async def boot(b, extra):
    ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=W < 700)
    await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify(Object.assign({ name: 'Nick', gfx: '" + GFX + "', mode: 'duel', stage: 'island', seen: " + SEEN + " }, " + extra + "))); } catch (e) {}")
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
    await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1800)
    return ctx, pg, errs
SETTLE = "(n) => { const T = __T; for (let i = 0; i < n; i++) T.visuals(1 / 60, 1 / 60); T.renderFrame(); }"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx, pg, errs = await boot(b, "{ color: 'orange' }")
        await pg.evaluate("() => { window.__noLoop = true; __T.openLook(); }"); await pg.evaluate(SETTLE, 160)
        r = await pg.evaluate("() => { const s = document.getElementById('look').getBoundingClientRect(); return { sheetTop: Math.round(s.top), sheetH: Math.round(s.height), tiles: document.querySelectorAll('#lookRail .ltile').length, locked: document.querySelectorAll('#lookRail .ltile.locked').length, name: document.getElementById('lookNameTxt').textContent }; }")
        print('locked view', json.dumps(r)); await pg.screenshot(path=SP + 'st/%s_locked.png' % TAG)
        await pg.click('#lookRail .ltile[data-w="tiara"]', force=True); await pg.wait_for_timeout(450)
        r = await pg.evaluate("() => document.getElementById('lookNote').textContent"); print('note', r); await pg.screenshot(path=SP + 'st/%s_note.png' % TAG)
        await ctx.close()
        ctx, pg, errs2 = await boot(b, "{ color: 'pink', owned: ['pirate','patch','flower','tophat','bowtie','tiara','lashes','hat','halo','fangs'], fresh: ['lashes'], look: { head: 'tiara' } }")
        await pg.evaluate("() => { window.__noLoop = true; __T.openLook(); }"); await pg.evaluate(SETTLE, 160)
        await pg.screenshot(path=SP + 'st/%s_head.png' % TAG)
        r = await pg.evaluate("() => { const r = document.getElementById('lookRail'); return { sw: r.scrollWidth, cw: r.clientWidth, more: r.classList.contains('more') }; }"); print('rail', json.dumps(r))
        await pg.evaluate("() => { const r = document.getElementById('lookRail'); r.scrollLeft = r.scrollWidth; }"); await pg.wait_for_timeout(200)
        await pg.click('#lookRail .ltile[data-w="halo"]'); await pg.wait_for_timeout(100); await pg.evaluate(SETTLE, 100)
        r = await pg.evaluate("() => ({ look: JSON.stringify(__T.myLook), less: document.getElementById('lookRail').classList.contains('less') })"); print('halo on', json.dumps(r))
        await pg.screenshot(path=SP + 'st/%s_halo.png' % TAG)
        await pg.click('#lc-face'); await pg.wait_for_timeout(450)
        await pg.click('#lookRail .ltile[data-w="lashes"]'); await pg.wait_for_timeout(80); await pg.click('#lookRail .ltile[data-w="patch"]'); await pg.wait_for_timeout(80); await pg.click('#lookRail .ltile[data-w="fangs"]'); await pg.wait_for_timeout(80)
        await pg.evaluate(SETTLE, 120); r = await pg.evaluate("() => ({ look: JSON.stringify(__T.myLook), fresh: __T.store.fresh, tabFresh: [...document.querySelectorAll('.lcat.fresh')].map(b => b.dataset.cat) })"); print('facial mix', json.dumps(r))
        await pg.screenshot(path=SP + 'st/%s_face.png' % TAG)
        await pg.click('#lc-cloth'); await pg.wait_for_timeout(450); await pg.click('#lookRail .ltile[data-w="bowtie"]'); await pg.wait_for_timeout(80); await pg.evaluate(SETTLE, 120)
        await pg.screenshot(path=SP + 'st/%s_cloth.png' % TAG)
        await pg.click('#lookNameBtn'); await pg.wait_for_timeout(300)
        r = await pg.evaluate("() => ({ modal: !document.getElementById('nameModal').hidden, title: document.getElementById('nameTitle').textContent, val: document.getElementById('nameInput').value })"); print('name card', json.dumps(r))
        await pg.fill('#nameInput', 'Sprinkle'); await pg.click('#nameOk'); await pg.wait_for_timeout(300)
        r = await pg.evaluate("() => ({ btn: document.getElementById('lookNameTxt').textContent, stored: __T.store.name, lookOpen: __T.lookOpen })"); print('renamed', json.dumps(r))
        await pg.evaluate(SETTLE, 30); await pg.screenshot(path=SP + 'st/%s_named.png' % TAG)
        print('errors', errs[:4], errs2[:4]); await ctx.close(); await b.close()
asyncio.run(main())
