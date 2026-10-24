"""v460: after the training match, one way on: Continue, to the Paint Shop.

- The user: "You should have one option after the tutorial, to continue. It doesn't do a rematch though, it takes the user to the
  locker and the store. It says "you've unlocked new items" or something like that".
- The training match's results (and a replay of it from Settings) show a single button, Continue, with "New items unlocked" under it.
  Rematch and Menu are gone from that screen. Continue goes back to the lobby and straight into the Locker page on its Paint Shop tab
  (My Locker is the other tab there). Every other match ends as before.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "  const due = false, eb = $('endBtn');\n  end.classList.toggle('gate', due); eb.innerHTML = due ? '<span>Main menu</span><small>Something new in the lobby</small>' :",
               "  const lsn = !NM && !!(endInfo && endInfo.lesson), due = lsn, eb = $('endBtn'); end.classList.toggle('lsn', lsn); // (v460: after the training match, only Continue, to the shop)\n"
               "  end.classList.toggle('gate', due); eb.innerHTML = lsn ? '<span>Continue</span><small>New items unlocked</small>' : due ? '<span>Main menu</span><small>Something new in the lobby</small>' :")
    s = rep(s, "if (end.classList.contains('gate')) return toMenu();",
               "if (end.classList.contains('lsn')) return irisClose(() => { showMenu(); camSnap = true; irisOpen(); setTimeout(() => openLocker('shop'), 60); }); if (end.classList.contains('gate')) return toMenu();")
    return s
