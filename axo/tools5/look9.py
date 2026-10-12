# The v9 look on the axolotl runtime: the premium face material and the thick paint coat, as exact-text edits on the v8 runtime base
# (tools/assets/axo_base_v227.js), so the change is reproducible and every anchor the game's embed builder (tools/mk_axo_embed.py)
# matches by text is kept verbatim: the sly eyes, the eye patch and the wading band it injects still land, and this runtime then
# overrides the injected coat block's result from the skin colour saved just before it (see COAT below).
#   python3 -I look9.py [base = S/tools/assets/axo_base_v227.js] [out = S/fable2/out/axo.js]
# The face: wet glossy eyes (their own low roughness and a full clear coat that follows the bump normal, the specular kept instead of
# killed with the ink), anti-aliased iris and pupil edges, depth in the iris (a limbal ring, fibres, a bright floor, a soft pupil edge with
# a halo), a soft main catchlight with a second small one and a faint wet sheen across the cornea; a soft permanent blush; the face skin
# a touch smoother with a warm sheen and a little light through it (wrap and back light in the skin's deeper colour); softer mouth lines
# in the sheets (lower ink, a soft halo). The coat: a crisp anti-aliased fill line with a rounded paint lip worked out from the signed
# distance to the line in metres (from screen derivatives), lumps in the thick paint, beads of paint splashed just past the edge, a soft
# shadow on the skin under the edge, a deeper saturated paint colour, a glass clear coat on the lumps (the clear coat normal follows the
# bump) and a fresnel sheen with a cheap sky reflection so the wet gloss reads on phones without the clear coat layer too. The wading
# band gets the same treatment (one union of the two paints).
import sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
SRC = sys.argv[1] if len(sys.argv) > 1 else S + '/tools/assets/axo_base_v227.js'
OUT = sys.argv[2] if len(sys.argv) > 2 else S + '/fable2/out/axo.js'
s = open(SRC).read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:100]!r}'
    s = s.replace(old, new)

# ---- v9b: the rest-space frame through to the fragment (for the paint's runs and beads), the soft body's gentle wobble ----
rep("varying vec3 vCp, vFace; varying vec4 vJelly, vFill, vMat; varying float vAlong, vFillO;`;",
    "varying vec3 vCp, vFace; varying vec4 vJelly, vFill, vMat; varying float vAlong, vFillO; varying vec2 vRest;`;")
rep("varying vec3 vCp, vFace; varying vec4 vJelly, vFill, vMat; varying float vAlong, vFillO;\nfloat sCoatM",
    "varying vec3 vCp, vFace; varying vec4 vJelly, vFill, vMat; varying float vAlong, vFillO; varying vec2 vRest;\nfloat sCoatM")
rep("""  float soft = 1.0 - jelly.w, h = clamp(transformed.y / uJelly.z, 0.0, 1.0);
  transformed += objectNormal * (jelly.x * uJelly.x + uJelly.w * soft * sin(position.x * 23.0 + position.y * 17.0 + uLag.w * 9.0) * sin(position.z * 19.0 - uLag.w * 7.0));""",
"""  float soft = 1.0 - jelly.w, h = clamp(transformed.y / uJelly.z, 0.0, 1.0);
  // (v9b: the body's own frame for the paint's runs and beads: across the rest body along the surface, and the rest height)
  { vec3 acr = cross(normal, vec3(0.0, -1.0, 0.0)); acr = normalize(acr + vec3(1e-3, 0.0, 0.0)); vRest = vec2(dot(position, acr), position.y); }
  // (v9b: a gentle wobble of the soft parts, so the body reads as paint; never the head)
  float wob = sin(position.y * 4.1 + position.x * 1.7 + uLag.w * 2.7) * sin(position.z * 3.3 - uLag.w * 1.9);
  transformed += objectNormal * (jelly.x * uJelly.x + uJelly.w * soft * sin(position.x * 23.0 + position.y * 17.0 + uLag.w * 9.0) * sin(position.z * 19.0 - uLag.w * 7.0) + soft * 0.005 * wob * (1.0 - 0.6 * jelly.z));""")
