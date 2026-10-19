"""v361: the first launch's eyes come up the colour the card shows picked.

The intro's character was made with no eye colour, so its eyes came up the model's own violet while the colour card had Brown picked
(the game's default for a new player). Now, as soon as it's made, it wears the look the cards show: the picked eye colour (Brown for a
new player) and the picked eye style (Round), so what you see is what's picked from the first moment, and what you keep if you just tap
Next."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "    I.noGhost = true; if (I.coatOn) I.coatOn(); if (I.setPaint) I.setPaint(PEARL); if (I.setExpression) I.setExpression('happy');\n",
               "    I.noGhost = true; if (I.coatOn) I.coatOn(); if (I.setPaint) I.setPaint(PEARL); if (I.setExpression) I.setExpression('happy');\n"
               "    if (I.setIris) I.setIris((EYE_COLS[myLook.iris] || EYE_COLS.brown).lin); if (I.setEyeStyle) I.setEyeStyle(EYE_STYLE_K[myLook.eyes] || 0); // (v361: the colour and style the cards show picked, not the model's own violet)\n")
    return s
