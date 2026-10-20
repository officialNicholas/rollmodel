"""v396: a new name and online play (the user: "Changing the name here may have implications on online play, we need to
account for that").

- The game server hears a new name at once. Until now it kept the old one until the game next connected, so a party's
  plates and the next match's rivals showed the name you had before. Now a rename (in Stats, the lobby, the locker, or a
  name sorted out on the Friends page) is passed on as soon as the account has it: the party sees it on your plate, and
  the next match carries it. A new connection says the new name anyway.
- Not while a match is being found or played: the name others see is the one the search or the match began with. Your
  name in Stats, the lobby and the locker says so instead of opening ("Change your name after the match").
- For a player with an account, the rename card says what a new username means: you log in with it, and your friends,
  ranks and progress stay with you (they belong to the account, not the name).
- (The game server, v396, keeps the name it has when a new one is one its filter turns away, as it already did at hello,
  and answers when it can't save one.)"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

SYNC = r"""// (v396) your username on the game server too: a rename reaches it at once (a party's plates, the next match's rivals),
// not only at the next connection. Told once per name per connection
function ptNameSync() {
  try {
    const n = onName(); if (!ON.net || !n) return; ON.net.name = n;
    if (!ON.me || n === ON.nameTold) return; ON.nameTold = n;
    ON.net.setName(n).then(x => { if (ON.me) ON.me.name = x; }, () => { if (ON.nameTold === n) ON.nameTold = ''; });
  } catch (e) {}
}
// not while a match is being found or played (the name others see is the one it began with): says so, and true
function nameBusy() {
  if (!onBusy()) return false;
  AU.nope(); frToast('<span>' + (ON.match ? 'Change your name after the match' : 'Change your name when you’re not looking for a match') + '</span>');
  return true;
}
"""

def apply(s):
    # the rename card: not mid-search or mid-match; with an account, what a new username means
    s = rep(s, "function openName(first) {\n  nameFirst = !!first; const inp = $('nameInput');",
               "function openName(first) {\n  if (!first && nameBusy()) return;\n"
               "  { const c = $('nameForm').querySelector('.cnote'); if (c) c.textContent = !first && acctReady() ? 'You’ll log in with your new name. Your friends, ranks and progress stay with you.' : 'It goes up in lights when you win.'; }\n"
               "  nameFirst = !!first; const inp = $('nameInput');")
    s = rep(s, "$('stRename').addEventListener('click', uiClick(() => { $('statsModal').hidden = true; openName(false); }));",
               "$('stRename').addEventListener('click', uiClick(() => { if (nameBusy()) return; $('statsModal').hidden = true; openName(false); })); // (v396: Stats stays up when it can't be changed now)")
    # the game server hears it: from the account (any rename, or one made on another phone), a name kept here only, and on connecting
    s = rep(s, "if (!r.needs_name && r.name) { store.sbs.name = r.name; if (store.name !== r.name) { store.name = r.name; paintName(); } }",
               "if (!r.needs_name && r.name) { store.sbs.name = r.name; if (store.name !== r.name) { store.name = r.name; paintName(); } ptNameSync(); }")
    s = rep(s, "unSubmit('nameInput', 'nameSt', 'nameOk', nm => { AU.ui(); store.name = nm; save(); paintName(); const go = nameFirst;",
               "unSubmit('nameInput', 'nameSt', 'nameOk', nm => { AU.ui(); store.name = nm; save(); paintName(); ptNameSync(); const go = nameFirst;")
    s = rep(s, "on('welcome', w => { ON.me = w; ON.fails = 0; ON.stale = ON.party ? Date.now() + 2500 : 0; onBack(); });",
               "on('welcome', w => { ON.me = w; ON.fails = 0; ON.stale = ON.party ? Date.now() + 2500 : 0; ON.nameTold = w.name; ptNameSync(); onBack(); }); // (v396: a rename made while it connected)")
    s = rep(s, "function ptLookSync() {", SYNC + "function ptLookSync() {")
    return s
