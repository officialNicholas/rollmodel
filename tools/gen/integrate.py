# swap the old goo character for the jelly (module from lab/char.js), wiring every place the game touched the old one
import re, sys
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/paint-the-canvas.v54-preredesign.html'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/paint-the-canvas.html'
s = open(SRC).read()
mod = open(SP + 'lab/char.js').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit('anchor x%d (want %d): %s' % (n, count, old[:120]))
    s = s.replace(old, new)

# ---- 1. the character section ----
a = s.index('// ---------- goo character ----------')
b = s.index('const lookC = { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0, flatK: 0 };')
b = s.index('\n', b) + 1
old = s[a:b]
rig = re.search(r'const RIG = \{.*?\};\n', old).group(0)
gloss = re.search(r'const glossMat = .*?\n', old).group(0)
bent = old[old.index('function bentTube('):old.index('// a profile [r, y] turned round the y axis')]
lathe = old[old.index('function latheW('):old.index('const mirrorX = ')]
new = '''// ---------- the jelly character ----------
// the paint roller a blob turns into (in body units): radius, half its length, and its axis dropped so it sits where the blob sits
const ROLL_R = 0.68, ROLL_H = 1.15, ROLL_Y = -0.14;
// every jelly shares these: (Graphics mode) how strongly light glows through it, and the outline's width per unit of distance
const JGLOW = { value: 1 }, GLINE = { value: 0.0042 };
// Graphics mode jelly. The scene's own light is often a dim moon, so every jelly also carries a light rig that moves with the
// camera, the way a film lights its characters: a warm soft key from up and to the left, a hot highlight in it, a bright rim behind
''' + rig + '''// the jelly and everything glossy on a character get a studio light map (soft boxes over the theme's sky) for their highlights
const CHAR_MATS = [], JELLY_GRAB = { fn: null }, jellyGrab = () => { if (JELLY_GRAB.fn) JELLY_GRAB.fn(); };
const charMat = m => { if (m.isMeshStandardMaterial) CHAR_MATS.push(m); return m; };
''' + gloss + '''// rings round a spine in the xy plane: the ring radius is rad(t), the spine's heading turns by ang(t) (0 = straight up, + leans to +x)
''' + bent + '''// a profile [r, y] turned round the y axis, the seam welded so it shades smoothly; out = which way the first segment's normal should face
''' + lathe + mod + '''
const BLOB_LODS = HI ? JYG.body : null;
let flashPh = 0, wearDt = 0.016;
// you, stood in the scene
const JP = makeJelly(C.ink), drop = JP.root, body = JP.body, dropMat = JP.mat, xrayMat = JP.xrayMat, gooU = JP.U;
scene.add(drop);
const shadowBlob = new THREE.Mesh(new THREE.CircleGeometry(0.4, 24), new THREE.MeshBasicMaterial({ color: C.outline, transparent: true, opacity: 0.2, depthWrite: false })); shadowBlob.rotation.x = -Math.PI / 2; scene.add(shadowBlob);
// the first rival
const JH = makeJelly(TEAMS[1].wet), cDrop = JH.root, cBody = JH.body, cMat = JH.mat, cXrayMat = JH.xrayMat, gooU2 = JH.U;
scene.add(cDrop);
const cShadow = new THREE.Mesh(new THREE.CircleGeometry(0.4, 24), new THREE.MeshBasicMaterial({ color: C.outline, transparent: true, opacity: 0.2, depthWrite: false })); cShadow.rotation.x = -Math.PI / 2; scene.add(cShadow);
const lookC = { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0, flatK: 0 };
'''
s = s[:a] + new + s[b:]

# ---- 2. the stars over a dizzy head sit higher on the taller jelly ----
rep("g.position.set(D.x, D.y + PR * 2.2 * V.gk + 0.15, D.z);", "g.position.set(D.x, D.y + PR * 2.45 * V.gk + 0.22, D.z);")

# ---- 3. the turret: no mount any more, a snout out of the face ----
a = s.index('// the turret a blob becomes: it sits down into a squat orange mount')
b = s.index('// the little ring on the ground where your turret')
s = s[:a] + "// the turret a jelly becomes grows a snout out of its face: where its shots leave (body units, from the body's middle)\nconst TURRET_RIG = { tip: new THREE.Vector3(0, 0.46, 1.42) };\n" + s[b:]
rep("const x0 = D.x + (tp.x * cy + tp.z * sy) * k, y0 = D.y + (tp.y + 0.82 + 0.3) * k, z0 = D.z + (-tp.x * sy + tp.z * cy) * k;", "const x0 = D.x + (tp.x * cy + tp.z * sy) * k, y0 = D.y + (tp.y + 0.82) * k, z0 = D.z + (-tp.x * sy + tp.z * cy) * k;")

