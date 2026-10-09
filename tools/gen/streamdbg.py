# why does the island compile the paint-stream program (and an AO-hooked uv one) mid-match? Full keys of every program with a given cache-key
# fragment, after warm-up and again after the match starts / a power-up is taken, with the object that triggered it
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
THEME = sys.argv[1] if len(sys.argv) > 1 else 'island'
JS = """(theme) => { const T = __T, R = T.renderer, P = T.P, out = []; window.__noLoop = true;
  const run = (k) => { for (let i = 0; i < k; i++) { T.step(0.016); T.visuals(0.016, 0.016); if (i % 4 === 0) T.renderFrame(); } T.renderFrame(); };
  const keys = () => new Map(R.info.programs.map(p => [p.id, String(p.cacheKey)]));
  // catch which object's draw makes a new program
  const P0 = R.info.programs.length; let who = [];
  const orig = R.renderBufferDirect.bind(R);
  R.renderBufferDirect = function (camera, scene, geometry, material, object, group) { const n = R.info.programs.length; const r = orig(camera, scene, geometry, material, object, group);
    if (R.info.programs.length > n) { let o = object, path = []; while (o) { path.push((o.name || o.type) + (o.userData && o.userData.tag ? '#' + o.userData.tag : '')); o = o.parent; } who.push({ mat: material.type + ':' + (material.name || '') + ':' + (material.customProgramCacheKey ? String(material.customProgramCacheKey()).slice(0, 40) : ''), vis: object.visible, layers: object.layers.mask, inst: !!object.isInstancedMesh, recv: object.receiveShadow, cast: object.castShadow, geoAttrs: Object.keys(geometry.attributes).join(','), path: path.slice(0, 6).join(' < '), cam: camera.type + (camera.isOrthographicCamera ? '(shadow?)' : ''), rt: R.getRenderTarget() ? 'RT' : 'screen' }); }
    return r; };
  const before = keys(); T.start(); run(120); const after = keys();
  for (const [id, k] of after) if (!before.has(id)) { out.push(['NEW', id, k]); for (const [id2, k2] of before) { const a = k.split(','), b = k2.split(','); if (a.length === b.length && a[a.length - 1] === b[b.length - 1]) { const d = []; a.forEach((x, i) => { if (x !== b[i]) d.push(i + ':' + b[i] + '->' + x); }); if (d.length < 8) out.push(['  vs', id2, d.join(' | ')]); } } }
  out.push(['who (match)', who]); who = [];
  const before2 = keys(); const pw = T.POWER_SPOTS.find(s => s[3]); if (pw) { P.x = pw[0]; P.z = pw[2]; } run(40); out.push(['power', JSON.stringify(P.power || null).slice(0, 80)]); const after2 = keys();
  for (const [id, k] of after2) if (!before2.has(id)) { out.push(['NEW2', id, k]); for (const [id2, k2] of before2) { const a = k.split(','), b = k2.split(','); if (a.length === b.length && a[a.length - 1] === b[b.length - 1]) { const d = []; a.forEach((x, i) => { if (x !== b[i]) d.push(i + ':' + b[i] + '->' + x); }); if (d.length < 8) out.push(['  vs', id2, d.join(' | ')]); } } }
  out.push(['who (power)', who]);
  return out; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 240, 'height': 520}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.wait_for_function('!__T.SLIME || (__T.SLIME.S.ready && __T.VP.slime)', polling=200, timeout=60000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(theme) => { __T.setStage && __T.setStage(theme === 'island' || theme === 'blank' ? theme : 'season'); __T.freshMap(); }", THEME)
        await pg.wait_for_timeout(3000)
        r = await pg.evaluate(JS, THEME)
        for row in r: print(json.dumps(row)[:1500])
        print('errors', errs[:3])
        await b.close()
asyncio.run(main())