# the runtime keeps the paint's living state in uDetail2 (x the flow, y the coat's high water, z the wade's high water, w how dry)
rep("""    if (this.coatMixT !== undefined) U.uCoatMix.value += (this.coatMixT - U.uCoatMix.value) * Math.min(1, dt * 3);
  }""", """    if (this.coatMixT !== undefined) U.uCoatMix.value += (this.coatMixT - U.uCoatMix.value) * Math.min(1, dt * 3);
    // the paint's living state (v9b): the high water of the coat and of the wading band (they slip down after the level over a couple
    // of seconds: the runs the shader leaves above the edge reach up to them), the flow of the streaks (quicker while it drains) and
    // how dry the skin is (the adapter's wet, uCoat.z, turned round)
    { const c = U.uCoat.value, D2 = U.uDetail2.value, pw = this._pw === undefined ? c.w : this._pw, pc = this._pc === undefined ? c.x : this._pc, dw = c.w - pw, dc = c.x - pc; this._pw = c.w; this._pc = c.x;
      D2.z = dw > 0 ? Math.max(D2.z, c.w) : Math.max(c.w, D2.z - dt * (D2.z - c.w) * 0.45);
      D2.y = dc > 0 ? Math.max(D2.y, c.x) : Math.max(c.x, D2.y - dt * (D2.y - c.x) * 0.55);
      D2.x = (D2.x + dt * (0.5 + 12 * Math.min(0.2, Math.max(0, -dw - dc) / Math.max(dt, 1e-3)))) % 1000; D2.w = 1 - c.z; }
  }""")
# the skin a touch more saturated under the texture (the hue turn untouched; the white belly stays white)
rep("""  float cr = Y + ch.x, cb = Y + ch.y; col = max(vec3(cr, (Y - 0.2126 * cr - 0.0722 * cb) / 0.7152, cb), vec3(0.0));
  float bk = smoothstep(0.1, 0.85, belly); sBelly = bk;""",
"""  float cr = Y + ch.x, cb = Y + ch.y; col = max(vec3(cr, (Y - 0.2126 * cr - 0.0722 * cb) / 0.7152, cb), vec3(0.0));
  col = max(mix(vec3(dot(col, vec3(0.2126, 0.7152, 0.0722))), col, 1.14), vec3(0.0));
  float bk = smoothstep(0.1, 0.85, belly); sBelly = bk;""")
# ---- v9b: the ear lobes hang under gravity. The lobes are rigidly skinned to the gill bones, so without this they turn with the head
# (up and back when it looks up on the jetpack, back in the victory). Each stalk's first joint is turned so the lobe's hang relative to
# the mesh's down stays what it is in rest, whatever the head does: the down direction in the lobe's would-be frame (the head's posed
# frame times the lobe's canonical relative frame, so the lobe's own turn never feeds back) against the down direction in its rest
# frame, as a shortest arc. The spring's flutter, drag and swing go on top; the hang eases off in the ball and the pound ----
rep("""    const g = this.chain.gills, gs = this.gs, hold = this.gillHoldS;
    const cm = hold, lo = 0.4;   // (one head in both states: the same gills, the same motion)""",
"""    const g = this.chain.gills, gs = this.gs, hold = this.gillHoldS;
    { const P = this.P, Fp = P.Fp, hi = P.idx.head, F0 = P.m.stand.F, k = 0.92 * hold * (1 - (this.ballOn || 0));
      if (!this.gillDownRest) { this.gillDownRest = []; for (let j = 0; j < 6; j++) this.gillDownRest.push(new THREE.Vector3(0, -1, 0).applyQuaternion(_q.copy(F0[g[j * 2]]).invert())); }
      if (k > 0.001) for (let j = 0; j < 6; j++) { const i1 = g[j * 2];
        _q.copy(Fp[hi]).multiply(P.Rel[i1]); _v.set(0, -1, 0).applyQuaternion(_q.invert());
        _q2.setFromUnitVectors(this.gillDownRest[j], _v); if (k < 0.999) _q2.slerp(_q.identity(), 1 - k); pose.q[i1].multiply(_q2); } }
    const cm = hold, lo = 0.4;   // (one head in both states: the same gills, the same motion)""")
# ---- shader globals and helpers ----
rep("float sCoatM = 0.0, faceInk = 0.0, sEyeM = 0.0, sDrawM = 0.0, sGill = 0.0, sFin = 0.0, sBelly = 0.0, sSpot = 0.0, sAO = 0.0;",
    "float sCoatM = 0.0, faceInk = 0.0, sEyeM = 0.0, sDrawM = 0.0, sGill = 0.0, sFin = 0.0, sBelly = 0.0, sSpot = 0.0, sAO = 0.0;\n"
    "float sFaceK = 0.0, sCoatH = 0.0, sCoatT = 0.0, sBead = 0.0, sDbgDm = 0.0, sDbgG = 0.0, sCatch = 0.0, sWetK = 0.0; vec3 sPaintC = vec3(0.0);   // v9: face skin, the coat's height (m) and thickness, beads, the paint colour")
