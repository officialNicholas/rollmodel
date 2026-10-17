"""v336: the Sly eyes show the eye.

- Their heavy upper lid sat right across the middle of the eye (the pupil half under it), and it stayed there whatever the mood: when a
  mood narrowed the eye (happy, glee, the smug ones), all that was left under the lid was a slit. In the intro you pick your eyes up close,
  and picking them sets off a proud wiggle with a happy face, so Sly looked like a squint there most of all.
- Now, as the Aggressive eyes already do (v279), the Sly eyes keep the open eye under their lid whatever the mood, and the mood moves the
  lid instead: a little lower when smug or pleased, higher when curious or startled. Eyes that close (a yawn, a doze, a sneeze, dizzy and
  bracing) and the sleepy ones keep the game's own faces; the hurt, sad and pouting shapes keep theirs, the lid a little higher.
- At rest the lid sits higher (SLY_UP face units; the iris is 0.165 across its radius), so the whole pupil and most of the iris show, and
  it rises a little with the eyes when they look up. It still slants down to the outer corner, with its dark lash line and wing. A blink
  closes it as before.
- In the intro you're still covered in paint, and the paint left only the eyeballs clear: the lid, its lash line and the wing were under
  it, so the raised lid would have vanished there (and a blink left a blank face). Now the paint leaves the Sly eye clear from its lash
  line down, with the lash line and the wing; the lid's skin above the line stays painted, like the rest of the face."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

SLY_UP = '0.085'

SLY = r"""
  // (v336) the Sly eyes keep the open eye under their heavy lid whatever the mood (a narrowed eye under it was a slit): the mood moves the
  // lid instead. [eye cell, mouth cell, how far the lid lifts]. Moods not here (eyes that close, sleepy) keep the game's own faces
  const SLY = { neutral: [0, 8, 0], happy: [0, 9, -0.03], glee: [0, 12, -0.03], content: [0, 24, -0.03], cute: [0, 27, -0.02], blep: [0, 25, -0.02], smirk: [0, 24, -0.045],
    focus: [0, 8, -0.02], ready: [0, 36, -0.02], menace: [0, 33, -0.05], angry: [0, 10, -0.04], curious: [5, 27, 0.06], leap: [5, 9, 0.06], peek: [5, 13, 0.08],
    startle: [5, 13, 0.09], scared: [5, 13, 0.1], sad: [22, 26, 0.05], pout: [22, 27, 0.04], hurt: [3, 11, 0.06] };
"""

def apply(s):
    # ---- the shader: the lid higher at rest, moved by the mood (fComp.z, as the Aggressive lid is), rising a little as the eyes look up
    up = "(" + SLY_UP + " + fComp.z + 0.5 * max(fPupil.y, 0.0)) * (1.0 - fMix.y)"
    s = rep(s, "float lidY = pc.y + 0.0 - 0.11 * ox - 0.12 * fMix.y, wht = eye.a * side;",
               "float lidY = pc.y + " + up + " - 0.11 * ox - 0.12 * fMix.y, wht = eye.a * side; // (v336: higher, moved by the mood)")
    s = rep(s, "float wy = pc.y + 0.0 - 0.11 * 0.18 - 0.12 * fMix.y,", "float wy = pc.y + " + up + " - 0.11 * 0.18 - 0.12 * fMix.y,")
    # ---- the moods: the Sly eyes' own table, beside the Aggressive one
    s = rep(s, "sleepy: [20, 36, -0.02, -0.08], doze: [6, 36, 0.5, 0], yawn: [6, 13, 0.5, 0], sneeze: [7, 13, 0.5, 0], dizzy: [7, 11, 0.5, 0], brace: [7, 11, 0.5, 0], shake: [7, 11, 0.5, 0] };\n",
               "sleepy: [20, 36, -0.02, -0.08], doze: [6, 36, 0.5, 0], yawn: [6, 13, 0.5, 0], sneeze: [7, 13, 0.5, 0], dizzy: [7, 11, 0.5, 0], brace: [7, 11, 0.5, 0], shake: [7, 11, 0.5, 0] };\n" + SLY.lstrip('\n'))
    s = rep(s, "ag = U.fStyle.value === 1, xa = ag ? AGG[this.expr] : null, xb = ag ? AGG[this.exprB] : null,",
               "ag = U.fStyle.value === 1, sl = U.fStyle.value === 4, xa = ag ? AGG[this.expr] : sl ? SLY[this.expr] : null, xb = ag ? AGG[this.exprB] : sl ? SLY[this.exprB] : null,")
    s = rep(s, "U.fComp.value.set(1, 1, ag ? (xa ? xa[2] : 0) + ((xb ? xb[2] : 0) - (xa ? xa[2] : 0)) * k : 0,",
               "U.fComp.value.set(1, 1, ag || sl ? (xa ? xa[2] : 0) + ((xb ? xb[2] : 0) - (xa ? xa[2] : 0)) * k : 0,")
    # ---- under a coat of paint (the intro): the paint leaves the Sly eye clear down from its lash line, and the lash line and wing, not
    # just the eyeball (the lid's skin above the line it covers, as it covers the rest of the face)
    s = rep(s, "float sCoatM = 0.0, faceInk = 0.0, sEyeM = 0.0,", "float sCoatM = 0.0, faceInk = 0.0, sEyeM = 0.0, sSlyM = 0.0,")
    s = rep(s, "c = mix(c, vec3(0.05, 0.015, 0.03), max(ll, wing)); c = mix(c, vec3(0.45, 0.17, 0.24), brow); dotK = max(dotK, max(max(ll, wing), max(brow, lid))); } }",
               "c = mix(c, vec3(0.05, 0.015, 0.03), max(ll, wing)); c = mix(c, vec3(0.45, 0.17, 0.24), brow); dotK = max(dotK, max(max(ll, wing), max(brow, lid))); sSlyM = max(sSlyM, max(wht - lid, max(ll, wing)) * vFace.z); } }")
    s = rep(s, "float cmF = smoothstep(0.8, 0.97, uCoat.x + 0.05 * (lumpLo - 0.5)) * (1.0 - sEyeM); cmF = max(cmF, full * (1.0 - sEyeM));",
               "float eyK = max(sEyeM, sSlyM), cmF = smoothstep(0.8, 0.97, uCoat.x + 0.05 * (lumpLo - 0.5)) * (1.0 - eyK); cmF = max(cmF, full * (1.0 - eyK)); // (v336: and the Sly eyes' lid, lash line and wing)")
    s = rep(s, "faceInk *= 1.0 - cm * (1.0 - sEyeM); sDrawM = faceInk;", "faceInk *= 1.0 - cm * (1.0 - eyK); sDrawM = faceInk;")
    return s
