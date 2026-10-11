
// ---------------- shader pieces ----------------
// vertex: the canonical place and the material data through to the fragment, the face's frame from the REST position (so the face rides the
// head rigidly), and the soft-body jelly layer on the skinned position (breathing, squash / stretch, lag, ripple; the head stays rigid)
const VERT_PARS = `
attribute vec4 cpos, jelly, fill, mat;
uniform float uCpScale;
uniform vec4 uJelly;   // x breath (m), y squash (-stretch .. +squash), z body height (m), w ripple (m)
uniform vec4 uLag;     // xyz: lag offset of the soft body (object space, m), w: time
uniform vec4 uHead;    // xyz: the face sphere's centre (rest, object space), w: its radius
uniform vec4 uFaceP;   // x the face centre's pitch, y the half angle of a face cell, z horizontal squeeze, w on
uniform float uCoatMix;
varying vec3 vCp, vFace; varying vec4 vJelly, vFill, vMat; varying float vAlong, vFillO;`;
const VERT_MAIN = `
{
  vCp = cpos.xyz * uCpScale; vAlong = cpos.w * uCpScale; vJelly = jelly; vFill = fill; vMat = mat; vFillO = mix(fill.x, fill.y, uCoatMix);
  vec3 d = position - uHead.xyz; float yw = atan(d.x, d.z), pt = atan(d.y, length(d.xz));
  vFace = vec3(yw / (uFaceP.y * uFaceP.z), (pt - uFaceP.x) / uFaceP.y, smoothstep(-0.05, 0.3, d.z / uHead.w) * smoothstep(0.72, 0.95, jelly.w) * (1.0 - smoothstep(0.2, 0.45, mat.y)) * uFaceP.w);
  float soft = 1.0 - jelly.w, h = clamp(transformed.y / uJelly.z, 0.0, 1.0);
  transformed += objectNormal * (jelly.x * uJelly.x + uJelly.w * soft * sin(position.x * 23.0 + position.y * 17.0 + uLag.w * 9.0) * sin(position.z * 19.0 - uLag.w * 7.0));
  float s = uJelly.y * soft; transformed.y *= 1.0 - s; transformed.xz *= 1.0 + 0.5 * s;
  transformed += uLag.xyz * soft * h;
}`;
const FRAG_PARS = `
uniform vec3 uSkin, uBelly, uSpot, uGill, uGillTip, uFinCore, uFinGlow, uPaint; uniform vec4 uCoat, uDetail, uDetail2; uniform float uCoatMix;
uniform sampler2D fCol, fMsk; uniform vec4 fCells, fMix, fPupil, fComp, fLash; uniform vec3 fIris; uniform float fStyle; uniform vec3 uKeyDir; uniform float uDebug, uFadeK, uIsCrawl; uniform vec4 uSwap;
varying vec3 vCp, vFace; varying vec4 vJelly, vFill, vMat; varying float vAlong, vFillO;
float sCoatM = 0.0, faceInk = 0.0, sEyeM = 0.0, sDrawM = 0.0, sGill = 0.0, sFin = 0.0, sBelly = 0.0, sSpot = 0.0, sAO = 0.0;
float aHash(vec3 p) { p = fract(p * vec3(0.1031, 0.1030, 0.0973)); p += dot(p, p.yzx + 33.33); return fract((p.x + p.y) * p.z); }
vec3 aHash3(vec3 p) { p = fract(p * vec3(0.1031, 0.1030, 0.0973)); p += dot(p, p.yxz + 33.33); return fract((p.xxy + p.yxx) * p.zyx); }
float aNoise(vec3 p) { vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(aHash(i), aHash(i + vec3(1.0, 0.0, 0.0)), f.x), mix(aHash(i + vec3(0.0, 1.0, 0.0)), aHash(i + vec3(1.0, 1.0, 0.0)), f.x), f.y),
             mix(mix(aHash(i + vec3(0.0, 0.0, 1.0)), aHash(i + vec3(1.0, 0.0, 1.0)), f.x), mix(aHash(i + vec3(0.0, 1.0, 1.0)), aHash(i + vec3(1.0, 1.0, 1.0)), f.x), f.y), f.z); }
// speckle spots: each cell of a jittered grid may hold one soft round spot (its size and whether it is there are random; dens is the share
// of cells that have one); a little noise breaks the circles; spots smaller than a pixel fade to their average cover instead of shimmering
float aSpots(vec3 p, float scale, float dens, float rmin, float rmax) {
  vec3 q = p * scale, i = floor(q), f = fract(q); float cov = 0.0, wob = (aNoise(q * 2.7) - 0.5) * 0.16, fw = length(fwidth(q));
  for (int z = -1; z <= 1; z++) for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) {
    vec3 o = vec3(float(x), float(y), float(z)), c = i + o; float pres = aHash(c + 17.31);
    if (pres > dens) continue;
    vec3 hp = aHash3(c); float r = mix(rmin, rmax, fract(pres * 7.13 + hp.x * 3.1)), dd = length(o + 0.2 + 0.6 * hp - f) + wob;
    float aa = 0.5 * fw + 0.02; cov = max(cov, 1.0 - smoothstep(r - aa, r + aa, dd));
  }
  float mean = dens * 3.1416 * (rmin + rmax) * (rmin + rmax) * 0.25 * 1.2;
  return mix(cov, min(mean, 1.0), smoothstep(0.35, 0.9, fw));
}
// bump from a height in metres, with the exact slope (unnormalized derivatives, as the game's skin bump): the same relief at any distance
vec3 aBump(vec3 sp, vec3 sn, float h) { vec3 dpx = dFdx(sp), dpy = dFdy(sp), r1 = cross(dpy, sn), r2 = cross(sn, dpx); float det = dot(dpx, r1);
  if (abs(det) < 1e-14) return sn; vec3 g = (dFdx(h) * r1 + dFdy(h) * r2) / det; float gl = length(g); if (gl > 0.9) g *= 0.9 / gl; return normalize(sn - g); }
vec2 fCell(float c, vec2 uv){ float col = mod(c, 4.0), row = floor(c * 0.25 + 0.01); return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) * 0.2); }
float fCone(vec2 p, vec2 a, vec2 b, float w0, float w1) { vec2 ab = b - a; float t = clamp(dot(p - a, ab) / dot(ab, ab), 0.0, 1.0); float d = length(p - a - ab * t) - mix(w0, w1, t); return 1.0 - smoothstep(-0.004, 0.012, d); }
float coatField(vec3 sp, float sy){ vec3 cq = sp * 5.0 + uCoat.y;
  float ch = 0.5 + 0.25 * sin(cq.x * 1.7 + sin(cq.y * 2.3)) * sin(cq.z * 1.9 + sin(cq.x * 1.3)) + 0.25 * sin(cq.y * 3.1 + cq.z * 1.1 + cq.x * 0.7);
  return clamp(0.55 * ch + 0.45 * sy, 0.0, 1.0); }`;
