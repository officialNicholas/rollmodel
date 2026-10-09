# Drifting clouds sat at body height, and with the lower camera one drifting in behind you hid you and the floor around you.
# Now a cloud fades to a faint ghost (its shadow stays) whenever it comes between the camera and you, or the floor just around and
# ahead of you: the line from the camera to each of those points is tested against the cloud's (padded) ellipsoid.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

rep("""    // go see-through while the drop is inside or right under it, so you can always see yourself
    const inside = drop.visible && inR(P.x, P.z, m.box, 0.5) && P.y + 0.9 > m.y0 - 0.6 && P.y < m.y1 + 0.4;
    g.userData.fade += ((inside ? 0.35 : 1) - g.userData.fade) * Math.min(1, rdt * 10);""",
"""    // go see-through while the drop is inside or right under it, or the cloud is between the camera and you (or the floor around you)
    const inside = drop.visible && inR(P.x, P.z, m.box, 0.5) && P.y + 0.9 > m.y0 - 0.6 && P.y < m.y1 + 0.4;
    const occ = !inside && state !== 'menu' && cloudHides(m.cx, 1.17, m.cz);
    g.userData.fade += ((inside ? 0.35 : occ ? 0.14 : 1) - g.userData.fade) * Math.min(1, rdt * (occ ? 12 : 6));""")
rep("// ---------- Palette Island: the sea all round it, little islands out on the water ----------",
"""// does a cloud at (x, y, z) stand between the camera and the player, or the floor just around and ahead of them?
const CLOUD_RXZ = 2.1, CLOUD_RY = 0.95, cloudPts = [[0, 0.5, 0], [1.7, 0.1, 0], [-1.7, 0.1, 0], [0, 0.1, 2.4], [0, 0.1, -1.2]];
function cloudHides(x, y, z) {
  const C = camera.position, sy = Math.sin(camYaw), cy = Math.cos(camYaw);
  const ox = (C.x - x) / CLOUD_RXZ, oy = (C.y - y) / CLOUD_RY, oz = (C.z - z) / CLOUD_RXZ, cc = ox * ox + oy * oy + oz * oz - 1;
  if (cc < 0) return true;
  for (const q of cloudPts) {
    // each point in the player's frame: right, up, and ahead the way the camera looks
    const tx = P.x + q[0] * cy + q[2] * sy, ty = P.y + q[1], tz = P.z - q[0] * sy + q[2] * cy;
    const dx = (tx - C.x) / CLOUD_RXZ, dy = (ty - C.y) / CLOUD_RY, dz = (tz - C.z) / CLOUD_RXZ;
    const a = dx * dx + dy * dy + dz * dz, b = ox * dx + oy * dy + oz * dz, disc = b * b - a * cc;
    if (disc < 0) continue; const t = (-b - Math.sqrt(disc)) / a; if (t > 0 && t < 1) return true;
  }
  return false;
}

// ---------- Palette Island: the sea all round it, little islands out on the water ----------""")
open(p, 'w').write(s)
print('ok')
