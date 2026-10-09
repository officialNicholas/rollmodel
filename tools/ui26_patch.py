#!/usr/bin/env python3
"""The edgy eyes become squid eyes: a heavy angular mask with pointed corners joined across the bridge, slab brows, big irises, sharp lights. On top of ui25_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui25_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# a tapered stroke, for the mask's points and the brows
rep("uniform sampler2D fCol, fMsk; uniform vec4 fCells, fMix, fPupil, fComp, fLash, fStrap, sCoat, mFace, mHead; uniform vec3 sPaint, fIris; uniform float fStyle;\n",
    "uniform sampler2D fCol, fMsk; uniform vec4 fCells, fMix, fPupil, fComp, fLash, fStrap, sCoat, mFace, mHead; uniform vec3 sPaint, fIris; uniform float fStyle;\n"
    "float fCone(vec2 p, vec2 a, vec2 b, float w0, float w1) { vec2 ab = b - a; float t = clamp(dot(p - a, ab) / dot(ab, ab), 0.0, 1.0); float d = length(p - a - ab * t) - mix(w0, w1, t); return 1.0 - smoothstep(-0.004, 0.012, d); }\n")
# the eye itself: a touch bigger and only lightly slanted; the mask does the attitude
rep("vec2 fqe = fq; if (fStyle > 0.5 && fStyle < 1.5) { float sd0 = fq.x < 0.0 ? -1.0 : 1.0; vec2 pc0 = vec2(sd0 * 0.4, 0.16); vec2 l = fq - pc0; l.y = l.y * 1.4 + 0.03; l.x = (l.x + l.y * sd0 * 0.5) * 1.06; fqe = pc0 + l; }",
    "float sqd = (fStyle > 0.5 && fStyle < 1.5) ? 1.0 : 0.0; vec2 fqe = fq; if (sqd > 0.5) { float sd0 = fq.x < 0.0 ? -1.0 : 1.0; vec2 pc0 = vec2(sd0 * 0.4, 0.16); vec2 l = fq - pc0; l.y = l.y * 1.18 + 0.02; l.x = (l.x + l.y * sd0 * 0.28) * 0.95; fqe = pc0 + l; }")
# the mask: the open eye's shape dilated into a thick ink rim, a wing off the outer corner, a point off the inner lower corner, and a slab brow angled down toward the middle. The eye blinks inside it; the mask stays
OLD = "  if (fStyle > 0.5 && fStyle < 1.5) { float d1 = max(max(texture2D(fCol, fCell(fCells.x, cuvE + vec2(0.024, 0.0))).a, texture2D(fCol, fCell(fCells.x, cuvE - vec2(0.024, 0.0))).a), max(texture2D(fCol, fCell(fCells.x, cuvE + vec2(0.0, 0.028))).a, texture2D(fCol, fCell(fCells.x, cuvE - vec2(0.0, 0.028))).a));\n    float rim = clamp(d1 - eye.a, 0.0, 1.0) * (1.0 - 0.5 * fMix.y); c = mix(c, vec3(0.03, 0.012, 0.02), rim); dotK = rim; }\n"
NEW = """  if (sqd > 0.5) { float d1 = 0.0; for (int k = 0; k < 16; k++) { float a = float(k) * 0.3927; d1 = max(d1, texture2D(fCol, fCell(0.0, cuvE + vec2(cos(a) * 0.064, sin(a) * 0.072))).a); }
    float hole = texture2D(fCol, fCell(0.0, cuvE)).a, rim = clamp(d1 - hole, 0.0, 1.0), sp = 0.0; // (the mask keeps the open eye's shape whatever the eye inside is doing)
    for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16);
      vec2 dw = normalize(vec2(sd, 0.5)); vec2 a = pc + dw * 0.2, b = a + dw * 0.3; sp = max(sp, fCone(fqe, a, b, 0.1, 0.003));
      vec2 di = normalize(vec2(-sd, -0.75)); a = pc + di * 0.18; b = a + di * 0.19; sp = max(sp, fCone(fqe, a, b, 0.085, 0.003));
      vec2 b0 = pc + vec2(sd * 0.2, 0.37), b1 = pc + vec2(-sd * 0.04, 0.3); sp = max(sp, fCone(fq, b0, b1, 0.042, 0.018)); }
    float mk = max(rim, sp); c = mix(c, vec3(0.03, 0.012, 0.02), mk);
    // lids down: the almond fills with ink and the lid line shows as a lighter crease
    float lidLine = eye.a * step(dot(eye.rgb, vec3(0.333)), 0.3); c = mix(c, vec3(0.03, 0.012, 0.02), hole * (1.0 - eye.a) * (1.0 - mk)); c = mix(c, vec3(0.46, 0.3, 0.38), hole * lidLine * (1.0 - mk)); dotK = max(mk, hole * (1.0 - eye.a)); }