rep("""float coatField(vec3 sp, float sy){ vec3 cq = sp * 5.0 + uCoat.y;
  float ch = 0.5 + 0.25 * sin(cq.x * 1.7 + sin(cq.y * 2.3)) * sin(cq.z * 1.9 + sin(cq.x * 1.3)) + 0.25 * sin(cq.y * 3.1 + cq.z * 1.1 + cq.x * 0.7);
  return clamp(0.55 * ch + 0.45 * sy, 0.0, 1.0); }`;""",
"""float coatField(vec3 sp, float sy){ vec3 cq = sp * 5.0 + uCoat.y;
  float ch = 0.5 + 0.25 * sin(cq.x * 1.7 + sin(cq.y * 2.3)) * sin(cq.z * 1.9 + sin(cq.x * 1.3)) + 0.25 * sin(cq.y * 3.1 + cq.z * 1.1 + cq.x * 0.7);
  return clamp(0.55 * ch + 0.45 * sy, 0.0, 1.0); }
// v9: the thick paint's own lumps (finer than the fill's), 0..1, and the beads splashed past its edge: a jittered grid of little domes
// (x their cover, y their height in metres)
float coatLump(vec3 sp){ vec3 w = sp * 26.0 + uCoat.y * 0.7;
  float a = sin(w.x + 1.4 * sin(w.z * 0.8)) * sin(w.y + 1.2 * sin(w.x * 0.7)) * sin(w.z * 0.9 + 1.1 * sin(w.y * 0.6));
  float k = 1.0 - smoothstep(0.25, 0.8, length(fwidth(w)) / 6.2832); return 0.5 + 0.5 * a * k; }
float coatLumpLo(vec3 sp){ vec3 w = sp * 17.0 + uCoat.y * 0.4; return 0.5 + 0.5 * sin(w.x + 1.5 * sin(w.z * 0.7 + 0.4)) * sin(w.y * 1.1 + 1.3 * sin(w.x * 0.8)) * sin(w.z + 1.2 * sin(w.y * 0.9)); }
vec2 coatBeads(vec3 sp, float band){
  // (one cell per pixel: each bead sits wholly inside its own cell of a 2.8 cm grid, so no neighbour search; nothing where there is no band)
  if (band < 0.002) return vec2(0.0);
  vec3 q = sp * 36.0 + uCoat.y, i = floor(q), f = fract(q); float fw = length(fwidth(q)), pres = aHash(i + 5.17);
  if (pres > 0.5) return vec2(0.0);
  vec3 hp = aHash3(i + 2.3); float r = mix(0.1, 0.25, hp.z * hp.z), dd = length(f - (0.25 + 0.5 * hp.xyz));
  float aa = 0.6 * fw + 0.02, m = (1.0 - smoothstep(r - aa, r + aa, dd)) * band * (1.0 - smoothstep(0.3, 0.8, fw));
  return vec2(m, m > 0.0 ? r * sqrt(max(0.0, 1.0 - dd * dd / (r * r))) / 36.0 * 0.9 : 0.0); }`;""")

# ---- the face ----
# the pupil loop: anti-aliased edges, iris depth, a soft pupil, premium catchlights (the anchors the embed builder edits stay verbatim)
rep("""    float ia = (1.0 - smoothstep(ri - 0.014, ri, r)) * em.r;
    vec3 ic = mix(irC, irC * 0.2, smoothstep(0.0, ri, r)); ic = mix(ic, vec3(0.004, 0.002, 0.003), 1.0 - smoothstep(rp - 0.012, rp, r));
    ic += irC * 1.12 * smoothstep(ri * 0.35, ri * 0.95, r) * smoothstep(0.2, -0.6, dd.y / ri) * (1.0 - smoothstep(ri * 0.95, ri, r));""",
"""    float faa = fwidth(r) * 1.2 + 0.0015, ia = (1.0 - smoothstep(ri - faa, ri + faa, r)) * em.r;
    // the iris: lighter round the pupil, deeper toward a dark limbal ring, fine radial fibres (fading where a pixel would blur them), a
    // bright floor where the light comes through from above; the pupil soft-edged with a dark halo
    float an = atan(dd.y, dd.x), fib = (0.5 + 0.5 * sin(an * 29.0 + sin(an * 7.0 + r * 50.0) * 1.3)) * (1.0 - smoothstep(0.25, 0.7, fwidth(an) * 29.0 / 6.2832));
    vec3 ic = mix(irC * 1.4, irC * 0.45, smoothstep(rp * 0.6, ri * 0.9, r)); ic *= 1.0 + 0.2 * (fib - 0.5) * smoothstep(rp, rp * 1.4, r);
    ic = mix(ic, irC * 0.14, smoothstep(ri * 0.84, ri * 0.98, r));
    ic = mix(ic, irC * 0.3, (1.0 - smoothstep(rp, rp + 0.03, r)) * 0.6); ic = mix(ic, vec3(0.004, 0.002, 0.003), 1.0 - smoothstep(rp - faa, rp + faa * 0.5, r));
    ic += irC * 1.25 * smoothstep(ri * 0.3, ri * 0.92, r) * smoothstep(0.25, -0.65, dd.y / ri) * (1.0 - smoothstep(ri * 0.9, ri, r));""")
