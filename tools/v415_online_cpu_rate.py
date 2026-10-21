"""v415: an online match against CPUs pays like CPUs, not like people. v414 paid every online match at the people rate (x1.5); with
v413 a party can play CPUs online, and matchmaking fills empty places with CPUs. Now the rate goes by who you played: all people x1.5,
all CPUs x1 (the online CPUs think at medium), a mix in between by how many of your rivals were people. The results' tag says which
("Online", "Online CPUs", "Online, 1 CPU")."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # who was in the match: the roster's CPUs and everyone else
    s = rep(s, "function netDress(m) {\n", "function netDress(m) {\n  if (NM) { NM.opp = Math.max(0, m.players.length - 1); NM.cpus = m.players.filter(p => p.cpu).length; } // (v415: for the dabs' rate)\n")
    s = rep(s, "  const who = solo ? '' : NM ? 'online' : tut || tut2 || tut3 ? 'medium' : diff, x = solo ? 1 : DAB_X[who] || 1;",
               "  const who = solo ? '' : NM ? 'online' : tut || tut2 || tut3 ? 'medium' : diff, nOpp = NM && NM.opp | 0, nCpu = NM ? Math.min(NM.cpus | 0, nOpp) : 0;\n"
               "  const x = solo ? 1 : NM && nCpu ? +(DAB_X.medium + (DAB_X.online - DAB_X.medium) * (nOpp - nCpu) / Math.max(1, nOpp)).toFixed(2) : DAB_X[who] || 1; // (v415: CPUs online pay like CPUs)")
    s = rep(s, "  if (x !== 1) why.push({ t: who === 'online' ? 'Online' : ",
               "  if (x !== 1) why.push({ t: who === 'online' ? (nCpu ? 'Online, ' + nCpu + (nCpu === 1 ? ' CPU' : ' CPUs') : 'Online') : ")
    return s
