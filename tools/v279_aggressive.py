"""v279: the Squid eyes become "Aggressive" (the style's save key stays 'edgy'). Gone are the almond eyes with their ink rims and the
point at the corner, that read as sunglasses. Now a heavy upper lid lies straight across each eye, slanting down toward the middle of
the face, with a dark lash line along its edge, a little shadow under it on the eye, and its edge catching the light above: a big iris
sitting high under it, so it always seems to be sizing you up. It keeps that look nearly all the time: whatever mood the game gives it,
the lids stay down (a startle or a fright opens them up a bit; shut eyes still shut), and it doesn't smile: its happy moods smirk
(the crooked one from the victory screen) and its resting mouth is a firm flat line (new, in the face sheet's tenth row). Its
personality: it always wants to win."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def region(s, a, b, new):
    assert s.count(a) == 1, (s.count(a), a[:120]); i = s.index(a); j = s.index(b, i) + len(b); return s[:i] + new + s[j:]

# the expressions it shows differently: [eye cell, mouth cell, lid lift, extra slant]. 36 is the flat mouth, 33 the smirk
AGG = ("  // (v279) the aggressive eyes keep their lids down whatever the mood, and never smile: [eye cell, mouth cell, how far the lid lifts,\n"
       "  // how much steeper it slants]. 36: the flat mouth; 33: the smirk. Shut eyes lift the lid out of the way\n"
       "  const AGG = { neutral: [0, 36, 0, 0], happy: [0, 33, -0.012, 0], glee: [0, 33, -0.012, 0], content: [0, 33, 0, 0], cute: [0, 33, -0.01, 0], blep: [0, 33, 0, 0], smirk: [0, 33, -0.015, 0.02],\n"
       "    curious: [0, 36, 0.035, -0.06], focus: [0, 36, -0.02, 0.04], menace: [0, 33, -0.035, 0.05], angry: [0, 10, -0.045, 0.08], leap: [0, 33, 0.02, 0],\n"
       "    peek: [5, 36, 0.08, -0.08], startle: [5, 13, 0.13, -0.12], scared: [5, 13, 0.16, -0.15], sad: [22, 26, 0.07, -0.25], pout: [22, 36, 0.05, -0.2], hurt: [3, 11, 0.04, -0.1],\n"
       "    sleepy: [20, 36, -0.02, -0.08], doze: [6, 36, 0.5, 0], yawn: [6, 13, 0.5, 0], sneeze: [7, 13, 0.5, 0], dizzy: [7, 11, 0.5, 0], brace: [7, 11, 0.5, 0], shake: [7, 11, 0.5, 0] };\n")

LID = r"""  // (v279) aggressive: a heavy upper lid straight across each eye, slanting down toward the middle of the face; under it a dark lash line
  // and a little shadow on the eye, above it the lid's edge catching the light. fComp.z lifts it (a fright opens the eyes up a bit),
  // fComp.w steepens it
  if (sqd > 0.5) { float sd = fq.x < 0.0 ? -1.0 : 1.0, ox = (fq.x - sd * 0.4) * sd, lidY = 0.205 + fComp.z + (0.13 + fComp.w) * ox, aw = fwidth(fq.y) + 0.0025, dy = fq.y - lidY;
    float ea0 = eye.a, aggL = 1.0 - smoothstep(-aw, aw, dy);
    c = mix(diffuseColor.rgb, c, aggL);
    c = mix(c, c * vec3(0.6, 0.56, 0.66), ea0 * aggL * (1.0 - smoothstep(0.0, 0.075, -dy)) * 0.8);
    float lit = ea0 * smoothstep(-aw, aw, dy) * (1.0 - smoothstep(0.012, 0.045, dy)); c = mix(c, mix(diffuseColor.rgb, vec3(1.0), 0.3), lit * 0.75);
    float lash = ea0 * (1.0 - smoothstep(0.012, 0.012 + aw * 1.5, abs(dy + 0.004))); c = mix(c, vec3(0.03, 0.012, 0.02), lash);
    eye.a *= aggL; em *= aggL; dotK = max(dotK, lash); }