// the skin: base tone, dorsal mottling, the belly, the tail fin's bands, spots, gill frills, cavities
const SKIN_FS = `
{
  vec3 cp = vCp; float belly = vJelly.x, tail = vJelly.y, thin = vJelly.z;
  float ao = vFill.z, finh = vMat.x, gill = vMat.y, sd = vMat.w;
  float n1 = aNoise(cp * 4.2), n2 = aNoise(cp * 11.0 + 7.1), n3 = aNoise(cp * 31.0 + 3.7);
  vec3 col = uSkin * (0.9 + 0.14 * n1 + 0.06 * n2);
  float mot = smoothstep(0.5, 0.78, aNoise(cp * 7.5 + 11.0)) * (1.0 - belly) * (1.0 - gill);   // soft darker patches on the back
  col *= 1.0 - 0.1 * mot;
  float bk = smoothstep(0.1, 0.85, belly + 0.1 * (n2 - 0.5)); col = mix(col, uBelly * (0.96 + 0.06 * n1), bk); sBelly = bk;
  // the tail fin: a darker blue-grey core band, the lower edge glowing, the spotted upper crest stays skin
  float core = tail * exp(-pow((finh - 0.4) / 0.19, 2.0)), glowE = tail * (1.0 - smoothstep(0.0, 0.24, finh));
  col = mix(col, uFinCore * (0.9 + 0.2 * n2), 0.78 * core); col = mix(col, uFinGlow, 0.5 * glowE); sFin = max(core, glowE);
  // speckle spots, two sizes (the canonical body's metres: the standing body is 1.75 tall)
  float dens = sd * uDetail.z;
  float sp = max(aSpots(cp, uDetail.y, 0.7 * dens, 0.17, 0.36), 0.92 * aSpots(cp + 9.7, uDetail.y * 2.3, 0.78 * dens, 0.15, 0.3));
  sp *= 1.0 - 0.75 * bk; col = mix(col, uSpot * (0.82 + 0.36 * n3), sp); sSpot = sp;
  // the gill frills: saturated, lighter toward the thin tips, fine filament streaks
  float fil = 0.5 + 0.5 * sin(vAlong * 480.0 + n2 * 8.0 + n3 * 4.0);
  vec3 gc = mix(uGill * (0.85 + 0.3 * n2), uGillTip, clamp(0.45 * vFill.w + 0.22 * fil * gill, 0.0, 1.0));
  col = mix(col, gc, gill); sGill = gill;
  col *= 1.0 - 0.22 * ao; sAO = ao;
  diffuseColor.rgb = col;
}`;
// the face: the game's slime face shader (eye layer or blink, the eye styles, pupils where the whites show, then the mouth)
const FACE_FS = `
if (vFace.z > 0.01 && abs(vFace.x * fComp.x) < 0.985 && abs(vFace.y * fComp.y) < 0.985) {
  vec2 fq = vFace.xy * fComp.xy; vec2 cuv = fq * 0.5 + 0.5;
  float sqd = (fStyle > 0.5 && fStyle < 1.5) ? 1.0 : 0.0, zmb = fStyle > 2.5 ? 1.0 : 0.0; vec2 fqe = fq; if (sqd > 0.5) { float sd0 = fq.x < 0.0 ? -1.0 : 1.0; vec2 pc0 = vec2(sd0 * 0.4, 0.16); vec2 l = fq - pc0; l.y = l.y * 1.1 + 0.01; l.x = (l.x + l.y * sd0 * 0.2) * 0.97; fqe = pc0 + l; }
  vec2 cuvE = fqe * 0.5 + 0.5;
  vec4 eA = texture2D(fCol, fCell(fCells.x, cuvE)), eB = texture2D(fCol, fCell(fCells.z, cuvE)), eye = mix(eA, eB, fMix.x);
  vec3 emL = mix(texture2D(fMsk, fCell(fCells.x, cuvE)).rgb, texture2D(fMsk, fCell(fCells.z, cuvE)).rgb, fMix.x); vec2 em = emL.rg;
  vec4 bl = texture2D(fCol, fCell(fMix.w, cuvE)); eye = mix(eye, bl, fMix.y); em *= 1.0 - fMix.y;
  float dotK = 0.0; if (fStyle > 1.5 && fStyle < 2.5) { eye.a = 0.0; em = vec2(0.0); }
  if (zmb > 0.5) eye.rgb = eye.rgb * vec3(0.78, 0.9, 0.6) + vec3(0.05, 0.06, 0.0) * eye.a;
  float lsh = 0.0; if (fLash.x + fLash.y > 0.0) lsh = mix(emL.b, texture2D(fMsk, fCell(fMix.w, cuvE)).b, fMix.y) * (fq.x < 0.0 ? fLash.x : fLash.y);
  vec3 c = mix(diffuseColor.rgb, eye.rgb, eye.a);
  if (sqd > 0.5) { float d1 = 0.0; for (int k = 0; k < 16; k++) { float a = float(k) * 0.3927; d1 = max(d1, texture2D(fCol, fCell(0.0, cuvE + vec2(cos(a) * 0.05, sin(a) * 0.052 + 0.026))).a); }
    float hole = texture2D(fCol, fCell(0.0, cuvE)).a, rim = clamp(d1 - hole, 0.0, 1.0), sp = 0.0;
    for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16); vec2 dw = normalize(vec2(sd, 0.45)); vec2 a = pc + dw * 0.18, b = a + dw * 0.26; sp = max(sp, fCone(fqe, a, b, 0.1, 0.004)); }
    float mk = max(rim, sp); c = mix(c, vec3(0.03, 0.012, 0.02), mk);
    float lidLine = eye.a * step(dot(eye.rgb, vec3(0.333)), 0.3); c = mix(c, vec3(0.03, 0.012, 0.02), hole * (1.0 - eye.a) * (1.0 - mk)); c = mix(c, vec3(0.46, 0.3, 0.38), hole * lidLine * (1.0 - mk)); dotK = max(mk, hole * (1.0 - eye.a)); }
  if (fStyle > 1.5 && fStyle < 2.5) { float bk = 1.0 - fMix.y * 0.92; for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy * 0.6; vec2 dd = (fq - pc) * vec2(1.0, 1.0 / max(0.08, bk)); float r = length(dd);
    float dk = 1.0 - smoothstep(0.125, 0.145, r); c = mix(c, vec3(0.03, 0.012, 0.02), dk); float hl = 1.0 - smoothstep(0.03, 0.046, length((fq - pc - vec2(-0.045, 0.05)) * vec2(1.0, 1.0 / max(0.08, bk)))); c = mix(c, vec3(1.0), hl * dk); dotK = max(dotK, dk); } }
  for (int i = 0; i < 2; i++) {
    float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy, dd = (fqe - pc) * vec2(1.0, 0.92); float r = length(dd), ri = mix(0.165, 0.235, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.92 : 1.14, zmb), rp = mix(0.092, 0.11, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.5 : 0.78, zmb);
    vec3 irC = mix(fIris, vec3(0.42, 0.6, 0.3), zmb);
    float ia = (1.0 - smoothstep(ri - 0.014, ri, r)) * em.r;
    vec3 ic = mix(irC, irC * 0.2, smoothstep(0.0, ri, r)); ic = mix(ic, vec3(0.004, 0.002, 0.003), 1.0 - smoothstep(rp - 0.012, rp, r));
    ic += irC * 1.12 * smoothstep(ri * 0.35, ri * 0.95, r) * smoothstep(0.2, -0.6, dd.y / ri) * (1.0 - smoothstep(ri * 0.95, ri, r));
    ic = mix(ic, vec3(0.72, 0.78, 0.62), zmb * 0.42 * smoothstep(rp, ri * 0.9, r) * (0.6 + 0.4 * sin(atan(dd.y, dd.x) * 11.0 + r * 60.0)));
    ic = mix(ic, vec3(0.02, 0.008, 0.014), sqd * smoothstep(ri - 0.032, ri - 0.012, r));
    c = mix(c, ic * (1.0 - 0.55 * em.g), ia);
    float cl = (1.0 - smoothstep(mix(0.03, 0.05, sqd), mix(0.042, 0.06, sqd), length(fqe - pc - vec2(-0.055, 0.06) * (1.0 + 0.3 * sqd) * fPupil.z))) + 0.8 * (1.0 - sqd) * (1.0 - smoothstep(0.012, mix(0.02, 0.026, sqd), length(fqe - pc - vec2(0.05, -0.05) * (1.0 + 0.3 * sqd) * fPupil.z)));
    c = mix(c, vec3(1.0), clamp(cl, 0.0, 1.0) * (1.0 - 0.75 * zmb) * em.r * (1.0 - 0.85 * em.g));
  }
  if (zmb > 0.5) { for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w), dd = fq - pc; float r = length(dd), an = atan(dd.y, dd.x);
      float vn = smoothstep(0.86, 0.99, sin(an * 7.0 + sin(r * 38.0 + an * 3.0) * 0.7 + sd * 1.3)) * smoothstep(0.12, 0.2, r) * (1.0 - smoothstep(0.3, 0.42, r)); c = mix(c, vec3(0.55, 0.03, 0.04), vn * eye.a * (1.0 - em.r * 0.7));
      float lidY = pc.y + (i == 0 ? 0.05 : 0.13) - sd * dd.x * 0.22, lid = eye.a * smoothstep(lidY - 0.012, lidY + 0.012, fq.y), crease = eye.a * (1.0 - smoothstep(0.0, 0.03, abs(fq.y - lidY)));
      c = mix(c, vec3(0.1, 0.045, 0.08), lid); c = mix(c, vec3(0.36, 0.2, 0.28), crease * 0.9);
      float ring = (1.0 - eye.a) * smoothstep(0.52, 0.3, length(dd * vec2(0.9, 1.35))) * smoothstep(0.02, -0.2, dd.y); c = mix(c, c * vec3(0.42, 0.34, 0.5), ring * 0.8); } }
  c = mix(c, vec3(0.016, 0.0025, 0.007), lsh);
  vec4 mA = texture2D(fCol, fCell(fCells.y, cuv)), mB = texture2D(fCol, fCell(fCells.w, cuv)), mo = mix(mA, mB, fMix.x) * fMix.z * (1.0 - zmb);
  c = mix(c, mo.rgb, mo.a);
  float zma = 0.0; if (zmb > 0.5) { float yl = -0.3 + 0.08 * fq.x - 0.12 * fq.x * fq.x, dl = fq.y - yl, inx = smoothstep(0.48, 0.44, abs(fq.x)), fw = fwidth(fq.y) + 0.004;
    float line = (1.0 - smoothstep(0.02 - fw, 0.02 + fw, abs(dl))) * inx, st = (1.0 - smoothstep(0.01, 0.01 + fw, abs(mod(fq.x + 0.075, 0.15) - 0.075))) * (1.0 - smoothstep(0.06, 0.06 + fw, abs(dl))) * inx * step(0.08, abs(fq.x));
    float tooth = 0.0; for (int i = 0; i < 3; i++) { float cx = i == 0 ? -0.2 : i == 1 ? 0.03 : 0.24, w = 0.036 * (1.0 - clamp(-dl / 0.09, 0.0, 1.0)); tooth = max(tooth, (1.0 - smoothstep(w - fw, w + fw, abs(fq.x - cx))) * step(-0.09, dl) * step(dl, 0.0)); }
    zma = max(line, st); c = mix(c, vec3(0.03, 0.012, 0.02), zma); c = mix(c, vec3(0.93, 0.9, 0.78), tooth * (1.0 - line)); zma = max(zma, tooth); }
  faceInk = max(max(max(max(eye.a, mo.a), lsh), dotK), zma) * vFace.z; diffuseColor.rgb = mix(diffuseColor.rgb, c, vFace.z); sEyeM = em.r * vFace.z;
}
sDrawM = faceInk;`;
// the paint coat: rising by the fill order (the crawl's from the ground contacts, the stand's from the feet), in lumps; wet paint levels the skin
const COAT_FS = `
if (uCoat.x > 0.001) {
  float ch = coatField(vCp, vFillO), cv = uCoat.x * 1.08 - 0.04;
  sCoatM = smoothstep(ch - 0.035, ch + 0.035, cv);
  vec3 pc = max(mix(vec3(dot(uPaint, vec3(0.2126, 0.7152, 0.0722))), uPaint, 1.1), vec3(0.0)) * 0.8;
  diffuseColor.rgb = mix(diffuseColor.rgb, pc, sCoatM) * (1.0 - 0.3 * (1.0 - smoothstep(0.0, 0.06, abs(cv - ch))) * step(uCoat.x, 0.995));
  faceInk *= 1.0 - sCoatM; sDrawM = faceInk;
}`;
// the relief: bumpy amphibian skin and pores (softer on the belly and the face), wrinkle bands across the joints, the gill filaments,
// the spots a hair lower; flat under the paint; fine octaves fade out where a pixel covers them (no shimmer)
const BUMP_FS = `
{
  vec3 cp = vCp; float fw = length(fwidth(cp)), k1 = 1.0 - smoothstep(0.25, 0.8, fw * 140.0), k2 = 1.0 - smoothstep(0.25, 0.8, fw * 330.0), k3 = 1.0 - smoothstep(0.25, 0.8, fw * 2.0 / 0.011);
  float amp = uDetail.x * (1.0 - 0.6 * sBelly) * (1.0 - 0.8 * faceInk) * (1.0 - sCoatM);
  float h = (aNoise(cp * 140.0) * 0.65 * k1 + aNoise(cp * 330.0 + 5.0) * 0.35 * k2) * amp;
  h += uDetail.w * vMat.z * k3 * (0.5 + 0.5 * sin(vAlong * 571.2 + aNoise(cp * 60.0) * 2.5)) * (1.0 - sCoatM) * (1.0 - faceInk);
  h += 0.35 * uDetail.x * sGill * (0.5 + 0.5 * sin(vAlong * 480.0 + aNoise(cp * 11.0 + 7.1) * 8.0)) * k3;
  h -= 0.5 * uDetail.x * sSpot;
  normal = aBump(-vViewPosition, normal, h);
}`;
const LIT_FS = `
{ float wet = max(sCoatM, 0.45 * uCoat.z);
  float rough = mix(0.52, 0.32, sBelly); rough = mix(rough, 0.52, sGill * 0.7); rough = mix(rough, 0.34, sFin * 0.6); rough = mix(rough, 0.72, sDrawM);
  material.roughness = min(max(mix(rough, 0.16, wet), 0.0525) + geometryRoughness, 1.0);
#ifdef USE_CLEARCOAT
  material.clearcoat = mix(0.12 + 0.28 * sBelly + 0.12 * sFin, 1.0, sCoatM) * (1.0 - 0.9 * sDrawM);
  material.clearcoatRoughness = min(max(mix(0.46 - 0.18 * sBelly, 0.07, sCoatM), 0.0525) + geometryRoughness, 1.0);
#endif
#ifdef USE_SHEEN
  material.sheenColor = uBelly * (0.5 * sBelly + 0.15 * sGill) * (1.0 - sCoatM); material.sheenRoughness = 0.42;
#endif
}`;
const LOOK_FS = `
{ float occ = sAO * (1.0 - 0.3 * sCoatM), ink = sDrawM * (1.0 - sCoatM);
  reflectedLight.indirectDiffuse *= 1.0 - 0.8 * occ; reflectedLight.directDiffuse *= 1.0 - 0.4 * occ; reflectedLight.indirectSpecular *= 1.0 - 0.85 * occ; reflectedLight.directSpecular *= 1.0 - 0.6 * occ;
#ifdef USE_CLEARCOAT
  clearcoatSpecularIndirect *= 1.0 - 0.85 * occ; clearcoatSpecularDirect *= 1.0 - 0.6 * occ;
#endif
  // the drawn face: matte ink, lit a little from within like the game's (it reads at any light)
  reflectedLight.directDiffuse *= 1.0 - 0.45 * ink; reflectedLight.indirectDiffuse *= 1.0 - 0.45 * ink; reflectedLight.directSpecular *= 1.0 - 0.9 * ink; reflectedLight.indirectSpecular *= 1.0 - 0.9 * ink;
  totalEmissiveRadiance += diffuseColor.rgb * ink * 0.5;
  // light through the thin parts (fin, frills, toe tips), in the skin's own deeper colour; the free edges of fins and frills lit
  vec3 vd = normalize(vViewPosition), kd = normalize(uKeyDir);
  float thin = vJelly.z * (1.0 - sCoatM) * (1.0 - ink);
  float back = pow(saturate(dot(vd, -normalize(kd + nonPerturbedNormal * 0.35))), 3.0), wrap = saturate((dot(nonPerturbedNormal, kd) + 0.75) / 1.75);
  vec3 deep = pow(max(diffuseColor.rgb, vec3(0.0)), vec3(1.35)) * 1.7;
  totalEmissiveRadiance += deep * thin * (0.8 * back + 0.16 * wrap) * (1.0 - 0.45 * sGill);
  float edge = 1.0 - saturate(dot(nonPerturbedNormal, vd));
  totalEmissiveRadiance += mix(diffuseColor.rgb, uFinGlow, 0.5) * vFill.w * (0.18 + 0.7 * back) * 0.55 * (1.0 - sCoatM) * (1.0 - ink);
  // a soft rim along the body's outline, a whisper of light on the moist skin
  float upk = saturate(dot(nonPerturbedNormal, normalize((viewMatrix * vec4(0.0, 1.0, 0.0, 0.0)).xyz)) + 0.4);
  totalEmissiveRadiance += mix(diffuseColor.rgb, vec3(1.0, 0.95, 0.92), 0.35) * pow(edge, 3.0) * (0.5 + 0.5 * upk) * 0.22 * (1.0 - ink) * (1.0 - 0.5 * sCoatM);
}`;
// a mesh fading in or out (the stand / crawl swap): a screen-space dither, so it is always drawn opaque and sorted right
// two ways a mesh shares the screen with the other one, both by a screen-space dither (always opaque, sorted right, no see-through double
// image): uFadeK >= 0 keeps the pixels whose threshold is under it, < 0 the others (a plain complementary dissolve); during the stand <->
// crawl morph (uSwap.x on) the crawl's share depends on where on the body the pixel is: each region changes over at the point of the morph
// (uSwap.y, the skeleton's crawl share) where both bodies are clean there: the hips, legs and tail early, the chest, arms and head late.
// The canonical place (vCp) is the same body point on both meshes, so the two stay complementary
const FADE_FS = `
{ vec2 fp = floor(gl_FragCoord.xy); float th = fract(52.9829189 * fract(dot(fp, vec2(0.06711056, 0.00583715))));
  if (uSwap.x > 0.5) {
    float tau = clamp((vCp.y - 0.55) / 0.35, 0.0, 1.0) * (1.0 - smoothstep(-0.25, -0.45, vCp.z)), lo = uSwap.z + uSwap.w * tau;
    float c = smoothstep(lo, lo + 0.12, uSwap.y);
    if (uIsCrawl > 0.5 ? th >= c : th < c) discard;
  } else if (uFadeK < 0.999) { if (uFadeK >= 0.0 ? th >= uFadeK : th < -uFadeK) discard; } }`;