# ---- 4. faces: the old per-blob face code goes, the jelly's mood and drive come in ----
a = s.index('// what a face is doing beyond its usual look: { mk:')
b = s.index('function rollPoof(D, on) {')
s = s[:a] + '''// what a jelly's face is doing: hurting beats gloating, a power shows on it, and otherwise it's the game (scared, straining, hunting)
function jellyMood(D, V) {
  const isP = D === P, L = V.look;
  if (D.st === 'ko') return 'ko';
  if (state === 'intro' && D.formK !== undefined && D.formK < 0.7) return 'shut';
  if (vic && D.vicPose) return vic.happy ? (D.vicPose.spin > 0.2 ? 'glee' : 'happy') : 'worried';
  if (D.st === 'play' && D.flatT > 0) return 'ko';
  if (D.st === 'play' && D.stunT > 0) return 'dizzy';
  const emo = D.emoT > 0 ? D.emo : null;
  if (emo === 'ouch' || emo === 'bonk') return 'hurt';
  if (emo === 'glee') return 'glee'; if (emo === 'smug') return 'smug'; if (emo === 'yawn') return 'yawn';
  if (D.giantT > 0) return 'derp';
  if (D.rocket) return D.rocket.ph === 'up' ? 'excited' : D.rocket.ph === 'dive' && !D.rocket.slow ? 'scared' : 'focus';
  if (D.turret) return 'focus';
  if (isP && (celebrating || menuReact > 0 || D.st === 'hide')) return 'happy';
  if (D.charging && D.charge > 0.3) return D.charge > 0.62 ? 'grit' : 'focus';
  if (D.slam) return 'grit';
  if ((isP && dangerK > 0) || D.wob > 0.6 || D.exposed || (D.air && D.vy < -7) || (D.st === 'play' && D.paint < 0.15 && state === 'play')) return 'scared';
  if (D.dry && D.st === 'play') return 'worried';
  if (D.cpu && D.ai && D.ai.mode === 'hunt') return 'angry';
  if (D.air) return D.vy > 1 ? 'excited' : 'neutral';
  if (state === 'menu') return 'neutral';
  return L.spd > 0.8 ? 'focus' : 'neutral';
}
const faceMood = D => jellyMood(D, D === P ? VP : D.look.V); // (kept for the tests)
// each frame, what the game is doing told to the jelly: where it is and how it moves, its face, where it looks, what it wears
const jyTo = new THREE.Vector3();
function jellyDrive(D, V, J, wearing, dt) {
  const S = J.S || (J.S = { pos: new THREE.Vector3(), wear: null }), L = V.look, A = J.A;
  S.pos.copy(V.root.position); S.yaw = V.root.rotation.y;
  const playing = D.st === 'play' && (state === 'play' || state === 'intro');
  S.spd = L.spd; S.turn = L.lean; S.air = !!D.air && D.st !== 'hide'; S.vy = D.vy || 0; S.roll = L.roll; S.fat = clamp((V.gk - 1) / (GIANT_K - 1), 0, 1);
  // a landing thumps the head down and slaps the ears
  if (A && V.wasAir && !S.air && D.st !== 'hide') { const imp = clamp(-(V.lastVy || 0) / 9, 0.18, 1); A.hsq.v += 5.5 * imp; A.hy.v -= 1.1 * imp; for (const E of A.ears) E.fl.v -= 8 * imp; }
  V.wasAir = S.air; V.lastVy = D.vy || 0;
  S.face = jellyMood(D, V);
  S.turretK = V.turK || 0; S.kick = D.turret ? D.turret.kick : 0; S.aimUp = D.turret ? ((D.turret.aim === undefined ? 0.4 : D.turret.aim) - 0.4) * 0.7 : 0;
  S.pitch = (D.charging ? -0.24 * D.charge : 0) - S.aimUp * 0.45 + (D.slam ? 0.18 : 0);
  // where it looks: at a rival that's close and in front, else into its turn; on the menu, wherever its idle fancy takes it
  let ly = -L.lean * 0.4, gx = 0, gy = 0;
  if (playing) { const F = nearestFoe(D); if (F) { const dx = F.x - D.x, dz = F.z - D.z, d = Math.hypot(dx, dz); if (d < 9) { let a = Math.atan2(dx, dz) - D.yaw; a = Math.atan2(Math.sin(a), Math.cos(a)); if (Math.abs(a) < 1.9) { const k = clamp(1.4 - d / 7, 0, 1); ly += clamp(a, -0.8, 0.8) * 0.65 * k; gx = clamp(a, -0.6, 0.6) * 0.5 * k; } } } }
  if (D === P && state === 'menu') { ly += idleLook.x * 5; gy += idleLook.y * 2.5; }
  S.lookYaw = ly; S.gazeX = gx; S.gazeY = gy; S.calmEyes = state === 'menu';
  S.wear = wearing; S.fangs = !!wearing && wearing.mouth === 'fangs'; S.wearOff = !!D.wearOff || (D.wearPop !== undefined && D.wearPop < 0); S.wearPop = D.wearPop === undefined ? 1 : clamp(D.wearPop / 0.6, 0, 1);
  if (S.faceK === undefined) S.faceK = 1;
  jellyAnim(J, S, dt);
  // every part follows the body's color and fades with it while it can't be knocked down again
  jellyColor(J); const op = V.mat.opacity; for (const m of J.parts) m.opacity = op; for (const e of J.eyes) e.ball.material.opacity = op * (J.faceFade === undefined ? 1 : J.faceFade);
}
''' + s[b:]

