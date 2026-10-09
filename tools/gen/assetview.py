# a test page for a packed accessory asset: decodes it exactly as the game will, renders four views (front, right, back, above) with axes
import sys, json
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
asset, out = sys.argv[1], sys.argv[2]
A = open(SP + asset).read()
html = """<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;background:#8cc4ee}canvas{display:block}</style></head><body>
<script src="t186/three.r186.iife.min.js"></script>
<script>
const A = %s;
// the game's decoder: positions (quantized to the box), normals and outline normals (bytes), uvs, indices, from one base64 blob
function assetGeo(A) {
  const bin = Uint8Array.from(atob(A.b), c => c.charCodeAt(0)).buffer, n = A.n; let o = n * 6; o += (4 - o %% 4) %% 4;
  const qp = new Uint16Array(bin, 0, n * 3), qn = new Int8Array(bin, o, n * 4), qi = new Int8Array(bin, o + n * 4, n * 4), qu = new Uint16Array(bin, o + n * 8, n * 2), ix = new Uint16Array(bin, o + n * 12, A.ni);
  const P = new Float32Array(n * 3), N = new Float32Array(n * 3), NI = new Float32Array(n * 3), UV = new Float32Array(n * 2);
  for (let i = 0; i < n; i++) { for (let k = 0; k < 3; k++) { P[i * 3 + k] = A.mn[k] + qp[i * 3 + k] / 65535 * (A.mx[k] - A.mn[k]); N[i * 3 + k] = qn[i * 4 + k] / 127; NI[i * 3 + k] = qi[i * 4 + k] / 127; } for (let k = 0; k < 2; k++) UV[i * 2 + k] = A.umn[k] + qu[i * 2 + k] / 65535 * (A.umx[k] - A.umn[k]); }
  const g = new THREE.BufferGeometry(), idx = new THREE.BufferAttribute(new Uint16Array(ix), 1); g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('normal', new THREE.BufferAttribute(N, 3)); g.setAttribute('uv', new THREE.BufferAttribute(UV, 2)); g.setIndex(idx);
  const ink = new THREE.BufferGeometry(); ink.setAttribute('position', g.attributes.position); ink.setAttribute('normal', new THREE.BufferAttribute(NI, 3)); ink.setIndex(idx);
  g.computeBoundingSphere(); ink.boundingSphere = g.boundingSphere; return { g, ink };
}
(async () => {
  const G = assetGeo(A), ld = u => new Promise(r => new THREE.TextureLoader().load(u, t => r(t)));
  const col = await ld('data:image/jpeg;base64,' + A.col), mr = await ld('data:image/jpeg;base64,' + A.mr); col.colorSpace = THREE.SRGBColorSpace; col.flipY = false; mr.flipY = false;
  const mat = new THREE.MeshStandardMaterial({ map: col, roughnessMap: mr, metalnessMap: mr, side: THREE.DoubleSide });
  const W = 1200, H = 400, R = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true }); R.setSize(W, H); document.body.appendChild(R.domElement); R.setScissorTest(true);
  const sc = new THREE.Scene(); sc.add(new THREE.HemisphereLight(0xffffff, 0x886644, 1.4)); const dl = new THREE.DirectionalLight(0xffffff, 2.2); dl.position.set(2, 4, 3); sc.add(dl);
  const m = new THREE.Mesh(G.g, mat); sc.add(m); const ink = new THREE.Mesh(G.ink, new THREE.MeshBasicMaterial({ color: 0x1a1030, side: THREE.BackSide }));
  ink.onBeforeRender = () => {}; ink.material.onBeforeCompile = sh => { sh.vertexShader = sh.vertexShader.replace('#include <begin_vertex>', 'vec3 transformed = position + normal * 0.02;'); }; sc.add(ink);
  sc.add(new THREE.AxesHelper(1.2));
  const c = new THREE.Vector3(0, (A.mn[1] + A.mx[1]) / 2, 0), views = [[0, 0.3, 3], [3, 0.3, 0], [0, 0.3, -3], [1.6, 2.6, 1.6]];
  views.forEach((v, i) => { const cam = new THREE.PerspectiveCamera(35, (W / 4) / H, 0.1, 50); cam.position.set(v[0], v[1] + c.y, v[2]); cam.lookAt(c); R.setViewport(i * W / 4, 0, W / 4, H); R.setScissor(i * W / 4, 0, W / 4, H); R.render(sc, cam); });
  document.title = 'done';
})();
</script></body></html>""" % A
open(SP + out, 'w').write(html); print('wrote', out, len(html))
