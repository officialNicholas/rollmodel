#!/usr/bin/env python3
"""The fight card (Smash style columns), paint around the screen edges, a faster matte in the intro, an eased camera turn, a clearer picker. On top of ui6_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui6_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CSS = '''
/* ===== the fight card: one column per blob, even, each in its color ===== */
.vsx{display:block}
.vsx::before,.vsx .vband.top{display:none}
.vsrow{position:absolute;inset:0;display:flex;align-items:stretch;gap:0;padding:0;width:auto}
.vcol{position:relative;flex:1;min-width:0;overflow:hidden;background:linear-gradient(180deg,var(--sc) 0%,var(--cd) 100%);animation:colin .5s cubic-bezier(.2,1.2,.35,1) both}
.vcol.foe{animation-delay:.08s}
.vcol.foe2{animation-delay:.16s}
.vcol+.vcol{box-shadow:-4px 0 0 var(--cream),-9px 0 14px rgba(0,0,0,.35)}
@keyframes colin{from{transform:translateY(-100%)}}
.vcol::before{content:"";position:absolute;inset:0;background:url(art/m_flecks.webp) center/320px;opacity:.16;mix-blend-mode:multiply;pointer-events:none}
.vcol::after{content:"";position:absolute;left:-34%;right:-34%;top:14%;bottom:-12%;background:var(--cd);-webkit-mask:url(art/m_splat2.webp) center/contain no-repeat;mask:url(art/m_splat2.webp) center/contain no-repeat;opacity:.55;transform:rotate(-14deg);pointer-events:none}
.vcol.foe::after{transform:rotate(12deg) scaleX(-1)}
.vhead{position:relative;z-index:2;min-height:62px;padding:8px 8px 7px;background:rgba(23,19,32,.94);display:grid;align-content:center;justify-items:center;text-align:center;box-shadow:0 4px 0 rgba(0,0,0,.25)}
.vhead small{font:800 10px/1 var(--font-ui);letter-spacing:.22em;text-transform:uppercase;color:var(--sc);margin-bottom:4px}
.vhead b{display:block;max-width:100%;font:900 clamp(18px,7vw,34px)/1 var(--font-head);font-style:italic;text-transform:uppercase;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-shadow:.05em .05em 0 var(--black)}
.vsrow.trio .vhead b{font-size:clamp(13px,4.6vw,26px)}
.vcol .vbox{position:absolute;left:50%;top:50%;width:150%;max-width:none;aspect-ratio:5/6;transform:translate(-50%,-44%);z-index:1;animation:figin .6s .18s cubic-bezier(.2,1.2,.35,1) both}
.vsrow.trio .vcol .vbox{width:170%}
.vcol .vbox::before,.vcol .vbox::after{display:none}
.vcol .vbox canvas{filter:drop-shadow(0 18px 14px rgba(0,0,0,.5))}
@keyframes figin{from{opacity:0;transform:translate(-50%,-30%)}}
.vsx .vband.bot{z-index:2;bottom:-10%;height:26%}
.vstitle{position:absolute;left:0;right:0;bottom:4.5%;z-index:3;margin:0;padding:0 16px;font:900 clamp(16px,5vw,26px)/1.2 var(--font-head);font-style:italic;text-transform:uppercase;color:#fff;text-shadow:.05em .05em 0 var(--black);animation:fadein .4s .5s both}
.vstitle b{color:#fff}
@media (min-aspect-ratio:1/1){.vcol .vbox{width:58%;top:15%;transform:translate(-50%,0)}.vsrow.trio .vcol .vbox{width:66%;top:15%}.vhead{min-height:54px}.vhead b{font-size:clamp(18px,4.5vw,32px)}.vsx .vband.bot{bottom:-14%;height:30%}.vstitle{bottom:3%;font-size:clamp(14px,2.8vw,22px)}@keyframes figin{from{opacity:0;transform:translate(-50%,14%)}}}
.vseam{position:absolute;left:-11px;top:-2%;bottom:-2%;width:22px;z-index:4;background:#FFF6E6;clip-path:polygon(44% 0,62% 0,52% 18%,74% 31%,46% 47%,68% 63%,42% 78%,60% 100%,40% 100%,48% 82%,26% 66%,52% 50%,30% 34%,50% 19%);filter:drop-shadow(0 0 5px #fff) drop-shadow(0 0 14px rgba(255,220,120,.9));animation:seamflick 1.1s steps(3) infinite}
@keyframes seamflick{0%{opacity:1}33%{opacity:.75}66%{opacity:.95}}
.vcol .pt{position:absolute;left:var(--x);bottom:-6%;width:var(--s);height:var(--s);border-radius:50%;background:#fff;opacity:0;mix-blend-mode:screen;animation:ptrise var(--d) linear var(--w) infinite;pointer-events:none;z-index:1}
@keyframes ptrise{0%{opacity:0;transform:translateY(0) scale(.6)}12%{opacity:.9}100%{opacity:0;transform:translateY(-110vh) translateX(var(--dx)) scale(1.2)}}
.vcol .vsweep{position:absolute;inset:0;z-index:2;background:linear-gradient(115deg,transparent 30%,rgba(255,255,255,.28) 45%,rgba(255,255,255,0) 60%);transform:translateX(-120%);animation:vsweep 1.2s .35s cubic-bezier(.4,0,.2,1) both;pointer-events:none;mix-blend-mode:screen}
@keyframes vsweep{to{transform:translateX(120%)}}
.vcol .vhead::after{content:"";position:absolute;right:6px;top:6px;width:48px;height:48px;background:var(--sc);-webkit-mask:url(art/m_splat.webp) center/contain no-repeat;mask:url(art/m_splat.webp) center/contain no-repeat;opacity:.35}
/* ===== paint around the screen edges: hit in the rival's color, low on your own, heat in orange ===== */
.vig::before,.vig::after{content:"";position:absolute;inset:-5%;opacity:0;pointer-events:none;transition:opacity .25s;background:var(--vc,var(--ink));-webkit-mask:url(art/m_splat2.webp) -22% -14%/64% auto no-repeat,url(art/m_splat.webp) 118% 108%/66% auto no-repeat,url(art/m_drip.webp) 18% -4%/44% auto no-repeat,url(art/m_drip.webp) 86% -6%/36% auto no-repeat,url(art/m_splat.webp) -20% 112%/54% auto no-repeat,url(art/m_splat2.webp) 120% -10%/50% auto no-repeat;mask:url(art/m_splat2.webp) -22% -14%/64% auto no-repeat,url(art/m_splat.webp) 118% 108%/66% auto no-repeat,url(art/m_drip.webp) 18% -4%/44% auto no-repeat,url(art/m_drip.webp) 86% -6%/36% auto no-repeat,url(art/m_splat.webp) -20% 112%/54% auto no-repeat,url(art/m_splat2.webp) 120% -10%/50% auto no-repeat}
.vig::after{background:var(--hc,#2E9BFF);-webkit-mask:url(art/m_splat.webp) -20% -12%/70% auto no-repeat,url(art/m_splat2.webp) 122% -8%/62% auto no-repeat,url(art/m_splat2.webp) -24% 118%/60% auto no-repeat,url(art/m_splat.webp) 124% 120%/74% auto no-repeat,url(art/m_drip.webp) 42% -4%/40% auto no-repeat,url(art/m_splat2.webp) 50% 128%/50% auto no-repeat;mask:url(art/m_splat.webp) -20% -12%/70% auto no-repeat,url(art/m_splat2.webp) 122% -8%/62% auto no-repeat,url(art/m_splat2.webp) -24% 118%/60% auto no-repeat,url(art/m_splat.webp) 124% 120%/74% auto no-repeat,url(art/m_drip.webp) 42% -4%/40% auto no-repeat,url(art/m_splat2.webp) 50% 128%/50% auto no-repeat;transition:none}
.vig.low::before{opacity:.72;animation:edgethrob .7s ease-in-out infinite alternate}
.vig.heat::before{--vc:#FF7A1E;opacity:.85;animation:edgethrob .45s ease-in-out infinite alternate}
.vig.danger::before{opacity:0}
@keyframes edgethrob{from{opacity:.32}to{opacity:.7}}
.vig.hit{opacity:1}
.vig.hit::after{animation:hitsplat 1s ease-out both}
@keyframes hitsplat{0%{opacity:0;transform:scale(1.18)}10%{opacity:1;transform:scale(1)}55%{opacity:.9;transform:scale(1.02)}100%{opacity:0;transform:scale(1.04)}}
@media (prefers-reduced-motion:reduce){.vig::before,.vig::after{animation:none}}
/* ===== the picker: the wings stay readable, arrows step through ===== */
.world{transform:scale(.86);opacity:.85;filter:brightness(.72)}
.world[aria-pressed="true"]{transform:scale(1);opacity:1;filter:none}
@media (max-aspect-ratio:1/1){.world{width:min(62vw,300px,calc((100dvh - 430px) * 1.1));min-width:min(56vw,240px)}.gallery{padding-left:max(10vw,calc(50% - 150px));padding-right:max(10vw,calc(50% - 150px))}}
.gnav{position:absolute;top:50%;z-index:3;width:42px;height:60px;margin-top:-30px;padding:0;border:0;border-radius:3px;background:#fff url(art/m_paperbg.webp) center/300px;color:var(--black);box-shadow:3px 4px 0 rgba(0,0,0,.45);font:900 30px/1 var(--font-ui);cursor:pointer}
.gnav.prev{left:8px}.gnav.next{right:8px}
.gnav:active{transform:translate(2px,3px);box-shadow:1px 1px 0 rgba(0,0,0,.45)}
.gnav[disabled]{opacity:.3}
@media (min-aspect-ratio:1/1){.gnav{top:54%}}
.sthumb{width:78px;height:58px}
.stxt small{color:var(--ink)}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]

# ---- the fight card ----
rep("""  const card = (D, name, cls) => '<div class="vsp ' + cls + '"><span class="vbox" id="vbox' + D.team + '" style="--sc:' + TEAMS[D.team].css + '"></span><b>' + escAttr(name) + '</b>' + (cls === 'me' ? '<span class="tape">You</span>' : '') + '</div>';
  let h = card(P, playerName(), 'me'); if (mode !== 'solo') { h += '<b class="vsbig">VS</b>' + card(H, NAMES[1], 'foe'); if (mode === 'trio') h += card(H2, NAMES[2], 'foe2'); }
  $('vsRow').innerHTML = h; $('vsRow').classList.toggle('trio', mode === 'trio');""",
"""  const card = (D, name, cls) => '<div class="vcol ' + cls + '" style="--sc:' + TEAMS[D.team].css + ';--cd:' + mixHex(TEAMS[D.team].wet, 0x0C0620, 0.62) + '">' + (cls === 'me' ? '' : '<i class="vseam" aria-hidden="true"></i>') + '<i class="vsweep" aria-hidden="true"></i><div class="vhead"><small>' + (cls === 'me' ? 'You' : 'CPU') + '</small><b>' + escAttr(name) + '</b></div><span class="vbox" id="vbox' + D.team + '"></span>' + Array.from({ length: 9 }, (_, i) => '<i class="pt" style="--x:' + (6 + Math.random() * 88).toFixed(0) + '%;--s:' + (3 + Math.random() * 7).toFixed(0) + 'px;--d:' + (2.2 + Math.random() * 2.4).toFixed(2) + 's;--w:' + (-Math.random() * 4).toFixed(2) + 's;--dx:' + ((Math.random() - 0.5) * 60).toFixed(0) + 'px"></i>').join('') + '</div>';
  let h = card(P, playerName(), 'me'); if (mode !== 'solo') { h += card(H, NAMES[1], 'foe'); if (mode === 'trio') h += card(H2, NAMES[2], 'foe2'); }
  $('vsRow').innerHTML = h; $('vsRow').classList.toggle('trio', mode === 'trio');""")

# ---- each fighter at its own angle, with its own face and pose ----
rep("""  const list = [[P, $('vbox0')]]; if (mode !== 'solo') list.push([H, $('vbox1')]); if (mode === 'trio') list.push([H2, $('vbox2')]);
  for (const [D] of list) if (D !== P) { D.look.drop.visible = true; D.yaw = P.yaw; D.flatT = 0; D.stunT = 0; D.dry = false; D.vsSt = D.st; D.st = 'play'; D.ip = { hop: 0, spin: 0, pitch: 0, roll: 0, sq: null, rise: null, sink: null, coat: null, watch: null, expr: 'angry', shut: false, stars: false }; }
  vsSnap = { t: 2, list, id: runId };""", """  const list = [[P, $('vbox0'), VS_POSE.me]]; if (mode !== 'solo') list.push([H, $('vbox1'), VS_POSE.foe]); if (mode === 'trio') list.push([H2, $('vbox2'), VS_POSE.foe2]);
  for (const [D, , pose] of list) { if (D !== P) { D.look.drop.visible = true; D.yaw = P.yaw; D.flatT = 0; D.stunT = 0; D.dry = false; D.vsSt = D.st; D.st = 'play'; }
    D.vsIp = D.ip; D.ip = Object.assign({ hop: 0, spin: 0, pitch: 0, roll: 0, sq: null, rise: null, sink: null, coat: null, watch: null, expr: null, shut: false, stars: false }, pose.ip); }
  vsSnap = { t: 2, list, id: runId };""")
rep("let vsSnap = null, portRT = null;", """// the three fighters: you cocky and up on your toes from a low lens, the first rival braced and glaring, the second waving it off
const VS_POSE = { me: { yaw: 0.55, low: 1, zoom: 0.96, ip: { expr: 'glee', earUp: 1, hand: 1, hop: 0.05, roll: 0.1 } }, foe: { yaw: -0.5, low: 0.35, zoom: 0.98, ip: { expr: 'angry', brace: 1, pitch: 0.1 } }, foe2: { yaw: 0.38, low: 0.7, zoom: 0.96, ip: { expr: 'happy', wave: 1, roll: -0.12 } } };
let vsSnap = null, portRT = null;""")
rep("function portraitOf(D, W, Hh) {", "function portraitOf(D, W, Hh, o) {\n  o = o || {};")
rep("  const tv = Math.tan(portCam.fov * Math.PI / 360), d = tall / (2 * tv * 0.8), ly = tall * 0.46, fx = Math.sin(D.yaw), fz = Math.cos(D.yaw);\n  portCam.aspect = W / Hh; portCam.updateProjectionMatrix(); portCam.position.set(D.x + fx * d, ly + d * 0.2, D.z + fz * d); portCam.up.set(0, 1, 0); portCam.lookAt(D.x, ly - 0.03, D.z); portCam.updateMatrixWorld();",
    "  const tv = Math.tan(portCam.fov * Math.PI / 360), d = tall / (2 * tv * (o.zoom || 0.8)), ly = tall * 0.46, low = o.low || 0, fx = Math.sin(D.yaw + (o.yaw || 0)), fz = Math.cos(D.yaw + (o.yaw || 0));\n  portCam.aspect = W / Hh; portCam.updateProjectionMatrix(); portCam.position.set(D.x + fx * d, ly + d * (0.2 - 0.3 * low), D.z + fz * d); portCam.up.set(0, 1, 0); portCam.lookAt(D.x, ly - 0.03 + 0.1 * low, D.z); portCam.updateMatrixWorld();")
rep("  if (q.id === runId) for (const [D, el] of q.list) { if (!el) continue; const c = portraitOf(D, 600, 720); el.replaceChildren(c); }\n  for (const [D] of q.list) if (D !== P) { D.look.drop.visible = false; D.ip = null; if (D.vsSt) { D.st = D.vsSt; D.vsSt = null; } }",
    "  if (q.id === runId) for (const [D, el, pose] of q.list) { if (!el) continue; const c = portraitOf(D, 600, 720, pose); el.replaceChildren(c); }\n  for (const [D] of q.list) { D.ip = D.vsIp || null; D.vsIp = null; if (D !== P) { D.look.drop.visible = false; if (D.vsSt) { D.st = D.vsSt; D.vsSt = null; } } }")
# ---- paint on the screen edges when you're hit ----
rep("function flashScreen() {", "function hitEdge(A) { if (reduceMotion || !A || A === P) return; const v = $('vig'); v.style.setProperty('--hc', TEAMS[A.team].css); restartCls(v, 'hit'); }\nfunction flashScreen() {")
rep("  if (hearable(B)) AU.squish(); if (B === P) AU.vox('oof');", "  if (hearable(B)) AU.squish(); if (B === P) { AU.vox('oof'); hitEdge(A); }")
rep("  if (hearable(A) || hearable(B)) { AU.bonk(1); AU.pop(); } if (B === P) AU.vox('oof'); hitStop(0.07, A, B);", "  if (hearable(A) || hearable(B)) { AU.bonk(1); AU.pop(); } if (B === P) { AU.vox('oof'); hitEdge(A); } hitStop(0.07, A, B);")
rep("if (hearable(B)) { AU.shrink(); AU.bonk(1); } if (B === P) AU.vox('eep'); hitStop(0.1, A, B);", "if (hearable(B)) { AU.shrink(); AU.bonk(1); } if (B === P) { AU.vox('eep'); hitEdge(A); } hitStop(0.1, A, B);")
rep("  if (by) { by.kos++; D.kod++; emote(by, 'glee', 1.4); }", "  if (by) { by.kos++; D.kod++; emote(by, 'glee', 1.4); if (D === P) hitEdge(by); }")

# ---- the intro: the drop is itself, matte, from the count of two ----
rep("      for (const D of ACTIVE) { if (D.st === 'out' || D.pot) continue; D.fT = [1, 0.8, 0.58][n - 1]; D.fV += 3.2; D.wob = 1; }",
    "      for (const D of ACTIVE) { if (D.st === 'out' || D.pot) continue; D.fT = n === 3 ? 0.62 : 1; D.fV += 3.2; D.wob = 1; if (n <= 2 && !D.introBare) { D.introBare = true; D.ipBurst = true; } }")
rep("soaked = !ipc && ((state === 'intro' && !D.introLeap && !D.introOut && !D.introCrawl && !D.introAct) || D.st === 'hide');",
    "soaked = !ipc && ((state === 'intro' && !D.introLeap && !D.introOut && !D.introCrawl && !D.introAct && !D.introBare) || D.st === 'hide');")
rep("D.stroke++; D.wearOff = true; D.peeked = false;", "D.stroke++; D.wearOff = true; D.peeked = false; D.introBare = false;")

# ---- the camera eases into a turn (a critically damped spring on its heading) ----
rep("camYaw = 0, gyCam = 0", "camYaw = 0, camYawV = 0, gyCam = 0")
rep("    let dy = P.yaw - camTurnS * 0.085 - camYaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); camYaw += dy * (1 - Math.exp(-rdt * 6.5));",
    "    let dy = P.yaw - camTurnS * 0.085 - camYaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); [camYaw, camYawV] = sdamp(camYaw, camYaw + dy, camYawV, 0.21, Math.min(rdt, 0.05));")
rep("  camYaw = P.yaw; look.spd = 0;", "  camYaw = P.yaw; camYawV = 0; look.spd = 0;")
rep("camYaw = bestYaw; AU.flip();", "camYaw = bestYaw; camYawV = 0; AU.flip();")
rep("  camYaw = P.yaw; introCam(true);", "  camYaw = P.yaw; camYawV = 0; introCam(true);")

# ---- the picker: arrows either side, and the lobby card says what it is ----
rep('      <div class="gallery" id="stagePick" role="group" aria-labelledby="worldTitle">', '      <button class="gnav prev" id="gPrev" type="button" aria-label="Previous canvas">&#8249;</button><button class="gnav next" id="gNext" type="button" aria-label="Next canvas">&#8250;</button>\n      <div class="gallery" id="stagePick" role="group" aria-labelledby="worldTitle">')
rep("function stepWorld(dir) {", "$('gPrev').addEventListener('click', () => { AU.init(); stepWorld(-1); }); $('gNext').addEventListener('click', () => { AU.init(); stepWorld(1); });\nfunction stepWorld(dir) {")
rep('<span class="stxt"><small>Exhibition</small>', '<span class="stxt"><small>Canvas &middot; tap to change</small>')
# ---- the ring announcer counts it in and calls Go; its lines are fetched ahead so the first one lands on time ----
rep("    if (n > 0) { showCount(String(n)); AU.cd(n); buzz(8);", "    if (n > 0) { showCount(String(n)); AU.cd(n); AU.say('cd' + n, 0.9); buzz(8);")
rep("  AU.music('play'); AU.go(); buzz([12, 30, 18]);", "  AU.music('play'); AU.go(); AU.say('go'); buzz([12, 30, 18]);")
rep("  el.hidden = false; AU.whoosh(); setTimeout(() => AU.say('ready'), 350);", "  el.hidden = false; AU.whoosh(); for (const k of ['cd3', 'cd2', 'cd1', 'go']) AU.say(k, 0); setTimeout(() => AU.say('ready'), 350);")
rep('<p class="ver">Version 76</p>', '<p class="ver">Version 77</p>')
rep('<p class="lhead critics" style="text-align:center;color:#B8B0C8">The critics</p><div class="seg" id="stages" role="group" aria-label="How harsh the critics are"></div>', '<p class="lhead critics" style="text-align:center;color:#B8B0C8">CPU difficulty</p><div class="seg" id="stages" role="group" aria-label="CPU difficulty"></div>')
rep("md[1] + ' \\u00b7 Critics ' + (CRITICS[diff] || 'fair').toLowerCase();", "md[1] + ' \\u00b7 CPU ' + (CRITICS[diff] || 'fair').toLowerCase();")
rep("md[1] + ', critics ' + (CRITICS[diff] || 'fair').toLowerCase());", "md[1] + ', CPU ' + (CRITICS[diff] || 'fair').toLowerCase());")
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