# ---- 5. blobVisual: the turret mount, the rocket on its back, the puddle -> how much it's sat on the floor ----
rep("  if (V.turK > 0.01) { sq = Math.max(sq, 0.2 * V.turK); hop += 0.3 * rad * V.turK; } // sat down in the mount (lifted onto it)\n", "  if (V.turK > 0.01) sq = Math.max(sq, 0.08 * V.turK); // a turret settles down low\n")
rep("  if (D.turret && D.st === 'play' && !(vic && D.vicPose)) sq = Math.max(sq, 0.16 + 0.22 * D.turret.kick); // a turret squats into a dome on its mount, and kicks with each shot", "  if (D.turret && D.st === 'play' && !(vic && D.vicPose)) sq = Math.max(sq, 0.06 + 0.2 * D.turret.kick); // and kicks with each shot")
a = s.index("  if (V.tur) { const on = !!D.turret && D.st === 'play';")
b = s.index("\n", s.index("V.turBarrel.rotation.x = V.turPitch; } }", a)) + 1
s = s[:a] + "  { const on = !!D.turret && D.st === 'play'; V.turK = (V.turK || 0) + ((on ? 1 : 0) - (V.turK || 0)) * Math.min(1, dt * (on ? 9 : 7)); }\n" + s[b:]
rep("V.rk.position.copy(gooJS(tv2.set(0, 0.1, -1).normalize(), U)).add(tv1.set(0, 0.02, -0.2));", "V.rk.position.set(0, 0.42, -1.0).applyMatrix4(V.J.head.matrix);")
rep("    const pk = pd.userData.k * isc; U.gPud.value = pd.userData.k; pd.visible = false;", "    const pk = pd.userData.k * isc; pd.visible = false;")
rep("  // the puddle: full while it sits on the ground, drawn in as it leaves it, trailing back a little at speed\n  const pd = V.puddle;", "  // how much it's sat on the floor: its toes spread out on it, and gather in under it as it leaves\n  U.gPud.value = V.root.visible && !hidden && D.st !== 'ko' && gy > -Infinity ? clamp(1 - (D.y - gy) * 1.6, 0, 1) * L.flat * clamp(1 - hop * 5, 0, 1) : 0;\n  const pd = V.puddle;")

