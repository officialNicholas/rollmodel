"""v371: a stroke you've bought or crafted is "Learned".

- The info card's pill says Learned (it said Yours for one bought with dabs, Crafted for the Giant); the starters still say Yours.
- The line under it says "Learned: it’s yours" ("It’s yours", "Crafted: it’s yours").
- Buying one says "Learned! Flash Freeze is your special stroke" ("Bought! ..."), and the Giant's craft finishing (or Skip) says
  "Learned! The Giant is yours" ("The Giant is ready!"). Ol' Bloop's lesson says "Learned! Tap Equip to make it your special stroke".
- A tag read out by VoiceOver says learned (it said owned).
- The nudge on the lock screen when a craft is done stays "The Giant is ready!"."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "const stReady = id => (stIsSkill(id) ? spName(id) : 'The ' + spName(id)) + ' is ready!';",
               "const stReady = id => (stIsSkill(id) ? spName(id) : 'The ' + spName(id)) + ' is ready!';\n"
               "const stLearnt = id => 'Learned! ' + (stIsSkill(id) ? spName(id) : 'The ' + spName(id)) + ' is yours'; // (v371: a craft done, on the page)")
    s = rep(s, "craftTick(); AU.ui(); renderStrokes(); stToast(stReady(id)); }", "craftTick(); AU.ui(); renderStrokes(); stToast(stLearnt(id)); }")
    s = rep(s, "if (!craftTick()) { renderStrokes(); stToast(stReady(id)); }", "if (!craftTick()) { renderStrokes(); stToast(stLearnt(id)); }")
    s = rep(s, "  stToast('Bought! ' + o.name + ' is ' + (stIsItem(id) ? 'your starting transform' : stIsSkill(id) ? 'your skill' : 'your special stroke'));",
               "  stToast('Learned! ' + o.name + ' is ' + (stIsItem(id) ? 'your starting transform' : stIsSkill(id) ? 'your skill' : 'your special stroke'));")
    s = rep(s, "own ? (ST_STARTERS.includes(o.id) ? 'yours' : 'owned') :", "own ? (ST_STARTERS.includes(o.id) ? 'yours' : 'learned') :")
    s = rep(s, "ow.innerHTML = ST_CHECK + (on ? 'Equipped' : ST_STARTERS.includes(id) || stBuys(o) ? 'Yours' : 'Crafted');",
               "ow.innerHTML = ST_CHECK + (on ? 'Equipped' : ST_STARTERS.includes(id) ? 'Yours' : 'Learned');")
    s = rep(s, "own ? (stBuys(o) ? 'It’s yours' : 'Crafted: it’s yours') :", "own ? 'Learned: it’s yours' :")
    s = rep(s, "tutShow('It’s ready! Tap Equip to make it your special stroke'", "tutShow('Learned! Tap Equip to make it your special stroke'")
    return s
