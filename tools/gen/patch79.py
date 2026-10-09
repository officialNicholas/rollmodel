import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# ---------- markup ----------
rep("""    <div class="row"><button class="btn" id="replayBtn" type="button">Same canvas</button><button class="btn" id="menuBtn" type="button">Menu</button></div>
  </section>
</div>""", """    <div class="row"><button class="btn" id="replayBtn" type="button">Same canvas</button><button class="btn" id="menuBtn" type="button">Menu</button></div>
  </section>

  <section class="victory" id="victory" hidden aria-live="polite">
    <div class="vtop"><b class="vplace" id="vPlace">1<small>st</small></b><span class="vtag" id="vTag">Winner</span></div>
    <div class="vfoot">
      <h2 class="vname" id="vName"></h2>
      <p class="vsub" id="vSub"></p>
      <div class="vcards" id="vCards"></div>
      <p class="vtap" id="vTap">Tap to see your canvas</p>
    </div>
  </section>
</div>""")

# ---------- style ----------
rep("""@media (prefers-reduced-motion:reduce){""", """/* the victory screen: the winner big over a burst of speed lines (drawn in 3D underneath), its name huge across the bottom */
.victory{position:absolute;inset:0;z-index:10;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;padding:max(18px,calc(env(safe-area-inset-top) + 12px)) 18px max(16px,env(safe-area-inset-bottom));overflow:hidden;cursor:pointer;-webkit-tap-highlight-color:transparent;--vc:var(--ink)}
.victory.out{animation:vicout .32s ease-in forwards;pointer-events:none}
@keyframes vicout{to{opacity:0;transform:scale(1.06)}}
.vtop{display:flex;align-items:flex-end;gap:12px;padding-right:56px}
.vplace{font:400 clamp(70px,22vw,132px)/.82 var(--font-display);color:var(--gold);text-shadow:var(--o4),0 8px 0 var(--outline);transform:rotate(-7deg);transform-origin:left bottom;animation:vplace .55s .3s cubic-bezier(.3,1.6,.45,1) both}
.vplace small{font-size:.4em;margin-left:.05em;vertical-align:.95em}
.vplace.word{font-size:clamp(46px,14vw,84px)}
@keyframes vplace{0%{opacity:0;transform:translateX(-60px) rotate(-30deg) scale(.4)}100%{opacity:1}}
.vtag{margin-bottom:.7em;font:800 17px/1 var(--font-ui);padding:8px 14px;border-radius:99px;background:var(--glass);border:3px solid var(--line);box-shadow:0 3px 0 var(--line);color:var(--white);white-space:nowrap;animation:vrise .4s .55s cubic-bezier(.3,1.5,.5,1) both}
@keyframes vrise{from{opacity:0;transform:translateY(16px)}}
.vfoot{display:flex;flex-direction:column;align-items:flex-start}
.vname{margin:0 0 0 2px;display:flex;flex-direction:column;align-items:flex-start;font:400 100px/.88 var(--font-display);color:var(--white);letter-spacing:-.01em;transform:rotate(-4deg);transform-origin:left bottom}
.vname .ln{display:block;white-space:nowrap}
.vname i{display:inline-block;font-style:normal;text-shadow:var(--o4),.06em .08em 0 var(--vc),calc(.06em + 3px) calc(.08em + 4px) 0 var(--outline);animation:vslam .44s cubic-bezier(.2,1.6,.4,1) both}
@keyframes vslam{0%{opacity:0;transform:translateY(-.4em) scale(2.4)}55%{opacity:1}100%{transform:none}}
.vsub{margin:14px 0 0;font:800 18px/1.2 var(--font-ui);color:var(--white);padding:8px 14px;border-radius:14px;background:var(--glass);border:3px solid var(--line);box-shadow:0 3px 0 var(--line);animation:vrise .4s .95s cubic-bezier(.3,1.5,.5,1) both}
.vsub b{font:400 1.25em/1 var(--font-display);color:var(--vc-hi,var(--gold))}
.vcards{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
.vcards:empty{display:none}
.vcard{display:grid;grid-template-columns:auto 40px auto;align-items:center;gap:8px;padding:7px 14px 7px 8px;background:var(--glass);border:3px solid var(--line);border-radius:16px;box-shadow:0 4px 0 var(--line);animation:vrise .4s cubic-bezier(.3,1.5,.5,1) both}
.vcard .vrank{font:400 26px/1 var(--font-display);color:var(--bone);text-shadow:var(--o2);min-width:.8em;text-align:center}
.vcard svg{width:40px;height:37px;display:block}
.vcard .vcn{display:block;font:800 14px/1.1 var(--font-ui);color:var(--muted);white-space:nowrap;max-width:9.5em;overflow:hidden;text-overflow:ellipsis}
.vcard .vcp{display:block;margin-top:3px;font:400 22px/1 var(--font-display);color:var(--cc)}
.vcard.me{border-color:var(--bone)}
.vtap{align-self:center;margin:14px 0 0;font:800 15px/1 var(--font-ui);color:var(--white);opacity:0;text-shadow:0 2px 0 var(--outline);animation:vtap 1.6s 1.9s ease-in-out infinite}
@keyframes vtap{0%,100%{opacity:.35}50%{opacity:1}}
@media (min-width:700px) and (min-aspect-ratio:1/1){
  .victory{padding:max(28px,env(safe-area-inset-top)) clamp(28px,5vw,64px) 28px}
  .vfoot{max-width:56%}
  .vtap{align-self:flex-start}
}
@media (prefers-reduced-motion:reduce){""")
rep("""  .threat.on,.threatArrow i{animation:none}""", """  .threat.on,.threatArrow i{animation:none}
  .vplace,.vtag,.vname i,.vsub,.vcard,.victory.out{animation:none}
  .vtap{animation:none;opacity:.8}""")

