"""v274: the victory screen, rethought as a fight poster. Dark ink, a slash of the winner's paint across it (a real dry brush stroke,
generated with Ludo and tinted in the shader), the winner's name huge in a condensed italic behind the winner, and the winner down low in
front of it all, lit hard from one side with a rim of its own color behind, glaring out at you through heavy narrowed lids (a new face:
"menace", lids drawn level across the eyes, a crooked sneer). No more jumping for joy: it drops in, hunkers down, gives you a sideways
look, then rears up and slams a hand down: a flash, a ring, its paint splattered on the poster behind it (a Ludo ink splat), the camera
jolted. The words are set like a broadcast: the event and stage in small spaced caps, a kicker over the name (Last one standing,
Victory, New best...), a row of stats in big italic numerals over hairlines, the rest of the field in thin rows, and a line that fills
as the screen counts down to the canvas. Portrait and landscape (the words in a column on the right there)."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def region(s, a, b, new):
    assert s.count(a) == 1, (s.count(a), a[:120]); i = s.index(a); j = s.index(b, i); return s[:i] + new + s[j:]

# ---------------------------------------------------------------- the face: a ninth row on the sheet (cells 32-35)
def face(s):
    s = rep(s, "const FACE_X = [['sleepy', 20], ['wink', 21], ['sad', 22], ['focus', 23]],", "const FACE_X = [['sleepy', 20], ['wink', 21], ['sad', 22], ['focus', 23], ['menace', 32]],")
    s = rep(s, "  focus: { h: 0.06, k: -0.1, c: 0.08, ch: -0.58, chc: 0.24, pu: 0.94, py: -0.04 },\n};",
            "  focus: { h: 0.06, k: -0.1, c: 0.08, ch: -0.58, chc: 0.24, pu: 0.94, py: -0.04 },\n"
            "  // (v274) the winner's glare: heavy lids drawn down nearly level across the eyes, a slight scowl to them, the lower lids pushed up\n"
            "  menace: { h: -0.2, k: -0.14, c: -0.03, ch: -0.72, chc: 0.2, pu: 0.84, py: -0.02 },\n};")
    s = rep(s, "const W = C * 4, H = C * 8, col = document.createElement('canvas')", "const W = C * 4, H = C * 9, col = document.createElement('canvas')") # (v274: a ninth row)
    s = rep(s, "pout: [22, 27], startle: [5, 13] };", "pout: [22, 27], startle: [5, 13], menace: [32, 33] };")
    s = rep(s, "  FACE_MX.forEach(([k, cell]) => { at(g, cell, ctx => big(ctx, () => MOUTHS2[k](ctx, false))); at(g, cell + 4, ctx => big(ctx, () => MOUTHS2[k](ctx, true))); });\n  return { col, msk };",
            "  FACE_MX.forEach(([k, cell]) => { at(g, cell, ctx => big(ctx, () => MOUTHS2[k](ctx, false))); at(g, cell + 4, ctx => big(ctx, () => MOUTHS2[k](ctx, true))); });\n"
            "  // (v274) a crooked sneer: flat on one side, the other corner hitched up, a dimple there; with fangs, one tooth showing under the raised side\n"
            "  const sneerY = u => MY - 0.014 - 0.02 * Math.sin(Math.PI * u * 0.8) + 0.064 * Math.pow(u, 2.4);\n"
            "  const sneer = (ctx, f) => { if (f) fang(ctx, 0.07, sneerY(0.74) + 0.004, 0.9); line(ctx, Array.from({ length: 29 }, (_, i) => { const u = i / 28; return [-0.13 + 0.27 * u, sneerY(u)]; }), 0.038); line(ctx, [[0.128, MY + 0.074], [0.154, MY + 0.042]], 0.026); };\n"
            "  at(g, 33, ctx => big(ctx, () => sneer(ctx, false))); at(g, 34, ctx => big(ctx, () => sneer(ctx, true)));\n"
            "  return { col, msk };")
    s = rep(s, "const fm = c => fang ? c + (c >= 24 ? 4 : 6) : c;", "const fm = c => fang ? c + (c >= 32 ? 1 : c >= 24 ? 4 : 6) : c;")
    s = rep(s, "return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) * 0.125); }", "return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) / 9.0); }")
    return s

# ---------------------------------------------------------------- the rig: menace (low, hands wide, tail lashing) and a hand slam
def rig(s):
    s = rep(s, "  { const cr = spr(L.cr, air ? 0 : clamp01(M.crouch || 0), 420, 28, dt);",
            "  // (v274) the winner's menace: down low, its weight forward over its hands, its shoulders hunched up between them; and a slam: one\n"
            "  // hand reared up high (M.slam 1), the body rising off it, then brought down hard (M.slam straight back to 0)\n"
            "  const mnK = spr(L.mnS || (L.mnS = { x: 0, v: 0 }), air ? 0 : clamp01(M.menace || 0), 150, 22, dt), slK = air ? 0 : clamp01(M.slam || 0);\n"
            "  if (mnK > 0.002) { out.root.y -= 0.04 * mnK; out.root.z += 0.012 * mnK; this.pitchTurn(out, sp[3], 0.1 * mnK); this.pitchTurn(out, sp[2], -0.05 * mnK); }\n"
            "  if (slK > 0.002) { out.root.y += 0.02 * slK; this.pitchTurn(out, sp[3], -0.14 * slK); this.worldTurn(out, sp[2], 0, -7 * slK); }\n"
            "  { const cr = spr(L.cr, air ? 0 : clamp01(M.crouch || 0), 420, 28, dt);")
    s = rep(s, "    const wvk = l.en === 'hand.R' ? wv : 0; if (wvk > 0.002) { const pk = P.fk('crawl', out), sh = pk[l.root], q = l.wq || (l.wq = new THREE.Vector3()), sw = Math.sin(this.t * 2 * Math.PI * 2.4);\n"
            "      q.set(sh.x + l.m * (0.1 + 0.07 * sw), sh.y + 0.17 + 0.02 * Math.abs(sw), sh.z + 0.2);",
            "    if (mnK > 0.002 && l.arm) { const q = l.mq || (l.mq = new THREE.Vector3()); q.copy(tp); q.x += l.m * 0.032 * mnK; q.z += 0.014 * mnK; tp = q; } // (v274: menacing, its hands set wide)\n"
            "    const slk = l.en === 'hand.R' ? slK : 0, wvk = l.en === 'hand.R' ? Math.max(wv, slk) : 0; if (wvk > 0.002) { const pk = P.fk('crawl', out), sh = pk[l.root], q = l.wq || (l.wq = new THREE.Vector3()), sw = slk > wv ? 0 : Math.sin(this.t * 2 * Math.PI * 2.4);\n"
            "      if (slk > wv) q.set(sh.x + l.m * 0.05, sh.y + 0.22, sh.z + 0.13); else q.set(sh.x + l.m * (0.1 + 0.07 * sw), sh.y + 0.17 + 0.02 * Math.abs(sw), sh.z + 0.2);")
    s = rep(s, "  if (sl > 0.001) { const tt = this.tailTarget, th = 4 * Math.PI * SL.u,",
            "  if (mnK > 0.002) { const tt = this.tailTarget; for (let k = 0; k < 6; k++) tt[k * 2] += Math.sin(this.t * 1.7 - k * 0.6) * (4 + 3 * k) * mnK; } // (v274: menacing, the tail lashing slowly)\n"
            "  if (sl > 0.001) { const tt = this.tailTarget, th = 4 * Math.PI * SL.u,")
    s = rep(s, "A.earCover = o.earCover || 0; A.motion.wave = o.wave || 0;", "A.earCover = o.earCover || 0; A.motion.wave = o.wave || 0; A.motion.menace = o.menace || 0; A.motion.slam = o.slam || 0;")
    s = rep(s, "  o.D = D; (I.kind === 'axo' ? AXOC : SLIME).update(I, o);",
            "  { const vp = vic && D.vicPose; o.menace = vp ? vp.menace || 0 : 0; o.slam = vp ? vp.slam || 0 : 0; } // (v274: the winner's stance)\n"
            "  o.D = D; (I.kind === 'axo' ? AXOC : SLIME).update(I, o);")
    return s

# ---------------------------------------------------------------- the backdrop
VIC_FS = r"""const VIC_FS = `uniform float uTime, uK, uT, uLand, uFlash; uniform vec3 uA, uB, uC; uniform vec2 uRes, uCen, uNameC; uniform vec4 uShock, uSplat;
uniform sampler2D uName, uBrush, uSplatT; varying vec2 vUv;
float h1(float n){ return fract(sin(n * 91.345) * 47453.5453); }
float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(h2(i), h2(i + vec2(1.0, 0.0)), f.x), mix(h2(i + vec2(0.0, 1.0)), h2(i + vec2(1.0, 1.0)), f.x), f.y); }
vec2 rot2(vec2 p, float a){ float c = cos(a), s = sin(a); return vec2(c * p.x + s * p.y, -s * p.x + c * p.y); }
// a brush stroke laid along x (q in its own frame, len its length, th its height), drawn in as far as wipe (0 none .. 1 all of it)
float brush(vec2 q, float len, float th, float wipe){ vec2 u = vec2(q.x / len + 0.5, q.y / th + 0.5); if (u.y < 0.0 || u.y > 1.0 || u.x < 0.0 || u.x > 1.0) return 0.0;
  return texture2D(uBrush, u).r * (1.0 - smoothstep(wipe - 0.05, wipe, u.x)); }
void main(){
  float asp = uRes.x / uRes.y; vec2 px = vUv * uRes, p = (vUv - uCen) * vec2(asp, 1.0); float r = length(p);
  vec3 ink = vec3(0.018, 0.015, 0.026), deep = mix(ink, uB, 0.3);
  // the ground: near black, the winner's color glowing low behind it, a slow smoke drifting through
  vec3 col = mix(deep, ink, smoothstep(0.05, 0.9, r)) + uA * 0.1 * exp(-r * r * 5.0);
  col += uA * 0.06 * (vn(p * 2.4 + vec2(uTime * 0.05, -uTime * 0.07)) - 0.5);
  // halftone out toward the corners: the winner's color printed in dots, growing toward the edges
  { vec2 hp = rot2(px, 0.785) / 6.5, hc = fract(hp) - 0.5; float f = smoothstep(0.5, 1.3, r) * (0.55 + 0.45 * vn(p * 1.6 + 3.0)), rad = 0.48 * sqrt(f);
    col = mix(col, uA * 0.36, (1.0 - smoothstep(rad - 0.07, rad, length(hc))) * 0.5 * smoothstep(0.15, 0.6, uT)); }
  // the slash: one stroke of the winner's paint right across behind it, swept in from the left; and a thin bone stroke under it, the other way
  float ang = mix(0.42, 0.2, uLand), wipe = 1.08 * (1.0 - pow(1.0 - clamp((uT - 0.08) / 0.3, 0.0, 1.0), 3.0));
  vec2 q = rot2(p - vec2(0.0, mix(0.02, 0.0, uLand)), ang); float L1 = asp * 1.9 + 0.8, th1 = mix(0.38, 0.56, uLand);
  float b1 = brush(q, L1, th1, wipe), up = clamp(q.y / th1 + 0.5, 0.0, 1.0);
  col = mix(col, uA * (0.36 + 0.22 * up) + uC * 0.06 * smoothstep(0.75, 1.0, up), b1);
  // streaks running along it
  { float row = floor(q.y * 30.0), hr = h1(row), hs = h1(row + 7.13), x = fract(q.x * (0.22 + 0.3 * hs) - uTime * (0.2 + 0.5 * hr) + hr * 9.0);
    col += vec3(0.9, 0.85, 0.8) * step(0.84, hs) * smoothstep(0.0, 0.02, x) * (1.0 - smoothstep(0.02, 0.28, x)) * (1.0 - smoothstep(0.08, 0.4, abs(fract(q.y * 30.0) - 0.5))) * 0.09; }
  // the slam's splat: its paint flung out over the poster behind it, darker than the stroke
  if (uSplat.z > 0.0 && uT > uSplat.z) { float a = clamp((uT - uSplat.z) / 0.13, 0.0, 1.0), sc = uSplat.w * (0.3 + 0.7 * (1.0 - pow(1.0 - a, 3.0)));
    vec2 sp = (vUv - uSplat.xy) * vec2(asp, 1.0) / sc + 0.5; float m = 0.0;
    if (sp.x > 0.0 && sp.x < 1.0 && sp.y > 0.0 && sp.y < 1.0) { float d = length(sp - 0.5); m = texture2D(uSplatT, sp).r * (1.0 - smoothstep(0.36, 0.5, d)) * (0.35 + 0.65 * smoothstep(0.12, 0.3, d)); } // (its spikes more than its middle)
    col = mix(col, uA * 0.85 + uC * 0.05, m * 0.9); }
  // the name: slammed down from big, a hard shadow under it; the place, a huge faint outline behind it all
  { float pn = clamp((uT - 0.4) / 0.2, 0.0, 1.0), en = 1.0 - pow(1.0 - pn, 3.0), sc = mix(1.25, 1.0, en);
    vec2 jolt = uShock.z > 0.0 && uT > uShock.z ? vec2(sin(uT * 97.0), cos(uT * 83.0)) * 0.006 * max(0.0, 1.0 - (uT - uShock.z) / 0.35) : vec2(0.0);
    vec2 nu = uNameC + (vUv - uNameC) / sc + jolt, o1 = vec2(6.0, -6.0) / uRes;
    float ng = texture2D(uName, vUv + jolt * 0.5).g, ns = texture2D(uName, nu - o1).r, nm = texture2D(uName, nu).r;
    col += vec3(0.9, 0.86, 0.8) * ng * 0.05 * smoothstep(0.3, 0.9, uT);
    col = mix(col, ink * 0.5, ns * 0.9 * en);
    col = mix(col, vec3(0.96, 0.93, 0.87), nm * smoothstep(0.0, 0.35, pn)); }
  // embers drifting up
  { vec2 fu = p * vec2(7.0, 5.0) + vec2(0.0, -uTime * 0.16), fi = floor(fu), ff = fract(fu) - 0.5; float fh = h2(fi);
    col += uC * step(0.9, fh) * (1.0 - smoothstep(0.0, 0.025 + 0.035 * fract(fh * 9.0), length(ff + 0.3 * (vec2(fract(fh * 3.0), fract(fh * 5.0)) - 0.5)))) * 0.4 * (0.6 + 0.4 * sin(uTime * 3.0 + fh * 30.0)); }
  // the slam's ring
  if (uShock.z > 0.0 && uT > uShock.z && uT < uShock.z + 0.6) { float a = uT - uShock.z, rr = length((vUv - uShock.xy) * vec2(asp, 1.0)), R = a * 2.4;
    col += uC * (1.0 - smoothstep(0.0, 0.012 + a * 0.06, abs(rr - R))) * (1.0 - a / 0.6) * 0.9; }
  // room for the words: the foot darkened (portrait), the right side (landscape); a vignette, grain
  col *= 1.0 - (1.0 - uLand) * 0.6 * smoothstep(0.4, 0.02, vUv.y) - uLand * 0.62 * smoothstep(0.5, 0.9, vUv.x);
  col *= 1.0 - 0.38 * smoothstep(0.55, 1.35, length((vUv - 0.5) * vec2(asp, 1.0)));
  col += (h2(floor(px) + fract(uTime * 7.0) * 113.0) - 0.5) * 0.035;
  col = mix(col, uC * 1.5, uFlash);
  gl_FragColor = vec4(mix(uC * 1.2, col, smoothstep(0.0, 1.0, uK)), 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;
const vicNameCv = document.createElement('canvas'), vicNameG = vicNameCv.getContext('2d'), vicNameTex = new THREE.CanvasTexture(vicNameCv);
vicNameTex.colorSpace = THREE.NoColorSpace; vicNameTex.generateMipmaps = false; vicNameTex.minFilter = THREE.LinearFilter;
const vicArt = f => { const t = new THREE.TextureLoader().load(f); t.colorSpace = THREE.NoColorSpace; return t; };
const vicU = { uTime: { value: 0 }, uK: { value: 0 }, uT: { value: 0 }, uLand: { value: 0 }, uFlash: { value: 0 }, uA: { value: new THREE.Color() }, uB: { value: new THREE.Color() }, uC: { value: new THREE.Color() },
  uRes: { value: new THREE.Vector2(1, 1) }, uCen: { value: new THREE.Vector2(0.5, 0.5) }, uNameC: { value: new THREE.Vector2(0.5, 0.7) }, uShock: { value: new THREE.Vector4(0, 0, 0, 0) }, uSplat: { value: new THREE.Vector4(0, 0, 0, 0) },
  uName: { value: vicNameTex }, uBrush: { value: vicArt('art/vic_brush.webp') }, uSplatT: { value: vicArt('art/vic_splat.webp') } };
"""

VIC_JS = r"""function vicTag(t) { $('vTagTxt').textContent = t; }
// (v274) the name, drawn for the backdrop (so the winner stands in front of it): one canvas the size of the screen, the name in red, the
// place's huge outline in green (the shader inks them); stacked in lines, as big as fits its block
const VIC_FONT = '"Barlow Condensed", "Arial Narrow", "Roboto Condensed", sans-serif', VIC_FACE = 'italic 900 100px "Barlow Condensed"';
function vicDrawName() {
  if (!vic) return; const W = Math.max(1, viewW), H = Math.max(1, viewH), land = vicLand(), dpr = Math.min(2, window.devicePixelRatio || 1), g = vicNameG;
  const lines = []; for (const w of vic.name.toUpperCase().split(' ').filter(Boolean)) { if (lines.length && (lines[lines.length - 1] + ' ' + w).length <= (land ? 16 : 9)) lines[lines.length - 1] += ' ' + w; else lines.push(w); }
  g.font = 'italic 900 100px ' + VIC_FONT; const widest = Math.max(1, ...lines.map(l => g.measureText(l).width)), maxW = land ? W * 0.56 : W - 28, maxH = land ? H * 0.6 : H * 0.34;
  const fs = clamp(Math.min(100 * maxW / (widest * 1.05), maxH / (lines.length * 0.84)), 40, land ? H * 0.46 : 280), lh = fs * 0.84, x0 = land ? Math.max(W * 0.045, 24) : 14;
  const cw = Math.round(W * dpr), ch = Math.round(H * dpr); if (vicNameCv.width !== cw || vicNameCv.height !== ch) { vicNameCv.width = cw; vicNameCv.height = ch; vicNameTex.dispose(); } g.setTransform(dpr, 0, 0, dpr, 0, 0); g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  g.globalCompositeOperation = 'lighter'; g.textBaseline = 'alphabetic';
  if (vic.ghost) { const gs = Math.round(H * (land ? 1.0 : 0.6)); g.font = 'italic 900 ' + gs + 'px ' + VIC_FONT; g.textAlign = 'right'; g.lineWidth = 2; g.strokeStyle = '#00FF00'; g.strokeText(vic.ghost, W * (land ? 0.6 : 1.06), land ? H * 1.04 : vic.nameTop + gs * 0.72 + lh * lines.length * 0.4); }
  g.font = 'italic 900 ' + fs.toFixed(1) + 'px ' + VIC_FONT; g.textAlign = 'left'; g.fillStyle = '#FF0000';
  lines.forEach((l, i) => g.fillText(l, x0, vic.nameTop + fs * 0.7 + i * lh));
  g.globalCompositeOperation = 'source-over';
  vic.lh = lh; vic.nameBot = vic.nameTop + fs * 0.7 + (lines.length - 1) * lh; vicNameTex.needsUpdate = true;
  vicU.uNameC.value.set((x0 + Math.min(maxW, widest * fs / 100) / 2) / W, 1 - (vic.nameTop + vic.nameBot) / 2 / H);
}
if (document.fonts && document.fonts.load) document.fonts.load(VIC_FACE).catch(() => {}); // (ready by the end of the first match)
// a stat: a big number (its unit small after it), a label under it
const vicStat = (n, unit, label, hi) => '<div class="vst' + (hi ? ' hi' : '') + '"><b>' + n + (unit ? '<small>' + unit + '</small>' : '') + '</b><span>' + label + '</span></div>';
const vicClock = s => Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0');
const VIC_HT = 1.25; // (the character from the floor to the top of a tall hat: the portrait framing fits this)
const VIC_SLAM = 1.66; // (when the slam lands, from the drop)
const vicRim = new THREE.DirectionalLight(0xFFFFFF, 0); vicRim.layers.set(4); scene.add(vicRim); scene.add(vicRim.target); // (only in the winner's pass)
function startVictory() {
  if (vic || state !== 'dead') return;
  const info = endInfo, solo = info.mode === 'solo', board = ACTIVE.map(D => ({ D, pct: info.show ? 9 - (info.places[D.team] || 4) : solo ? Math.round(info.you) : info.tot[D.team] })).sort((a, b) => b.pct - a.pct);
  for (const e of board) e.place = info.show ? info.places[e.D.team] || 4 : 1 + board.filter(o => o.pct > e.pct).length;
  let feat;
  if (info.show) feat = info.winners.slice().sort((a, b) => (b === P) - (a === P) || ally(b, P) - ally(a, P)).slice(0, 2);
  else if (solo || info.winner) feat = [solo ? P : info.winner];
  else { const tie = board.find(e => e.D !== P && e.pct === info.tot[0]); feat = tie ? [P, tie.D] : [P]; }
  const happy = info.show ? !info.draw || feat.length > 1 : solo ? info.newBest : true, lead = feat[0], col = new THREE.Color(TEAMS[lead.team].wet);
  // (the camera well off the sun's side: the winner lit hard from one side, the other side in shadow)
  vic = { t: 0, feat, happy, yaw: Math.atan2(sun.position.x, sun.position.z) - 1.05, name: '', ghost: '', slamAt: 0, po: [], nameTop: 100, nameBot: 200, lh: 100, cy: 0.5, room: 0.4,
    saved: feat.map(D => ({ D, x: D.x, y: D.y, z: D.z, yaw: D.yaw, st: D.st, paint: D.paint, power: D.power, vis: lookRoot(D).visible, ip: D.ip })) };
  // the featured blobs, awake and full, on their marks: three-quarters on to the camera; a pair side by side, turned in to each other
  const bx = lead.x, bz = lead.z, by = Math.max(0, surfaceUnder(bx, bz, lead.y + 2, true)), rx = Math.cos(vic.yaw), rz = -Math.sin(vic.yaw);
  feat.forEach((D, i) => {
    const two = feat.length > 1, off = two ? (i ? 0.66 : -0.66) : 0;
    Object.assign(D, { x: bx + rx * off, z: bz + rz * off, y: by, yaw: vic.yaw + (two ? (i ? -0.95 : 0.95) : 0.55), st: 'play', paint: 1, power: null, giantT: 0, slam: false, missile: false, charging: false, flatT: 0, stunT: 0, rollT: 0, immuneT: 0, air: false, vy: 0, exposed: false, dry: false, dilT: 0, spd: 0, turn: 0, squash: 0, wob: 0, turret: null, rocket: null, tGuard: 0, knockT: 0, flung: false, airSling: false, dashT: 0, dashDir: 0, kx: 0, kz: 0 });
    const V = D === P ? VP : D.look.V; Object.assign(V.look, { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0 }); V.flatK = 0; V.gk = 1; V.misK = 0; V.turPitch = 0; // its plain round self, not mid-roll or still a roller
    if (V.slime) V.slime.setForm('slime'); // (and not still a turret, a giant or a rocket)
    D.ip = null; const ip = ipReset(D); ip.expr = happy ? 'menace' : 'focus'; ip.watch = { yaw: 0, pitch: 0.85, look: [0, 0] }; // (its face and where it looks: its own, for the screen)
    lookRoot(D).visible = true; vicLayer(D, true);
  });
  vicU.uA.value.copy(col); vicU.uB.value.copy(col).multiplyScalar(0.3); vicU.uC.value.copy(col).lerp(COL_WHITE, 0.6); vicU.uK.value = 0; vicU.uT.value = 0; vicU.uFlash.value = 0; vicU.uShock.value.set(0, 0, 0, 0); vicU.uSplat.value.set(0, 0, 0, 0);
  vicRim.color.copy(col).lerp(COL_WHITE, 0.3);
  // the words
  vicEl.style.setProperty('--vc', hexCss(TEAMS[lead.team].wet)); vicEl.style.setProperty('--vc-hi', colVars(lead)[1]);
  const me = board.find(e => e.D === P); let w;
  if (info.show) w = sdVicWords(info, feat, me);
  else if (solo) { const you = Math.round(info.you); w = { kick: info.newBest ? 'New best' : "Time's up", name: playerName(), ghost: you + '%',
    stats: vicStat(you, '%', 'Canvas painted', true) + (!info.newBest ? vicStat(info.best, '%', 'Your best', false) : info.prevBest ? vicStat('+' + (you - info.prevBest), '%', 'On your old best', false) : vicStat('1st', '', 'Canvas on record', false)) }; }
  else if (feat.length > 1 || !info.winner) w = { kick: 'Dead even', name: feat.length > 1 ? playerName() + ' & ' + nameOf(feat[1]) : playerName(), ghost: '', stats: vicStat(me.pct, '%', 'Each', true) + vicStat(vicClock(info.time || 0), '', 'Time', false) };
  else { const k = info.kos[lead.team] || 0, cov = Math.round([info.you, info.cpu, info.cpu2][lead.team] || 0), lead2 = board[1] ? board[0].pct - board[1].pct : 0;
    w = { kick: lead === P ? 'Victory' : 'Winner', name: nameOf(lead), ghost: '1', stats: vicStat(cov, '%', 'Canvas', true) + vicStat(k, '', k === 1 ? 'KO' : 'KOs', false) + vicStat('+' + lead2, '', 'Winning margin', false) }; }
  vicTag(w.kick); vic.name = w.name; vic.ghost = w.ghost; $('vName').textContent = w.name; $('vName').setAttribute('aria-label', w.kick + ': ' + w.name);
  $('vStats').innerHTML = w.stats; [...$('vStats').children].forEach((el, i) => el.style.animationDelay = (0.95 + i * 0.08).toFixed(2) + 's');
  $('vCards').innerHTML = solo ? '' : board.filter(e => !feat.includes(e.D)).map((e, i) => '<div class="vrow' + (e.D === P ? ' me' : '') + '" style="--cc:' + colVars(e.D)[1] + ';animation-delay:' + (1.2 + i * 0.08).toFixed(2) + 's"><b class="vr">' + String(e.place).padStart(2, '0') + '</b>' + faceIcon(e.D, false)
    + '<span class="vn">' + escAttr(nameOf(e.D)) + (e.D === P ? '<em>You</em>' : '') + '</span><b class="vp">' + (info.show ? (info.kos[e.D.team] || 0) + '<small>' + ((info.kos[e.D.team] || 0) === 1 ? 'KO' : 'KOs') + '</small>' : e.pct + '<small>%</small>') + '</b></div>').join('');
  $('vTap').textContent = 'Tap to see the canvas'; $('vStage').textContent = TH.label + ' · ' + (solo ? 'Time trial' : (MODES.find(m => m[0] === mode) || MODES[0])[1]);
  vicEl.classList.remove('out'); vicEl.hidden = false; reAdd.delete(bannerEl); bannerEl.classList.remove('on'); vicFit(); flashScreen();
  if (document.fonts && document.fonts.check && !document.fonts.check(VIC_FACE)) document.fonts.load(VIC_FACE).then(() => { if (vic) vicFit(); }).catch(() => {}); // (drawn again in its own face when it's in)
  hud.classList.add('off'); hintEl.classList.remove('on'); bannerEl.classList.remove('on'); $('vig').className = 'vig'; edgeReset();
  const id = runId;
  AU.whoosh(); setTimeout(() => { if (!vic || id !== runId) return; AU.splat(1.2); const won = solo ? info.newBest : info.show ? info.win > 0 : info.winner === P; AU.sting(won ? 'win' : info.winner ? 'lose' : 'draw'); setTimeout(() => AU.say(solo ? (info.newBest ? 'best' : 'time') : won ? 'victory' : info.winner ? 'defeat' : 'draw'), 650); AU.music(won ? 'win' : 'lost'); buzz(won ? [30, 40, 30] : 20); }, 420);
}
// each featured blob drops in, splats down and hunkers into its stance; then rears a hand up and slams it down (once), and holds there,
// breathing hard, its tail lashing
function vicPose(i, t) {
  const tt = t - 0.1 - i * 0.14, o = { hop: 0, sq: 0, rise: 0, spin: 0, coil: 0, kick: 0, leap: false, side: 1, twirl: 0, ball: false, stand: false, menace: 0, slam: 0 };
  if (tt < 0) o.hop = 6;
  else if (tt < 0.3) { const u = tt / 0.3; o.hop = 4.2 * (1 - u * u); }
  else if (tt < 0.7) { const u = (tt - 0.3) / 0.4; o.sq = 0.9 * Math.pow(1 - u, 1.8); o.hop = u > 0.35 ? Math.sin((u - 0.35) / 0.65 * Math.PI) * 0.1 : 0; }
  o.menace = (vic.happy ? 1 : 0.45) * smoothstep(0.4, 0.85, tt);
  if (vic.happy) { const s0 = VIC_SLAM - 0.44;
    if (tt > s0 && tt < VIC_SLAM - 0.06) o.slam = smoothstep(s0, VIC_SLAM - 0.16, tt); else if (tt >= VIC_SLAM - 0.06 && tt < VIC_SLAM) o.slam = (VIC_SLAM - tt) / 0.06;
    const k = tt - VIC_SLAM; if (k > 0 && k < 0.5) o.sq += 0.3 * Math.exp(-k * 10) * Math.min(1, k / 0.03); }
  o.rise = 0.045 * Math.sin(t * 2.3) * o.menace; // (breathing hard)
  return o;
}
// where it looks: a sideways look first (the head half away, the eyes slid round to you), then square on to you for the slam and after;
// a pair glare at each other until the slam. Its face: the glare, a snarl on the slam
function vicWatch(D, i, t, rdt) {
  const ip = D.ip; if (!ip || !ip.watch) return; const W = ip.watch, tt = t - 0.1 - i * 0.14, two = vic.feat.length > 1, O = two ? vic.feat[1 - i] : null;
  const rel = a => clamp(wrapA(a - D.yaw), -1.1, 1.1), toCam = rel(Math.atan2(vicCam.position.x - D.x, vicCam.position.z - D.z)), toO = O ? rel(Math.atan2(O.x - D.x, O.z - D.z)) : 0;
  const side = vic.happy ? (tt < VIC_SLAM - 0.4 ? 1 : tt > 4.6 && tt < 5.5 ? smoothstep(4.6, 4.8, tt) * (1 - smoothstep(5.3, 5.5, tt)) : 0) : 1;
  const tgt = two && tt < VIC_SLAM - 0.3 ? toO : toCam, hy = side > 0 && !two ? tgt * (1 - 0.75 * side) - 0.28 * side * Math.sign(tgt || 1) : tgt;
  W.yaw += (hy * 1.1 - W.yaw) * (1 - Math.exp(-rdt * (tt > VIC_SLAM - 0.45 && tt < VIC_SLAM ? 22 : 7))); // (snapped round for the slam)
  W.pitch = 0.85 + (vic.happy ? -0.1 : -0.22) * smoothstep(0.5, 1.0, tt);
  W.look[0] = clamp((tgt - hy) * 0.22, -0.13, 0.13) * (side > 0 ? 1 : 0.4); W.look[1] = vic.happy ? 0.03 : -0.04;
  ip.expr = !vic.happy ? 'focus' : tt > VIC_SLAM - 0.3 && tt < VIC_SLAM + 0.5 ? 'angry' : 'menace';
}
// the layout: the name's block under the event line, the winner in the room between it and the words at the foot (portrait), or on the
// left in front of its name with the words in a column on the right (landscape)
function vicFit() {
  if (!vic) return; const land = vicLand(), H = Math.max(1, viewH); vicEl.classList.toggle('land', land);
  const meta = $('vStage'), panel = $('vPanel'), mb = meta.offsetTop + meta.offsetHeight;
  vic.nameTop = land ? Math.max(mb + 48, H * 0.2) : mb + 46; vicDrawName(); $('vKick').style.top = Math.round(vic.nameTop - 38) + 'px';
  if (land) { vic.cy = clamp((vic.nameTop + vic.nameBot) / 2 / H + (vic.feat.length > 1 ? 0.24 : 0.14), 0.45, 0.68); vic.room = 0.74; } // (a pair lower: it covers less of its two names)
  else { vic.y0 = vic.nameBot - vic.lh * 0.4; vic.y1 = panel.offsetTop - 10; }
}
window.addEventListener('resize', () => { if (vic) vicFit(); });
const vicV = new THREE.Vector3();
function vicFrame(rdt) {
  vic.t += rdt; const t = vic.t, W = viewW, Hh = viewH, land = vicLand();
  vic.feat.forEach((D, i) => { D.vicPose = vicPose(i, t); vicWatch(D, i, t, rdt); });
  vicU.uTime.value = clock; vicU.uT.value = t; vicU.uK.value = clamp((t - 0.02) / 0.22, 0, 1); vicU.uRes.value.set(W, Hh); vicU.uLand.value = land ? 1 : 0;
  const fov = land ? 26 : 30; if (vicCam.fov !== fov || Math.abs(vicCam.aspect - W / Hh) > 1e-4) { vicCam.fov = fov; vicCam.aspect = W / Hh; vicCam.updateProjectionMatrix(); }
  let mx = 0, mz = 0, my = 0; for (const D of vic.feat) { mx += D.x; mz += D.z; my += D.y; } const n = vic.feat.length; mx /= n; mz /= n; my /= n;
  const tv = Math.tan(fov * Math.PI / 360), th = tv * W / Hh, a = vic.yaw + Math.sin(t * 0.3) * 0.035, push = 1.07 - 0.07 * smoothstep(0.4, 7, t), ppm = d => Hh / (2 * tv * d); // (px per metre at d)
  // the framing: as big as fits across; in portrait the top of its head into the foot of its name and its feet clear of the words (its
  // middle, 0.42 m up, is the point the view is centred on); in landscape the floor-to-hat height in 74% of the screen
  let dist = (n > 1 ? (land ? 1.3 : 0.92) : land ? 0.66 : 0.56) / th / (land ? 0.62 : 1), cy; // (portrait: big, a tail run off the edge if need be; landscape: in the left 62%)
  if (land) { dist = Math.max(dist, (VIC_HT + 0.05) / (2 * tv * 0.74)); cy = vic.cy || 0.5; }
  else { const y0 = vic.y0 || Hh * 0.3, y1 = Math.max(y0 + 60, vic.y1 || Hh * 0.7); if (y0 + 0.98 * ppm(dist) > y1) dist = 0.98 * Hh / (2 * tv * (y1 - y0)); cy = clamp((y0 + 0.52 * ppm(dist) + Math.max(0, y1 - y0 - 0.98 * ppm(dist)) * (n > 1 ? 0.45 : 0.3)) / Hh, 0.25, 0.7); }
  dist *= push; const cx = land ? 0.31 : n > 1 ? 0.5 : 0.45; vicU.uCen.value.set(cx, 1 - cy); // (one alone a little left of centre: turned, its head comes to the middle)
  vicCam.setViewOffset(W, Hh, (0.5 - cx) * W, (0.5 - cy) * Hh, W, Hh);
  // (low, looking up at it; jolted by the slam)
  vicCam.position.set(mx + Math.sin(a) * dist, my + 0.18, mz + Math.cos(a) * dist); vicV.set(mx, my + 0.42, mz);
  const sk = vic.slamAt ? Math.max(0, 1 - (t - vic.slamAt) / 0.32) : 0; if (sk > 0 && !reduceMotion) { const e = sk * sk * dist * 0.022; vicCam.position.x += Math.sin(t * 91) * e; vicCam.position.y += Math.cos(t * 77) * e; vicV.y += Math.sin(t * 63) * e * 0.5; }
  vicCam.lookAt(vicV);
  // the rim: behind it and up, on the side away from the sun
  vicRim.position.set(mx - Math.sin(a) * 3 - Math.cos(a) * 1.6, my + 2.4, mz - Math.cos(a) * 3 + Math.sin(a) * 1.6); vicRim.target.position.set(mx, my + 0.4, mz); vicRim.target.updateMatrixWorld();
  // the slam lands: a flash, a ring, its paint splattered over the poster behind it, the camera jolted
  if (vic.happy && !vic.slamAt && t >= VIC_SLAM + 0.1) { vic.slamAt = t; const D = vic.feat[0];
    vicV.set(D.x + Math.sin(D.yaw) * 0.3, D.y + 0.05, D.z + Math.cos(D.yaw) * 0.3).project(vicCam); const ux = vicV.x * 0.5 + 0.5, uy = vicV.y * 0.5 + 0.5;
    vicU.uShock.value.set(ux, uy, t, 1); vicU.uSplat.value.set(vicU.uCen.value.x, vicU.uCen.value.y + 0.07, t, land ? 0.62 : 0.48); // (the splat bursts out round it, the ring from its hand)
    AU.slam(); AU.splat(1.4); AU.vox('hyah'); buzz([45]); }
  vicU.uFlash.value = vic.slamAt && !reduceMotion ? 0.2 * Math.pow(Math.max(0, 1 - (t - vic.slamAt) / 0.14), 2) : 0;
  if (t > 9) endVictory();
}
"""

SD_WORDS = r"""// the victory screen's words for a Showdown (v274: a kicker, the name, the stats)
function sdVicWords(info, feat, me) {
  const duo = info.mode === 'duo', inWin = info.winners.includes(P), name = duo || info.draw ? feat.map(sdName).join(' & ') : sdName(feat[0]);
  const k = feat.reduce((s, D) => s + (info.kos[D.team] || 0), 0), hp = feat.reduce((s, D) => s + (info.hearts[D.team] || 0), 0), clk = vicStat(vicClock(info.time || 0), '', 'Time', false);
  if (info.draw) return { kick: info.timeUp ? 'Dead even' : 'Out together', name, ghost: '', stats: vicStat(k, '', k === 1 ? 'KO' : 'KOs', true) + clk };
  return { kick: inWin ? (duo ? 'Your team wins' : 'Last one standing') : 'Winner', name, ghost: '1', stats: vicStat(k, '', k === 1 ? 'KO' : 'KOs', true) + vicStat(hp, '', hp === 1 ? 'Heart left' : 'Hearts left', false) + clk };
}
"""

MARKUP_OLD_START = """  <section class="victory" id="victory" hidden aria-live="polite">
    <div class="vrib" aria-hidden="true"></div>"""
MARKUP_NEW = """  <section class="victory" id="victory" hidden aria-live="polite">
    <p class="vmeta" id="vStage"></p>
    <div class="vkick" id="vKick"><i class="vkb" aria-hidden="true"></i><span id="vTagTxt">Winner</span></div>
    <h2 class="vsr" id="vName"></h2>
    <div class="vpanel" id="vPanel">
      <div class="vstats" id="vStats"></div>
      <div class="vranks" id="vCards"></div>
      <div class="vgo"><span id="vTap">Tap to see the canvas</span><i class="vbar" aria-hidden="true"></i></div>
    </div>
  </section>
"""

CSS = """
/* (v274) the victory screen as a fight poster: the backdrop and the name are drawn in 3D underneath; these are the words over them */
#victory{display:block;padding:0;--vc:#E3122F;--vc-hi:#FF6A7F;--vbone:#F5F0E8;--vdim:rgba(245,240,232,.56)}
#victory .vsr{position:absolute;width:1px;height:1px;margin:-1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
#victory .vmeta{position:absolute;left:18px;top:max(18px,calc(env(safe-area-inset-top) + 12px));margin:0;display:flex;align-items:center;gap:10px;font:600 13px/1 var(--font-cond);letter-spacing:.26em;text-transform:uppercase;color:var(--vdim);white-space:nowrap;animation:vfade .5s .3s both}
#victory .vmeta::before{content:"";width:22px;height:2px;background:var(--vc-hi)}
#victory .vkick{position:absolute;left:16px;top:60px;display:flex;align-items:center;gap:10px;font:italic 800 23px/1 var(--font-cond);letter-spacing:.05em;text-transform:uppercase;color:var(--vbone);white-space:nowrap;animation:vkick .5s .55s cubic-bezier(.2,.9,.25,1) both}
#victory .vkb{width:13px;height:13px;flex:none;background:var(--vc-hi);transform:skewX(-14deg)}
#victory .vpanel{position:absolute;left:18px;right:18px;bottom:max(16px,calc(env(safe-area-inset-bottom) + 8px));display:flex;flex-direction:column;gap:16px}
#victory .vstats{position:relative;display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);padding-top:13px;border-top:1px solid rgba(245,240,232,.16)}
#victory .vstats::before{content:"";position:absolute;left:0;top:-2px;width:40px;height:3px;background:var(--vc-hi)}
#victory .vst{display:flex;flex-direction:column;gap:6px;min-width:0;padding:0 12px;border-left:1px solid rgba(245,240,232,.12);animation:vup .5s cubic-bezier(.2,.9,.25,1) both}
#victory .vst:first-child{padding-left:0;border-left:0}
#victory .vst b{font:italic 800 46px/.84 var(--font-cond);color:var(--vbone);font-variant-numeric:tabular-nums;letter-spacing:-.01em;white-space:nowrap}
#victory .vst b small{margin-left:2px;font-size:.5em;color:var(--vdim)}
#victory .vst span{font:800 10px/1.15 var(--font-ui);letter-spacing:.17em;text-transform:uppercase;color:var(--vdim)}
#victory .vst.hi b{color:var(--vc-hi)}
#victory .vranks{display:flex;flex-direction:column}
#victory .vranks:empty{display:none}
#victory .vrow{display:grid;grid-template-columns:32px 30px minmax(0,1fr) auto;align-items:center;gap:10px;height:38px;border-top:1px solid rgba(245,240,232,.09);animation:vup .45s cubic-bezier(.2,.9,.25,1) both}
#victory .vrow:last-child{border-bottom:1px solid rgba(245,240,232,.09)}
#victory .vrow .vr{font:italic 800 19px/1 var(--font-cond);color:var(--vdim);font-variant-numeric:tabular-nums}
#victory .vrow .bico{width:28px;height:28px;border-width:2px;border-color:rgba(0,0,0,.55)}
#victory .vrow .vn{min-width:0;font:800 14px/1 var(--font-ui);color:var(--vbone);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#victory .vrow .vn em{margin-left:8px;padding:2px 5px;font:800 9px/1 var(--font-ui);letter-spacing:.14em;font-style:normal;text-transform:uppercase;color:#120D18;background:var(--cc);border-radius:2px;vertical-align:2px}
#victory .vrow .vp{font:italic 700 21px/1 var(--font-cond);color:var(--cc);font-variant-numeric:tabular-nums}
#victory .vrow .vp small{margin-left:3px;font-size:.62em;letter-spacing:.06em;color:var(--vdim)}
#victory .vgo{position:relative;display:flex;justify-content:center;padding:2px 0 8px;animation:vfade .5s 1.5s both}
#victory .vgo span{font:600 12px/1 var(--font-cond);letter-spacing:.32em;text-transform:uppercase;color:var(--vdim)}
#victory .vbar{position:absolute;left:0;right:0;bottom:0;height:2px;background:rgba(245,240,232,.1);overflow:hidden}
#victory .vbar::after{content:"";position:absolute;inset:0;background:var(--vc-hi);transform-origin:left;animation:vbar 7.5s 1.5s linear both}
#victory.land .vmeta{left:max(28px,calc(env(safe-area-inset-left) + 8px))}
#victory.land .vkick{left:max(26px,calc(env(safe-area-inset-left) + 6px))}
#victory.land .vpanel{left:auto;right:max(28px,calc(env(safe-area-inset-right) + 10px));top:50%;bottom:auto;width:min(36%,360px);transform:translateY(-44%);gap:14px}
#victory.land .vst b{font-size:40px}
#victory.land .vrow{height:34px}
@keyframes vkick{from{opacity:0;clip-path:inset(0 100% 0 0);transform:translateX(-18px)}to{clip-path:inset(0 -20% 0 0)}}
@keyframes vup{from{opacity:0;transform:translateY(14px)}}
@keyframes vfade{from{opacity:0}}
@keyframes vbar{from{transform:scaleX(0)}}
@media (prefers-reduced-motion:reduce){#victory .vmeta,#victory .vkick,#victory .vst,#victory .vrow,#victory .vgo,#victory .vbar::after{animation:none}}
"""

def apply(s):
    s = face(s); s = rig(s)
    # the font: Barlow Condensed for the poster's words (the iOS app carries its own copy)
    s = rep(s, '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bowlby+One&family=Figtree:wght@600;700;800;900&display=swap">',
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,600;1,700;1,800;1,900&family=Bowlby+One&family=Figtree:wght@600;700;800;900&display=swap">')
    s = rep(s, '  --font-ui:"Figtree",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;\n', '  --font-ui:"Figtree",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;\n  --font-cond:"Barlow Condensed","Arial Narrow","Roboto Condensed",sans-serif;\n')
    s = rep(s, "<h3>Type</h3><p>Bowlby One and Figtree (SIL Open Font License)</p>", "<h3>Type</h3><p>Bowlby One, Figtree and Barlow Condensed (SIL Open Font License)</p>")
    # the markup and its style
    i = s.index(MARKUP_OLD_START); j = s.index('  </section>\n', i) + len('  </section>\n'); s = s[:i] + MARKUP_NEW + s[j:]
    s = rep(s, "/* the victory screen: the winner big over a burst of speed lines", CSS.lstrip('\n') + "/* the victory screen: the winner big over a burst of speed lines")
    # the backdrop, the name, the screen's run
    s = region(s, "const VIC_FS = `", "const vicBg = new THREE.Scene()", VIC_FS)
    s = region(s, "function vicName(name) {", "// a splat bursting behind an element", "")
    s = region(s, "function vicTag(t, dot) {", "function restoreVictory() {", VIC_JS)
    s = region(s, "// the victory screen's words for a Showdown\nfunction sdVicWords(info, feat, me) {", "const sdCardStat = ", SD_WORDS)
    s = rep(s, "lookRoot(D).visible = s0.vis; vicLayer(D, false); }\n  vic = null;", "lookRoot(D).visible = s0.vis; vicLayer(D, false); D.ip = s0.ip; }\n  vic = null;")
    # the light for it: the key hard from the side, less fill, a rim of its color from behind
    s = rep(s, "  const hi = hemi.intensity, si = sun.intensity; keySave.copy(sun.color); hemi.intensity = Math.max(hi, 0.85 * LIGHT_K); sun.intensity = Math.max(si, 0.95 * LIGHT_K); sun.color.copy(vicKey);\n"
            "  const ac = renderer.autoClear; renderer.autoClear = false; renderer.clearDepth(); renderer.render(scene, vicCam); renderer.autoClear = ac;\n"
            "  hemi.intensity = hi; sun.intensity = si; sun.color.copy(keySave);",
            "  const hi = hemi.intensity, si = sun.intensity; keySave.copy(sun.color); hemi.intensity = 0.55 * LIGHT_K; sun.intensity = 1.2 * LIGHT_K; sun.color.copy(vicKey); vicRim.intensity = 2.4 * LIGHT_K; // (v274: hard from the side, a rim behind)\n"
            "  const ac = renderer.autoClear; renderer.autoClear = false; renderer.clearDepth(); renderer.render(scene, vicCam); renderer.autoClear = ac;\n"
            "  hemi.intensity = hi; sun.intensity = si; sun.color.copy(keySave); vicRim.intensity = 0;")
    # its shaders made at load on every device now (the rim light is only in this pass)
    s = rep(s, "  if (post) try { const ds = [P, H, H2, H3]; for (const D of ds) vicLayer(D, true);", "  try { const ds = [P, H, H2, H3]; for (const D of ds) vicLayer(D, true);")
    return s
