"""v280: on the first launch's "All set?" card the character looked happy (cheeks up, blushing, a big open smile); now it's ready for
action. A new face, 'ready': the determined squint over the firm flat mouth (v279), its pupils a touch smaller. The card sets it as the
character's face while it's up, and the little moves it makes there (the perk, a look round, a tilt, a proud lift) show that or a confident smirk
instead of a grin. "Not yet" goes back to the usual friendly face for the picks; "Let's roll" keeps it ready for the launch. With the
Aggressive eyes, 'ready' is their heavy lid pulled a little lower."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the face, in the character's own tables (the axolotl's: the slime's older copies are left alone)
    s = rep(s, "startle: [5, 13], menace: [32, 33] };", "startle: [5, 13], menace: [32, 33], ready: [23, 36] };")
    s = rep(s, "const PUPILS = { peek: { pu: 1.08, py: 0 }, leap: { pu: 1.12, py: 0 }, curious: { pu: 1.14, py: 0.04 }, startle: { pu: 0.7, py: 0 }, smirk: { pu: 1, py: -0.06 } };",
               "const PUPILS = { peek: { pu: 1.08, py: 0 }, leap: { pu: 1.12, py: 0 }, curious: { pu: 1.14, py: 0.04 }, startle: { pu: 0.7, py: 0 }, smirk: { pu: 1, py: -0.06 }, ready: { pu: 0.9, py: -0.02 } };")
    s = rep(s, "focus: [0, 36, -0.02, 0.04],", "focus: [0, 36, -0.02, 0.04], ready: [0, 36, -0.025, 0.05],")
    # the intro's "All set?" card: ready for action while it's up, the friendly face back if you go back to the picks
    s = rep(s, "    else if (ph === 'iris') { shot(look || 'eyes'); card('flIris'); AU.flm.layer(1); if (was === 'confirm') move('look'); }",
               "    else if (ph === 'iris') { shot(look || 'eyes'); card('flIris'); AU.flm.layer(1); if (was === 'confirm') { move('look'); if (X.I && X.I.setExpression) X.I.setExpression('happy'); } }")
    s = rep(s, "    else if (ph === 'confirm') { shot('stood'); card('flAsk'); move('perk'); }",
               "    else if (ph === 'confirm') { shot('stood'); card('flAsk'); move('perk'); if (X.I && X.I.setExpression) X.I.setExpression('ready'); } // (v280: ready for action, not happy)")
    s = rep(s, "    if (mv.face && I.face) I.face(mv.face, 0.15); // (the move's face, held over its own while it lasts)",
               "    if (mv.face && I.face) I.face(X.ph === 'confirm' || X.ph === 'wink' ? ({ happy: 'ready', glee: 'smirk', content: 'ready', cute: 'ready', curious: 'ready' })[mv.face] || mv.face : mv.face, 0.15); // (the move's face, held over its own while it lasts; v280: on All set? no grins)")
    return s