# ---------- the 3D side: a speed-line burst drawn first, then just the winner on its own layer ----------
rep("// ---------- your painting: a top-down snapshot of the canvas ----------", r"""// ---------- the victory screen ----------
const VIC_FS = `uniform float uTime, uK; uniform vec3 uA, uB, uC; uniform vec2 uRes, uCen; varying vec2 vUv;
float h1(float n){ return fract(sin(n * 91.345) * 47453.5453); }
float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
void main(){
  vec2 p = (vUv - uCen) * vec2(uRes.x / uRes.y, 1.0);
  float r = length(p), a = atan(p.y, p.x) + uTime * 0.035;
  vec3 col = mix(uB, uA, smoothstep(1.25, 0.05, r));
  col = mix(col, uC, smoothstep(0.42, 0.0, r) * 0.85);
  // speed lines: strips of different widths and shades, streaming out from behind the winner
  float f = a / 6.2831853 * 64.0, id = floor(f), u = fract(f) - 0.5;
  float q = h1(id), q2 = h1(id + 17.3), w = (0.05 + 0.33 * q2) * (0.3 + 0.7 * smoothstep(0.05, 0.95, r));
  float line = smoothstep(w, w * 0.35, abs(u));
  float flow = fract(r * (0.55 + q) - uTime * (0.6 + 1.4 * q) + q2 * 7.0);
  float dash = smoothstep(0.0, 0.07, flow) * smoothstep(0.78 + 0.18 * q, 0.5, flow);
  float m = line * dash * smoothstep(0.1 + 0.22 * q2, 0.32 + 0.3 * q2, r) * uK;
  vec3 lc = q > 0.64 ? vec3(1.0) : q < 0.24 ? vec3(0.03, 0.01, 0.07) : mix(uA, vec3(1.0), 0.5);
  col = mix(col, lc, m * (q > 0.64 ? 0.9 : q < 0.24 ? 0.8 : 0.55));
  // sparkles flying outward
  vec2 g = vec2(a * 10.0, r * 7.0 - uTime * 2.4), gi = floor(g), gf = fract(g) - 0.5; float hs = h2(gi);
  col += step(0.87, hs) * smoothstep(0.13, 0.0, length(gf * vec2(1.0, 0.55))) * (0.55 + 0.45 * sin(uTime * 9.0 + hs * 40.0)) * smoothstep(0.12, 0.5, r) * uK;
  col *= 1.0 - 0.5 * smoothstep(0.75, 1.7, r);
  gl_FragColor = vec4(mix(vec3(1.0), col, smoothstep(0.0, 0.5, uK)), 1.0);
}`;
const vicU = { uTime: { value: 0 }, uK: { value: 0 }, uA: { value: new THREE.Color() }, uB: { value: new THREE.Color() }, uC: { value: new THREE.Color() }, uRes: { value: new THREE.Vector2(1, 1) }, uCen: { value: new THREE.Vector2(0.5, 0.62) } };
const vicBg = new THREE.Scene(), vicBgCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
vicBg.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({ uniforms: vicU, depthTest: false, depthWrite: false, vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }', fragmentShader: VIC_FS })));
const vicCam = new THREE.PerspectiveCamera(32, 1, 0.05, 80); vicCam.layers.set(2);
hemi.layers.enable(2); sun.layers.enable(2);
const lookRoot = D => D === P ? drop : D.look.drop;
const vicLayer = (D, on) => lookRoot(D).traverse(o => { if (o.material && o.material.depthFunc === THREE.GreaterDepth) return; if (on) o.layers.enable(2); else o.layers.disable(2); });
const vicEl = $('victory'), vicMeasure = document.createElement('canvas').getContext('2d');
let vic = null, endImg = null;
const hexCss = c => '#' + c.toString(16).padStart(6, '0');
const blobSVG = c => '<svg viewBox="0 0 48 44" aria-hidden="true"><path d="M24 3.5C36 3.5 44.5 13 44.5 25C44.5 36 35.5 41.5 24 41.5C12.5 41.5 3.5 36 3.5 25C3.5 13 12 3.5 24 3.5Z" fill="' + c + '" stroke="#0C0620" stroke-width="3"/><path d="M12.5 14C15.5 10.6 19 9 22.6 8.6" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="3.2" stroke-linecap="round"/><ellipse cx="17.5" cy="23" rx="4.6" ry="6" fill="#fff" stroke="#0C0620" stroke-width="2"/><ellipse cx="30.5" cy="23" rx="4.6" ry="6" fill="#fff" stroke="#0C0620" stroke-width="2"/><circle cx="18.3" cy="24.4" r="2.4" fill="#0C0620"/><circle cx="31.3" cy="24.4" r="2.4" fill="#0C0620"/></svg>';
// the big name: one line per word, sized to fit the screen, letters slamming down one after another
function vicName(name) {
  const el = $('vName'), words = name.toUpperCase().split(' ').filter(Boolean), land = viewW / viewH > 1.05 && viewW >= 700;
  const lines = []; for (const w of words) { if (lines.length && (lines[lines.length - 1] + ' ' + w).length <= 6) lines[lines.length - 1] += ' ' + w; else lines.push(w); }
  vicMeasure.font = '400 100px "Bowlby One", "Arial Black", sans-serif';
  const widest = Math.max(...lines.map(l => vicMeasure.measureText(l).width)) || 100, maxW = (land ? viewW * 0.5 : viewW - 36) - 24;
  el.style.fontSize = clamp(Math.floor(100 * maxW / widest), 40, land ? 150 : 132) + 'px';
  let h = '', k = 0; for (const l of lines) { h += '<span class="ln">'; for (const ch of l) h += ch === ' ' ? ' ' : '<i style="animation-delay:' + (0.48 + 0.055 * k++).toFixed(3) + 's">' + ch.replace(/&/g, '&amp;') + '</i>'; h += '</span>'; }
  el.innerHTML = h; el.setAttribute('aria-label', name);
}
function startVictory() {
  const info = endInfo, solo = info.mode === 'solo', board = ACTIVE.map(D => ({ D, pct: Math.round(teamCov(D.team)) })).sort((a, b) => b.pct - a.pct);
  for (const e of board) e.place = 1 + board.filter(o => o.pct > e.pct).length;
  let feat;
  if (solo || info.winner) feat = [solo ? P : info.winner];
  else { const tie = board.find(e => e.D !== P && e.pct === Math.round(info.you)); feat = tie ? [P, tie.D] : [P]; }
  const happy = solo ? info.newBest : !!info.winner, lead = feat[0], col = new THREE.Color(TEAMS[lead.team].wet);
  vic = { t: 0, feat, happy, yaw: camYaw + Math.PI + 0.35, saved: feat.map(D => ({ D, x: D.x, y: D.y, z: D.z, yaw: D.yaw, st: D.st, paint: D.paint, vis: lookRoot(D).visible })) };
  // the featured blobs, awake and full, on their marks (side by side for a draw)
  const bx = lead.x, bz = lead.z, by = Math.max(0, surfaceUnder(bx, bz, lead.y + 2, true)), rx = Math.cos(vic.yaw), rz = -Math.sin(vic.yaw);
  feat.forEach((D, i) => {
    const off = feat.length > 1 ? (i ? 0.62 : -0.62) : 0;
    Object.assign(D, { x: bx + rx * off, z: bz + rz * off, y: by, yaw: vic.yaw + (feat.length > 1 ? (i ? -0.25 : 0.25) : 0), st: 'play', paint: 1, giantT: 0, slam: false, missile: false, charging: false, flatT: 0, stunT: 0, rollT: 0, immuneT: 0, air: false, vy: 0, exposed: false, dry: false, dilT: 0, spd: 0, turn: 0, squash: 0, wob: 0 });
    lookRoot(D).visible = true; vicLayer(D, true);
  });
  vicU.uA.value.copy(col); vicU.uB.value.copy(col).multiplyScalar(0.3); vicU.uC.value.copy(col).lerp(COL_WHITE, 0.62); vicU.uK.value = 0;
  // the words
  vicEl.style.setProperty('--vc', hexCss(TEAMS[lead.team].wet)); vicEl.style.setProperty('--vc-hi', lead === P ? 'var(--ink-hi)' : lead === H ? 'var(--holy-hi)' : 'var(--wolf-hi)');
  const pl = $('vPlace'), me = board.find(e => e.D === P);
  if (solo) { pl.className = 'vplace word'; pl.textContent = Math.round(info.you) + '%'; $('vTag').textContent = info.newBest ? 'New best!' : "Time's up"; vicName(playerName()); $('vSub').innerHTML = info.newBest ? (info.prevBest ? 'Old best ' + info.prevBest + '%' : 'Your first canvas') : 'Your best is <b>' + info.best + '%</b>'; }
  else if (feat.length > 1 || !info.winner) { pl.className = 'vplace word'; pl.textContent = 'Draw'; $('vTag').textContent = 'Dead even'; vicName(feat.length > 1 ? playerName() + ' & ' + nameOf(feat[1]) : playerName()); $('vSub').innerHTML = '<b>' + me.pct + '%</b> each'; }
  else { pl.className = 'vplace'; pl.innerHTML = '1<small>st</small>'; $('vTag').textContent = lead === P ? 'Winner!' : me.place === 2 ? 'You came 2nd' : 'You came ' + me.place + (me.place === 3 ? 'rd' : 'th'); vicName(nameOf(lead)); $('vSub').innerHTML = '<b>' + board[0].pct + '%</b> of the canvas'; }
  $('vCards').innerHTML = solo ? '' : board.filter(e => !feat.includes(e.D)).map((e, i) => '<div class="vcard' + (e.D === P ? ' me' : '') + '" style="--cc:' + (e.D === P ? 'var(--ink-hi)' : e.D === H ? 'var(--holy-hi)' : 'var(--wolf-hi)') + ';animation-delay:' + (1.15 + i * 0.12).toFixed(2) + 's"><b class="vrank">' + e.place + '</b>' + blobSVG(hexCss(TEAMS[e.D.team].wet)) + '<span><span class="vcn">' + nameOf(e.D) + '</span><b class="vcp">' + e.pct + '%</b></span></div>').join('');
  $('vTap').textContent = 'Tap to see the canvas';
  vicEl.classList.remove('out'); vicEl.hidden = false; flashScreen();
  hud.classList.add('off'); hintEl.classList.remove('on'); bannerEl.classList.remove('on'); $('vig').className = 'vig';
  const id = runId;
  AU.whoosh(); setTimeout(() => { if (vic && id === runId) { AU.splat(1.2); buzz(20); } }, 520);
  setTimeout(() => { if (!vic || id !== runId) return; if (happy) { AU.fanfare(); buzz([30, 40, 30]); } else if (!info.winner) AU.draw(); else AU.lose(); }, 640);
}
// each featured blob drops in, splats down, then bounces (and every so often spins, if it's happy)
function vicPose(i, t) {
  const tt = t - 0.1 - i * 0.14; let hop = 0, sq = 0, rise = 0, spin = 0;
  if (tt < 0) hop = 6;
  else if (tt < 0.4) { const u = tt / 0.4; hop = 4.2 * (1 - u * u); }
  else if (tt < 0.78) { const u = (tt - 0.4) / 0.38; sq = 0.95 * Math.pow(1 - u, 1.7); hop = u > 0.32 ? Math.sin((u - 0.32) / 0.68 * Math.PI) * 0.24 : 0; }
  else { const c = (tt - 0.78) % 2.7;
    if (vic.happy && c < 0.64) { const u = c / 0.64; hop = Math.sin(u * Math.PI) * 0.6; spin = (1 - Math.cos(u * Math.PI)) * Math.PI; sq = u > 0.88 ? (u - 0.88) * 3 : 0; rise = u < 0.45 ? 0.6 : 0; }
    else { const ph = (c * (vic.happy ? 1.8 : 1.1)) % 1; hop = ph < 0.36 ? Math.sin(ph / 0.36 * Math.PI) * (vic.happy ? 0.16 : 0.07) : 0; sq = ph >= 0.36 && ph < 0.52 ? (1 - (ph - 0.36) / 0.16) * 0.3 : 0; } }
  return { hop, sq, rise, spin };
}
function vicFrame(rdt) {
  vic.t += rdt; const t = vic.t, W = viewW, Hh = viewH, land = W / Hh > 1.05 && W >= 700;
  vic.feat.forEach((D, i) => { D.vicPose = vicPose(i, t); });
  vicU.uTime.value = clock; vicU.uK.value = clamp((t - 0.05) / 0.35, 0, 1); vicU.uRes.value.set(W, Hh);
  const cx = land ? 0.66 : 0.5, cy = land ? 0.44 : 0.36; vicU.uCen.value.set(cx, 1 - cy);
  const fov = land ? 27 : 33; if (vicCam.fov !== fov || Math.abs(vicCam.aspect - W / Hh) > 1e-4) { vicCam.fov = fov; vicCam.aspect = W / Hh; vicCam.updateProjectionMatrix(); }
  vicCam.setViewOffset(W, Hh, (0.5 - cx) * W, (0.5 - cy) * Hh, W, Hh);
  let mx = 0, mz = 0, my = 0; for (const D of vic.feat) { mx += D.x; mz += D.z; my += D.y; } const n = vic.feat.length; mx /= n; mz /= n; my /= n;
  const dist = (n > 1 ? 3.9 : 2.45) * (land ? 1.12 : 1) * (1.07 - 0.07 * Math.min(1, t / 4)), a = vic.yaw + Math.sin(t * 0.4) * 0.05;
  vicCam.position.set(mx + Math.sin(a) * dist, my + 0.3, mz + Math.cos(a) * dist); vicCam.lookAt(mx, my + 0.44, mz);
  if (t > 9) endVictory();
}
function restoreVictory() {
  for (const s0 of vic.saved) { const D = s0.D; Object.assign(D, { x: s0.x, y: s0.y, z: s0.z, yaw: s0.yaw, st: s0.st, paint: s0.paint }); D.vicPose = null; lookRoot(D).visible = s0.vis; vicLayer(D, false); }
  vic = null;
}
function endVictory() {
  if (!vic || vic.t < 0.8) return;
  restoreVictory(); vicEl.classList.add('out'); setTimeout(() => { if (!vic) vicEl.hidden = true; }, 330); flashScreen(); AU.whoosh();
  outro = true; outroT = 0; const id = runId;
  if (endInfo && (endInfo.mode === 'solo' ? endInfo.newBest : endInfo.win > 0)) confetti(P.x, P.y + 1, P.z, 110, 5);
  setTimeout(() => { if (id === runId && state === 'dead') showEnd(endImg); }, 650);
}
function abortVictory() { if (vic) restoreVictory(); vicEl.hidden = true; vicEl.classList.remove('out'); }
vicEl.addEventListener('click', () => { AU.init(); endVictory(); });
function renderVictory() {
  renderer.setRenderTarget(null); renderer.render(vicBg, vicBgCam);
  const ac = renderer.autoClear; renderer.autoClear = false; renderer.clearDepth(); renderer.render(scene, vicCam); renderer.autoClear = ac;
}

// ---------- your painting: a top-down snapshot of the canvas ----------""")