rep("""    float cl = (1.0 - smoothstep(mix(0.03, 0.05, sqd), mix(0.042, 0.06, sqd), length(fqe - pc - vec2(-0.055, 0.06) * (1.0 + 0.3 * sqd) * fPupil.z))) + 0.8 * (1.0 - sqd) * (1.0 - smoothstep(0.012, mix(0.02, 0.026, sqd), length(fqe - pc - vec2(0.05, -0.05) * (1.0 + 0.3 * sqd) * fPupil.z)));
    c = mix(c, vec3(1.0), clamp(cl, 0.0, 1.0) * (1.0 - 0.75 * zmb) * em.r * (1.0 - 0.85 * em.g));""",
"""    // the catchlights: a soft main one up and to the left with a faint glow round it, a small sharp one low and right, and a faint wet
    // sheen over the top of the cornea
    float caa = fwidth(fqe.x) * 1.2 + 0.001, r1 = mix(0.036, 0.05, sqd) * (0.8 + 0.2 * fPupil.z), d1 = length((fqe - pc - vec2(-0.055, 0.062) * (1.0 + 0.3 * sqd) * fPupil.z) * vec2(1.0, 1.12));
    float cl = (1.0 - smoothstep(r1 - caa, r1 + caa, d1)) + 0.22 * (1.0 - smoothstep(r1, r1 * 2.4, d1));
    float d2 = length(fqe - pc - vec2(0.052, -0.05) * (1.0 + 0.3 * sqd) * fPupil.z), r2 = mix(0.013, 0.018, sqd); cl += 0.85 * (1.0 - smoothstep(r2 - caa, r2 + caa, d2));
    cl += 0.1 * smoothstep(0.1, 0.55, dd.y / ri) * (1.0 - smoothstep(ri * 0.7, ri * 1.3, r));
    float ck = clamp(cl, 0.0, 1.0) * (1.0 - 0.75 * zmb) * em.r * (1.0 - 0.85 * em.g); c = mix(c, vec3(1.0), ck); sCatch = max(sCatch, (1.0 - smoothstep(r1 - caa, r1 + caa, d1)) * (1.0 - 0.75 * zmb) * em.r * (1.0 - 0.85 * em.g));""")
# the dot eyes: glossy black beads
rep("""    float dk = 1.0 - smoothstep(0.125, 0.145, r); c = mix(c, vec3(0.03, 0.012, 0.02), dk); float hl = 1.0 - smoothstep(0.03, 0.046, length((fq - pc - vec2(-0.045, 0.05)) * vec2(1.0, 1.0 / max(0.08, bk)))); c = mix(c, vec3(1.0), hl * dk); dotK = max(dotK, dk); } }""",
"""    float daa = fwidth(r) * 1.2 + 0.0015, dk = 1.0 - smoothstep(0.135 - daa, 0.135 + daa, r); c = mix(c, vec3(0.03, 0.012, 0.02), dk); float hl = 1.0 - smoothstep(0.03, 0.046, length((fq - pc - vec2(-0.045, 0.05)) * vec2(1.0, 1.0 / max(0.08, bk)))); c = mix(c, vec3(1.0), hl * dk); dotK = max(dotK, dk); dotG = max(dotG, dk); } }""")
rep("""  float dotK = 0.0; if (fStyle > 1.5 && fStyle < 2.5) { eye.a = 0.0; em = vec2(0.0); }""",
    """  float dotK = 0.0, dotG = 0.0; if (fStyle > 1.5 && fStyle < 2.5) { eye.a = 0.0; em = vec2(0.0); }""")
