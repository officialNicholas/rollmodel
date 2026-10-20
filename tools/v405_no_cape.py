"""v405: the hero cape comes out of the game (the user: "remove cape item").

It's off the item list, so the Paint Shop and the locker no longer offer it and no CPU rival wears it; a saved look that had it goes
back to nothing on the back (the look is only ever rebuilt from items still on the list). It's never drawn, not even on someone online
whose older game still sends it. Anyone who bought it gets the 480 dabs back, once."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, ", { id: 'cape', name: 'Hero cape', slot: 'back', stage: 'blank' }", "")
    s = rep(s, "W.cape.visible = !off && look.back === 'cape';", "W.cape.visible = false; /* (v405: the cape's gone) */")
    # bought it: the dabs back, once (from the save as it was, before the owned list is rebuilt without it)
    a = "const OWNED = new Set(Array.isArray(store.owned) ? store.owned.filter(id => ITEMS.some(w => w.id === id)) : []);"
    s = rep(s, a, "if (!store.capeBack && Array.isArray(store.bought) && store.bought.includes('cape')) { store.capeBack = 1; store.drops = (store.drops || 0) + 480; store.bought = store.bought.filter(i => i !== 'cape'); if (Array.isArray(store.owned)) store.owned = store.owned.filter(i => i !== 'cape'); } // (v405: the cape's gone; what it cost comes back)\n" + a)
    return s
