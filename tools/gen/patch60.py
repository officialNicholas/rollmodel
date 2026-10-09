import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# the CPU lets its roll finish its dash before pounding, so a stun roll actually lands
rep("  if (D === P) kick($('slamBtn'), 'press');\n", "  if (D === P) kick($('slamBtn'), 'press');\n  if (D.ai && D.rollT > ROLL_T - ROLL_DASH) return false;\n")
open(F, 'w').write(s)
print('ok')
