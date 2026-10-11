#!/usr/bin/env python3
"""The axolotl's merged runtime (ws/axo/axo.js, an ES module importing three) as a plain script for the single-file game: the game's
global THREE instead of the import, the exports gathered into one AXO object, and a second way to build a character's mesh from a
pack already in memory (meshFrom) that shares one geometry between every character wearing that body, where loadMesh fetched its own.
usage: mk_axo_embed.py [axo.js] [out.js]"""
import re, sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
SRC = sys.argv[1] if len(sys.argv) > 1 else S + '/ws/axo/axo.js'
OUT = sys.argv[2] if len(sys.argv) > 2 else S + '/axo_embed.js'
s = open(SRC).read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("import * as THREE from 'three';\n", '')
# meshFrom: the same body as loadMesh, from { meta, buf } in memory; the geometry is built once per body and kept on the pack entry
m = re.search(r"export async function loadMesh\(base, tex, matOpts = \{\}\) \{\n  const meta = await \(await fetch\(base \+ '\.json'\)\)\.json\(\), buf = await \(await fetch\(base \+ '\.bin'\)\)\.arrayBuffer\(\);\n  const n = meta\.n, g = new THREE\.BufferGeometry\(\);\n", s)
assert m, 'loadMesh head not found'
body_start = m.end()
# the geometry block runs until the line that names the mesh (matOpts.name); everything after it is per character
gi = s.index("  if (matOpts && matOpts.name) meta.name = matOpts.name;", body_start)
geo_block = s[body_start:gi]
fn_end = s.index("\n}\n", gi) + 3
per_char = s[gi:fn_end - 3]
mesh_from = ("function meshFrom(pre, tex, matOpts = {}) {\n"
             "  // (pre: { meta, buf } from the pack; the geometry is made the first time and shared after that)\n"
             "  const base = pre.name || '', meta = JSON.parse(JSON.stringify(pre.meta)), buf = pre.buf, n = meta.n;\n"
             "  let g = pre.geo; if (!g) { g = new THREE.BufferGeometry();\n" + geo_block + "  pre.geo = g; }\n" + per_char + "\n}\n")
s = s[:fn_end] + mesh_from + s[fn_end:]
# exports: plain declarations, their names collected
names = []
def strip_export(mo):
    kind, name = mo.group(1), mo.group(2); names.append(name); return kind + ' ' + name
s = re.sub(r'^export (async function|function|class|const) ([A-Za-z_$][\w$]*)', strip_export, s, flags=re.M)
for mo in re.finditer(r'^export const \{ ([^}]*) \} = (__\w+);', s, flags=re.M): names += [x.strip() for x in mo.group(1).split(',')]
s = re.sub(r'^export const \{', 'const {', s, flags=re.M)
assert 'export ' not in re.sub(r'//.*', '', s), 'an export left over'
names.append('meshFrom')
# the game's own additions to the shading:
# wading (uCoat.w): the paint it walks through, washed up from the ground in a clean wavy line by the fill order, apart from the lumpy coat
rep("""if (uCoat.x > 0.001) {
  float ch = coatField(vCp, vFillO), cv = uCoat.x * 1.08 - 0.04;
  sCoatM = smoothstep(ch - 0.035, ch + 0.035, cv);
  vec3 pc = max(mix(vec3(dot(uPaint, vec3(0.2126, 0.7152, 0.0722))), uPaint, 1.1), vec3(0.0)) * 0.8;
  diffuseColor.rgb = mix(diffuseColor.rgb, pc, sCoatM) * (1.0 - 0.3 * (1.0 - smoothstep(0.0, 0.06, abs(cv - ch))) * step(uCoat.x, 0.995));""",
"""if (uCoat.x > 0.001 || uCoat.w > 0.001) {
  float ch = coatField(vCp, vFillO), cv = uCoat.x * 1.08 - 0.04, cOn = step(0.001, uCoat.x), wOn = step(0.001, uCoat.w);
  sCoatM = smoothstep(ch - 0.035, ch + 0.035, cv) * cOn;
  float wv = uCoat.w - vFillO + 0.02 * sin(vCp.x * 31.0 + vCp.z * 17.0 + uCoat.y) + 0.012 * sin(vCp.z * 53.0 - vCp.x * 23.0 + uCoat.y * 0.7);
  float wm = smoothstep(-0.007, 0.007, wv) * wOn, we = (1.0 - smoothstep(0.0, 0.028, abs(wv))) * wOn * (1.0 - sCoatM);
  vec3 pc = max(mix(vec3(dot(uPaint, vec3(0.2126, 0.7152, 0.0722))), uPaint, 1.1), vec3(0.0)) * 0.8;
  diffuseColor.rgb = mix(diffuseColor.rgb, pc, sCoatM) * (1.0 - 0.3 * (1.0 - smoothstep(0.0, 0.06, abs(cv - ch))) * step(uCoat.x, 0.995) * cOn);
  diffuseColor.rgb = mix(diffuseColor.rgb, pc, wm * (1.0 - sCoatM)) * (1.0 - 0.24 * we); sCoatM = max(sCoatM, wm);""")