# the mouth over the face, then a gentle permanent blush on the cheeks and the face skin mask; the eyeball mask takes the dot eyes too
rep("""  faceInk = max(max(max(max(eye.a, mo.a), lsh), dotK), zma) * vFace.z; diffuseColor.rgb = mix(diffuseColor.rgb, c, vFace.z); sEyeM = em.r * vFace.z;
}
sDrawM = faceInk;`;""",
"""  faceInk = max(max(max(max(eye.a, mo.a), lsh), dotK), zma) * vFace.z;
  { float bm = exp(-(pow((abs(fq.x) - 0.6) / 0.25, 2.0) + pow((fq.y + 0.3) / 0.19, 2.0))) * (1.0 - faceInk);
    c = mix(c, mix(c, vec3(0.95, 0.3, 0.42), 0.5), 0.3 * bm); }
  diffuseColor.rgb = mix(diffuseColor.rgb, c, vFace.z); sEyeM = max(em.r * (1.0 - 0.6 * em.g), dotG) * vFace.z; sFaceK = vFace.z * (1.0 - faceInk);
}
sDrawM = faceInk;`;""")

# ---- the coat: the v8 block stays (the embed builder rewrites it into the wading-aware one); its result is replaced from the skin saved first ----
rep("""const COAT_FS = `
if (uCoat.x > 0.001) {""", """const COAT_FS = `
vec3 preCoat = diffuseColor.rgb;
if (uCoat.x > 0.001) {""")
rep("""  faceInk *= 1.0 - sCoatM; sDrawM = faceInk;
}`;""",
"""  faceInk *= 1.0 - sCoatM; sDrawM = faceInk;
}
// v9b: the paint as living paint, after the old slime's (the game's v207 coat): one signed distance to the paint's edge in metres
// (the fill's field and the wading line, whichever reaches further, each turned into metres by how fast it runs across the pixel),
// so the edge is soft and anti-aliased at any distance and its lip the same width on the body wherever it is; the face never takes
// the field's line: over the face the paint comes as a soft fade near full (the eyes stay clear). Above the edge thin runs of paint
// are left where the level has just dropped, sliding down after it (the high water the runtime keeps); the paint carries streaks
// flowing down and beads sliding down its surface; a rounded lip, soft lumps in the thick paint, a smooth glossy full coat; the
// wading paint swells round the contacts like a base melting into its puddle, rippling. Out of the paint the skin dries from the top.
// out of the paint the skin stays wet a while and dries from the top down (uCoat.z the adapter's wet, 1 soaked .. 0 dry)
sWetK = smoothstep(-0.1, 0.1, uCoat.z - (0.1 + 0.75 * vFillO));
if (uCoat.x > 0.001 || uCoat.w > 0.001) {
  float gcp = max(length(fwidth(vCp)), 1e-5), flow = uDetail2.x;
  // the body's own frame for the runs and beads: down the rest body (gravity in either body's rest), across it along the surface
  float hc = vRest.x;
  float run = clamp(pow(aNoise(vec3(hc * 24.0, flow * 0.04, 4.1)), 3.0) * 1.3, 0.0, 1.0) * (1.0 - smoothstep(0.25, 0.7, fwidth(hc) * 24.0));
  float lumpLo = coatLumpLo(vCp), lump = coatLump(vCp);
  // the fill coat: its field with a lobed edge; the runs above the edge reach toward where the level was a moment ago
  float ch = coatField(vCp, vFillO) - 0.03 * lumpLo * lumpLo - 0.005, cv = uCoat.x * 1.08 - 0.04, kch = gcp / max(fwidth(ch), 1e-5);
  float dm = uCoat.x > 0.001 ? (cv - ch) * kch + max(0.0, uDetail2.y - uCoat.x) * 1.08 * kch * run : -1e3;
  // the wading paint: the line from the fill order, wavy and lobed, rippling; its runs the same way
  float wv = uCoat.w - vFillO + 0.02 * sin(vCp.x * 31.0 + vCp.z * 17.0 + uCoat.y) + 0.012 * sin(vCp.z * 53.0 - vCp.x * 23.0 + uCoat.y * 0.7) + 0.022 * lumpLo + 0.006 * sin(vCp.x * 41.0 + vCp.z * 29.0 - flow * 2.6);
  float kwv = gcp / max(fwidth(wv), 1e-5);
  float dw = uCoat.w > 0.001 ? wv * kwv + max(0.0, uDetail2.z - uCoat.w) * kwv * run : -1e3;
  float wadeK = uCoat.w > 0.001 ? smoothstep(-0.02, 0.02, dw - dm) : 0.0;
  dm = max(dm, dw);
  float aa = max(0.012, gcp * 1.2), full = step(0.995, uCoat.x);
  float cm = smoothstep(-aa, aa, dm); cm = max(cm, full);
  // the face: no line across it; the paint comes over it as a soft fade near full, and never over the eyeballs
  float cmF = smoothstep(0.8, 0.97, uCoat.x + 0.05 * (lumpLo - 0.5)) * (1.0 - sEyeM); cmF = max(cmF, full * (1.0 - sEyeM));
  cm = mix(cm, cmF, vFace.z);
  // the paint colour: the team's, deep and saturated; the streaks flowing down it, the creases between the lumps a shade darker
  float flw = aNoise(vec3(hc * 35.0, vRest.y * 2.2 + flow * 0.5, 7.7));
  vec3 pc = max(mix(vec3(dot(uPaint, vec3(0.2126, 0.7152, 0.0722))), uPaint, 1.25), vec3(0.0)) * 0.85;
  pc *= 1.0 + 0.1 * (flw - 0.5) * (1.0 - full) - 0.1 * (1.0 - lump) * smoothstep(0.0, 0.05, dm) * (1.0 - full);
  // the thickness: a rounded lip over the first 4 cm, soft lumps in the thick paint, none in a fresh full coat; the beads sliding down
  // the paint from its edge, one to a column in some columns; the wading paint swollen round the contacts (the base in its puddle)
  float t = clamp(dm / 0.04, 0.0, 1.0), lip = sqrt(max(0.0, 1.0 - (1.0 - t) * (1.0 - t)));
  float bc = hc * 70.0, bi = floor(bc), bfx = fract(bc) - 0.5, brn = fract(sin(bi * 91.7 + uCoat.y) * 4375.85);
  float by = fract(flow * (0.22 + 0.2 * brn) + brn) * 0.14, bd = length(vec2(bfx / 0.42, (dm - by) / 0.011)), bAA = 1.0 - smoothstep(0.15, 0.4, fwidth(bc));
  float bead = (1.0 - smoothstep(0.55, 1.0, bd)) * step(brn, 0.45) * bAA * smoothstep(0.01, 0.03, dm) * (1.0 - full) * (1.0 - vFace.z);
  float swell = wadeK * smoothstep(0.1, 0.0, vFillO) * uCoat.w;
  sBead = bead; sCoatT = cm * max(lip, bead);
  float ripple = 0.15 * sin(vCp.x * 17.0 + vCp.z * 11.0 - flow * 3.1) * sin(vCp.z * 13.0 - vCp.x * 7.0 + flow * 2.3) * wadeK;
  sCoatH = (0.0055 * lip + 0.0025 * (lump - 0.5) * t + 0.004 * bead * (1.0 - bd * bd) + 0.003 * ripple * t + 0.012 * swell * (0.5 + 0.5 * lump)) * cm * (1.0 - full) + full * 0.0008 * (lump - 0.5);
  sCoatM = cm; sPaintC = pc; sWetK *= 1.0 - cm;
  // the skin under the edge in the paint's shadow; the lip a shade lighter (its thin rim lets the skin's light through)
  vec3 skin = preCoat * (1.0 - 0.26 * (1.0 - smoothstep(-0.035, 0.0, dm)) * smoothstep(-0.07, -0.03, dm));
  diffuseColor.rgb = mix(skin, mix(pc, mix(pc, preCoat, 0.35), 0.45 * (1.0 - t) * (1.0 - full) * (1.0 - vFace.z)), cm);
  faceInk *= 1.0 - cm * (1.0 - sEyeM); sDrawM = faceInk;
}`;""")
# the coat's height goes into the relief (the skin's own relief is hidden under the paint, as before)
rep("""  h -= 0.5 * uDetail.x * sSpot;
  normal = aBump(-vViewPosition, normal, h);
}`;""",
"""  h -= 0.5 * uDetail.x * sSpot;
  h += sCoatH;
  normal = aBump(-vViewPosition, normal, h);
}`;""")