# ---- 6. who's who: the player's and rivals' visuals ----
a = s.index("const VP = { root: drop, body, mat: dropMat, hull: dropHull,")
b = s.index("// a CPU each frame: body, face, color")
s = s[:a] + '''const VP = { root: drop, body, mat: dropMat, hull: JP.hull, U: gooU, look, shadow: shadowBlob, flatK: 0, gk: 1, puddle: null, J: JP }, VC = { root: cDrop, body: cBody, mat: cMat, hull: JH.hull, U: gooU2, look: lookC, shadow: cShadow, flatK: 0, gk: 1, puddle: null, J: JH };
// a CPU's whole look in one place: the first rival's is made from the parts above, the second gets its own
addBat(VP); addBat(VC); addRig(VP); addRig(VC); addRocket(VP); addRocket(VC);
const LH = { D: H, drop: cDrop, body: cBody, mat: cMat, xrayMat: cXrayMat, U: gooU2, J: JH, shadow: cShadow, look: lookC, V: VC, stars: starsC, warn: cWarn, warnFill: cWarnFill, foeMark, mark: cMark, col: COL_HOLY };
function makeCpuLook(D, color) {
  const J = makeJelly(color), drop = J.root; drop.visible = false; scene.add(drop);
  const shadow = new THREE.Mesh(cShadow.geometry, cShadow.material); shadow.rotation.x = -Math.PI / 2; shadow.visible = false; scene.add(shadow);
  const warnCol = new THREE.Color(color).lerp(COL_WHITE, 0.5);
  const warnFill = new THREE.Mesh(cWarnFill.geometry, cWarnFill.material.clone()); warnFill.material.color.copy(warnCol); warnFill.rotation.x = -Math.PI / 2; warnFill.visible = false; scene.add(warnFill);
  const warn = new THREE.Mesh(cWarn.geometry, cWarn.material.clone()); warn.material.color.copy(warnCol); warn.rotation.x = -Math.PI / 2; warn.renderOrder = 6; warn.visible = false; scene.add(warn);
  const fm = new THREE.Mesh(foeMark.geometry, foeMark.material); fm.rotation.x = -Math.PI / 2; fm.visible = false; scene.add(fm);
  const mark = new THREE.Sprite(new THREE.SpriteMaterial({ map: markTexs['!'], depthTest: false, transparent: true, fog: false })); mark.renderOrder = 950; mark.visible = false; scene.add(mark);
  const look = { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0, flatK: 0 };
  const V = { root: drop, body: J.body, mat: J.mat, hull: J.hull, U: J.U, look, shadow, flatK: 0, gk: 1, puddle: null, J }; addBat(V); addRig(V); addRocket(V);
  return { D, drop, body: J.body, mat: J.mat, xrayMat: J.xrayMat, U: J.U, J, shadow, look, V, stars: makeStars(), warn, warnFill, foeMark: fm, mark, col: new THREE.Color(color) };
}
const L2 = makeCpuLook(H2, TEAMS[2].wet);
H.look = LH; H2.look = L2;
LH.wearing = { head: null, mouth: null }; L2.wearing = { head: null, mouth: null };
function rollRivalLooks() { const heads = [null, null, 'halo', 'hat']; for (const L of [LH, L2]) L.wearing = { head: heads[Math.random() * heads.length | 0], mouth: Math.random() < 0.35 ? 'fangs' : null }; }
''' + s[b:]
rep("    blobVisual(D, L.V, dt, ke, kf); placeFaceCpu(L, dt); placeStars(L.stars, D, L.V);", "    blobVisual(D, L.V, dt, ke, kf); jellyDrive(D, L.V, L.J, L.wearing, dt); placeStars(L.stars, D, L.V);")
rep("    const gy = blobVisual(P, VP, dt, ke, kf); VP.flatK = VP.flatK; placeFace(dt); placeStars(starsP, P, VP);", "    const gy = blobVisual(P, VP, dt, ke, kf); jellyDrive(P, VP, JP, myLook, dt); placeStars(starsP, P, VP);")

# ---- 7. the customizer: color, the witch hat, the halo, fangs ----
rep("// your look: color (above), eye shape, and this season's accessories: one on your head, one on your back, one in your mouth\nconst EYES = [['round', 'Round'], ['googly', 'Googly'], ['sleepy', 'Sleepy'], ['angry', 'Angry'], ['happy', 'Happy'], ['cyclops', 'Cyclops']];\nconst WEAR = [{ id: 'fangs', name: 'Fangs', slot: 'mouth' }, { id: 'wings', name: 'Bat wings', slot: 'back' }, { id: 'halo', name: 'Halo', slot: 'head' }, { id: 'hat', name: 'Witch hat', slot: 'head' }, { id: 'horns', name: 'Devil horns', slot: 'head' }];",
    "// your look: color (above), and this season's accessories: one on your head, and fangs\nconst WEAR = [{ id: 'hat', name: 'Witch hat', slot: 'head' }, { id: 'halo', name: 'Halo', slot: 'head' }, { id: 'fangs', name: 'Fangs', slot: 'mouth' }];")
rep("const myLook = (() => { const l = store.look || {}, ok = (v, slot) => WEAR.some(w => w.id === v && w.slot === slot) ? v : null; return { eyes: EYES.some(e => e[0] === l.eyes) ? l.eyes : 'round', head: ok(l.head, 'head'), back: ok(l.back, 'back'), mouth: ok(l.mouth, 'mouth') }; })();",
    "const myLook = (() => { const l = store.look || {}, ok = (v, slot) => WEAR.some(w => w.id === v && w.slot === slot) ? v : null; return { head: ok(l.head, 'head'), mouth: ok(l.mouth, 'mouth') }; })();")
