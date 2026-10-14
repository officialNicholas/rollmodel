"""v260: the first-launch intro on top of v259. When the sound starts afresh (the app back from the background, or a call ended: v258's
renew), the intro's music stems are on the old audio context, so they come back on the new one: the layers that were in, on a new
clock, the stems' buffers carried over. Apply after v257_intro.py."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def apply(s):
    if "renew() { M.S = null; if (M.on) begin(); }," not in s:  # (the intro's own engine carries it from 6d88869 on)
        s = rep(s, "        wake() { if (M.on && !M.S) begin(); },\n",
                   "        wake() { if (M.on && !M.S) begin(); },\n"
                   "        // (v260) the sound started afresh on a new context: the stems come back on it, with the layers that were in\n"
                   "        renew() { M.S = null; if (M.on) begin(); },\n")
    s = rep(s, "    check();\n    try { window.dispatchEvent(new Event('aurenew')); } catch (e) {}\n",
               "    check(); if (api.flm && api.flm.renew) api.flm.renew(); // (v260: the first launch's music too)\n    try { window.dispatchEvent(new Event('aurenew')); } catch (e) {}\n")
    return s
