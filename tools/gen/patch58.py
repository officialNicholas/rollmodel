import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# a pound started as a giant finishes as a giant: the clock can't run out mid-pound (landing ends it anyway)
rep("  if (D.giantT > 0) { D.giantT -= dt;", "  if (D.giantT > 0) { D.giantT = D.slam ? Math.max(D.giantT - dt, 0.05) : D.giantT - dt;")
# and it holds full size through the pound instead of flickering small
rep("const gt = D.giantT > 0 ? (D.giantT < 0.9 && Math.sin(clock * 40) > 0 ? GIANT_K * 0.75 : GIANT_K) : 1;",
    "const gt = D.giantT > 0 ? (D.giantT < 0.9 && !D.slam && Math.sin(clock * 40) > 0 ? GIANT_K * 0.75 : GIANT_K) : 1;")
open(F, 'w').write(s)
print('ok')
