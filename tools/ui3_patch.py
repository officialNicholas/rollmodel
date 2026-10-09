#!/usr/bin/env python3
"""WET PAINT: the Studio and the Gallery. Applies to the pristine v71 file so it can be re-run."""
import sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
SRC = '/home/claude/paint-v71.html'; DST = '/home/claude/paint-the-canvas.html'
s = open(SRC).read(); n0 = len(s)

def rep(old, new, count=1):
    global s
    c = s.count(old)
    assert c == count, f'expected {count} match(es), found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---------- glyphs (white line icons, currentColor) ----------
I = {
 'hanger': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.5a2.2 2.2 0 0 0-2.2 2.2c0 1 .7 1.6 1.4 2.1.5.4.8.7.8 1.2v1.2L3.5 15.6a1.6 1.6 0 0 0 .9 2.9h15.2a1.6 1.6 0 0 0 .9-2.9L12 10.2" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 'comm': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4.5" y="4" width="15" height="17" rx="2.5" fill="none" stroke="currentColor" stroke-width="2.1"/><path d="M9 2.8h6v3H9z" fill="currentColor"/><path d="M8.3 12.6l2.3 2.3 4.9-4.9M8.3 17.2h7.4" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 'help': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9.2" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M9.6 9.5a2.5 2.5 0 1 1 3.6 2.2c-.8.4-1.2 1-1.2 1.8v.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="17" r="1.35" fill="currentColor"/></svg>',
 'gear': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19.7 12.6L22.2 13.9L20.6 17.9L17.9 17.0L17.0 17.9L17.9 20.6L13.9 22.2L12.6 19.7L11.4 19.7L10.1 22.2L6.1 20.6L7.0 17.9L6.1 17.0L3.4 17.9L1.8 13.9L4.3 12.6L4.3 11.4L1.8 10.1L3.4 6.1L6.1 7.0L7.0 6.1L6.1 3.4L10.1 1.8L11.4 4.3L12.6 4.3L13.9 1.8L17.9 3.4L17.0 6.1L17.9 7.0L20.6 6.1L22.2 10.1L19.7 11.4ZM15.2 12a3.2 3.2 0 1 0 -6.4 0a3.2 3.2 0 1 0 6.4 0Z" fill="currentColor" fill-rule="evenodd"/></svg>',
 'trophy': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4h10v5a5 5 0 0 1-10 0zM7 6H4v2a3 3 0 0 0 3 3M17 6h3v2a3 3 0 0 1-3 3M12 14v3M8.5 20h7M9.5 17h5" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 'drop': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.5s6 7 6 11.2a6 6 0 0 1-12 0C6 10.5 12 3.5 12 3.5z" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linejoin="round"/></svg>',
 'phone_p': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6.5" y="2.5" width="11" height="19" rx="2.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10.5 18h3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
 'phone_l': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.5" y="6.5" width="19" height="11" rx="2.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M18 10.5v3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
 'edit': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/></svg>',
 'check': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7"/></svg>',
 'sound': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="M16 8.5a5 5 0 0 1 0 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
 'mute': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="M16.5 9.5l5 5M21.5 9.5l-5 5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
}

# ---------- CSS ----------
css = open(S + '/tools/ui3.css').read() + '''
/* ---- the gallery additions: reputation on results, commissions ---- */
.reprow{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:10px;padding:8px 10px;border:2px solid var(--black);border-radius:6px;background:var(--paper);color:var(--black);box-shadow:3px 3px 0 rgba(255,255,255,.18);animation:rowin .5s .6s cubic-bezier(.2,1.2,.35,1) both}
.repl{display:grid;gap:2px}
.repl small{font:800 9.5px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.repl b{font:900 14px/1 var(--font-head);text-transform:uppercase;white-space:nowrap}
.xpmeter{width:132px;height:74px;justify-self:center;background:url(art/xp_fill.webp) 0 0/792px 444px no-repeat;filter:drop-shadow(2px 2px 0 rgba(23,19,32,.25))}
.xpgain{font:400 22px/1 var(--font-display);color:var(--black);white-space:nowrap}
.xpgain small{display:block;font:800 9.5px/1 var(--font-ui);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-top:3px}
.reprow.up .repl b{color:var(--gold-lo)}
.commdone{display:grid;gap:6px}
.commdone:empty{display:none}
.commdone .cd{display:flex;align-items:center;gap:8px;padding:6px 10px;border-radius:6px;background:var(--gold);border:2px solid var(--black);color:var(--black);font:800 13px/1.2 var(--font-ui);box-shadow:3px 3px 0 rgba(255,255,255,.18);animation:rowin .5s cubic-bezier(.2,1.2,.35,1) both}
.commdone .cd b{font:900 12px/1 var(--font-head);text-transform:uppercase;margin-left:auto;white-space:nowrap}
.comms{display:grid;gap:10px}
.comm{display:grid;grid-template-columns:44px minmax(0,1fr) auto;align-items:center;gap:10px;padding:8px 10px 8px 8px;border:2px solid var(--black);border-radius:6px;background:#fff;box-shadow:3px 3px 0 var(--black)}
.comm .ring{position:relative;width:44px;height:44px;border-radius:50%;background:conic-gradient(var(--ink) calc(var(--p) * 1%),var(--paper-2) 0);display:grid;place-items:center;border:2px solid var(--black)}
.comm .ring::after{content:attr(data-n);width:30px;height:30px;border-radius:50%;background:#fff;display:grid;place-items:center;font:900 11px/1 var(--font-head);color:var(--black)}
.comm .ct{min-width:0;display:grid;gap:3px}
.comm .ct b{font:900 14px/1.1 var(--font-head);text-transform:uppercase}
.comm .ct small{font:700 11px/1.2 var(--font-ui);color:var(--muted)}
.comm .cr{font:900 12px/1 var(--font-head);color:var(--gold-lo);white-space:nowrap}
.comm.done{background:var(--gold)}
.comm.done .cr{color:var(--black)}
.cnote.small{font-size:12.5px}
@media (max-width:374px){.xpmeter{width:110px;height:62px;background-size:660px 372px}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k)
s = s[:j] + css + s[j:]

# ---------- markup: the Studio ----------
a = s.index('    <div class="mhome" id="mHome">'); b = s.index('    <div class="mworld" id="mWorld" hidden>')
LOBBY = '''    <div class="mhome lobby" id="mHome">
      <div class="ltop" id="lobbyTop">
        <button class="swatch me nametag" id="nameBtn" type="button" aria-label="Change your name"><span class="swc"><span class="nface" id="nameFace" aria-hidden="true"></span></span><span class="swt"><b id="nameShow">Player</b><small id="repName">Unknown</small><span class="repbar" aria-hidden="true"><i id="repFill"></i></span></span><span class="swlvl" id="repLvl" aria-label="Reputation level">1</span></button>
        <div class="ltools"><span class="tape exhib" id="seasonTag"><b>Season 1</b> Halloween</span><button class="ib2 setb" id="setBtn" type="button" aria-label="Settings" aria-haspopup="dialog">''' + I['gear'] + '''</button></div>
      </div>
      <h1 class="logo paint" id="logo"><span class="tcard" role="img" aria-label="Roll Model"></span><span class="season"><b>Season 1</b>Halloween</span></h1>
      <div class="lcol left" id="lobbyRail">
        <button class="plate hot" id="lookBtn" type="button" aria-haspopup="dialog">''' + I['hanger'] + '''<span>Locker</span></button>
        <button class="plate" id="commBtn" type="button" aria-haspopup="dialog">''' + I['comm'] + '''<span>Commissions</span><i class="pbadge" id="commBadge" hidden></i></button>
        <button class="plate" id="howBtn" type="button" aria-haspopup="dialog">''' + I['help'] + '''<span>How to play</span></button>
      </div>
      <div class="lcol right" id="lobbyRight">
        <div class="plate stat" title="Wins">''' + I['trophy'] + '''<b id="statWins">0</b><span>Wins</span></div>
        <div class="plate stat" title="Best coverage">''' + I['drop'] + '''<b id="statBest">0%</b><span>Best</span></div>
      </div>
      <div class="lbot" id="lobbyBot">
        <div class="lineup" id="lineup" aria-label="Who's in the exhibition"></div>
        <div class="lgo" id="mCta">
          <button class="show" id="stageBtn" type="button" aria-label="Pick the exhibition"><img class="sthumb" id="stageThumb" alt=""><span class="stxt"><small>Exhibition</small><b id="lobbyStage">The Studio</b><em id="lobbyMode">1v1</em></span><span class="sarrow" aria-hidden="true">&#9656;</span></button>
          <button class="playbtn" id="homePlay" type="button"><span class="pbl">Play</span></button>
        </div>
      </div>
    </div>
    <div class="lsay" id="heroSay" hidden><span id="heroSayTxt"></span></div>
