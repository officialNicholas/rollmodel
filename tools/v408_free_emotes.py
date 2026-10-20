"""v408: the four victory emotes are everyone's (the user: "make the three emotes free and always in your locker. No longer
purchases. We'll make other purchasable emotes in the future"). Slam, Lovestruck, Backflip and Showstopper are owned from the start
and sit in My Locker's Emotes row in that order; none is in the Paint Shop (its Emotes filter shows up again once there are emotes
to buy). Anyone who bought one in 407 keeps it, of course; nothing is refunded (they were on sale for one version)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "OWNED.add('slam'); BOUGHT.add('slam'); Object.assign(PRICES, { hearts: 420, flip: 600, spin: 750 }); // (v407: Slam is everyone's; the others' prices)",
               "for (const id of ['slam', 'hearts', 'flip', 'spin']) { OWNED.add(id); BOUGHT.add(id); } // (v408: the four emotes are everyone's, free)")
    s = rep(s, "const ems = EMOTE_ITEMS.filter(w => bought(w.id)).sort((a, b) => a.id === 'slam' ? -1 : b.id === 'slam' ? 1 : PRICE(a) - PRICE(b))",
               "const ems = EMOTE_ITEMS.filter(w => bought(w.id))")
    return s