"""
rep(OLD, NEW)
# big irises with a dark limbal ring, a large crisp catchlight and a small one
rep("vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy, dd = (fqe - pc) * vec2(1.0, 0.92); float r = length(dd), ri = 0.165 * fPupil.z, rp = 0.092 * fPupil.z;",
    "vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy, dd = (fqe - pc) * vec2(1.0, 0.92); float r = length(dd), ri = mix(0.165, 0.205, sqd) * fPupil.z, rp = mix(0.092, 0.1, sqd) * fPupil.z;")
rep("    c = mix(c, ic * (1.0 - 0.55 * em.g), ia);\n    float cl = (1.0 - smoothstep(0.03, 0.042, length(fqe - pc - vec2(-0.055, 0.06) * fPupil.z))) + 0.8 * (1.0 - smoothstep(0.012, 0.02, length(fqe - pc - vec2(0.05, -0.05) * fPupil.z)));",
    "    ic = mix(ic, vec3(0.02, 0.008, 0.014), sqd * smoothstep(ri - 0.045, ri - 0.012, r));\n    c = mix(c, ic * (1.0 - 0.55 * em.g), ia);\n    float cl = (1.0 - smoothstep(mix(0.03, 0.05, sqd), mix(0.042, 0.06, sqd), length(fqe - pc - vec2(-0.055, 0.06) * (1.0 + 0.3 * sqd) * fPupil.z))) + 0.8 * (1.0 - smoothstep(0.012, mix(0.02, 0.026, sqd), length(fqe - pc - vec2(0.05, -0.05) * (1.0 + 0.3 * sqd) * fPupil.z)));")
# the chip
rep("""edgy: '<svg viewBox="0 0 40 40"><path d="M6 23C10 13 22 11 34 15C30 24 18 29 6 23Z" fill="#171320"/><path d="M8.5 22.5C12 15.5 22 14 31.5 16.5C28 23 18 26.5 8.5 22.5Z" fill="#fff"/><circle cx="20" cy="20" r="4.6" fill="#8A5636"/><circle cx="20.5" cy="20.4" r="2.4" fill="#171320"/><circle cx="18.6" cy="18.4" r="1.3" fill="#fff"/></svg>'""",
    """edgy: '<svg viewBox="0 0 40 40"><path d="M3 20C8 11 16 9 23 12L37 8L30 16C33 20 30 26 24 29L15 36L13 29C7 28 3 24 3 20Z" fill="#171320"/><path d="M10 20C13 14 20 13 26 16C25 23 18 27 11 25C9.5 24 9.5 22 10 20Z" fill="#fff"/><path d="M10 9L22 5L21 9Z" fill="#171320"/><circle cx="18.5" cy="19.5" r="5.6" fill="#8A5636"/><circle cx="19" cy="20" r="3" fill="#171320"/><circle cx="16.4" cy="17.2" r="1.9" fill="#fff"/></svg>'""")
rep("const EYE_STYLES = { round: 'Round', edgy: 'Edgy', dot: 'Dot' }", "const EYE_STYLES = { round: 'Round', edgy: 'Squid', dot: 'Dot' }")
rep('<p class="ver">Version 95</p>', '<p class="ver">Version 96</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
