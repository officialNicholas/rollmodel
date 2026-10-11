// 3D eyes: for each mesh, two glossy eyeballs (teal iris ring, dark pupil, painted catchlights plus the real clearcoat reflection) set into
// soft raised sockets with upper and lower lid shells, parented to the head bone so they ride every pose rigidly. Both meshes get the same
// eye from the shared FACE definition: the same size, the same direction from the head centre and the same gaze, in head radii, with the
// ball sunk into wherever that direction meets each mesh's own skin. Expressions move the lids, the look turns the balls, the eye style
// swaps the iris map and the lid rest.
import * as THREE from 'three';
import { FACE } from './look.js';

function irisTexture(style) {
  const W = 512, H = 256, c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d');
  const cx = W * 0.25, cy = H * 0.5;
  const bg = g.createRadialGradient(cx, cy, 10, cx, cy, 170); bg.addColorStop(0, '#ffffff'); bg.addColorStop(0.45, '#f7f5f9'); bg.addColorStop(0.8, '#e2dde8'); bg.addColorStop(1, '#c9c2d2'); g.fillStyle = bg; g.fillRect(0, 0, W, H);
  if (style === 3) { for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2 + 0.3; g.strokeStyle = 'rgba(190,30,40,0.5)'; g.lineWidth = 1.6; g.beginPath(); g.moveTo(cx + Math.cos(a) * 52, cy + Math.sin(a) * 52); g.quadraticCurveTo(cx + Math.cos(a + 0.2) * 85, cy + Math.sin(a + 0.25) * 85, cx + Math.cos(a - 0.1) * 120, cy + Math.sin(a) * 120); g.stroke(); } }
  // iris radius / pupil radius in pixels (the equirect's 512 px = 360 deg, so 58 px is a 41 deg half-angle: a big expressive iris)
  const ri = style === 2 ? 0 : style === 1 ? 50 : style === 3 ? 52 : 58, rp = style === 2 ? 44 : style === 3 ? 16 : style === 1 ? 30 : 27;
  if (ri > 0) {
    const teal = style === 3 ? ['#c3dcb0', '#8fb886', '#4f7a52', '#2b4a33'] : ['#8cf6ff', '#22cfe2', '#0b8aa0', '#063f4c'];
    const ir = g.createRadialGradient(cx, cy, rp * 0.9, cx, cy, ri); ir.addColorStop(0, teal[1]); ir.addColorStop(0.45, teal[0]); ir.addColorStop(0.8, teal[1]); ir.addColorStop(0.95, teal[2]); ir.addColorStop(1, teal[3]);
    g.fillStyle = ir; g.beginPath(); g.arc(cx, cy, ri, 0, Math.PI * 2); g.fill();
    for (let i = 0; i < 56; i++) { const a = i / 56 * Math.PI * 2, w = 0.5 + (i % 3) * 0.4; g.strokeStyle = 'rgba(0,50,70,' + (0.1 + 0.1 * (i % 2)) + ')'; g.lineWidth = w; g.beginPath(); g.moveTo(cx + Math.cos(a) * rp, cy + Math.sin(a) * rp); g.lineTo(cx + Math.cos(a + 0.06) * (ri - 3), cy + Math.sin(a + 0.06) * (ri - 3)); g.stroke(); }
    g.strokeStyle = 'rgba(6,30,40,0.85)'; g.lineWidth = 3.5; g.beginPath(); g.arc(cx, cy, ri - 1.5, 0, Math.PI * 2); g.stroke();
    // limbal shadow: the lid's shadow on the top of the iris
    const sh = g.createLinearGradient(0, cy - ri, 0, cy); sh.addColorStop(0, 'rgba(0,20,30,0.45)'); sh.addColorStop(1, 'rgba(0,20,30,0)'); g.save(); g.beginPath(); g.arc(cx, cy, ri, 0, Math.PI * 2); g.clip(); g.fillStyle = sh; g.fillRect(cx - ri, cy - ri, ri * 2, ri); g.restore();
  }
  g.fillStyle = '#07050a'; g.beginPath(); g.arc(cx + (style === 3 ? 7 : 0), cy + (style === 3 ? 5 : 0), rp, 0, Math.PI * 2); g.fill();
  if (style === 2) { g.strokeStyle = 'rgba(8,6,10,0.9)'; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, rp + 1, 0, Math.PI * 2); g.stroke(); }
  // painted catchlights: a big soft one up-left, a pin-point down-right (the real reflection adds the sharp one)
  g.fillStyle = 'rgba(255,255,255,0.92)'; g.beginPath(); g.ellipse(cx - 19, cy - 19, style === 2 ? 11 : 13, style === 2 ? 9 : 11, -0.5, 0, Math.PI * 2); g.fill();
  g.fillStyle = 'rgba(255,255,255,0.75)'; g.beginPath(); g.arc(cx + 17, cy + 15, 5, 0, Math.PI * 2); g.fill();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}