a = s.index("const EYE_ICON = {"); b = s.index("const WEAR_ICON = {")
s = s[:a] + s[b:]
rep("  wings: '<path d=\"M20 22C16 14 9 10 2 12c2 3 2 6 1 9 2-1 4-1 6 1 1-2 3-3 5-2 1-2 3-2 6 2zM20 22c4-8 11-12 18-10-2 3-2 6-1 9-2-1-4-1-6 1-1-2-3-3-5-2-1-2-3-2-6 2z\" fill=\"#6A4AA0\" stroke=\"#D9C8FF\" stroke-width=\"1.6\" stroke-linejoin=\"round\"/>',\n", "")
a = s.index("  horns: '<path d=\"M9 30c"); b = s.index("\n", a) + 1; s = s[:a] + s[b:]
rep("  $('eyeOpts').innerHTML = EYES.map(([id, name]) => '<button class=\"lopt\" type=\"button\" data-e=\"' + id + '\" aria-label=\"' + name + ' eyes\" title=\"' + name + '\" aria-pressed=\"' + (myLook.eyes === id) + '\"><svg viewBox=\"0 0 40 40\" aria-hidden=\"true\">' + EYE_ICON[id] + '</svg></button>').join('');\n", "")
rep("  $('lookEyes').textContent = (EYES.find(e => e[0] === myLook.eyes) || EYES[0])[1]; $('lookColor').textContent = colorOf().name;", "  $('lookColor').textContent = colorOf().name;")
rep("$('eyeOpts').addEventListener('click', e => { const b = e.target.closest('.lopt'); if (!b) return; AU.init(); myLook.eyes = b.dataset.e; saveLook(); renderLook(); lookPop(); });\n", "")
rep("myLook[w.slot] = myLook[w.slot] === w.id ? null : w.id; saveLook(); renderLook(); lookPop(); heroT = 0; if (w.slot === 'back' && myLook.back) lookSpin = Math.PI / 2; });", "myLook[w.slot] = myLook[w.slot] === w.id ? null : w.id; saveLook(); renderLook(); lookPop(); heroT = 0; });")
rep('    <div class="lgroup"><p class="lhead">Eyes <b id="lookEyes">Round</b></p><div class="lopts" id="eyeOpts" role="group" aria-label="Eyes"></div></div>\n', '')
rep("wide = myLook.back === 'wings' ? 1.95 : 1.55, tall = myLook.head === 'hat' ? 1.25 : myLook.head ? 1.05 : 0.88;", "wide = 1.75, tall = myLook.head === 'hat' ? 1.45 : myLook.head ? 1.22 : 1.04;")
rep("if (lookOpen) { const a = hero.yaw, ly = myLook.head === 'hat' ? 0.44 : 0.36;", "if (lookOpen) { const a = hero.yaw, ly = myLook.head === 'hat' ? 0.52 : 0.42;")

# ---- 8. the customizer's drop-in: the face and the accessories fading and popping in ----
a = s.index("// your face and accessories get their own materials, so fading them never touches a rival's face or the stage's outlines")
b = s.index("const strand = new THREE.Group();")
s = s[:a] + "// your face fades in (its own eye materials, so a rival's never fade with it) and your accessories pop in after it\n" + s[b:]
a = s.index("function introFade(kf, kw) {"); b = s.index("function introFrame() {")
s = s[:a] + '''function introFade(kf, kw) {
  if (JP.S) { JP.S.faceK = kf; JP.S.wearPop = kw < 1 ? kw : 1; JP.S.eyeOpen = kf; } JP.faceFade = kf;
  for (const e of JP.eyes) { e.ball.visible = e.lu.visible = e.ll.visible = kf > 0.02; }
  JP.wear.hat.userData.hide = JP.wear.halo.userData.hide = kw < 0.02;
}
''' + s[b:]
rep("  const tipY = drop.position.y + gooJS(tv2.set(0, 1, 0)).y * body.scale.y;", "  const tipY = drop.position.y + jyTo.set(0, 1.34, 0.06).applyMatrix4(JP.head.matrix).y * body.scale.y;")
rep("  const eo = Math.max(0.02, easeOut((t - IN_LAND - 0.14) / 0.26));\n  for (const it of eyes) { it.e.scale.y *= eo; it.pu.scale.multiplyScalar(eo); }\n  for (const a of pArcs) if (a.visible) a.scale.y *= eo;\n", "")
open(OUT, 'w').write(s)
print('ok', len(s))