'''
s = s[:a] + LOBBY + s[b:]
rep('<h2 id="worldTitle">Pick a world</h2>', '<h2 id="worldTitle">Pick a canvas</h2>')
rep("$('worldTitle').textContent = 'Pick a world'", "$('worldTitle').textContent = 'Pick a canvas'")
rep('<div class="seg" id="stages" role="group" aria-label="How good the CPUs are"></div>', '<p class="lhead critics" style="text-align:center;color:#B8B0C8">The critics</p><div class="seg" id="stages" role="group" aria-label="How harsh the critics are"></div>')

# the orientation pick, the turn-your-phone card, the opening night (VS) and the commissions
ORIENT = '''  <section class="orient" id="orient" hidden role="dialog" aria-modal="true" aria-labelledby="orientTitle">
    <div class="obody">
      <h2 class="otitle" id="orientTitle">How do you hold your brush?</h2>
      <p class="osub">Pick one to start. You can change it any time in Settings.</p>
      <div class="ocards" role="radiogroup" aria-label="Screen orientation">
        <button class="ocard" type="button" role="radio" data-o="port" aria-checked="false"><span class="ocheck">''' + I['check'] + '''</span><span class="oart"><img src="art/prev_p.webp" alt="The game held upright"></span><b>Upright</b><small>One thumb, portrait</small></button>
        <button class="ocard" type="button" role="radio" data-o="land" aria-checked="false"><span class="ocheck">''' + I['check'] + '''</span><span class="oart"><img src="art/prev_l.webp" alt="The game turned wide"></span><b>Wide</b><small>Two hands, landscape</small></button>
      </div>
      <button class="ybtn" id="orientOk" type="button">Select</button>
    </div>
  </section>
  <div class="rotate" id="rotate" hidden><div class="rbody"><span class="rph" id="rotateIcon" aria-hidden="true">''' + I['phone_p'] + '''</span><b>Turn your phone</b><small id="rotateSub">Roll Model is set to portrait</small><button class="ybtn" id="rotateSwap" type="button">Play this way instead</button></div></div>
  <section class="vsx" id="vsx" hidden aria-live="polite"><div class="vband top"></div><div class="vband bot"></div><div></div><div class="vsrow" id="vsRow"></div><p class="vstitle" id="vsTitle"></p></section>
  <div class="modal" id="commModal" hidden>
    <div class="card" role="dialog" aria-modal="true" aria-labelledby="commTitle">
      <h2 class="ctitle" id="commTitle">Commissions</h2>
      <p class="cnote small">Three jobs at a time. Finish one for reputation, and a new one comes in.</p>
      <div class="comms" id="commList"></div>
      <button class="btn play sm" id="commClose" type="button">Back to the studio</button>
    </div>
  </div>
