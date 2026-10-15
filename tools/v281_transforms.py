"""v281: the pick-ups (the Roller, the Turret, the Paint Trap, the Whirlwind) are called Transforms: grab one and you change into it.
The lesson's call when the roller turns up reads "This is a TRANSFORM item. TAP it!" (or Press F); the Strokes page's third tab, its
heading, a card's label and the toast when you pick one say Transform; the How to play card calls them Transforms; Ol' Bloop's lines
and the lesson's checklist do too. The locker's wearables are still "items": those are a different thing."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the lesson, when the roller turns up in your hand
    s = rep(s, "say('This is your *ROLLER*. *TAP* it!', 'This is your *ROLLER*. Press *F*!')", "say('This is a *TRANSFORM* item. *TAP* it!', 'This is a *TRANSFORM* item. Press *F*!')")
    s = rep(s, "'Dodging', 'The roller', 'The orb', 'Finding items'];", "'Dodging', 'Transforms', 'The orb', 'Finding items'];")
    # the Strokes page: the tab, its heading, the card's label, the toast, what a screen reader hears
    s = rep(s, '<span class="stk">Item</span><span class="stnow" id="stItemNow">', '<span class="stk">Transform</span><span class="stnow" id="stItemNow">')
    s = rep(s, "item: { h: 'Items', s: 'You start every match holding it',", "item: { h: 'Transforms', s: 'You start every match holding it',")
    s = rep(s, "$('stPopKind').textContent = item ? 'Item' : skill ? 'Skill' : 'Special stroke';", "$('stPopKind').textContent = item ? 'Transform' : skill ? 'Skill' : 'Special stroke';")
    s = rep(s, "stToast(spName(id) + ' is your starting item');", "stToast(spName(id) + ' is your starting transform');")
    s = rep(s, "(k === 'skill' ? 'Skill: ' : 'Item: ') + o.name", "(k === 'skill' ? 'Skill: ' : 'Transform: ') + o.name")
    # Ol' Bloop
    s = rep(s, "Skills and items have their own tabs up top", "Skills and transforms have their own tabs up top")
    s = rep(s, "your special move, a skill and the item you start with.", "your special move, a skill and the transform you start with.")
    # How to play
    s = rep(s, '<span class="cap">Pick-ups</span>', '<span class="cap">Transforms</span>')
    s = rep(s, "$('howItems').textContent = 'A roller or a turret turns up on the canvas now and then. Grab it and it waits in your hand: ' + say('tap its button', 'press F') + ' when you want it. The roller lays wide stripes and refills you; the turret plants you and fires paint. Picking up another drops the one you hold.';",
               "$('howItems').textContent = 'Transforms turn up on the canvas now and then: a roller, a turret, a paint trap or a whirlwind. Grab one and it waits in your hand; ' + say('tap its button', 'press F') + ' and you change into it. The roller lays wide stripes and refills you; the turret plants you and fires paint. You start every match holding the one you picked under Strokes. Picking up another drops the one you hold.';")
    return s
