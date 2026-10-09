#!/usr/bin/env python3
"""Opening night portraits: the blobs themselves, dressed as they will play, on the VS card. Runs on top of ui5_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui5_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CSS = '''
/* ===== opening night: the blobs in person ===== */
.vsp{position:relative;gap:2px}
.vsp.me{animation:vsinL .6s cubic-bezier(.2,1.35,.35,1) both}
.vsp.foe{animation:vsinR .6s .07s cubic-bezier(.2,1.35,.35,1) both}
.vsp.foe2{animation:vsinR .6s .14s cubic-bezier(.2,1.35,.35,1) both}
@keyframes vsinL{from{opacity:0;transform:translateX(-70%) scale(1.25)}}
@keyframes vsinR{from{opacity:0;transform:translateX(70%) scale(1.25)}}
.vbox{position:relative;width:min(40vw,280px);aspect-ratio:5/6}
.vbox::before{content:"";position:absolute;inset:4% -16% -8%;background:var(--sc,var(--ink));-webkit-mask:url(art/m_splat2.webp) center/contain no-repeat;mask:url(art/m_splat2.webp) center/contain no-repeat;transform:rotate(var(--rot,-8deg));opacity:.92}
.vbox::after{content:"";position:absolute;left:14%;right:14%;bottom:-2%;height:9%;border-radius:50%;background:rgba(0,0,0,.5);filter:blur(5px)}
.vbox canvas{position:absolute;inset:0;width:100%;height:100%;z-index:1;filter:drop-shadow(0 10px 8px rgba(0,0,0,.45))}
.vsp.me .vbox{--rot:-9deg}
.vsp.foe .vbox{--rot:8deg}
.vsp.foe2 .vbox{--rot:-5deg}
.vsrow{gap:0}
.vsbig{position:relative;z-index:2;margin:0 -24px}
.vsrow.trio .vbox{width:min(29vw,200px)}
.vsrow.trio .vsbig{font-size:clamp(40px,11vw,80px);margin:0 -8px}
.vsp b{position:relative;z-index:2;margin-top:-6px}
@media (min-aspect-ratio:1/1){.vbox{width:min(40vw,54vh,280px)}.vsrow.trio .vbox{width:min(29vw,46vh,200px)}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]

# the card: a portrait box per blob, filled a frame later with a render of the blob itself
rep("""  const card = (D, name, me) => '<div class="vsp"><span class="swc" style="--sc:' + TEAMS[D.team].css + ';--cd:' + mixHex(TEAMS[D.team].wet, 0x0C0620, 0.62) + '">' + faceIcon(D, false) + '</span><b>' + escAttr(name) + '</b>' + (me ? '<span class="tape">You</span>' : '') + '</div>';
  let h = card(P, playerName(), true); if (mode !== 'solo') { h += '<b class="vsbig">VS</b>' + card(H, NAMES[1], false); if (mode === 'trio') h += card(H2, NAMES[2], false); }
  $('vsRow').innerHTML = h;""", """  const card = (D, name, cls) => '<div class="vsp ' + cls + '"><span class="vbox" id="vbox' + D.team + '" style="--sc:' + TEAMS[D.team].css + '"></span><b>' + escAttr(name) + '</b>' + (cls === 'me' ? '<span class="tape">You</span>' : '') + '</div>';
  let h = card(P, playerName(), 'me'); if (mode !== 'solo') { h += '<b class="vsbig">VS</b>' + card(H, NAMES[1], 'foe'); if (mode === 'trio') h += card(H2, NAMES[2], 'foe2'); }
  $('vsRow').innerHTML = h; $('vsRow').classList.toggle('trio', mode === 'trio');
  // the rivals step out, dressed, with their game face on; the portraits are taken two frames on, once their bodies have settled
  const list = [[P, $('vbox0')]]; if (mode !== 'solo') list.push([H, $('vbox1')]); if (mode === 'trio') list.push([H2, $('vbox2')]);
  for (const [D] of list) if (D !== P) { D.look.drop.visible = true; D.yaw = P.yaw; D.flatT = 0; D.stunT = 0; D.dry = false; D.vsSt = D.st; D.st = 'play'; D.ip = { hop: 0, spin: 0, pitch: 0, roll: 0, sq: null, rise: null, sink: null, coat: null, watch: null, expr: 'angry', shut: false, stars: false }; }
  vsSnap = { t: 2, list, id: runId };""")

# the portrait renderer and its tick, before showVS
rep("function showVS(cb) {", r"""// ---------- opening night portraits: one blob at a time, alone on a clear ground, under the studio key light ----------
let vsSnap = null, portRT = null; const portCam = new THREE.PerspectiveCamera(34, 0.8, 0.05, 60); portCam.layers.set(4);
function portraitOf(D, W, Hh) {
  if (!portRT || portRT.width !== W || portRT.height !== Hh) { if (portRT) portRT.dispose(); portRT = new THREE.WebGLRenderTarget(W, Hh, { colorSpace: THREE.SRGBColorSpace }); }
  const look = lookOf(D), tall = look.head === 'hat' ? 1.3 : look.head === 'tophat' ? 1.22 : look.head === 'pirate' ? 1.16 : look.head === 'tiara' ? 1.1 : look.head ? 1.08 : 0.92;
  const tv = Math.tan(portCam.fov * Math.PI / 360), d = tall / (2 * tv * 0.8), ly = tall * 0.46, fx = Math.sin(D.yaw), fz = Math.cos(D.yaw);
  portCam.aspect = W / Hh; portCam.updateProjectionMatrix(); portCam.position.set(D.x + fx * d, ly + d * 0.2, D.z + fz * d); portCam.up.set(0, 1, 0); portCam.lookAt(D.x, ly - 0.03, D.z); portCam.updateMatrixWorld();
  for (const o of [P, H, H2]) vicLayer(o, o === D);
  const shWas = lobbyShadow.visible, stWas = strand.visible; lobbyShadow.visible = false; strand.visible = false;
  const hi = hemi.intensity, si = sun.intensity; keySave.copy(sun.color); lobbySunPos.copy(sun.position); lobbyTgt.copy(sun.target.position);
  hemi.intensity = Math.max(hi, 0.8 * LIGHT_K); sun.intensity = Math.max(si, 1.15 * LIGHT_K); sun.color.copy(lobbyKey);
  sun.position.set(D.x + fx * 3 - fz * 3.2, 5.5, D.z + fz * 3 + fx * 3.2); sun.target.position.set(D.x, 0.4, D.z); sun.target.updateMatrixWorld();
  renderer.setRenderTarget(portRT); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, portCam);
  const buf = new Uint8Array(W * Hh * 4); renderer.readRenderTargetPixels(portRT, 0, 0, W, Hh, buf); renderer.setRenderTarget(null); renderer.setClearColor(0x120A24, 1);
  hemi.intensity = hi; sun.intensity = si; sun.color.copy(keySave); sun.position.copy(lobbySunPos); sun.target.position.copy(lobbyTgt); sun.target.updateMatrixWorld();
  lobbyShadow.visible = shWas; strand.visible = stWas; for (const o of [P, H, H2]) vicLayer(o, o === P && state === 'menu');
  const c = document.createElement('canvas'); c.width = W; c.height = Hh; const g = c.getContext('2d'), id = g.createImageData(W, Hh);
  for (let y = 0; y < Hh; y++) id.data.set(buf.subarray((Hh - 1 - y) * W * 4, (Hh - y) * W * 4), y * W * 4);
  g.putImageData(id, 0, 0); return c;
}
function vsSnapTick() {
  const q = vsSnap; if (--q.t > 0) return; vsSnap = null;
  if (q.id === runId) for (const [D, el] of q.list) { if (!el) continue; const c = portraitOf(D, 600, 720); el.replaceChildren(c); }
  for (const [D] of q.list) if (D !== P) { D.look.drop.visible = false; D.ip = null; if (D.vsSt) { D.st = D.vsSt; D.vsSt = null; } }
}
function showVS(cb) {""")
rep("  cpuLook(LH, dt, rdt, ke, kf, playing); cpuLook(L2, dt, rdt, ke, kf, playing);", "  cpuLook(LH, dt, rdt, ke, kf, playing); cpuLook(L2, dt, rdt, ke, kf, playing);\n  if (vsSnap) vsSnapTick();")
rep('<p class="ver">Version 75</p>', '<p class="ver">Version 76</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