'''
rep('  <div class="iris" id="iris" hidden aria-hidden="true">', ORIENT + '  <div class="iris" id="iris" hidden aria-hidden="true">')
# settings: screen and sound above visuals
rep('''      <div class="sgrp">
        <p class="lhead">Visuals</p>''', '''      <div class="sgrp">
        <p class="lhead">Screen</p>
        <div class="seg duo" id="orientPick" role="group" aria-label="Screen"><button type="button" data-o="port" aria-pressed="false">''' + I['phone_p'] + '''Upright</button><button type="button" data-o="land" aria-pressed="false">''' + I['phone_l'] + '''Wide</button></div>
      </div>
      <div class="sgrp">
        <p class="lhead">Sound</p>
        <div class="seg duo" id="soundPick" role="group" aria-label="Sound"><button type="button" data-s="on" aria-pressed="false">''' + I['sound'] + '''On</button><button type="button" data-s="off" aria-pressed="false">''' + I['mute'] + '''Off</button></div>
      </div>
      <div class="sgrp">
        <p class="lhead">Visuals</p>''')
# the victory tag: the red dot for a sale
rep('<span class="vtag" id="vTag">Winner</span>', '<span class="vtag" id="vTag"><i class="reddot" id="vDot" hidden></i><span id="vTagTxt">Winner</span></span>')
# results: reputation and commissions after the board
rep('''    <div class="board" id="board" role="list" aria-label="Scores"></div>
    <button class="btn play two" id="endBtn" type="button">''', '''    <div class="board" id="board" role="list" aria-label="Scores"></div>
    <div class="reprow" id="repRow" hidden><div class="repl"><small>Reputation</small><b id="repRowName">Unknown</b></div><div class="xpmeter" id="xpMeter" role="meter" aria-label="Reputation"></div><b class="xpgain" id="xpGain">+0<small>XP</small></b></div>
    <div class="commdone" id="commDone"></div>
    <button class="btn play two" id="endBtn" type="button">''')

# ---------- JS: the Studio render path (your blob on a stroke of your paint, over sketchbook paper, on its own camera layer) ----------
rep('''// ---------- your painting: a top-down snapshot of the canvas ----------''', r'''// ---------- the Studio: your blob alone on a roller stroke of its own paint, over sketchbook paper. Its own camera layer over a
// shader backdrop (the way the victory screen draws the winner), so the canvas never shows in the menu ----------
const lobbyU = { uTime: { value: 0 }, uDim: { value: 0 }, uCol: { value: new THREE.Color(0xE3122F) }, uInvPV: { value: new THREE.Matrix4() }, uCam: { value: new THREE.Vector3() }, uBlob: { value: new THREE.Vector3() }, uWallN: { value: new THREE.Vector2(0, 1) } };
const lobbyBg = new THREE.Scene();
// the studio: a paper floor and a back wall, cast from the live camera so the stroke runs under the blob's feet in true perspective
lobbyBg.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({ uniforms: lobbyU, depthTest: false, depthWrite: false, vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }',
  fragmentShader: `uniform mat4 uInvPV; uniform vec3 uCam, uBlob, uCol; uniform vec2 uWallN; uniform float uTime, uDim; varying vec2 vUv;
float hs(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(hs(i), hs(i + vec2(1.0, 0.0)), f.x), mix(hs(i + vec2(0.0, 1.0)), hs(i + vec2(1.0, 1.0)), f.x), f.y); }
void main(){
  vec4 w = uInvPV * vec4(vUv * 2.0 - 1.0, 1.0, 1.0); vec3 dir = normalize(w.xyz / w.w - uCam);
  vec3 n3 = vec3(uWallN.x, 0.0, uWallN.y); vec2 t2 = vec2(-uWallN.y, uWallN.x); vec3 W = uBlob - n3 * 2.4;
  float dn = dot(dir, n3); float tw = dn < -1e-4 ? dot(W - uCam, n3) / dn : -1.0;
  float tf = dir.y < -1e-4 ? -uCam.y / dir.y : -1.0;
  vec3 paper = vec3(0.93, 0.885, 0.80); vec3 c;
  bool onFloor = tf > 0.0 && (tw <= 0.0 || tf < tw);
  if (onFloor) {
    vec3 h = uCam + dir * tf; vec2 q = h.xz;
    c = paper * (0.985 + 0.03 * hs(floor(q * 60.0)));
    vec2 g = fract(q * 1.1); float ln = 1.0 - smoothstep(0.0, 0.03, min(g.x, g.y)); c *= 1.0 - 0.045 * ln;
    vec2 rel = q - uBlob.xz; float along = dot(rel, t2), across = dot(rel, uWallN) + 0.1 * sin(along * 0.9) - 0.1;
    float edge = (hs(floor(vec2(along * 14.0, 0.0))) - 0.5) * 0.08, d = abs(across) - (0.66 + edge);
    float bristle = 0.9 + 0.2 * vn(vec2(along * 2.0, across * 24.0)), k = (1.0 - smoothstep(-0.012, 0.012, d)) * (1.0 - smoothstep(7.5, 9.0, abs(along)));
    c = mix(c, uCol * bristle, k);
    c *= 0.8 + 0.2 * smoothstep(0.0, 1.6, dot(h - W, n3));
    vec2 fp = q * 22.0 + vec2(uTime * 0.08, uTime * 0.03); vec2 fi = floor(fp), ff = fract(fp) - 0.5; float fh = hs(fi); float fl = step(0.975, fh) * (1.0 - smoothstep(0.0, 0.12 + 0.1 * fract(fh * 7.0), length(ff)));
    c = mix(c, uCol * 0.9, fl * 0.5 * (1.0 - k));
  } else if (tw > 0.0) {
    vec3 h = uCam + dir * tw; vec2 wq = vec2(dot(h.xz - W.xz, t2), h.y);
    c = paper * 0.95 * (0.985 + 0.03 * hs(floor(wq * 60.0)));
    vec2 g = fract(wq * 1.1); float ln = 1.0 - smoothstep(0.0, 0.03, min(g.x, g.y)); c *= 1.0 - 0.035 * ln;
    float pool = smoothstep(2.8, 0.3, length((wq - vec2(dot(uBlob.xz - W.xz, t2), 1.2)) * vec2(0.75, 1.0)));
    c *= 0.84 + 0.2 * pool; c *= 1.0 - 0.14 * smoothstep(1.5, 4.5, wq.y); c *= 0.88 + 0.12 * smoothstep(0.0, 0.45, wq.y);
  } else { c = paper * 0.78; }
  float v = smoothstep(1.5, 0.55, length((vUv - 0.5) * vec2(1.0, 1.1))); c *= 0.86 + 0.14 * v;
  c *= 1.0 - uDim; gl_FragColor = vec4(c, 1.0);
  #include <colorspace_fragment>
}` })));
const lobbyCam = new THREE.PerspectiveCamera(32, 1, 0.05, 80); lobbyCam.layers.set(4);
const lobbyShadow = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d'), r = g.createRadialGradient(64, 64, 6, 64, 64, 62); r.addColorStop(0, 'rgba(23,19,32,.5)'); r.addColorStop(0.55, 'rgba(23,19,32,.22)'); r.addColorStop(1, 'rgba(23,19,32,0)'); g.fillStyle = r; g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c), m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false })); m.rotation.x = -Math.PI / 2; m.layers.set(4); m.visible = false; m.renderOrder = -1; scene.add(m); return m; })();
let warming = false;
const lobbyOn = () => state === 'menu' && !vic && !warming && (menuPage === 'home' || lookOpen);
const lobbyKey = new THREE.Color(0xFFF1E2), lobbySunPos = new THREE.Vector3(), lobbyTgt = new THREE.Vector3();
const heroSay = $('heroSay');
function renderLobby() {
  vicLayer(P, true); drop.visible = true; strand.layers.enable(4);
  const sc = 0.9 + 0.5 * clamp(P.y, 0, 1); lobbyShadow.visible = true; lobbyShadow.position.set(P.x, 0.01, P.z); lobbyShadow.scale.set(sc, sc, 1); lobbyShadow.material.opacity = clamp(1 - P.y * 0.6, 0.3, 1);
  lobbyCam.copy(camera, false); lobbyCam.layers.set(4); lobbyCam.updateMatrixWorld();
  camera.updateMatrixWorld(); camera.matrixWorldInverse.copy(camera.matrixWorld).invert(); lobbyU.uInvPV.value.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse).invert(); lobbyU.uCam.value.copy(camera.position); lobbyU.uBlob.value.set(P.x, 0, P.z);
  const nx = camera.position.x - P.x, nz = camera.position.z - P.z, nl = Math.hypot(nx, nz) || 1; lobbyU.uWallN.value.set(nx / nl, nz / nl); lobbyU.uTime.value = clock; lobbyU.uDim.value = lookOpen ? 0.04 : 0; lobbyU.uCol.value.setHex(TEAMS[0].wet);
  // what it's saying, by its head
  if (!heroSay.hidden) { const h = tv2.set(P.x, 0.98, P.z).project(camera), sx = (h.x * 0.5 + 0.5) * viewW, sy = (0.5 - h.y * 0.5) * viewH, flip = sx > viewW * 0.58; heroSay.classList.toggle('flip', flip); heroSay.style.left = (flip ? sx - 14 : sx + 14).toFixed(0) + 'px'; heroSay.style.top = (sy - 8).toFixed(0) + 'px'; }
  renderer.setRenderTarget(null); renderer.render(lobbyBg, vicBgCam);
  const hi = hemi.intensity, si = sun.intensity; keySave.copy(sun.color); lobbySunPos.copy(sun.position); lobbyTgt.copy(sun.target.position);
  hemi.intensity = Math.max(hi, 0.8 * LIGHT_K); sun.intensity = Math.max(si, 1.15 * LIGHT_K); sun.color.copy(lobbyKey);
  sun.position.set(P.x + nx / nl * 3 - nz / nl * 3.2, 5.5, P.z + nz / nl * 3 + nx / nl * 3.2); sun.target.position.set(P.x, 0.4, P.z); sun.target.updateMatrixWorld();
  const ac = renderer.autoClear; renderer.autoClear = false; renderer.clearDepth(); renderer.render(scene, lobbyCam); renderer.autoClear = ac;
  hemi.intensity = hi; sun.intensity = si; sun.color.copy(keySave); sun.position.copy(lobbySunPos); sun.target.position.copy(lobbyTgt); sun.target.updateMatrixWorld();
}
// where the blob stands: the space the top bar, the side plates and the dock leave, its feet low in it
function lobbyFrame() {
  const r = stage.getBoundingClientRect(), W = r.width, Hh = r.height, land = W > Hh;
  const rc = id => { const e = $(id); return e && e.offsetParent !== null ? e.getBoundingClientRect() : { left: 0, right: 0, top: 0, bottom: 0, width: 0, height: 0 }; };
  const top = rc('lobbyTop'), lg = rc('logo'), L = rc('lobbyRail'), R = rc('lobbyRight'), bot = rc('lobbyBot');
  const x0 = (L.right || r.left) - r.left + 6, x1 = (R.left || r.right) - r.left - 6, y0 = Math.max(top.bottom, lg.bottom || 0) - r.top, y1 = (bot.top || r.bottom) - r.top;
  if (!(x1 - x0 > 60) || !(y1 - y0 > 60)) return heroDist;
  const fw = x1 - x0, fh = y1 - y0, tx = (x0 + x1) / 2, feetY = y0 + fh * (land ? 0.86 : 0.86);
  const tall = myLook.head === 'hat' ? 1.25 : myLook.head === 'tophat' ? 1.18 : myLook.head === 'tiara' ? 1.05 : myLook.head === 'pirate' ? 1.12 : myLook.head ? 1.05 : 0.88;
  const px = Math.min(fh * (land ? 0.9 : 0.92), fw * 0.74, Hh * 0.6);
  const tv = Math.tan(heroFov() * Math.PI / 360), dist = clamp(tall * Hh / (2 * tv * px), 1.65, 12), ly = 0.36;
  heroDist = dist; hero.mx = P.x; hero.mz = P.z;
  const lookY = feetY - ly * Hh / (2 * tv * dist); heroOff.x = W / 2 - tx; heroOff.y = Hh / 2 - lookY;
  return heroDist;
}
// what it says in the studio
const SAY_LINES = ["Let's roll.", "Who's getting painted today?", 'Fresh canvas. Big feelings.', 'I feel fast today.', 'Paint first. Think later.', 'The critics are watching.', 'Nice look, by the way.', 'One more. Just one more.', 'I was born for this.', 'Mind the wet paint.'];
let sayT = 0, sayLast = -1;
function heroSpeak(t) { $('heroSayTxt').textContent = t; heroSay.hidden = false; heroSay.style.animation = 'none'; void heroSay.offsetWidth; heroSay.style.animation = ''; sayT = 7 + Math.random() * 3; }
function sayRandom() { let i; do { i = (Math.random() * SAY_LINES.length) | 0; } while (i === sayLast); sayLast = i; heroSpeak(SAY_LINES[i]); }
function sayTick(rdt) { if (!(state === 'menu' && menuPage === 'home' && !lookOpen && $('orient').hidden)) { if (!heroSay.hidden) heroSay.hidden = true; sayT = Math.min(sayT, 1.2); return; } sayT -= rdt; if (sayT <= 0) sayRandom(); }

