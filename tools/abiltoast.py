import asyncio, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/abil'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, t in [(390, 844, 'p'), (844, 390, 'l')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{look:1}, runs: 9, xp: 140, drops: 168, tut: { ph: 'done' } })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(3000)
            await pg.add_style_tag(content='.abtoast{animation:none!important}')
            await pg.evaluate("(() => { document.getElementById('abilBtn').click(); const t = document.querySelector('.abtoast'), c = t.cloneNode(true); c.classList.add('keep'); t.parentNode.appendChild(c); t.remove(); window.__abKeep = setInterval(() => document.getElementById('lobbyRail').classList.add('abup'), 50); })()"); await pg.wait_for_timeout(300)
            print(t, await pg.evaluate("(() => { const e = document.querySelector('.abtoast'); if (!e) return 'none'; const r = e.getBoundingClientRect(), top = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2); const cs = getComputedStyle(e); return [JSON.stringify(r), top && (top.id || top.className), cs.opacity, cs.visibility, cs.zIndex]; })()"))
            print(t, await pg.evaluate("(() => { const out = []; let e = document.querySelector('.abtoast'); while (e && e !== document.documentElement) { const cs = getComputedStyle(e); if (cs.overflow !== 'visible' || cs.clipPath !== 'none' || cs.contain !== 'none' || cs.maskImage !== 'none' || cs.webkitMaskImage !== 'none') out.push((e.id || e.className) + ' ov=' + cs.overflow + ' clip=' + cs.clipPath.slice(0, 40) + ' contain=' + cs.contain + ' mask=' + (cs.maskImage || cs.webkitMaskImage).slice(0, 40)); e = e.parentElement; } return out; })()"))
            await pg.screenshot(path=f'{OUT}/{t}_toast.png', timeout=120000, clip={'x': 0, 'y': 120 if t == 'p' else 60, 'width': min(w, 420), 'height': 260})
            print(t, 'errors', errs[:4]); await ctx.close()
        await b.close()
asyncio.run(main())
