"""cq01: the Season Conquest level back on top of the current game: the Sunken Keep stage and the Jellyfish Boss fight as they
played in v319 (the modules v309_conquest_stage to v319_keep_polish, applied in v319's order, after the whole release list).

The old modules are applied as they are. Where code they patch has changed since v319, FIX swaps their anchor (in both the text
looked for and its replacement) for today's form:
- v332_lesson_perf added the slow-motion uniforms to the last pass's shader and to the edge overlay's condition."""
import importlib

MODS = ['v309_conquest_stage', 'v311_conquest_boss', 'v315_boss_demo', 'v316_keep_look', 'v316_boss_bar', 'v316_boss_sfx',
        'v317_boss_moves', 'v318_boss_moves2', 'v319_boss_intro', 'v319_keep_polish']

FIX = {'v319_boss_intro': [
    ("uniform vec3 uEdgeC, uHitC, uVigC;", "uniform vec3 uEdgeC, uHitC, uVigC; uniform vec4 uSlowV; uniform vec2 uSlowPx;"),
    ("  if (EDGE.on || heatK > 0.02) edgeOverlay();\n", "  if (EDGE.on || heatK > 0.02 || EDGE_U.uSlowV.value.x > 0.003) edgeOverlay();\n"),
]}

def shim(name):
    fixes = FIX.get(name, [])
    def rep(s, a, b, n=1):
        if s.count(a) != n:
            for o, w in fixes:
                if o in a: a = a.replace(o, w); b = b.replace(o, w)
        c = s.count(a); assert c == n, (name, c, n, a[:160]); return s.replace(a, b)
    return rep

def apply(s):
    for m in MODS:
        mod = importlib.import_module(m); mod.rep = shim(m); s = mod.apply(s)
    return s
