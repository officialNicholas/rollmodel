import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)

# wedged: roll out the most open way near where you were headed, not back the way you came
rep("for (let i = 0; i < 24; i++) { const a = D.yaw + i / 24 * 6.2832, sc = clearRun(D, a, 3) + 0.2 * Math.cos(a - D.yaw - Math.PI); if (sc > bs) { bs = sc; best = a; } }",
    "for (let i = 0; i < 24; i++) { const a = D.yaw + i / 24 * 6.2832, sc = clearRun(D, a, 3) + 0.35 * Math.cos(a - D.yaw); if (sc > bs) { bs = sc; best = a; } }")

old_start = "// hitting a wall glances you off it instead of sticking\nfunction moveFlat(D, dt) {"
old_end = "// rolling down a ramp speeds you up, rolling up slows you a little"
i = s.find(old_start); j = s.find(old_end)
assert i > 0 and j > i
s = s[:i] + r"""// which way the wall you just touched faces: sample around the blob and point away from what's solid
function wallNormal(D) {
  let sx = 0, sz = 0;
  for (let i = 0; i < 16; i++) { const a = i / 16 * 6.2832, c = Math.sin(a), q = Math.cos(a); if (blockedAt(D.x + c * 0.5, D.z + q * 0.5, D.y)) { sx -= c; sz -= q; } }
  const l = Math.hypot(sx, sz); return l > 0.01 ? [sx / l, sz / l] : null;
}
const wrapA = a => Math.atan2(Math.sin(a), Math.cos(a));
// hitting a wall slides you along it: you keep the part of your roll that runs along the wall and lose the part that ran into it
function moveFlat(D, dt) {
  if (blockedAt(D.x, D.z, D.y) && !nudgeFree(D)) return unstick(D);
  const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw), d = D.spd * dt, x0 = D.x, z0 = D.z, kx = D.kx * dt, kz = D.kz * dt;
  let hit = false;
  const nx = D.x + fx * d + kx; if (!blockedAt(nx, D.z, D.y)) D.x = nx; else { hit = true; D.kx = 0; }
  const nz = D.z + fz * d + kz; if (!blockedAt(D.x, nz, D.y)) D.z = nz; else { hit = true; D.kz = 0; }
  // pressed against something and getting nowhere: after a moment, break free
  if (hit && !D.charging && !D.slam && Math.hypot(D.x - x0, D.z - z0) < d * 0.4) D.stuck += dt; else D.stuck = Math.max(0, D.stuck - dt * 3);
  if (D.stuck > 0.2) return unstick(D);
  if (!hit || D.slam || D.charging || D.bonkCD > 0 || D.spd < 0.3) return;
  const pref = D.turn > 0.2 ? -1 : D.turn < -0.2 ? 1 : 0, n = wallNormal(D);
  let ny = null, into = 1;
  if (n) {
    const dot = fx * n[0] + fz * n[1]; into = clamp(-dot, 0, 1);
    // the two ways along the wall, the one you were already leaning toward first (or the way you're steering, or the more open side)
    const tA = [n[1], -n[0]], tB = [-n[1], n[0]], yA = Math.atan2(tA[0] + n[0] * 0.14, tA[1] + n[1] * 0.14), yB = Math.atan2(tB[0] + n[0] * 0.14, tB[1] + n[1] * 0.14);
    const lean = fx * tA[0] + fz * tA[1];
    let first = Math.abs(lean) > 0.25 ? (lean > 0 ? 'A' : 'B') : pref ? (Math.sign(wrapA(yA - D.yaw)) === pref ? 'A' : 'B') : (clearRun(D, yA, 1.5) >= clearRun(D, yB, 1.5) ? 'A' : 'B');
    const order = first === 'A' ? [yA, yB] : [yB, yA];
    for (const y of order) if (clearRun(D, y, 1.25) >= 0.75) { ny = y; break; }
  }
  if (ny === null) {
    // boxed into a corner: back out toward the most open side
    let bs = -1; for (let i = 0; i < 16; i++) { const a = D.yaw + Math.PI + (i - 8) / 16 * 6.2832, c = clearRun(D, a, 2.5); if (c > bs) { bs = c; ny = a; } }
    into = 1;
  }
  D.yaw = ny; D.spd *= 1 - 0.5 * into; D.turn *= 0.3; D.bonkCD = 0.12;
  // only a real knock gets the bonk; a glancing touch just slides
  const k = clamp(D.spd / 7, 0.3, 1) * into;
  if (into > 0.45 && D.spd > 0.8) {
    D.squash = Math.max(D.squash, 0.2 + 0.3 * k); D.wob = Math.max(D.wob, 0.6);
    if (D === P) { shake = Math.max(shake, 0.03 + 0.05 * k); buzz(6); }
    if (hearable(D)) AU.bonk(0.4 + 0.6 * k);
    for (let i = 0; i < 4; i++) { const a = Math.random() * 6.283; spawnPart(D.x + fx * 0.3, D.y + 0.25, D.z + fz * 0.3, Math.cos(a) * 1.4, 0.8 + Math.random(), Math.sin(a) * 1.4, 0.3, puHaloMat, 0.5); }
  }
}
""" + s[j:]
open(F, 'w').write(s)
print('ok')