# draw it
rep("function renderFrame() {\n", "function renderFrame() {\n  if (vic) return renderVictory();\n")
# poses drive the featured blobs, and their faces are happy
rep("  U.gSquash.value = sq; U.gRise.value = rise;", "  if (vic && D.vicPose) { const vp = D.vicPose; hop = vp.hop; sq = vp.sq; rise = vp.rise; spinY = vp.spin; }\n  U.gSquash.value = sq; U.gRise.value = rise;")
rep("  const happy = P.st === 'hide' || celebrating || menuReact > 0,", "  const happy = P.st === 'hide' || celebrating || menuReact > 0 || !!(vic && vic.happy && P.vicPose),")
# the camera, poses and burst tick with the visuals
rep("  // camera\n  if (state === 'menu') {", "  if (vic) vicFrame(rdt);\n  // camera\n  if (state === 'menu') {")

# ---------- the end of a match: "Time!", then the victory screen, then the canvas ----------
rep("""  const [a, b] = fmtPair(you, cpu);
  if (mode === 'solo') banner(newBest ? 'New best!' : 'Time!', a + ' covered', true);
  else banner(win > 0 ? 'You win!' : win < 0 ? nameOf(winner) + ' wins' : 'Draw', mode === 'trio' ? a + ' / ' + b + ' / ' + Math.round(cpu2) + '%' : a + ' vs ' + b, true);
  if (mode === 'solo' ? newBest : win > 0) { celebrating = true; setTimeout(() => AU.fanfare(), 350); confetti(P.x, P.y + 1, P.z, 130, 5); flashScreen(); buzz([30, 40, 30]); }
  else { buzz([40, 30, 60]); setTimeout(() => { if (id === runId) win < 0 ? AU.lose() : AU.draw(); }, 350); }
  setTimeout(() => { if (id !== runId) return; outro = true; hud.classList.add('off'); hintEl.classList.remove('on'); $('vig').className = 'vig'; }, 1300);
  setTimeout(() => { if (id !== runId) return; let img = null; try { img = snapshotPainting(); } catch (e) { img = null; } showEnd(img); }, 2700);""",
"""  banner(mode === 'solo' ? "Time's up!" : 'Time!', '', false); buzz([40, 30, 40]); slow = 0.6;
  if (mode === 'solo' ? newBest : win > 0) celebrating = true;
  setTimeout(() => { if (id !== runId || state !== 'dead') return; endImg = null; try { endImg = snapshotPainting(); } catch (e) { endImg = null; } startVictory(); }, 1450);""")
rep("function resetRun() {\n  runId++;", "function resetRun() {\n  abortVictory(); runId++;")
# keys move the victory along too
rep("  if (!nameModal.hidden) { if (e.key === 'Escape') { e.preventDefault(); closeName(); } return; }",
    "  if (!nameModal.hidden) { if (e.key === 'Escape') { e.preventDefault(); closeName(); } return; }\n  if (vic) { if (e.key === ' ' || e.key === 'Enter' || e.key === 'Escape') { e.preventDefault(); endVictory(); } return; }")
open(F, 'w').write(s)
print('ok')
