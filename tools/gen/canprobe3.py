import asyncio, sys, json
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640})
        await ctx.add_init_script("window.__skipIntro = false; window.__introKind = 'cannon'; window.__noPitch = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + sys.argv[1], timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.setStage('island'); T.genWorld(88, { themes: ['island'] }); T.mapUsed = false;
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          document.getElementById('menu').hidden = true; T.beginMatch(); for (let i = 0; i < 108; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); }
          window.__cam2 = () => { const c = T.camera, P = T.P; c.position.set(P.x + 2.2, P.y + 0.8, P.z + 2.2); c.lookAt(P.x, P.y + 0.4, P.z); c.updateMatrixWorld(); }; }""")
        names = []
        for mode in ['all', 'noslime', 'nooldblob', 'noroot']:
            info = await pg.evaluate("""(mode) => { const T = __T, V = T.VP, I = V.slime; const keep = []; 
              if (mode === 'noslime') { keep.push([I.root, I.root.visible]); I.root.visible = false; }
              if (mode === 'nooldblob' && V.oldBlob) { keep.push([V.oldBlob, V.oldBlob.visible]); V.oldBlob.visible = false; }
              if (mode === 'noroot') { keep.push([V.root, V.root.visible]); V.root.visible = false; }
              window.__cam2(); T.renderFrame(); setTimeout(() => {}, 0); window.__keep = keep;
              const kids = []; V.root.traverse(o => { if (o.visible && o.isMesh) kids.push((o.name || o.type) + ':' + (o.material && (o.material.type + '/' + (o.material.customProgramCacheKey ? o.material.customProgramCacheKey() : '')))); });
              return { oldBlob: V.oldBlob ? V.oldBlob.visible : null, slimeVis: I.root.visible, kids: kids.slice(0, 30) }; }""", mode)
            fn = SP + 'rx/_cp_%s.png' % mode; await pg.screenshot(path=fn); names.append(fn); print(mode, json.dumps(info)[:900])
            await pg.evaluate("() => { for (const [o, v] of window.__keep) o.visible = v; }")
        ims = [Image.open(f).convert('RGB').crop((0, 100, 360, 460)) for f in names]
        s = Image.new('RGB', (360 * len(ims), 360));
        for i, im in enumerate(ims): s.paste(im, (i * 360, 0))
        s.save(SP + 'rx/canprobe_' + sys.argv[1].replace('.html','') + '.png'); print(errs[:3]); await b.close()
asyncio.run(main())