// ---------- your painting: a top-down snapshot of the canvas ----------''')
rep('''  if (vic) return renderVictory();
  if (post) {''', '''  if (vic) return renderVictory();
  if (lobbyOn()) return renderLobby();
  if (post) {''')
rep('''  const scOn = shadowCache.on; shadowCache.on = false; // (and with the shadow cache off, so everything is drawn into the shadows both times)
  try { renderFrame(); sun.shadow.needsUpdate = true; renderFrame(); } catch (e) {}
  shadowCache.on = scOn;''', '''  const scOn = shadowCache.on; shadowCache.on = false; warming = true; // (and with the shadow cache off, so everything is drawn into the shadows both times)
  try { renderFrame(); sun.shadow.needsUpdate = true; renderFrame(); } catch (e) {}
  shadowCache.on = scOn;''')
rep('''  sun.shadow.needsUpdate = true;
  try { renderFrame(); } catch (e) {}
}''', '''  sun.shadow.needsUpdate = true;
  try { renderFrame(); } catch (e) {}
  warming = false; if (lobbyOn()) try { renderFrame(); } catch (e) {}
}''')
rep('''  if (lookOpen) return lookFrame();
  const r = stage.getBoundingClientRect(), d = $('mCta').getBoundingClientRect(), l = $('logo').getBoundingClientRect(), W = r.width, Hh = r.height;
  if (!(d.height > 0)) return heroDist;''', '''  if (lookOpen) return lookFrame();
  return lobbyFrame();
  const r = stage.getBoundingClientRect(), d = $('mCta').getBoundingClientRect(), l = $('logo').getBoundingClientRect(), W = r.width, Hh = r.height;
  if (!(d.height > 0)) return heroDist;''')
rep('''    else { const a = hero.yaw + clock * 0.045, R = ARENA * 0.66, Y = 10.5 + ARENA * 0.14 + Math.sin(clock * 0.3) * 0.35; dPos.set(Math.sin(a) * R, Y, Math.cos(a) * R); dLook.set(-Math.sin(a) * R * 0.22, 0.4, -Math.cos(a) * R * 0.22); }''',
    '''    else { const a = hero.yaw + Math.sin(clock * 0.21) * 0.05, ly = 0.36, d2 = dist; dPos.set(hero.mx + Math.sin(a) * d2, ly + 0.02 + d2 * 0.13 + Math.sin(clock * 0.47) * 0.025, hero.mz + Math.cos(a) * d2); dLook.set(hero.mx, ly + 0.02, hero.mz); }
    sayTick(rdt);''')
rep('''  drop.visible = shadowBlob.visible = false; LH.drop.visible = LH.shadow.visible = false; L2.drop.visible = L2.shadow.visible = false; // the menu shows the canvas, not the blobs''',
    '''  drop.visible = true; shadowBlob.visible = false; LH.drop.visible = LH.shadow.visible = false; L2.drop.visible = L2.shadow.visible = false; // the studio shows your blob alone (the rivals wait for the opening night)''')
rep('''menu.classList.remove('looking'); lookEl.hidden = true; drop.visible = false; heroT = 0; menuPose();''', '''menu.classList.remove('looking'); lookEl.hidden = true; heroT = 0; menuPose(); renderLobbyUI(); sayT = 0.6;''')
rep("  if (state === 'menu' && lookOpen && !lookIntro && !vic && menuReact <= 0) {", "  if (state === 'menu' && (lookOpen || menuPage === 'home') && !lookIntro && !vic && menuReact <= 0) {")
rep("canvas.addEventListener('pointerdown', e => { if (lookOpen) lookDrag = { id: e.pointerId, x: e.clientX }; });",
    "canvas.addEventListener('pointerdown', e => { if (lookOpen || lobbyOn()) lookDrag = { id: e.pointerId, x: e.clientX, x0: e.clientX, t: performance.now() }; });")