// debug views (the material breakdown): 1 roughness, 2 the detail normal under one light, 3 occlusion, 4 regions (belly red / thin green / gill blue), 5 spots, 6 canonical place
const DEBUG_FS = `
if (uDebug > 0.5) {
  if (uDebug < 1.5) gl_FragColor = vec4(vec3(material.roughness), 1.0);
  else if (uDebug < 2.5) { float l = 0.15 + 0.85 * max(0.0, dot(normal, normalize(vec3(0.4, 0.7, 0.6)))); gl_FragColor = vec4(vec3(l), 1.0); }
  else if (uDebug < 3.5) gl_FragColor = vec4(vec3(1.0 - sAO), 1.0);
  else if (uDebug < 4.5) gl_FragColor = vec4(sBelly, vJelly.z, sGill, 1.0);
  else if (uDebug < 5.5) gl_FragColor = vec4(vec3(1.0 - sSpot), 1.0);
  else gl_FragColor = vec4(fract(vCp * 4.0), 1.0);
}`;

// ---------------- the palette: every colour from the team colour ----------------
const _c = new THREE.Color(), _hsl = {};
function hsl(h, s, l) { return new THREE.Color().setHSL(((h % 1) + 1) % 1, Math.max(0, Math.min(1, s)), Math.max(0, Math.min(1, l))); }
function mixHue(a, b, t) { let d = b - a; d -= Math.round(d); return a + d * t; }
export function palette(team) {
  _c.set(team); _c.getHSL(_hsl); const h = _hsl.h, s = _hsl.s, l = _hsl.l;
  const slate = 0.64;   // blue-grey
  return {
    skin: hsl(h, 0.5 + 0.2 * s, 0.55 + 0.04 * (l - 0.5)),
    belly: hsl(mixHue(h, 0.09, 0.78), 0.6, 0.72),
    spot: hsl(mixHue(h, slate, 0.72), 0.26, 0.26),
    gill: hsl(h, 0.72 + 0.28 * s, 0.38),
    gillTip: hsl(mixHue(h, 0.97, 0.15), 0.7, 0.6),
    finCore: hsl(mixHue(h, slate, 0.75), 0.3, 0.25),
    finGlow: hsl(mixHue(h, 0.04, 0.45), 0.85, 0.58),
  };
}
let SHEETS = null;
function faceSheets(C) {
  if (SHEETS) return SHEETS; const sh = makeFaceSheets(C);
  const col = new THREE.CanvasTexture(sh.col), msk = new THREE.CanvasTexture(sh.msk); col.colorSpace = THREE.SRGBColorSpace; col.anisotropy = 4; msk.colorSpace = THREE.NoColorSpace;
  for (const t of [col, msk]) { t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; }
  return SHEETS = { col, msk };
}

