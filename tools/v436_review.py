"""v436: nothing in the app reads as unfinished (App Review, guideline 2.1: "coming soon" placeholders get apps rejected as incomplete).
- the Strokes page's filler cards ("More soon") are gone; a rail just ends with its last stroke;
- a party mode the server has switched off (its card in the party picker, or a vote for it) says it isn't in parties yet, rather than "Coming soon";
- the account email and password reset messages, for a server without email, say what's true now rather than promising it;
- the messages for a build without a server (never the App Store one) say online play isn't available, not that it's coming."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, """const soon = '<span class="sgcard soon" aria-hidden="true"><i class="sghook"></i><span class="sgcb"><span class="sgca">' + stImg('soon') + '</span></span><span class="sgcf">More soon</span></span>';""",
            "const soon = ''; // (v436: no filler cards)")
    s = rep(s, "(x ? 'Coming soon' : 'Not for a party this size')", "(x ? 'Not in parties yet' : 'Not for a party this size')", 2)
    s = rep(s, "'<b>Coming soon</b><p>Emails for accounts are on their way.</p>", "'<b>Email</b><p>Adding an email isn’t available right now. Your account works without one.</p>")
    s = rep(s, "'<p class=\"frfine acw\">Account emails are switching on soon. Your email is kept for when they do.</p>'",
            "'<p class=\"frfine acw\">Your email stays private. It’s only used for your account.</p>'")
    s = rep(s, "'Password resets are coming soon.'", "'Password reset isn’t available right now. Try again later.'")
    s = rep(s, "frToast('<span>Online play is coming soon</span>')", "frToast('<span>Online play isn’t available right now</span>')")
    s = rep(s, "'Online matches are coming soon'", "'Online matches aren’t available right now'", 2)
    s = rep(s, ": '<p class=\"tttease\">Soon: the top three on <b>Friends</b> and <b>Global</b> win dabs every week.</p>';", ": '';")
    s = rep(s, "const bar = !x.on ? 'Coming soon' : ", "const bar = !x.on ? 'Not in parties yet' : ", 2)
    s = rep(s, "' <i class=\"soontag\">Coming soon</i>'", "' <i class=\"soontag\">Off</i>'")
    return s