rep("canvas.addEventListener('pointermove', e => { if (lookOpen && lookDrag && lookDrag.id === e.pointerId) {", "canvas.addEventListener('pointermove', e => { if ((lookOpen || lobbyOn()) && lookDrag && lookDrag.id === e.pointerId) {")
rep("const endLookDrag = e => { if (lookDrag && lookDrag.id === e.pointerId) lookDrag = null; };",
    "const endLookDrag = e => { if (lookDrag && lookDrag.id === e.pointerId) { if (e.type === 'pointerup' && !lookOpen && lobbyOn() && Math.abs(e.clientX - lookDrag.x0) < 8 && performance.now() - lookDrag.t < 400 && $('orient').hidden) { AU.init(); menuReact = 0.7; AU.pop(); sayRandom(); if (Math.random() < 0.6) AU.vox(['hup', 'whee', 'giggle', 'hoh'][(Math.random() * 4) | 0]); } lookDrag = null; } };")
rep("  AI = AI_LV[diff]; mapUsed = true; resetRun(); gyCam = 0; state = 'intro';", "  vicLayer(P, false); lobbyShadow.visible = false; heroSay.hidden = true; AI = AI_LV[diff]; mapUsed = true; resetRun(); gyCam = 0; state = 'intro';")
rep('''  resetRun(); decorate(); renderStages(); AU.music('menu'); menuPose(); heroT = 0;''', '''  resetRun(); decorate(); renderStages(); AU.music('menu'); menuPose(); heroT = 0; renderLobbyUI(); sayT = 1.4; camSnap = true;''')

# ---------- the lobby's controls, the lineup, reputation and commissions ----------
rep('''$('modes').addEventListener('click', e => { const t = e.target.closest('button'); if (!t || t.dataset.m === mode || building) return; AU.init(); AU.ui(); mode = t.dataset.m; store.mode = mode; save(); applyMode(); renderModes(); if (state === 'menu') { freshMap(); resetRun(); decorate(); menuPose(); renderStages(); } });''',
'''function setMode(m) { mode = m; store.mode = mode; save(); applyMode(); renderModes(); if (state === 'menu') { freshMap(); resetRun(); decorate(); menuPose(); renderStages(); } renderLobbyUI(); }
$('modes').addEventListener('click', e => { const t = e.target.closest('button'); if (!t || t.dataset.m === mode || building) return; AU.init(); AU.ui(); setMode(t.dataset.m); });
const stageArt = () => { const b = $('stagePick').querySelector('.world[data-s="' + stageSel + '"] img.art') || $('seasonGrid').querySelector('.stg[data-s="' + stageSel + '"] img.art') || $('stagePick').querySelector('.world[data-s="season"] img.art'); return b ? b.src : ''; };
const CRITICS = { easy: 'Gentle', medium: 'Fair', hard: 'Harsh' };
// reputation: experience from every exhibition, levels, and a title for the band you're in
const REP_NAMES = ['Unknown', 'Local talent', 'Rising star', 'Crowd pleaser', 'Headliner', 'Master'];
const xpNeed = lv => 100 + 45 * (lv - 1);
function repOf(xp) { let lv = 1, x = Math.max(0, xp | 0); while (x >= xpNeed(lv) && lv < 99) { x -= xpNeed(lv); lv++; } return { lv, x, need: xpNeed(lv), name: REP_NAMES[Math.min(REP_NAMES.length - 1, Math.floor((lv - 1) / 3))] }; }
// commissions: three jobs at a time
const COMMS = [{ id: 'play3', t: 'Three exhibitions', d: 'Play 3 matches, any mode', n: 3, k: 'play' }, { id: 'win1', t: 'Beat a rival', d: 'Win a 1v1', n: 1, k: 'win1' }, { id: 'cov35', t: 'Cover 35%', d: 'Paint 35% of a canvas in one match', n: 1, k: 'cov', v: 35 }, { id: 'trio', t: 'Three-way', d: 'Enter a 3-way exhibition', n: 1, k: 'trio' }, { id: 'solo40', t: 'Solo show', d: 'Cover 40% in a solo match', n: 1, k: 'solo', v: 40 }, { id: 'win3', t: 'On a roll', d: 'Win 3 matches', n: 3, k: 'win' }, { id: 'play5', t: 'Regular', d: 'Play 5 matches', n: 5, k: 'play' }, { id: 'cov50', t: 'Half the canvas', d: 'Paint 50% of a canvas in one match', n: 1, k: 'cov', v: 50 }, { id: 'hard1', t: 'Harsh critics', d: 'Win with the critics on harsh', n: 1, k: 'hard' }];
const COMM_XP = 60;
function commState() { if (!store.comm || !store.comm.active) store.comm = { active: [], prog: {}, done: [] }; const c = store.comm; while (c.active.length < 3) { const pool = COMMS.filter(x => !c.active.includes(x.id) && !c.done.includes(x.id)); if (!pool.length) break; c.active.push(pool[(Math.random() * pool.length) | 0].id); } return c; }
function commProgress(info) {
  const c = commState(), fin = [];
  for (const id of c.active) { const k = COMMS.find(x => x.id === id); if (!k) continue; let p = c.prog[id] || 0;
    if (k.k === 'play') p++; else if (k.k === 'win' && info.win > 0) p++; else if (k.k === 'win1' && info.mode === 'duel' && info.win > 0) p = 1; else if (k.k === 'cov' && info.you >= k.v) p = 1; else if (k.k === 'trio' && info.mode === 'trio') p = 1; else if (k.k === 'solo' && info.mode === 'solo' && info.you >= k.v) p = 1; else if (k.k === 'hard' && info.diff === 'hard' && info.win > 0) p = 1;
    c.prog[id] = p; if (p >= k.n) fin.push(k); }
  for (const k of fin) { c.active = c.active.filter(x => x !== k.id); c.done.push(k.id); delete c.prog[k.id]; }
  commState(); return fin;
}
function renderComms() { const c = commState(); $('commList').innerHTML = c.active.map(id => { const k = COMMS.find(x => x.id === id), p = c.prog[id] || 0; return '<div class="comm" style="--p:' + Math.round(100 * p / k.n) + '"><div class="ring" data-n="' + p + '/' + k.n + '"></div><div class="ct"><b>' + k.t + '</b><small>' + k.d + '</small></div><b class="cr">+' + COMM_XP + ' XP</b></div>'; }).join('') || '<p class="cnote">Every commission done. The critics are speechless.</p>'; }
function openComms() { if (state !== 'menu' || lookOpen) return; renderComms(); store.commSeen = (store.comm && store.comm.done.length) || 0; save(); $('commBadge').hidden = true; $('commModal').hidden = false; setTimeout(() => $('commClose').focus({ preventScroll: true }), 30); }
function closeComms() { $('commModal').hidden = true; $('commBtn').focus({ preventScroll: true }); }
$('commBtn').addEventListener('click', () => { AU.init(); AU.ui(); openComms(); });
$('commClose').addEventListener('click', () => { AU.init(); AU.ui(); closeComms(); });
$('commModal').addEventListener('click', e => { if (e.target === $('commModal')) closeComms(); });
// the studio: your swatch card, who's in the show, the exhibition card
const swatchOf = (D, name, me) => '<span class="lu' + (me ? ' me' : '') + '" style="--cd:' + mixHex(TEAMS[D.team].wet, 0x0C0620, 0.62) + '">' + faceIcon(D, false) + escAttr(name) + '</span>';
function renderLobbyUI() {
  const r = repOf(store.xp || 0); $('repName').textContent = r.name; $('repLvl').textContent = r.lv; $('repFill').style.width = Math.round(100 * r.x / r.need) + '%';
  $('lobbyStage').textContent = TH.label; const art = stageArt(); if (art && $('stageThumb').src !== art) $('stageThumb').src = art;
  const md = MODES.find(m => m[0] === mode) || MODES[0];
  $('lobbyMode').textContent = mode === 'solo' ? 'Solo \\u00b7 60 seconds' : md[1] + ' \\u00b7 Critics ' + (CRITICS[diff] || 'fair').toLowerCase();
  let wins = 0; for (const k in (store.wins || {})) wins += store.wins[k] || 0; $('statWins').textContent = wins;
  let best = 0; for (const k in (store.bestCov || {})) best = Math.max(best, store.bestCov[k] || 0); $('statBest').textContent = best + '%';
  try { $('nameFace').innerHTML = faceIcon(P, false); } catch (e) {}
  const lu = [swatchOf(P, playerName(), true)]; if (mode !== 'solo') { lu.push('<span class="vs">vs</span>', swatchOf(H, NAMES[1], false)); if (mode === 'trio') lu.push(swatchOf(H2, NAMES[2], false)); }
  $('lineup').innerHTML = lu.join('');
  const c = commState(), fresh = c.done.length - (store.commSeen || 0); $('commBadge').hidden = fresh <= 0; $('commBadge').textContent = fresh;
}''')
rep("$('homePlay').addEventListener('click', () => { AU.init(); AU.ui(); openWorlds(); });",
    "$('homePlay').addEventListener('click', () => { AU.init(); if (state !== 'menu' || building || lookOpen) return; AU.pop(); start(); });\n$('stageBtn').addEventListener('click', () => { AU.init(); AU.ui(); openWorlds(); });")
