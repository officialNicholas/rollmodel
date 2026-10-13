"""Stage geometry census: what the built stage draws (each mesh in stageGroup: triangles, material, shadow, size) and, for the dressed
stages, which builder lines put the most triangles into the merged props. usage: census.py <stage>"""
import asyncio, json, sys, re
from playwright.async_api import async_playwright
STAGE = sys.argv[1]
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 195, 'height': 422}, device_scale_factor=1, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'%s', seen:{look:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}" % STAGE)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_census.html', timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.wait_for_timeout(1000)
        R = await pg.evaluate("""(() => { const out = [], g = __T.stageGroup; let tot = 0, totS = 0;
          g.traverse(o => { if (!o.isMesh || o === g) return; const geo = o.geometry; let n = (geo.index ? geo.index.count : geo.attributes.position ? geo.attributes.position.count : 0) / 3; if (o.isInstancedMesh) n *= o.count;
            if (!geo.boundingSphere) geo.computeBoundingSphere(); const bs = geo.boundingSphere, m = Array.isArray(o.material) ? o.material[0] : o.material;
            out.push({ n: Math.round(n), vis: o.visible, cs: !!o.castShadow, tr: !!m.transparent, so: m.colorWrite === false || (m.name || '').includes('shadow'), mt: m.type.replace('Material', ''), col: m.color ? '#' + m.color.getHexString() : '', map: !!m.map, r: +bs.radius.toFixed(1), c: [+bs.center.x.toFixed(1), +bs.center.y.toFixed(1), +bs.center.z.toFixed(1)], fc: o.frustumCulled, inst: !!o.isInstancedMesh, ds: o.material.side, name: o.name || '' }); });
          let sc = 0, sv = 0, stv = 0; __T.scene.traverse(o => { if (o.isMesh && o.visible) { const geo = o.geometry; let n = (geo.index ? geo.index.count : geo.attributes.position ? geo.attributes.position.count : 0) / 3, v = geo.attributes.position ? geo.attributes.position.count : 0; if (o.isInstancedMesh) { n *= o.count; v *= o.count; } sc += n; sv += v; let inS = false; for (let q = o; q; q = q.parent) if (q === g) inS = true; if (inS && !(o.material && o.material.colorWrite === false)) stv += v; } }); window.__verts = [sv, stv];
          const top = []; __T.scene.traverse(o => { if (!(o.isMesh || o.isPoints || o.isLine) || !o.visible) return; let p = o, inSt = false, vis = true; for (; p; p = p.parent) { if (p === g) inSt = true; if (!p.visible) vis = false; } if (inSt || !vis) return; const geo = o.geometry; let n = (geo.index ? geo.index.count : geo.attributes.position ? geo.attributes.position.count : 0) / 3; if (o.isInstancedMesh) n *= o.count; if (n < 2000) return; if (!geo.boundingSphere) geo.computeBoundingSphere(); const m = Array.isArray(o.material) ? o.material[0] : o.material; const path = []; for (let q = o; q && q !== __T.scene; q = q.parent) path.push(q.name || q.type); top.push({ n: Math.round(n), mt: m.type, col: m.color ? m.color.getHexString() : '', r: +geo.boundingSphere.radius.toFixed(1), c: geo.boundingSphere.center.toArray().map(v => +v.toFixed(1)), pos: o.getWorldPosition(new __T.THREE.Vector3()).toArray().map(v => +v.toFixed(1)), path: path.slice(0, 4).join('<'), cs: o.castShadow, sk: !!o.isSkinnedMesh, inst: !!o.isInstancedMesh }); });
          return { top, meshes: out, scene: sc, census: window.__vcCensus || {}, verts: window.__verts, cn: window.__vcN || {}, bands: window.__vcB || {}, arena: __T.ARENA, theme: __T.TH.id }; })()""")
        ms = R['meshes']; print('stage', R['theme'], 'arena', R['arena'], 'meshes', len(ms), 'stage tris', sum(m['n'] for m in ms if m['vis']), 'scene visible tris', int(R['scene']))
        print('vertices: scene visible %d, stage (drawn, not the shadow-only mesh) %d' % tuple(R['verts']))
        print('shadow-only tris', sum(m['n'] for m in ms if m['so']), '| transparent tris', sum(m['n'] for m in ms if m['tr'] and m['vis']), '| not culled (frustumCulled false)', sum(m['n'] for m in ms if not m['fc']))
        for m in sorted(ms, key=lambda m: -m['n'])[:30]: print('   %7d %s %-8s %s r %5.1f c %s %s%s%s%s' % (m['n'], 'V' if m['vis'] else '-', m['mt'][:8], m['col'], m['r'], m['c'], 'S' if m['cs'] else ' ', 'T' if m['tr'] else ' ', 'O' if m['so'] else ' ', ' inst' if m['inst'] else ''))
        print('outside stageGroup, visible, >= 2000 tris:')
        for m in sorted(R['top'], key=lambda m: -m['n'])[:25]: print('   %7d %-22s #%s r %5.1f pos %s %s%s%s %s' % (m['n'], m['mt'][:22], m['col'], m['r'], m['pos'], 'S' if m['cs'] else ' ', 'K' if m['sk'] else ' ', 'I' if m['inst'] else ' ', m['path'][:60]))
        C = R['census']; tot = sum(C.values())
        if tot:
            lines = open(S + '/ws/pc_census.html').read().split('\n')
            print('vcBag census: %d tris through vcBag; by distance band' % tot, R['bands'])
            for k, v in sorted(C.items(), key=lambda kv: -kv[1])[:40]:
                ln = re.findall(r'L(\d+)', k); src = lines[int(ln[-1]) - 1].strip()[:150] if ln else ''
                fn = k.split(' <- ')[-1].strip().replace('at ', '')[:40]
                print('   %7d %5d  %-28s | %s' % (v, R['cn'].get(k, 0), fn[:28], src[:130]))
        print('errors', errs[:4])
        json.dump(R, open(f'{S}/perf248/census_{STAGE}.json', 'w'))
        await b.close()
asyncio.run(main())
