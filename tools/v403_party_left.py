"""v403: "<name> left the party" (the user: 'we need a "player" left the party message'). When someone is no longer in your
party's member list, a toast says so: "<name> left the party", or "<name> was removed" when the leader (you) took them out. In the
lobby (or any menu page); during a match the party's list isn't shown, so it waits for the lobby view after it.

Also (the user: "remove the credits page from the app"): Settings' Credits button and its page are gone; How to play, Terms of
Service and Privacy Policy share the row three ways.

And (the user: 'turning sensitivity needs a "default" button which returns that slider back to default'): a Default button beside
the Turning value puts it back to 80%; it's dimmed while the slider is already there."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v403) Turning's Default button, beside its value */
.trndef{appearance:none;margin-left:8px;padding:5px 9px 4px;border:0;border-radius:6px;background:#FFF8EA;color:#171320;font:400 11px/1 var(--font-display);letter-spacing:.03em;text-transform:uppercase;text-shadow:none;box-shadow:0 0 0 2px #171320,0 2px 0 2px #171320;cursor:pointer;transform:skewX(-6deg)}
.trndef:active{transform:skewX(-6deg) translateY(2px);box-shadow:0 0 0 2px #171320}
.trndef:disabled{opacity:.45;cursor:default}
"""

def apply(s):
    s = rep(s, "    for (const m of v.members) if (m.id !== my && !was.members.some(x => x.id === m.id)) { AU.pop(); buzz(12); onSay(hdOf(m.name) + ' joined your party'); }",
               "    for (const m of v.members) if (m.id !== my && !was.members.some(x => x.id === m.id)) { AU.pop(); buzz(12); onSay(hdOf(m.name) + ' joined your party'); }\n"
               "    for (const m of was.members) if (m.id !== my && !v.members.some(x => x.id === m.id)) { const out = ON.kicked && ON.kicked.has(m.id); if (ON.kicked) ON.kicked.delete(m.id); // (v403: who's gone, said on screen)\n"
               "      frToast('<span><b>' + frEsc(hdOf(m.name)) + '</b> ' + (out ? 'was removed' : 'left the party') + '</span>'); onSay(hdOf(m.name) + (out ? ' was removed' : ' left the party')); if (!out) AU.nope && AU.nope(); }")
    s = rep(s, "function ptKick(id) { if (!ON.net) return; ON.net.partyKick(id)",
               "function ptKick(id) { if (!ON.net) return; (ON.kicked = ON.kicked || new Set()).add(id); ON.net.partyKick(id)")
    # no Credits
    s = rep(s, '<button class="sbtn" id="credBtn" type="button" aria-haspopup="dialog"><span>Credits</span></button>', '')
    s = rep(s, "for (const [id, k] of [['tosBtn', 'tos'], ['privBtn', 'priv'], ['credBtn', 'cred']])", "for (const [id, k] of [['tosBtn', 'tos'], ['privBtn', 'priv']])")
    s = rep(s, "#setModal .sbtns.four{grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}", "#setModal .sbtns.four{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}")
    # Turning: a Default button
    s = rep(s, '<p class="slab">Turning <b class="trnv" id="turnVal">80%</b></p>', '<p class="slab">Turning <b class="trnv" id="turnVal">80%</b><button class="trndef" id="turnDef" type="button" aria-label="Turning back to default (80%)">Default</button></p>')
    s = rep(s, "lab.textContent = v + '%'; el.setAttribute('aria-valuetext', v + '%'); } };",
               "lab.textContent = v + '%'; el.setAttribute('aria-valuetext', v + '%'); } const d = $('turnDef'); if (d) d.disabled = v === 80; };\n"
               "  $('turnDef').addEventListener('click', () => { AU.init(); AU.ui(); store.turn = 80; save(); show(); }); // (v403)")
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