rep('''  $('cvName').textContent = TH.label; $('shuffleBtn').setAttribute('aria-label', 'Shuffle the canvas. Now: ' + TH.label);
  renderWorlds();''', '''  $('cvName').textContent = TH.label; $('shuffleBtn').setAttribute('aria-label', 'Shuffle the canvas. Now: ' + TH.label);
  for (const b of el.children) b.textContent = CRITICS[b.dataset.d] || b.textContent;
  renderWorlds(); if (typeof renderLobbyUI === 'function' && $('lineup')) renderLobbyUI();''')
rep("function paintName() { const n = playerName(); NAMES[0] = n; $('nameShow').textContent = store.name ? n : 'Add your name';", "function paintName() { const n = playerName(); NAMES[0] = n; $('nameShow').textContent = store.name ? n : 'Name';")
# the rivals are named while you're still in the studio, so the lineup can show them
rep("  pickRivalNames(); rollRivalLooks(); AU.init(); AU.music('end');", "  rollRivalLooks(); AU.init(); AU.music('end');")
rep("function showMenu() {\n  state = 'menu';", "function showMenu() {\n  pickRivalNames(); state = 'menu';")

# ---------- experience from every exhibition ----------
rep('''  wr.played++; if (ry > wr.best) wr.best = ry; if (win > 0 && mode !== 'solo') wr.wins++;
  save();''', '''  wr.played++; if (ry > wr.best) wr.best = ry; if (win > 0 && mode !== 'solo') wr.wins++;
  // reputation: paint earns it, a win earns more, and a finished commission pays
  endInfo.diff = diff; let gain = Math.round(16 + ry * 0.9 + (win > 0 ? 36 : win === 0 && mode !== 'solo' ? 12 : 0) + (newBest ? 14 : 0) + (mode === 'trio' ? 8 : 0));
  const fin = commProgress(endInfo); gain += fin.length * COMM_XP; endInfo.xp0 = store.xp || 0; store.xp = endInfo.xp0 + gain; endInfo.xp = gain; endInfo.comms = fin;
  save();''')
# the results placard: reputation fills, commissions tick
rep("  $('vTap').textContent = 'Tap to see the canvas';", "  $('vTap').textContent = 'Tap to see the canvas';")
rep('''function judgeGo() {''', '''const XP_FRAMES = 36;
function xpFrame(el, k) { k = clamp(Math.round(k), 0, XP_FRAMES - 1); const fw = el.clientWidth || 132, fh = el.clientHeight || 74; el.style.backgroundPosition = (-(k % 6) * fw) + 'px ' + (-Math.floor(k / 6) * fh) + 'px'; }
let repAnim = 0;
function showRep(info) {
  const row = $('repRow'), m = $('xpMeter'); cancelAnimationFrame(repAnim);
  if (!info || !(info.xp > 0)) { row.hidden = true; $('commDone').innerHTML = ''; return; }
  const r0 = repOf(info.xp0), r1 = repOf(info.xp0 + info.xp), up = r1.lv > r0.lv; row.hidden = false; row.classList.toggle('up', up);
  $('repRowName').textContent = r0.name; $('xpGain').innerHTML = '+' + info.xp + '<small>XP</small>'; xpFrame(m, (XP_FRAMES - 1) * r0.x / r0.need);
  $('commDone').innerHTML = (info.comms || []).map((k, i) => '<div class="cd" style="animation-delay:' + (1.6 + i * 0.15).toFixed(2) + 's">Commission done: ' + k.t + '<b>+' + COMM_XP + ' XP</b></div>').join('');
  const t0 = performance.now(), dur = up ? 1700 : 1100, f0 = r0.x / r0.need, f1 = r1.x / r1.need;
  const step = () => { const u = clamp((performance.now() - t0 - 900) / dur, 0, 1), e = u * u * (3 - 2 * u); let f;
    if (up) { const half = 0.55; f = e < half ? f0 + (1 - f0) * (e / half) : f1 * ((e - half) / (1 - half)); if (e >= half && !row.classList.contains('lv')) { row.classList.add('lv'); $('repRowName').textContent = r1.name; $('repRowName').animate([{ transform: 'scale(1.6)' }, { transform: 'none' }], { duration: 420, easing: 'cubic-bezier(.3,1.6,.5,1)' }); AU.fanfare(); AU.say('levelup'); } }
    else f = f0 + (f1 - f0) * e;
    xpFrame(m, (XP_FRAMES - 1) * f); if (u < 1) repAnim = requestAnimationFrame(step); };
  row.classList.remove('lv'); repAnim = requestAnimationFrame(step);
}
function judgeGo() {''')
rep("  paintName();\n  const PT_B = ", "  paintName(); showRep(info);\n  const PT_B = ")

# ---------- the opening night: VS, then the match ----------
rep('''    if (mapUsed) { building = true; freshMap(); clearTimeout(warmQ); warmRender(); building = false; }
    beginMatch();''', '''    if (mapUsed) { building = true; freshMap(); clearTimeout(warmQ); warmRender(); building = false; }
    showVS(beginMatch);''')