// ---------------- the character's look: shared uniforms for its two meshes, the face's state ----------------
export class Look {
  constructor(opts = {}) {
    const sh = faceSheets(opts.faceCell || 320), v3 = () => ({ value: new THREE.Color() });
    this.U = {
      uSkin: v3(), uBelly: v3(), uSpot: v3(), uGill: v3(), uGillTip: v3(), uFinCore: v3(), uFinGlow: v3(), uTeam: v3(),
      uPaint: { value: new THREE.Color(opts.color || 0xff6b8a) }, uCoat: { value: new THREE.Vector4(0, Math.random() * 40, 0, 0) }, uCoatMix: { value: 1 },
      uJelly: { value: new THREE.Vector4(0, 0, 1.6, 0) }, uLag: { value: new THREE.Vector4(0, 0, 0, 0) }, uFaceP: { value: new THREE.Vector4(FACE.pitch, FACE.half, FACE.squeeze, 1) },
      fCol: { value: sh.col }, fMsk: { value: sh.msk }, fCells: { value: new THREE.Vector4(0, 8, 0, 8) }, fMix: { value: new THREE.Vector4(0, 0, 1, 6) }, fPupil: { value: new THREE.Vector4(0, -0.03, 1, 0) },
      fComp: { value: new THREE.Vector4(1, 1, 0, 0) }, fLash: { value: new THREE.Vector4(0, 0, 0, 0) }, fIris: { value: new THREE.Vector3(0.14, 0.045, 0.28) }, fStyle: { value: 0 },
      uKeyDir: { value: new THREE.Vector3(0.3, 0.6, 0.7) }, uDebug: { value: 0 }, uSwap: { value: new THREE.Vector4(0, 0, 0.18, 0.26) },
      // skin detail: x relief amplitude (m), y spot cells per metre, z spot amount, w wrinkle depth (m)
      uDetail: { value: new THREE.Vector4(0.0009, 26, 1.0, 0.0007) }, uDetail2: { value: new THREE.Vector4(0, 0, 0, 0) },
    };
    this.meshU = {};   // per-mesh uniforms (the fade), by mesh name
    this.fangs = false; this.expr = 'neutral'; this.exprB = 'neutral'; this.exprK = 1; this.blinkT = 1 + Math.random() * 2; this.blinkK = 0; this.flut = 0; this.flutT = 0;
    this.look = [0, 0]; this.dart = [0, 0]; this.dartT = 0.5; this.att = { t: 1 + Math.random() * 2, eye: [0, 0] }; this.t = 0; this.emote = null; this.turnV = 0; this.tbCool = 0;
    this.setColor(opts.color || 0xff6b8a); this.setIris(opts.iris || 'violet'); this.setEyeStyle(opts.eyes || 'round');
  }
  setColor(c) { const p = palette(c); const U = this.U; U.uTeam.value.set(c); U.uPaint.value.set(c);
    for (const [k, u] of [['skin', 'uSkin'], ['belly', 'uBelly'], ['spot', 'uSpot'], ['gill', 'uGill'], ['gillTip', 'uGillTip'], ['finCore', 'uFinCore'], ['finGlow', 'uFinGlow']]) U[u].value.copy(p[k]);
    return this; }
  setIris(k) { const e = EYE_COLS[k]; if (e) this.U.fIris.value.set(...e.lin); else { const c = new THREE.Color(k); this.U.fIris.value.set(c.r, c.g, c.b); } this.iris = k; return this; }
  setEyeStyle(k) { this.U.fStyle.value = typeof k === 'string' ? (EYE_STYLE_K[k] || 0) : k; return this; }
  setPaint(level) { this.U.uCoat.value.x = level; return this; }
  setFangs(on) { this.fangs = !!on; return this; }
  setLashes(l, r = l) { this.U.fLash.value.x = l; this.U.fLash.value.y = r; return this; }
  setExpression(name) { if (!(name in EXPR)) name = 'neutral'; if (name === this.exprB) return this; if (this.exprK < 1) this.expr = this.exprK > 0.5 ? this.exprB : this.expr; this.exprB = name; this.exprK = 0; return this; }
  // a short-lived expression (a reaction) that falls back to the current one
  emoteFor(name, dur = 0.8) { if (!this.emote) this.emote = { back: this.exprB }; this.emote.t = dur; this.setExpression(name); return this; }
  blink() { this.blinkK = 0.13; return this; }
  flutter(n = 3) { this.flut = n; this.flutT = 0; return this; }
  // (v6 put 3D eyes on the heads; v7 draws the game's eyes on the skin. Kept so v6 callers do not break: it does nothing.)
  attachEyes() { return this; }
  setFade(which, fade) { this.fades = this.fades || {}; this.fades[which] = fade; const u = this.meshU[which]; if (u) u.uFadeK.value = fade; }
  // the stand <-> crawl morph's change-over (u: the skeleton's crawl share; null: off). See FADE_FS
  setMorphSwap(u) { const S = this.U.uSwap.value; if (u === null || u === undefined) S.x = 0; else { S.x = 1; S.y = u; } }
  // the stand / crawl swap: k of the pixels show the incoming mesh, exactly the rest the outgoing one (complementary dither)
  setSwap(inc, out, k) { const a = this.meshU[inc], b = this.meshU[out]; if (a) a.uFadeK.value = k >= 0.999 ? 1 : Math.max(0, k); if (b) b.uFadeK.value = k <= 0.001 ? 1 : k >= 0.999 ? 0 : -k; }
  // the head's turn rate (rad/s) from the animator: a quick turn brings a blink, as the game's slime does
  turnRate(w) { this.turnV = w; }
  // per frame: expression crossfade and reactions, blinks (double blinks now and then, flutters, a blink with a fast turn), glances and darts,
  // pupils easing toward the look target (x right, y up, in face units), head squash compensation
  update(dt, look, squash = 0) {
    this.t += dt; const U = this.U;
    if (this.emote) { this.emote.t -= dt; if (this.emote.t <= 0) { const b = this.emote.back; this.emote = null; this.setExpression(b); } }
    if (this.exprK < 1) { this.exprK = Math.min(1, this.exprK + dt / 0.12); if (this.exprK >= 1) this.expr = this.exprB; }
    if (this.flut > 0) { this.flutT -= dt; if (this.flutT <= 0) { this.blinkK = 0.075; this.flut--; this.flutT = 0.15; this.blinkT = Math.max(this.blinkT, 1.4); } }
    this.tbCool -= dt; if (Math.abs(this.turnV) > 3.2 && this.tbCool <= 0) { this.blinkK = Math.max(this.blinkK, 0.11); this.tbCool = 1.4; }
    this.blinkT -= dt; if (this.blinkT <= 0) { this.blinkK = 0.13; this.blinkT = Math.random() < 0.22 ? 0.26 : 1.6 + Math.random() * 3.4; } if (this.blinkK > 0) this.blinkK -= dt;
    const A = this.att; A.t -= dt; if (A.t <= 0) { A.t = 1.2 + Math.random() * 2.8; A.eye[0] = (Math.random() * 2 - 1) * 0.1; A.eye[1] = (Math.random() * 2 - 1) * 0.045; if (Math.random() < 0.5) this.blinkK = Math.max(this.blinkK, 0.1); }
    this.dartT -= dt; if (this.dartT <= 0) { this.dartT = 0.35 + Math.random() * 0.9; this.dart[0] = (Math.random() * 2 - 1) * 0.035; this.dart[1] = (Math.random() * 2 - 1) * 0.02; }
    const lx = (look ? look[0] : 0) + A.eye[0] + this.dart[0], ly = (look ? look[1] : 0) + A.eye[1] + this.dart[1];
    this.look[0] += (lx - this.look[0]) * Math.min(1, dt * 26); this.look[1] += (ly - this.look[1]) * Math.min(1, dt * 26);
    const shut = this.blinkK > 0 && !NO_SHUT[this.exprB];
    const pa = pupilOf(this.expr), pb = pupilOf(this.exprB), k = this.exprK, fang = this.fangs ? 6 : 0, ea = EXPR[this.expr], eb = EXPR[this.exprB];
    U.fCells.value.set(ea[0], ea[1] + fang, eb[0], eb[1] + fang); U.fMix.value.set(k, shut ? 1 : 0, 1, 6);
    U.fPupil.value.set(this.look[0], this.look[1], pa.pu + (pb.pu - pa.pu) * k, pa.py + (pb.py - pa.py) * k);
    U.fComp.value.set(1, 1, 0, 0); U.uLag.value.w = this.t;
    if (this.coatMixT !== undefined) U.uCoatMix.value += (this.coatMixT - U.uCoatMix.value) * Math.min(1, dt * 3);
  }
}
// the body material for one mesh of one character (the look's uniforms are shared by the character's two meshes; the head frame, the
// canonical scale, the skinning data and the fade are this mesh's own)
export function axoMaterial(tex, look, meta) {
  const mat = new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.5, metalness: 0, clearcoat: 0.3, clearcoatRoughness: 0.35, sheen: 1, sheenRoughness: 0.42, sheenColor: 0x000000, envMapIntensity: 0.7 });
  const own = { uFadeK: { value: 1 }, uIsCrawl: { value: meta.name === 'crawl' ? 1 : 0 } }; look.meshU[meta.name || ('m' + Object.keys(look.meshU).length)] = own; meta.fadeU = own;
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, look.U, own);
    sh.vertexShader = VERT_PARS + '\n' + sh.vertexShader.replace('#include <skinning_vertex>', '#include <skinning_vertex>\n' + VERT_MAIN);
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\n' + FRAG_PARS)
      .replace('#include <clipping_planes_fragment>', '#include <clipping_planes_fragment>\n' + FADE_FS)
      .replace('#include <color_fragment>', '#include <color_fragment>\n' + SKIN_FS + FACE_FS + COAT_FS)
      .replace('#include <normal_fragment_maps>', '#include <normal_fragment_maps>\n' + BUMP_FS)
      .replace('#include <lights_physical_fragment>', '#include <lights_physical_fragment>\n' + LIT_FS)
      .replace('#include <aomap_fragment>', '#include <aomap_fragment>\n' + LOOK_FS)
      .replace('#include <colorspace_fragment>', '#include <colorspace_fragment>\n' + DEBUG_FS);
    if (meta.dqTex) dqsShader(sh, meta);
    const fc = (meta.face && meta.face.c) || meta.headAbs, fr = (meta.face && meta.face.r) || meta.headr;
    sh.uniforms.uHead = { value: new THREE.Vector4(fc[0], fc[1], fc[2], fr) }; sh.uniforms.uCpScale = { value: meta.cpScale || 4.0 };
  };
  mat.customProgramCacheKey = () => 'axo7-body';
  return mat;
}