"""

FLAT = ("  // (v279) the aggressive one's resting mouth: a firm flat line, the far corner set a touch higher; with fangs, one tooth under it\n"
        "  const flatY = u => MY - 0.004 - 0.008 * Math.sin(Math.PI * u) + 0.016 * u * u;\n"
        "  const flat = (ctx, f) => { if (f) fang(ctx, 0.05, flatY(0.68) + 0.002, 0.8); line(ctx, Array.from({ length: 17 }, (_, i) => { const u = i / 16; return [-0.095 + 0.19 * u, flatY(u)]; }), 0.036); };\n"
        "  at(g, 36, ctx => big(ctx, () => flat(ctx, false))); at(g, 37, ctx => big(ctx, () => flat(ctx, true)));\n")

ICON = ("edgy: '<svg viewBox=\"0 0 40 40\"><defs><clipPath id=\"esAggC\"><path d=\"M5.5 15.2L34.5 20.6C34.5 29 25 33.5 18.5 32.6C10 31.6 5.5 25 5.5 15.2Z\"/></clipPath></defs>"
        "<path d=\"M5.5 15.2L34.5 20.6C34.5 29 25 33.5 18.5 32.6C10 31.6 5.5 25 5.5 15.2Z\" fill=\"#fff\" stroke=\"#171320\" stroke-width=\"2.2\" stroke-linejoin=\"round\"/>"
        "<g clip-path=\"url(#esAggC)\"><circle cx=\"20\" cy=\"21.5\" r=\"7.6\" fill=\"#8A5636\"/><circle cx=\"20.2\" cy=\"21.8\" r=\"3.6\" fill=\"#171320\"/><circle cx=\"17.4\" cy=\"21\" r=\"2\" fill=\"#fff\"/></g>"
        "<path d=\"M4.6 15L35.4 20.8\" stroke=\"#171320\" stroke-width=\"3.6\" stroke-linecap=\"round\"/></svg>'")

def apply(s):
    # the name
    s = rep(s, "const EYE_STYLES = { round: 'Round', edgy: 'Squid', dot: 'Dot', zombie: 'Zombie' };", "const EYE_STYLES = { round: 'Round', edgy: 'Aggressive', dot: 'Dot', zombie: 'Zombie' };")
    s = rep(s, "const EYE_STYLES = { round: 'Round', edgy: 'Squid', dot: 'Dot', sly: 'Sly', zombie: 'Zombie' }", "const EYE_STYLES = { round: 'Round', edgy: 'Aggressive', dot: 'Dot', sly: 'Sly', zombie: 'Zombie' }")
    # its icon: the eye under a heavy slanted lid
    a = s.index("const ES_ICON_T = { round:"); i = s.index("edgy: '<svg", a); j = s.index("</svg>'", i) + len("</svg>'")
    s = s[:i] + ICON + s[j:]
    # the face sheet gains a tenth row (cells 36-39): the flat mouth and its fanged twin
    s = rep(s, "function makeFaceSheets(C) {\n  const W = C * 4, H = C * 9,", "function makeFaceSheets(C) {\n  const W = C * 4, H = C * 10,")
    s = rep(s, "return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) / 9.0); }", "return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) / 10.0); }")
    a = "  at(g, 33, ctx => big(ctx, () => sneer(ctx, false))); at(g, 34, ctx => big(ctx, () => sneer(ctx, true)));\n"
    s = rep(s, a, a + FLAT)
    # the shader (the axolotl's face, the last FACE_FS; the slime's older copies are left alone): no almond warp, and the lid in place of the rim and corner point
    fi = s.rindex("const FACE_FS = `"); fj = s.index('`;', fi); pre, F, post = s[:fi], s[fi:fj], s[fj:]
    F = rep(F, "sly = fStyle > 3.5 ? 1.0 : 0.0; vec2 fqe = fq; if (sqd > 0.5) { float sd0 = fq.x < 0.0 ? -1.0 : 1.0; vec2 pc0 = vec2(sd0 * 0.4, 0.16); vec2 l = fq - pc0; l.y = l.y * 1.1 + 0.01; l.x = (l.x + l.y * sd0 * 0.2) * 0.97; fqe = pc0 + l; }",
               "sly = fStyle > 3.5 ? 1.0 : 0.0; vec2 fqe = fq; if (sqd > 0.5) { float sd0 = fq.x < 0.0 ? -1.0 : 1.0; fqe.x = sd0 * 0.4 + (fq.x - sd0 * 0.4) * 0.87; } // (v279: the aggressive eyes a little wider)")
    F = region(F, "  if (sqd > 0.5) { float d1 = 0.0; for (int k = 0; k < 16; k++) { float a = float(k) * 0.3927; d1 = max(d1, texture2D(fCol, fCell(0.0, cuvE + vec2(cos(a) * 0.05, sin(a) * 0.052 + 0.026))).a); }\n    float hole",
               "dotK = max(mk, hole * (1.0 - eye.a)); }\n", LID)
    # the iris a little smaller than the squid's (it fills the eye under the lid), sitting high, its dark ring softer
    F = rep(F, "vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w) + fPupil.xy, dd = (fqe - pc) * vec2(1.0, 0.92); float r = length(dd), ri = mix(0.165, 0.235, sqd)",
               "vec2 pc = vec2(sd * 0.4, 0.16 + fPupil.w + 0.018 * sqd) + fPupil.xy, dd = (mix(fqe, fq, sqd) - pc) * vec2(1.0, 0.92); float r = length(dd), ri = mix(0.165, 0.205, sqd)")
    F = rep(F, "    ic = mix(ic, vec3(0.02, 0.008, 0.014), sqd * smoothstep(ri - 0.032, ri - 0.012, r));\n    ic = mix(ic, vec3(0.3, 0.17, 0.2), sly",
               "    ic = mix(ic, vec3(0.02, 0.008, 0.014), 0.7 * sqd * smoothstep(ri - 0.03, ri - 0.012, r));\n    ic = mix(ic, vec3(0.3, 0.17, 0.2), sly")
    s = pre + F + post
    # the moods: the aggressive table over the usual one, and the lid's lift and slant into the face's spare uniform
    a = "startle: [5, 13], menace: [32, 33] };"
    i = s.index(a); j = s.index("\n", i) + 1; s = s[:j] + AGG + s[j:]
    s = rep(s, "fang = this.fangs ? 6 : 0, ea = EXPR[this.expr], eb = EXPR[this.exprB];",
               "fang = this.fangs ? 6 : 0, ag = U.fStyle.value === 1, xa = ag ? AGG[this.expr] : null, xb = ag ? AGG[this.exprB] : null, ea = xa || EXPR[this.expr], eb = xb || EXPR[this.exprB];")
    s = rep(s, "U.fComp.value.set(1, 1, 0, 0);", "U.fComp.value.set(1, 1, ag ? (xa ? xa[2] : 0) + ((xb ? xb[2] : 0) - (xa ? xa[2] : 0)) * k : 0, ag ? (xa ? xa[3] : 0) + ((xb ? xb[3] : 0) - (xa ? xa[3] : 0)) * k : 0);")
    return s