rep('''function beginMatch() {''', '''function showVS(cb) {
  if (window.__instant || reduceMotion) return cb();
  const el = $('vsx'), md = MODES.find(m => m[0] === mode) || MODES[0];
  const card = (D, name, me) => '<div class="vsp"><span class="swc" style="--sc:' + TEAMS[D.team].css + ';--cd:' + mixHex(TEAMS[D.team].wet, 0x0C0620, 0.62) + '">' + faceIcon(D, false) + '</span><b>' + escAttr(name) + '</b>' + (me ? '<span class="tape">You</span>' : '') + '</div>';
  let h = card(P, playerName(), true); if (mode !== 'solo') { h += '<b class="vsbig">VS</b>' + card(H, NAMES[1], false); if (mode === 'trio') h += card(H2, NAMES[2], false); }
  $('vsRow').innerHTML = h; $('vsTitle').innerHTML = '<b>' + escAttr(TH.label) + '</b> \\u00b7 ' + (mode === 'solo' ? 'Solo, 60 seconds' : md[1] + ', critics ' + (CRITICS[diff] || 'fair').toLowerCase());
  el.hidden = false; AU.whoosh(); setTimeout(() => AU.say('ready'), 350); buzz([15, 30, 15]);
  const id = runId; setTimeout(() => { if (id !== runId && state !== 'menu') { el.hidden = true; return cb(); } slashWipe({ dur: 1.0, onPeak: () => { el.hidden = true; cb(); } }); }, 2100);
}
function beginMatch() {''')

# ---------- the paint tank: the painted meter, one frame per level ----------
rep("const tankS = { x: 0, vx: 0, y: 0, vy: 0, set: false };", "const tankS = { x: 0, vx: 0, y: 0, vy: 0, set: false }; let tankFrame = -1;")
rep("  const pc = Math.round(P.paint * 100); if (pc !== tankPct) { tankPct = pc; tankTrack.setAttribute('aria-valuenow', String(Math.max(0, pc))); }",
    "  const pc = Math.round(P.paint * 100); if (pc !== tankPct) { tankPct = pc; tankTrack.setAttribute('aria-valuenow', String(Math.max(0, pc))); }\n  const fk = Math.round(clamp(P.paint, 0, 1) * 35); if (fk !== tankFrame) { tankFrame = fk; tankTrack.style.backgroundPosition = (-(fk % 6) * 88) + 'px ' + (-Math.floor(fk / 6) * 50) + 'px'; }")
rep("const sx = (tv1.x * 0.5 + 0.5) * viewW, sy = (0.5 - tv1.y * 0.5) * viewH, rp = Math.abs(tv2.x - tv1.x) * 0.5 * viewW, W = 17, Hh = 52, off = Math.max(20, rp + 8);",
    "const sx = (tv1.x * 0.5 + 0.5) * viewW, sy = (0.5 - tv1.y * 0.5) * viewH, rp = Math.abs(tv2.x - tv1.x) * 0.5 * viewW, W = 88, Hh = 50, off = Math.max(20, rp + 8);")

# ---------- the curator's voice ----------
rep("    vox(name, v) { if (!ctx || T() - voxT < 0.45) return false;", '''    // the curator: recorded lines, one at a time
    say(name, v) { if (!ctx || store.muted || location.protocol === 'file:') return false; const k = 'say_' + name, go = b => { try { const s = ctx.createBufferSource(), g = ctx.createGain(); s.buffer = b; g.gain.value = v == null ? 0.95 : v; s.connect(g); g.connect(sfx || out || ctx.destination); s.start(); } catch (e) {} };
      if (SAY[k]) { if (SAY[k].buf) go(SAY[k].buf); return true; } SAY[k] = {}; fetch((window.VOICE_BASE || 'voice/') + k + '.mp3').then(r => r.ok ? r.arrayBuffer() : Promise.reject()).then(b => new Promise((ok, bad) => { const p = ctx.decodeAudioData(b, ok, bad); if (p && p.catch) p.catch(bad); })).then(b => { SAY[k].buf = b; go(b); }).catch(() => {}); return true; },
    vox(name, v) { if (!ctx || T() - voxT < 0.45) return false;''')
rep("function makeAudio() {\n  let ctx = null, out, sfx,", "function makeAudio() {\n  const SAY = {};\n  let ctx = null, out, sfx,")
# the verdict is read out
rep("AU.sting(won ? 'win' : info.winner ? 'lose' : 'draw'); if (won) setTimeout(() => AU.vox('yay'), 380);", "AU.sting(won ? 'win' : info.winner ? 'lose' : 'draw'); setTimeout(() => AU.say(solo ? (info.newBest ? 'best' : 'time') : won ? 'victory' : info.winner ? 'defeat' : 'draw'), 650); if (won) setTimeout(() => AU.vox('yay'), 380);")

# ---------- the board's crown stays; the victory tag gets the red dot ----------
rep("$('vTag').textContent = info.newBest ? 'New best!' : \"Time's up\";", "vicTag(info.newBest ? 'New best!' : \"Time's up\", info.newBest);")
rep("$('vTag').textContent = 'Dead even';", "vicTag('Dead even', false);")
rep("$('vTag').textContent = lead === P ? 'Winner!' : me.place === 2 ? 'You came 2nd' : 'You came ' + me.place + (me.place === 3 ? 'rd' : 'th');", "vicTag(lead === P ? 'Sold' : me.place === 2 ? 'You came 2nd' : 'You came ' + me.place + (me.place === 3 ? 'rd' : 'th'), lead === P);")
rep("function startVictory() {", "function vicTag(t, dot) { $('vTagTxt').textContent = t; $('vDot').hidden = !dot; }\nfunction startVictory() {")

