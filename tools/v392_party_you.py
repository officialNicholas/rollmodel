"""v392: no name plate under your own character in a party (the user: "You" is redundant). Only the others' plates show, each with
their handle, the leader's crown and the tick when they're ready; you're the one in the middle, and the Ready button says where you
are."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "const plates = []; if (inp && me) plates.push({ key: 'me', m: me, me: true });",
               "const plates = []; // (v392: none under you)")
    return s