# ---- the material: the wet eye, the face skin, the paint's glass coat ----
rep("""const LIT_FS = `
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
}`;""",
"""const LIT_FS = `
{ float wet = max(sCoatM, 0.8 * sWetK), inkM = clamp(sDrawM - sEyeM, 0.0, 1.0);
  float rough = mix(0.52, 0.32, sBelly); rough = mix(rough, 0.52, sGill * 0.7); rough = mix(rough, 0.34, sFin * 0.6);
  rough = mix(rough, 0.4, 0.6 * sFaceK);   // (the face skin a touch smoother)
  rough = mix(rough, 0.72, inkM); rough = mix(rough, 0.1, sEyeM);   // (matte ink, a wet eye)
  material.roughness = min(max(mix(rough, 0.05, wet), 0.0525) + geometryRoughness, 1.0);
#ifdef USE_CLEARCOAT
  material.clearcoat = mix(0.12 + 0.28 * sBelly + 0.12 * sFin + 0.2 * sFaceK, 1.0, max(max(sCoatM, 0.45 * sEyeM), 0.7 * sWetK)) * (1.0 - 0.9 * inkM);
  material.clearcoatRoughness = min(max(mix(0.46 - 0.18 * sBelly - 0.1 * sFaceK, 0.03, max(max(sCoatM, sEyeM), sWetK)), 0.0525) + geometryRoughness, 1.0);
#endif
#ifdef USE_SHEEN
  material.sheenColor = (uBelly * (0.5 * sBelly + 0.15 * sGill) + mix(diffuseColor.rgb, vec3(1.0), 0.5) * 0.3 * sFaceK) * (1.0 - sCoatM); material.sheenRoughness = 0.42;
#endif
}`;""")
rep("""const LOOK_FS = `
{ float occ = sAO * (1.0 - 0.3 * sCoatM), ink = sDrawM * (1.0 - sCoatM);""",
"""const LOOK_FS = `
{ float occ = sAO * (1.0 - 0.3 * sCoatM), ink = clamp(sDrawM - sEyeM, 0.0, 1.0) * (1.0 - sCoatM), eyeK = sEyeM * (1.0 - sCoatM);""")
rep("""  reflectedLight.directDiffuse *= 1.0 - 0.45 * ink; reflectedLight.indirectDiffuse *= 1.0 - 0.45 * ink; reflectedLight.directSpecular *= 1.0 - 0.9 * ink; reflectedLight.indirectSpecular *= 1.0 - 0.9 * ink;
  totalEmissiveRadiance += diffuseColor.rgb * ink * 0.5;""",
"""  reflectedLight.directDiffuse *= 1.0 - 0.45 * ink; reflectedLight.indirectDiffuse *= 1.0 - 0.45 * ink; reflectedLight.directSpecular *= 1.0 - 0.9 * ink; reflectedLight.indirectSpecular *= 1.0 - 0.9 * ink;
  totalEmissiveRadiance += diffuseColor.rgb * ink * 0.5;
  // the eye: lit a little from within too (its white stays bright in shade), its gloss kept
  reflectedLight.directDiffuse *= 1.0 - 0.15 * eyeK; reflectedLight.indirectDiffuse *= 1.0 - 0.15 * eyeK; totalEmissiveRadiance += diffuseColor.rgb * eyeK * 0.42;
  { float ck = sCatch * vFace.z * (1.0 - sCoatM); reflectedLight.directDiffuse *= 1.0 - ck; reflectedLight.indirectDiffuse *= 1.0 - ck; reflectedLight.directSpecular *= 1.0 - ck; totalEmissiveRadiance = mix(totalEmissiveRadiance, vec3(1.0), ck); }""")