# ---------- the slash wipe: chunky blades streak across the screen, it flashes at the peak, and the reveal is behind it ----------
rep('function showNewItem(id) {', r'''const slashEl = document.createElement('canvas'); slashEl.className = 'slash'; slashEl.hidden = true; stage.appendChild(slashEl);
let slashAnim = null;
function slashWipe(o) {
  o = o || {}; const ink = TEAMS[0].css, cols = o.cols || [ink, '#F4EEE3', '#171320', ink, '#F4EEE3', ink, '#171320', '#F4EEE3'];
  if (reduceMotion) { if (o.onPeak) o.onPeak(); if (o.onEnd) setTimeout(o.onEnd, 50); return; }
  const dur = o.dur || 1.15, cv = slashEl, g = cv.getContext('2d'), dpr = Math.min(2, window.devicePixelRatio || 1), W = viewW, H = viewH, D = Math.hypot(W, H);
  cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); cv.hidden = false;
  const n = 8, shapes = [];
  for (let i = 0; i < n; i++) { const r = Math.random; shapes.push({ t0: i * 0.06 + r() * 0.04, y: (i / (n - 1) - 0.5) * H * 1.5 + (r() - 0.5) * H * 0.12, th: 0.16 + r() * 0.3 + (i > n - 3 ? 0.25 : 0), len: 0.7 + r() * 0.6, ang: -0.6 + (r() - 0.5) * 0.18, col: cols[i % cols.length], flip: r() < 0.5 }); }
  const t0 = performance.now(); if (slashAnim) cancelAnimationFrame(slashAnim); let peaked = false;
  const draw = () => {
    const t = (performance.now() - t0) / 1000, u = t / dur; g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, W, H);
    for (const s of shapes) { const k = clamp((t - s.t0) / (dur * 0.64), 0, 1); if (k <= 0 || k >= 1) continue;
      const e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2, x = -D * 0.95 + e * D * 2.1, L = D * s.len, T = D * s.th * 0.5 * Math.sin(Math.min(1, k * 1.5) * Math.PI) * (s.flip ? -1 : 1);
      g.save(); g.translate(W / 2, H / 2); g.rotate(s.ang); g.translate(x, s.y);
      g.beginPath(); g.moveTo(-L, 0); g.lineTo(-L * 0.35, -T); g.lineTo(L * 0.45, -T * 0.6); g.lineTo(L, 0); g.lineTo(L * 0.35, T * 0.45); g.lineTo(-L * 0.45, T * 0.85); g.closePath();
      g.fillStyle = s.col; g.strokeStyle = '#171320'; g.lineWidth = 7; g.lineJoin = 'round'; g.fill(); g.stroke(); g.restore(); }
    const f = u > 0.52 ? 1 - Math.pow(clamp((u - 0.52) / 0.48, 0, 1), 1.5) : u > 0.4 ? (u - 0.4) / 0.12 : 0;
    if (u > 0.52 && !peaked) { peaked = true; if (o.onPeak) o.onPeak(); }
    if (f > 0) { g.globalAlpha = f; g.fillStyle = '#F4EEE3'; g.fillRect(0, 0, W, H); g.globalAlpha = 1; }
    if (u < 1) slashAnim = requestAnimationFrame(draw); else { slashAnim = null; cv.hidden = true; g.clearRect(0, 0, W, H); if (o.onEnd) o.onEnd(); }
  };
  try { AU.whoosh(); } catch (e) {} draw();
}
function showNewItem(id) {''')
rep("  el.hidden = false; void el.offsetWidth; el.classList.add('on'); AU.fanfare(); setTimeout(() => AU.power(), 700); buzz([20, 40, 20, 40, 30]);", "  slashWipe({ onPeak: () => { el.hidden = false; void el.offsetWidth; el.classList.add('on'); AU.fanfare(); setTimeout(() => AU.power(), 700); buzz([20, 40, 20, 40, 30]); } });")

# ---------- screen orientation ----------
rep('''$('setBtn').addEventListener('click', uiClick(openSettings));''', '''$('setBtn').addEventListener('click', uiClick(openSettings));
// ---------- screen orientation: picked on the first launch, changed in Settings. On a phone held the other way the game asks for a turn ----------
const ORIENT_NAMES = { port: 'upright', land: 'wide' };
let orientPick = null;
const touchy = () => matchMedia('(pointer: coarse)').matches;
function orientNative(v) { try { const h = window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.orient; if (h) h.postMessage(v || ''); } catch (e) {} }
function applyOrient() { const v = store.orient || ''; document.documentElement.dataset.orient = v; for (const b of $('orientPick').children) b.setAttribute('aria-pressed', String(b.dataset.o === v)); orientNative(v); checkRotate(); }
function setOrient(v) { store.orient = v; save(); applyOrient(); heroT = 0; }
function checkRotate() {
  const want = store.orient, el = $('rotate'); if (!want || !touchy() || !$('orient').hidden || window.__noRotate) { el.hidden = true; return; }
  const land = viewW > viewH, wrong = want === 'land' ? !land : land;
  if (wrong && el.hidden) { $('rotateIcon').innerHTML = want === 'land' ? '%(phone_l)s' : '%(phone_p)s'; $('rotateIcon').classList.toggle('toLand', want === 'land'); $('rotateSub').textContent = 'Roll Model is set to ' + ORIENT_NAMES[want] + '. Turn your phone, or play it this way.'; if (state === 'play') pause(); }
  el.hidden = !wrong;
}
function paintOrient() { for (const b of $('orient').querySelectorAll('.ocard')) b.setAttribute('aria-checked', String(b.dataset.o === orientPick)); }
function openOrient() { const el = $('orient'); orientPick = viewW > viewH ? 'land' : 'port'; paintOrient(); el.hidden = false; checkRotate(); setTimeout(() => $('orientOk').focus({ preventScroll: true }), 40); }
$('orient').addEventListener('click', e => { const c = e.target.closest('.ocard'); if (!c) return; AU.init(); if (c.dataset.o !== orientPick) { AU.ui(); orientPick = c.dataset.o; paintOrient(); } });
$('orientOk').addEventListener('click', () => { AU.init(); AU.pop(); const el = $('orient'); el.classList.add('out'); setTimeout(() => { el.hidden = true; el.classList.remove('out'); checkRotate(); sayT = 0.8; }, 380); store.orient = orientPick || 'port'; save(); applyOrient(); heroT = 0; });
$('orientPick').addEventListener('click', e => { const t = e.target.closest('button'); if (!t || t.dataset.o === store.orient) return; AU.init(); AU.ui(); setOrient(t.dataset.o); });
$('rotateSwap').addEventListener('click', () => { AU.init(); AU.ui(); setOrient(viewW > viewH ? 'land' : 'port'); });
window.addEventListener('resize', () => setTimeout(checkRotate, 0));
$('soundPick').addEventListener('click', e => { const t = e.target.closest('button'); if (!t || (t.dataset.s === 'off') === !!store.muted) return; toggleSound(); paintSettings(); });''' % { 'phone_l': I['phone_l'].replace("'", "\\'"), 'phone_p': I['phone_p'].replace("'", "\\'") })
rep("function paintSettings() { for (const b of $('gfxPick').children) b.setAttribute('aria-pressed', String(b.dataset.g === gfxPick));",
    "function paintSettings() { for (const b of $('soundPick').children) b.setAttribute('aria-pressed', String((b.dataset.s === 'off') === !!store.muted)); for (const b of $('orientPick').children) b.setAttribute('aria-pressed', String(b.dataset.o === (store.orient || ''))); for (const b of $('gfxPick').children) b.setAttribute('aria-pressed', String(b.dataset.g === gfxPick));")
rep('''showMenu();
await bootStep(0.82, 0.97, 'Setting the stage');''', '''applyOrient(); showMenu();
await bootStep(0.82, 0.97, 'Setting the stage');''')
rep('''for (const ev of ['pointerdown', 'keydown', 'touchend']) window.addEventListener(ev, () => AU.touch(), { capture: true, passive: true });''',
'''if (!store.orient) { if (bootHold) { const w = setInterval(() => { if (!bootHold) { clearInterval(w); openOrient(); } }, 100); } else openOrient(); }
for (const ev of ['pointerdown', 'keydown', 'touchend']) window.addEventListener(ev, () => AU.touch(), { capture: true, passive: true });''')
# boot copy
rep("await bootStep(0.1, 0.5, 'Building the canvas');", "await bootStep(0.1, 0.5, 'Priming the canvas');")
rep("await bootStep(0.82, 0.97, 'Setting the stage');", "await bootStep(0.82, 0.97, 'Hanging the show');")

open(DST, 'w').write(s)
print('ok', n0, '->', len(s))
