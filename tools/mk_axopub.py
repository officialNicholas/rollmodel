"""Package the merged axolotl runtime (ws/axo) as a self-contained page for the rig preview artifact: the page body without the
document skeleton (the artifact adds it), three.js from ./lib through the import map, the meshes as base64 text (the artifact serves
text, not raw binary), the camera widened on a tall phone screen, and the controls scrolling at phone width.
usage: mk_axopub.py <out dir>"""
import base64, os, shutil, sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
SRC = S + '/ws/axo'; OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:80]); return s.replace(a, b)
h = open(SRC + '/preview.html').read()
h = rep(h, '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">', '')
h = rep(h, '</style>', '@media (max-width:600px){#hud{display:none}#ui{max-height:40vh;overflow-y:auto;pointer-events:auto;-webkit-overflow-scrolling:touch;background:linear-gradient(rgba(223,230,238,0),rgba(223,230,238,.85) 18px)}}\n</style>')
h = rep(h, '<script type="importmap">{"imports":{"three":"/node_modules/three/build/three.module.js","three/addons/":"/node_modules/three/examples/jsm/"}}</script></head><body>',
        '<script type="importmap">{"imports":{"three":"./lib/three.module.js","three/addons/":"./lib/addons/"}}</script>')
h = rep(h, 'const cam = new THREE.PerspectiveCamera(32, innerWidth / innerHeight, 0.05, 50); cam.position.set(2.6, 1.6, 3.4);',
        'const cam = new THREE.PerspectiveCamera(32, innerWidth / innerHeight, 0.05, 50); cam.position.set(2.6, 1.6, 3.4); const fitCam = () => { cam.aspect = innerWidth / innerHeight; cam.fov = cam.aspect < 0.8 ? 32 / Math.max(0.45, cam.aspect / 0.8) : 32; cam.updateProjectionMatrix(); }; fitCam();')
h = rep(h, "addEventListener('resize', () => { cam.aspect = innerWidth / innerHeight; cam.updateProjectionMatrix(); R.setSize(innerWidth, innerHeight); });",
        "addEventListener('resize', () => { fitCam(); R.setSize(innerWidth, innerHeight); });")
h = rep(h, '</script></body></html>', '</script>')
open(OUT + '/index.html', 'w').write(h)
j = open(SRC + '/axo.js').read()
j = rep(j, "buf = await (await fetch(base + '.bin')).arrayBuffer();", "buf = Uint8Array.from(atob((await (await fetch(base + '.b64.txt')).text()).trim()), c => c.charCodeAt(0)).buffer;")
open(OUT + '/axo.js', 'w').write(j)
for m in ('axo_stand', 'axo_crawl'):
    open(f'{OUT}/{m}.b64.txt', 'w').write(base64.b64encode(open(f'{SRC}/{m}.bin', 'rb').read()).decode())
    shutil.copy(f'{SRC}/{m}.json', f'{OUT}/{m}.json')
if not os.path.exists(OUT + '/lib'): shutil.copytree(S + '/axopub3/lib', OUT + '/lib')
print('ok', sorted(os.listdir(OUT)))
