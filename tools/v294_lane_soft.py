"""v294: the Whirlwind's lane on the ground at half its strength (strip, rails, chevrons and the lock flash alike), so it tells you
where the charge will go without shouting over the stage."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    return rep(s, "gl_FragColor = vec4(c, clamp(a * uA, 0.0, 1.0)); }",
                  "gl_FragColor = vec4(c, clamp(a * uA, 0.0, 1.0) * 0.5); } // (v294: half strength)")