# a roll for the game's look (the menu's head tilts to the beat), with the yaw and the pitch
rep("(N.glance[2] + drift[2]) * amt];", "(N.glance[2] + drift[2]) * amt + (this.look.roll || 0) * 0.6];")
# the face, bigger on the rounder head (v211): the face's cells span a narrower angle, so the eyes and the mouth come out larger, as on
# the old character's ball of a head
rep("const FACE = { pitch: 0.12, half: 0.9, squeeze: 1.0 };", "const FACE = { pitch: 0.1, half: 1.1, squeeze: 1.0 };")
# the sly eyes (fStyle 4, v210): heavy lids in eyeshadow pink with a thick lash line that flicks out into a wing, a soft shadow above,
# arched brows, and a pale ringed iris with a small pupil showing under the lid
rep("float sqd = (fStyle > 0.5 && fStyle < 1.5) ? 1.0 : 0.0, zmb = fStyle > 2.5 ? 1.0 : 0.0;",
    "float sqd = (fStyle > 0.5 && fStyle < 1.5) ? 1.0 : 0.0, zmb = (fStyle > 2.5 && fStyle < 3.5) ? 1.0 : 0.0, sly = fStyle > 3.5 ? 1.0 : 0.0;")
rep("vec3 irC = mix(fIris, vec3(0.42, 0.6, 0.3), zmb);", "vec3 irC = mix(fIris, vec3(0.42, 0.6, 0.3), zmb); irC = mix(irC, mix(fIris, vec3(0.86, 0.85, 0.9), 0.74), sly);")
rep("rp = mix(0.092, 0.11, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.5 : 0.78, zmb);", "rp = mix(0.092, 0.11, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.5 : 0.78, zmb) * mix(1.0, 0.66, sly);")
rep("    ic = mix(ic, vec3(0.02, 0.008, 0.014), sqd * smoothstep(ri - 0.032, ri - 0.012, r));",
    "    ic = mix(ic, vec3(0.02, 0.008, 0.014), sqd * smoothstep(ri - 0.032, ri - 0.012, r));\n"
    "    ic = mix(ic, vec3(0.3, 0.17, 0.2), sly * (1.0 - smoothstep(0.006, 0.02, abs(r - ri * 0.93))) * smoothstep(0.3, -0.4, dd.y / ri)); ic = mix(ic, vec3(0.42, 0.19, 0.2), sly * (1.0 - smoothstep(rp - 0.012, rp, r)));")
rep("  c = mix(c, vec3(0.016, 0.0025, 0.007), lsh);\n  vec4 mA", """  if (sly > 0.5) { for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w), dd = fq - pc; float ox = dd.x * sd, aw = fwidth(fq.y) + 0.003, side = step(0.0, fq.x * sd);
      float lidY = pc.y + 0.0 - 0.11 * ox - 0.12 * fMix.y, wht = eye.a * side;
      float sh = side * (1.0 - wht) * (1.0 - smoothstep(0.04, 0.27, length((dd - vec2(sd * 0.03, 0.11)) * vec2(0.85, 1.55)))); c = mix(c, c * vec3(0.95, 0.6, 0.72), 0.85 * sh);
      float lid = wht * smoothstep(lidY - aw, lidY + aw, fq.y); c = mix(c, mix(vec3(0.5, 0.22, 0.33), vec3(0.66, 0.34, 0.45), smoothstep(lidY, lidY + 0.07, fq.y)), lid);
      float ll = wht * (1.0 - smoothstep(0.019, 0.019 + aw * 2.0, abs(fq.y - lidY + 0.006)));
      float wy = pc.y + 0.0 - 0.11 * 0.18 - 0.12 * fMix.y, wing = side * fCone(fq, vec2(pc.x + sd * 0.16, wy - 0.004), vec2(pc.x + sd * 0.32, wy + 0.085), 0.026, 0.003);
      float brow = side * max(fCone(fq, vec2(sd * 0.14, pc.y + 0.22), vec2(sd * 0.46, pc.y + 0.35), 0.048, 0.04), fCone(fq, vec2(sd * 0.46, pc.y + 0.35), vec2(sd * 0.67, pc.y + 0.29), 0.04, 0.014));
      c = mix(c, vec3(0.05, 0.015, 0.03), max(ll, wing)); c = mix(c, vec3(0.45, 0.17, 0.24), brow); dotK = max(dotK, max(max(ll, wing), max(brow, lid))); } }
  c = mix(c, vec3(0.016, 0.0025, 0.007), lsh);
  vec4 mA""")
