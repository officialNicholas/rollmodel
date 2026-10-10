#!/usr/bin/env python3
"""The shop shows the items themselves: each one rendered alone, lit, on a square card, no character under it (the two eye looks keep their drawn icons). The cards are plain blocks rather than buttons, so every browser sizes them the same. On top of ui71_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui71_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# the item alone: its own meshes in a little lit scene of their own, framed by their bounds, on nothing
a = s.index("const shopPics = new Map(); let shopPicKey = '';"); b = s.index("  const url = c ? c.toDataURL('image/png') : ''; shopPics.set(w.id, url); return url;\n}", a) + len("  const url = c ? c.toDataURL('image/png') : ''; shopPics.set(w.id, url); return url;\n}")
s = s[:a] + r'''const shopPics = new Map(); let shopPicKey = '', picRT = null, picScene = null, picCam = null;
const PIC_SRC = { pirate: () => pWear.pirate, tophat: () => pWear.top, bowtie: () => pWear.bow, pearls: () => pWear.pearls, patch: () => pWear.patch, flower: () => pWear.flower, tiara: () => pWear.tiara, glasses: () => pWear.glasses, hockey: () => pWear.hockey, bunny: () => pWear.bunny, skull: () => pWear.skull, hat: () => pWear.hat, halo: () => pWear.halo }; // (fangs, lashes and the zombie eyes keep their drawn icons: white teeth on a pale card say nothing)
function itemPic(w) {
  const src = PIC_SRC[w.id]; if (!src || typeof pWear === 'undefined') return '';
  const S = 320; if (!picRT) { picRT = new THREE.WebGLRenderTarget(S, S, { colorSpace: THREE.SRGBColorSpace }); picScene = new THREE.Scene(); picCam = new THREE.PerspectiveCamera(28, 1, 0.01, 100);
    const hm = new THREE.HemisphereLight(0xFFFFFF, 0x9088A8, 1.1), dl = new THREE.DirectionalLight(0xFFFFFF, 1.7), fl = new THREE.DirectionalLight(0xFFE6C8, 0.5); dl.position.set(1.6, 2.6, 2.4); fl.position.set(-2, 0.6, 1.4); picScene.add(hm, dl, fl); }
  picScene.environment = scene.environment || null;
  const o = src().clone(); o.traverse(q => { q.visible = true; }); o.position.set(0, 0, 0); o.rotation.set(0, 0, 0); o.scale.setScalar(1); picScene.add(o); o.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(o), c = box.getCenter(new THREE.Vector3()), sz = box.getSize(new THREE.Vector3()), r = Math.max(sz.x, sz.y, sz.z) * 0.5 || 0.5, dir = new THREE.Vector3(0.38, 0.5, 1).normalize(), d = r / Math.tan(14 * Math.PI / 180) * 1.28;
  picCam.position.copy(c).addScaledVector(dir, d); picCam.lookAt(c); picCam.updateProjectionMatrix(); picCam.updateMatrixWorld(true);
  const cc = renderer.getClearColor(new THREE.Color()), ca = renderer.getClearAlpha(); renderer.setClearColor(0x000000, 0); renderer.setRenderTarget(picRT); renderer.clear(); renderer.render(picScene, picCam);
  const buf = new Uint8Array(S * S * 4); renderer.readRenderTargetPixels(picRT, 0, 0, S, S, buf); renderer.setRenderTarget(null); renderer.setClearColor(cc, ca); picScene.remove(o);
  const cv = document.createElement('canvas'); cv.width = cv.height = S; const g = cv.getContext('2d'), id = g.createImageData(S, S);
  for (let y = 0; y < S; y++) id.data.set(buf.subarray((S - 1 - y) * S * 4, (S - y) * S * 4), y * S * 4);
  g.putImageData(id, 0, 0); return cv.toDataURL('image/png');
}
function shopPic(w) {
  if (shopPicKey !== 'items') { shopPics.clear(); shopPicKey = 'items'; }
  if (shopPics.has(w.id)) return shopPics.get(w.id);
  let url = ''; try { url = itemPic(w); } catch (e) { url = ''; }
  shopPics.set(w.id, url); return url;
}''' + s[b:]
# the cards: plain blocks, square pictures of the item alone
rep("""      return '<button class="shitem' + (found ? (broke ? ' broke' : '') : ' locked') + (found && owns(w.id) && needFind(w) && !bought(w.id) ? ' fresh' : '') + '" type="button" role="listitem" data-w="' + w.id + '" aria-label="'""",
    """      return '<div class="shitem' + (found ? (broke ? ' broke' : '') : ' locked') + (found && owns(w.id) && needFind(w) && !bought(w.id) ? ' fresh' : '') + '" role="button" tabindex="0" data-w="' + w.id + '" aria-label="'""")
rep("""<span class="shp">' + DROP_SVG + PRICE(w) + '</span></span></span></button>'; }).join(''); }""", """<span class="shp">' + DROP_SVG + PRICE(w) + '</span></span></span></div>'; }).join(''); }""")
rep("$('shopGrid').addEventListener('click', e => {", "$('shopGrid').addEventListener('keydown', e => { if ((e.key === 'Enter' || e.key === ' ') && e.target.closest('.shitem')) { e.preventDefault(); e.target.closest('.shitem').click(); } });\n$('shopGrid').addEventListener('click', e => {")
css = '''
/* the shop's cards: square, the item alone on them */
.shgrid{grid-template-columns:repeat(auto-fill,minmax(148px,1fr))}
.shpic{aspect-ratio:1/1;height:auto}
.shpic img{object-fit:contain;padding:9%;box-sizing:border-box}
.shpic svg{padding:16%}
.shitem.locked .shpic img{filter:grayscale(1) brightness(.5) contrast(1.2);opacity:.85}
@media (max-height:520px) and (min-aspect-ratio:1/1){.shgrid{grid-template-columns:repeat(auto-fill,minmax(118px,1fr))}.shpic{height:auto}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