rep("""  // a soft rim along the body's outline, a whisper of light on the moist skin
  float upk = saturate(dot(nonPerturbedNormal, normalize((viewMatrix * vec4(0.0, 1.0, 0.0, 0.0)).xyz)) + 0.4);
  totalEmissiveRadiance += mix(diffuseColor.rgb, vec3(1.0, 0.95, 0.92), 0.35) * pow(edge, 3.0) * (0.5 + 0.5 * upk) * 0.22 * (1.0 - ink) * (1.0 - 0.5 * sCoatM);
}`;""",
"""  // a soft rim along the body's outline, a whisper of light on the moist skin
  float upk = saturate(dot(nonPerturbedNormal, normalize((viewMatrix * vec4(0.0, 1.0, 0.0, 0.0)).xyz)) + 0.4);
  totalEmissiveRadiance += mix(diffuseColor.rgb, vec3(1.0, 0.95, 0.92), 0.35) * pow(edge, 3.0) * (0.5 + 0.5 * upk) * 0.22 * (1.0 - ink) * (1.0 - 0.5 * sCoatM);
  // the face skin: a little light through it (wrapped round the terminator and through from behind, in the skin's deeper colour)
  totalEmissiveRadiance += deep * sFaceK * (1.0 - sCoatM) * (0.1 * wrap + 0.07 * back);
  // the wet paint: a fresnel sheen and a cheap reflection of the sky and ground off the bumped surface (the clear coat layer, where
  // there is one, adds the real one), the beads and the lip catching most
  if (sCoatM + sWetK > 0.002) { vec3 wup = normalize((viewMatrix * vec4(0.0, 1.0, 0.0, 0.0)).xyz), rv = reflect(-vd, normal); float ru = dot(rv, wup) * 0.5 + 0.5;
    float fr = pow(1.0 - saturate(dot(normal, vd)), 3.5), sky = mix(0.08, 0.5, smoothstep(0.35, 0.9, ru)) * (0.6 + 0.4 * fr);
    vec3 refl = mix(vec3(1.0), sPaintC * 2.0, 0.3);
    totalEmissiveRadiance += refl * (0.14 * fr + 0.22 * sky * (0.35 + 0.65 * sCoatT)) * max(sCoatM, 0.5 * sWetK); }
}`;""")
# the clear coat follows the bump on the paint and the eye (the lumps and the lip reflect)
rep("""      .replace('#include <normal_fragment_maps>', '#include <normal_fragment_maps>\\n' + BUMP_FS)""",
    """      .replace('#include <normal_fragment_maps>', '#include <normal_fragment_maps>\\n' + BUMP_FS)
      .replace('#include <clearcoat_normal_fragment_maps>', '#include <clearcoat_normal_fragment_maps>\\n#ifdef USE_CLEARCOAT\\nclearcoatNormal = normalize(mix(clearcoatNormal, normal, max(max(sCoatM, sEyeM), sWetK)));\\n#endif')""")
