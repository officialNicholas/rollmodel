"""v204: the window in the dim round what each between-match tip points at: the four panes against the target, brightness inside vs
outside from the screenshot, and the shots (the shop's Back to the lobby tip from the user's report among them)"""
import asyncio, io
from PIL import Image
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
GEOM = """(() => { const t = __T.tutTip, d = document.getElementById('tutDim'), st = document.getElementById('stage') || document.body, r0 = st.getBoundingClientRect();
  const at = !t || !t.at ? null : typeof t.at === 'string' ? document.getElementById(t.at) : typeof t.at === 'function' ? t.at() : t.at;
  const R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
  return { key: t && t.key, cls: d.className, target: at ? R(at) : null, panes: [...d.children].map(R), op: getComputedStyle(d.children[0]).opacity, bf: getComputedStyle(d.children[0]).backdropFilter }; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, tag in [(430, 932, 'port'), (844, 390, 'land')]:
            for ph, own, steps in [('locker', "['fangs','flower']", [('lobby', 'locker', None), ('shopback', 'back', 'dabsBtn')]),
                                   ('shop', "[]", [('shopflower', 'buyflower', 'dabsBtn')]),
                                   ('locker', "['fangs','flower']", [('lockerface', 'face', 'lookBtn')])]:
                ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
                await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', runs: 1, drops: 60, owned: " + own + ", tut: { ph: '" + ph + "' }, seen: { look: 1 } })); } catch (e) {}")
                pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
                await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
                await pg.wait_for_function("__T.tutTip && __T.tutTip.key", timeout=240000)
                for name, key, click in steps:
                    if click: await pg.evaluate(f"document.getElementById('{click}').click()")
                    await pg.wait_for_function(f"__T.tutTip && __T.tutTip.key === '{key}'", timeout=60000); await pg.wait_for_timeout(1600)
                    g = await pg.evaluate(GEOM); png = await pg.screenshot(); im = Image.open(io.BytesIO(png)).convert('L'); k = im.width / w
                    def lum(x0, y0, x1, y1):
                        c = im.crop((int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k))); return round(sum(c.getdata()) / max(1, c.width * c.height))
                    t = g['target']; inside = lum(t[0] + 4, t[1] + 4, t[2] - 4, t[3] - 4) if t else None
                    a, bb, l, r = g['panes']; gap = [l[2], a[3], r[0], bb[1]]
                    print(f"{tag} {name:11s} key={g['key']:9s} target={t} gap={gap} inside_lum={inside} panes_on={g['op']} blur={g['bf']} errs={errs}")
                    im2 = Image.open(io.BytesIO(png)); im2.save(f'{WS}/ui/cut_{tag}_{name}.png')
                await ctx.close()
        await b.close()
asyncio.run(main())