let IRIS = null;
// lid rests per expression: a = upper lid edge above the eye's horizontal (rad), b = lower lid edge below it, k = tilt (inner corner down when > 0)
const LID3 = {
  neutral: { a: 1.0, b: 0.75, k: 0.0 }, happy: { a: 0.85, b: 0.25, k: 0.08 }, angry: { a: 0.5, b: 0.65, k: -0.55 },
  hurt: { L: { a: 0.5, b: 0.5, k: 0.3 }, R: { a: -0.12, b: 0.12, k: 0.25 } }, glee: { a: -0.12, b: 0.12, k: 0.2 }, scared: { a: 1.3, b: 1.0, k: 0.12 },
  yawn: { a: 0.0, b: 0.12, k: 0.1 }, dizzy: { a: 0.4, b: 0.45, k: 0.4 }, peek: { a: 1.25, b: 0.95, k: 0.0 }, leap: { a: 1.25, b: 0.95, k: 0.0 }, brace: { a: -0.12, b: 0.12, k: 0.35 },
};
const NO_SHUT = { glee: 1, hurt: 1, yawn: 1, dizzy: 1, brace: 1 };
const _o = new THREE.Vector3(), _d = new THREE.Vector3(), _z = new THREE.Vector3(0, 0, 1);
export class EyeRig {
  constructor(look, meshRec) {
    IRIS = IRIS || [0, 1, 2, 3].map(irisTexture);
    this.look = look; this.rec = meshRec; const meta = meshRec.meta, r = meta.headr, E = FACE.eye;
    const R = r * E.size; this.R = R;
    const headAbs = new THREE.Vector3(...meta.headAbs), hb = meta.bones.find(b => b.name === 'head'), headJoint = new THREE.Vector3(...hb.pos);
    this.ballMat = new THREE.MeshPhysicalMaterial({ map: IRIS[0], roughness: 0.06, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.4 });
    this.lidMat = new THREE.MeshPhysicalMaterial({ color: 0xff8da6, roughness: 0.6, metalness: 0, clearcoat: 0.25, clearcoatRoughness: 0.35 });
    this.socketMat = new THREE.MeshPhysicalMaterial({ color: 0xff9fb6, roughness: 0.68, metalness: 0, clearcoat: 0.15, clearcoatRoughness: 0.4 });
    this.lashMat = new THREE.MeshStandardMaterial({ color: 0x5a1c33, roughness: 0.7, metalness: 0 });
    // where the eye direction meets this mesh's skin (rest pose): the ball is sunk into the surface there
    const probe = new THREE.Mesh(meshRec.mesh.geometry, new THREE.MeshBasicMaterial()); const rc = new THREE.Raycaster(); rc.far = r * 2.5;
    this.eyes = [];
    for (const sd of [-1, 1]) {
      _d.set(sd * Math.sin(E.yaw), 0, Math.cos(E.yaw));   // a level ray from the eye height: the same height on a flat head and a round one
      rc.set(_o.set(headAbs.x, meta.headMid + E.height * meta.headH, headAbs.z), _d); const hits = rc.intersectObject(probe, false); let dist = r * 0.95; for (const h of hits) { if (h.distance > r * 0.3) { dist = h.distance; break; } }
      const centre = _o.addScaledVector(_d, dist - R * E.embed);
      const g = new THREE.Group(); g.position.copy(centre).sub(headJoint);
      const fwd = new THREE.Vector3(0, 0, 1).addScaledVector(_d, E.gaze).normalize(); fwd.y += E.tilt; fwd.normalize(); g.quaternion.setFromUnitVectors(_z, fwd);
      const socket = new THREE.Mesh(new THREE.SphereGeometry(R * E.socket, 28, 18), this.socketMat); socket.scale.set(1.0, 0.95, 0.55); socket.position.z = R * 0.05;
      const ball = new THREE.Mesh(new THREE.SphereGeometry(R, 40, 28), this.ballMat);
      const up = new THREE.Mesh(new THREE.SphereGeometry(R * E.lid, 36, 14, 0, Math.PI * 2, 0, Math.PI * 0.5 + 0.12), this.lidMat);
      const lo = new THREE.Mesh(new THREE.SphereGeometry(R * E.lid, 36, 14, 0, Math.PI * 2, Math.PI * 0.5 - 0.12, Math.PI * 0.5 + 0.12), this.lidMat);
      const lash = new THREE.Mesh(new THREE.TorusGeometry(R * E.lid, R * 0.022, 6, 40, Math.PI * 1.1), this.lashMat); lash.rotation.set(Math.PI / 2 - 0.12, 0, -Math.PI * 0.05 + Math.PI); lash.position.y = -R * 0.0;
      const upPivot = new THREE.Group(), loPivot = new THREE.Group(); upPivot.add(up); upPivot.add(lash); loPivot.add(lo);
      g.add(socket); g.add(ball); g.add(upPivot); g.add(loPivot);
      for (const m of [socket, ball, up, lo, lash]) { m.castShadow = true; m.renderOrder = 4; }
      meshRec.byName.head.add(g); this.eyes.push({ sd, g, ball, up: upPivot, lo: loPivot, socket, dist });
    }
    this.probeDist = this.eyes.map(e => +e.dist.toFixed(3));
  }
  lidParams(name, sd) { const F = LID3[name] || LID3.neutral; return F.L ? (sd < 0 ? F.L : F.R) : F; }
  update(expr, exprB, exprK, blinkK, lookV, style, team, fade) {
    this.ballMat.map = IRIS[style] || IRIS[0];
    const skin = team.clone().lerp(new THREE.Color(1, 0.93, 0.9), 0.12); this.lidMat.color.copy(skin).multiplyScalar(style === 1 ? 0.78 : 0.92); this.socketMat.color.copy(skin).multiplyScalar(1.0);
    const shut = blinkK > 0 && !NO_SHUT[exprB];
    for (const E of this.eyes) {
      const pa = this.lidParams(expr, E.sd), pb = this.lidParams(exprB, E.sd); let a = pa.a + (pb.a - pa.a) * exprK, b = pa.b + (pb.b - pa.b) * exprK, k = pa.k + (pb.k - pa.k) * exprK;
      if (style === 1) { a -= 0.3; k -= 0.3; } if (style === 3) { a -= E.sd < 0 ? 0.45 : 0.15; k += 0.15; }
      if (shut) { a = -0.12; b = 0.12; }
      a = Math.min(1.3, a); b = Math.min(1.05, b);
      // the shells sit closed at the eye's horizontal; opening swings the upper lid's edge up (about the eye's x axis) and the lower lid's edge down;
      // the tilt rolls the upper lid about the eye's axis, the inner corner down for a scowl
      E.up.rotation.set(-a, 0, -k * E.sd); E.lo.rotation.set(b, 0, -k * E.sd * 0.3);
      E.ball.rotation.set(-lookV[1] * 0.8, lookV[0] * 0.9, 0);
    }
    for (const E of this.eyes) E.g.visible = fade > 0.5;   // through the swap the eyes follow the body that is drawn solid (no see-through balls on the fading head)
  }
}
