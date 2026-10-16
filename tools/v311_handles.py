"""v311: an online account shows as a handle: @ and the username, in small letters (@number1).

- Your own name, wherever the game shows it (the tape over the power bar, your stats, the locker, the versus card, the tally, the
  results, the winner screen, Showdown's lists and banners), is your handle once you're signed in with an account. Without an account
  it stays as it was.
- Other players with accounts show by their handles too: the rival in an online match, and everyone in the Friends and online lists
  (friends, requests, the Friends board, the room, "You vs ..."). CPU rivals keep their plain names, so a handle always means a person.
- Where names are set in capitals (the tape, the versus card, the tally, the winner screen), a handle keeps its small letters.
- Settings says "Signed in as @number1", and the welcome after making an account or logging in says the handle."""
import re

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HELP = r"""
// (v311) a player with an account online shows as a handle: @ and the username in small letters. Your own name is yours once you're
// signed in; a name that's a handle keeps its small letters where names are set in capitals (the class hd)
const isHd = n => typeof n === 'string' && n.charAt(0) === '@';
const hdOf = n => { const t = String(n == null ? '' : n).trim(); return t ? (isHd(t) ? t : '@' + t).toLowerCase() : t; };
const hdOn = () => { try { return !!(window.acctReady && window.acctReady()); } catch (e) { return false; } };
const playerName = () => { const n = cleanName(store.name) || 'You'; return store.name && hdOn() ? hdOf(n) : n; };
const nmHtml = n => isHd(n) ? '<bdi class="hd">' + escAttr(n) + '</bdi>' : escAttr(n);
function nmSet(el, n) { if (!el) return; el.textContent = n; el.classList.toggle('hd', isHd(n)); }
"""

CSS = r"""
/* (v311) a handle keeps its small letters where names are set in capitals */
.hd{text-transform:none!important}
"""

def apply(s):
    s = rep(s, "const playerName = () => cleanName(store.name) || 'You';", HELP.strip('\n'))
    s = rep(s, "const me = playerName().toLowerCase(), pool = RIVAL_NAMES", "const me = playerName().replace(/^@/, '').toLowerCase(), pool = RIVAL_NAMES")
    # ---------------- your own name: the labels set from code
    s = rep(s, "function paintName() { const n = playerName(); NAMES[0] = n; $('nameShow').textContent = store.name ? n : 'Name'; { const pn = $('pbName'); if (pn) pn.textContent = n; } const lt = $('lookNameTxt'); if (lt) lt.textContent = n; }",
               "function paintName() { const n = playerName(); NAMES[0] = n; nmSet($('nameShow'), store.name ? n : 'Name'); nmSet($('pbName'), n); nmSet($('lookNameTxt'), n); }")
    s = rep(s, "$('pbName').textContent = n; $('pbXp')", "nmSet($('pbName'), n); $('pbXp')")
    s = rep(s, "$('stName').textContent = playerName();", "nmSet($('stName'), playerName());")
    s = rep(s, "$('lookNameTxt').textContent = playerName();", "nmSet($('lookNameTxt'), playerName());")
    # ---------------- names in matches and on the screens after
    s = rep(s, "<small>' + (cls === 'me' ? 'You' : cls === 'me ally' ? 'Teammate' : NM ? 'Online' : 'CPU') + '</small><b>' + escAttr(name) + '</b>",
               "<small>' + (cls === 'me' ? 'You' : cls === 'me ally' ? 'Teammate' : NM ? 'Online' : 'CPU') + '</small><b' + (isHd(name) ? ' class=\"hd\"' : '') + '>' + escAttr(name) + '</b>")
    s = rep(s, "nm.textContent = nameOf(e.D);", "nmSet(nm, nameOf(e.D));")
    s = rep(s, "jl = '<span class=\"jl\" data-a=\"left\">' + escAttr(playerName()) + '</span>';", "jl = '<span class=\"jl\" data-a=\"left\">' + nmHtml(playerName()) + '</span>';")
    s = rep(s, "escAttr(D === P ? playerName() : nameOf(D)) + '</span>';", "nmHtml(D === P ? playerName() : nameOf(D)) + '</span>';")
    s = rep(s, "<span class=\"bn\"><b>' + escAttr(nm) + '</b>", "<span class=\"bn\"><b>' + nmHtml(nm) + '</b>", 2)
    s = rep(s, "'<span class=\"vn\">' + escAttr(nameOf(e.D))", "'<span class=\"vn\">' + nmHtml(nameOf(e.D))")
    s = rep(s, "<span class=\"sdn\">' + escAttr(sdName(D)) + '</span>", "<span class=\"sdn\">' + nmHtml(sdName(D)) + '</span>")
    s = rep(s, "for (const w of vic.name.toUpperCase().split(' ').filter(Boolean))", "for (const w of vic.name.split(' ').filter(Boolean).map(w => isHd(w) ? w : w.toUpperCase()))")
    s = rep(s, "t.nm.textContent = nm;", "nmSet(t.nm, nm);")
    s = rep(s, "$('kofBy').textContent = by ? nameOf(by) : (koLine(reason, true) || 'Out!');", "nmSet($('kofBy'), by ? nameOf(by) : (koLine(reason, true) || 'Out!'));")
    s = rep(s, "$('sdSpecN').textContent = nameOf(S);", "nmSet($('sdSpecN'), nameOf(S));")
    # ---------------- other players with accounts: the online rival, the Friends and online lists, the account row
    s = rep(s, "NAMES[1] = String(fo.name || 'Rival').slice(0, 16);", "NAMES[1] = fo.name ? hdOf(String(fo.name).slice(0, 16)) : 'Rival'; // (v311: a person, by their handle)")
    s, n = re.subn(r"frEsc\((f|r|p|o|fresh\[0\])\.name\)", r"frEsc(hdOf(\1.name))", s); assert n == 12, n
    s = rep(s, "'Signed in as <b>' + frEsc(nm) + '</b>'", "'Signed in as <b>' + frEsc(hdOf(nm)) + '</b>'")
    s = rep(s, "t = 'Delete <b>' + frEsc(nm) + '</b> for good?", "t = 'Delete <b>' + frEsc(hdOf(nm)) + '</b> for good?")
    s = rep(s, "acDone('<span>Welcome, <b>' + frEsc(me.name) + '</b>! Your account is ready.</span>');", "acDone('<span>Welcome, <b>' + frEsc(hdOf(me.name)) + '</b>! Your account is ready.</span>');")
    s = rep(s, "acDone('<span>Welcome back, <b>' + frEsc(me.name) + '</b>!</span>');", "acDone('<span>Welcome back, <b>' + frEsc(hdOf(me.name)) + '</b>!</span>');")
    # ---------------- signing in or out (and the first frame once accounts are known) puts the right name up
    s = rep(s, "function acPaintAll() { if (!$('setModal').hidden) acSetPaint();", "function acPaintAll() { try { paintName(); paintPBar(); } catch (e) {} /* (v311: handle or plain name) */ if (!$('setModal').hidden) acSetPaint();")
    s = rep(s, "window.acctReady = acctReady; window.acctOpen = acctOpen;", "window.acctReady = acctReady; window.acctOpen = acctOpen; setTimeout(() => { try { paintName(); paintPBar(); } catch (e) {} }, 0); // (v311: your handle from the first frame)")
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