# the eye patch (fLash.z): the slime's black leather over the right eye (a raised rim, stitches, a shine, an inked edge), on a strap drawn
# in the face's own space, from high on the far side of the forehead down across the patch and away over the side of the head
rep("""  c = mix(c, vec3(0.016, 0.0025, 0.007), lsh);
  vec4 mA = texture2D(fCol, fCell(fCells.y, cuv))""",
"""  c = mix(c, vec3(0.016, 0.0025, 0.007), lsh);
  if (fLash.z > 0.0) {
    vec2 sdv = normalize(vec2(1.9, -0.8)); float sb = abs(dot(fq - vec2(-0.92, 0.74), vec2(-sdv.y, sdv.x))), saa = fwidth(sb) * 1.25 + 1e-4, sfd = (1.0 - smoothstep(0.88, 0.97, max(abs(fq.x), abs(fq.y)))) * fLash.z;
    float band = (1.0 - smoothstep(0.042 - saa, 0.042 + saa, sb)) * sfd, bed = (1.0 - smoothstep(0.058 - saa, 0.058 + saa, sb)) * sfd;
    c = mix(c, vec3(0.016, 0.0025, 0.007), bed); c = mix(c, mix(vec3(0.04, 0.025, 0.032), vec3(0.1, 0.07, 0.08), 1.0 - smoothstep(0.0, 0.03, sb)), band);
    vec2 pq = (fq - vec2(0.4, 0.15)) / vec2(0.37, 0.4); float pr = length(vec2(pq.x, pq.y * (pq.y > 0.0 ? 1.1 : 0.94))), pa = fwidth(pr) * 1.25 + 1e-4;
    float pb = (1.0 - smoothstep(1.0 - pa, 1.0 + pa, pr)) * fLash.z;
    vec3 pcol = mix(vec3(0.03, 0.019, 0.025), vec3(0.075, 0.05, 0.06), smoothstep(0.79 - pa, 0.84 + pa, pr));
    float sh = 1.0 - smoothstep(0.0, 0.52, length(pq - vec2(-0.3, 0.36))); pcol += vec3(0.3, 0.28, 0.32) * sh * sh * 0.65;
    float stc = step(0.55, fract(atan(pq.y, pq.x) * 4.4)) * (1.0 - smoothstep(0.016, 0.036, abs(pr - 0.895))); pcol = mix(pcol, vec3(0.42, 0.33, 0.26), stc * 0.75);
    float pin = smoothstep(0.93 - pa, 0.95 + pa, pr) * (1.0 - smoothstep(1.06 - pa, 1.08 + pa, pr)) * fLash.z;
    c = mix(c, pcol, pb); c = mix(c, vec3(0.016, 0.0025, 0.007), pin * 0.95); em.r *= 1.0 - pb; lsh = max(lsh, max(max(bed, pb), pin));
  }
  vec4 mA = texture2D(fCol, fCell(fCells.y, cuv))""")
out = ("// ---------- the axolotl (Roll Model's character): its runtime, made from the axolotl pipeline's axo.js by tools/mk_axo_embed.py ----------\n"
       "const AXO = (() => {\n" + s.rstrip() + "\nreturn { " + ', '.join(dict.fromkeys(names)) + " };\n})();\n")
open(OUT, 'w').write(out)
print('ok', len(out), 'exports', len(set(names)))