# the sheets' mouth lines: a little less ink, a soft halo under each line
rep("""  const line = (ctx, pts, w) => { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.strokeStyle = 'rgba(' + INK + ',0.92)'; ctx.lineWidth = w || 0.045; ctx.stroke(); };""",
"""  const line = (ctx, pts, w) => { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.strokeStyle = 'rgba(' + INK + ',0.16)'; ctx.lineWidth = (w || 0.045) * 2.2; ctx.stroke(); ctx.strokeStyle = 'rgba(' + INK + ',0.84)'; ctx.lineWidth = w || 0.045; ctx.stroke(); };""")
rep("""    ctx.restore(); path(); ctx.strokeStyle = 'rgba(' + INK + ',0.85)'; ctx.lineWidth = 0.032; ctx.stroke();
  };""",
"""    ctx.restore(); path(); ctx.strokeStyle = 'rgba(' + INK + ',0.14)'; ctx.lineWidth = 0.07; ctx.stroke(); ctx.strokeStyle = 'rgba(' + INK + ',0.8)'; ctx.lineWidth = 0.03; ctx.stroke();
  };""")
# debug views for the coat: 7 the mask (r), the thickness (g), the beads (b); 8 the height
rep("""  else gl_FragColor = vec4(fract(vCp * 4.0), 1.0);
}`;""", """  else if (uDebug < 6.5) gl_FragColor = vec4(fract(vCp * 4.0), 1.0);
  else if (uDebug < 7.5) gl_FragColor = vec4(sCoatM, sCoatT, sBead, 1.0);
  else if (uDebug < 8.5) gl_FragColor = vec4(vec3(0.5 + sCoatH * 40.0), 1.0);
  else if (uDebug < 9.5) gl_FragColor = vec4(vec3(vFillO), 1.0);
  else if (uDebug < 10.5) gl_FragColor = vec4(vec3(0.5 + sDbgDm * 4.0), 1.0);
  else gl_FragColor = vec4(vec3(sDbgG * 300.0), 1.0);
}`;""")
s = s.replace("// Roll Model axolotl runtime v7, single module:", "// Roll Model axolotl runtime v9 (v7 + the baked texture of v8 + the v9 face material and paint coat, axo/tools5/look9.py), single module:", 1)
open(OUT, 'w').write(s); print('ok', len(s))
