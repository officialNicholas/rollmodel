"""v444: Paint the Stage says what wins (the user: "The sub text needs to explain more that it's paint coverage"). Under the name, in
place of "Out-paint the CPUs": "Cover more floor than the CPUs"; online, in place of "Real rivals, no CPUs": "Cover more floor than real
rivals". The strip over the card still says "Most paint wins"."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, '<b>Paint the Stage</b><small>Out-paint the CPUs</small>', '<b>Paint the Stage</b><small>Cover more floor than the CPUs</small>')
    s = rep(s, '<b>Paint the Stage</b><small>Real rivals, no CPUs</small>', '<b>Paint the Stage</b><small>Cover more floor than real rivals</small>')
    return s
