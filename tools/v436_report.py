"""v436: Report a player (App Review, guideline 1.2: players can see each other's usernames and play together, so they need a way to
report someone, as well as block them). From the Friends page:
- a friend's ... menu has Report next to Remove friend and Block;
- someone asking to be your friend has a ... button with Report and Block;
- a new list, Played online recently, has the real players from your last online matches (never the CPUs), each with Report and
  Block, so someone you met in matchmaking can be reported too.
Report asks what for (Offensive name, Cheating, Bullying, Something else), with Block them too as a tick box, and thanks you. The
report goes to rm_report (supabase/migrations/20261023000000_reports.sql); you look at it in the admin dashboard. The fine print on the
Friends page now says there's no chat. The recent players stay on the phone (not in the account's saved progress)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = (".frmenu.frrep span:first-child{flex-basis:100%}.frrb{display:inline-flex;align-items:center;gap:6px;font:700 12.5px/1.2 var(--font-ui);color:#4E4660;cursor:pointer}"
       ".frrb input{width:18px;height:18px;accent-color:#C2283C;margin:0}.frrow .frago{font:600 12px/1.3 var(--font-ui);color:#6E6680}\n")

JS = r"""
// ---- (v436) Report: a player can be reported from the Friends page (a friend, a request, someone met online), for one of four reasons
const FR_WHY = [['name', 'Offensive name'], ['cheating', 'Cheating'], ['bullying', 'Bullying'], ['other', 'Something else']];
function frRepMenu(id, name, place) {
  return '<div class="frmenu frrep"><span>Report ' + frEsc(hdOf(name)) + ' for:</span>' + FR_WHY.map(([k, t]) => '<button class="frb ghost" data-act="report" data-id="' + id + '" data-why="' + k + '" data-place="' + place + '" type="button">' + t + '</button>').join('')
    + '<label class="frrb"><input type="checkbox" id="frRepBlk"' + (FR.repBlk ? ' checked' : '') + '> Block them too</label><button class="frb ghost" data-act="nvm" type="button">Cancel</button></div>';
}
// the ... menu of someone who isn't a friend (a request, someone met online): Report, Block (asked first), or the report's reasons
function frOtherMenu(r, place) {
  const conf = FR.confirm;
  if (conf === 'report') return frRepMenu(r.id, r.name, place);
  if (conf === 'block') return '<div class="frmenu"><span>Block ' + frEsc(hdOf(r.name)) + '?</span><button class="frb bad" data-act="block" data-id="' + r.id + '" type="button">Block</button><button class="frb ghost" data-act="nvm" type="button">Keep</button></div>';
  return '<div class="frmenu"><button class="frb ghost" data-act="askreport" data-id="' + r.id + '" type="button">Report</button><button class="frb ghost" data-act="askblock" data-id="' + r.id + '" type="button">Block</button></div>';
}
const frMoreBtn = r => '<button class="frb ghost ic" data-act="more" data-id="' + r.id + '" type="button" aria-expanded="' + (FR.menu === r.id) + '" aria-label="More for ' + frEsc(hdOf(r.name)) + '">' + FR_MORE + '</button>';
function frReqRow(r) {
  const open = FR.menu === r.id;
  return '<li class="frrow' + (open ? ' open' : '') + '">' + frFace(r.look) + '<span class="frwho"><b>' + frEsc(hdOf(r.name)) + '</b><small>Rank ' + (r.rank | 0) + '</small></span><span class="frbtns"><button class="frb go" data-act="acc" data-id="' + r.id + '" type="button">Accept</button><button class="frb ghost ic" data-act="dec" data-id="' + r.id + '" type="button" aria-label="Decline ' + frEsc(hdOf(r.name)) + '">' + FR_X + '</button>' + frMoreBtn(r) + '</span>'
    + (open ? frOtherMenu(r, 'request') : '') + '</li>';
}
// the real players from your last online matches (the phone keeps the last 12), less your friends, requests and blocks
function frSawOnline(m) {
  const me = FR.me && FR.me.id, ok = id => typeof id === 'string' && /^[0-9a-f-]{36}$/i.test(id) && id !== me;
  const met = (m && Array.isArray(m.players) ? m.players : []).filter(p => p.slot !== m.you && !p.cpu && ok(p.sb)); if (!met.length) return;
  let L = Array.isArray(store.recent) ? store.recent.filter(x => x && ok(x.id)) : [];
  for (const p of met) { L = L.filter(x => x.id !== p.sb); L.unshift({ id: p.sb, name: String(p.name || 'Player').slice(0, 20), look: p.look && typeof p.look === 'object' ? p.look : {}, at: Date.now() }); }
  store.recent = L.slice(0, 12); save();
}
function frRecentHtml(b) {
  const skip = new Set([...b.friends, ...b.incoming, ...b.outgoing, ...b.blocked].map(r => r.id)), L = (Array.isArray(store.recent) ? store.recent : []).filter(r => r && r.id && !skip.has(r.id));
  if (!L.length) return '';
  const ago = t => { const s = Math.max(0, (Date.now() - (+t || 0)) / 1000); return s < 3600 ? Math.max(1, Math.round(s / 60)) + 'm ago' : s < 86400 ? Math.round(s / 3600) + 'h ago' : Math.round(s / 86400) + 'd ago'; };
  return '<section><h4>Played online recently</h4><ul class="frlist">' + L.map(r => { const open = FR.menu === r.id;
    return '<li class="frrow sm' + (open ? ' open' : '') + '">' + frFace(r.look) + '<span class="frwho"><b>' + frEsc(hdOf(r.name)) + '</b><small class="frago">Played ' + ago(r.at) + '</small></span><span class="frbtns">' + frMoreBtn(r) + '</span>' + (open ? frOtherMenu(r, 'recent') : '') + '</li>'; }).join('') + '</ul></section>';
}
async function frReport(b) {
  const id = b.dataset.id, why = b.dataset.why, place = b.dataset.place || 'friends', blk = !!($('frRepBlk') && $('frRepBlk').checked); FR.repBlk = blk;
  b.closest('.frmenu').querySelectorAll('button').forEach(x => { x.disabled = true; });
  try {
    const r = await sbRpc('rm_report', { p_other: id, p_reason: why, p_place: place, p_note: null, p_block: blk });
    if (r && r.ok) { FR.menu = ''; FR.confirm = ''; FR.err = ''; if (place === 'recent' && blk) store.recent = (store.recent || []).filter(x => x.id !== id), save(); frToast('<span>Thanks. <b>Report sent.</b> We look at every report within 24 hours.</span>'); hap('success'); await frPoll(); }
    else FR.err = r && r.why === 'slow_down' ? 'You’ve sent a lot of reports this hour. Try again later.' : r && r.why === 'not_found' ? 'That player isn’t around any more.' : 'Couldn’t send the report. Try again.';
  } catch (err) { FR.err = (err && (err.status === 404 || /PGRST202|Could not find the function/i.test(String(err.message || '')))) ? 'Couldn’t send the report. Try again later.' : frErrText(err); }
  frRender();
}
"""

def apply(s):
    # a friend's ... menu: Report beside Remove friend and Block; its reasons when picked
    s = rep(s, "+ (!open ? '' : '<div class=\"frmenu\">' + (conf ? '<span>' + (conf === 'remove' ? 'Remove ' : 'Block ')",
            "+ (!open ? '' : conf === 'report' ? frRepMenu(f.id, f.name, 'friends') : '<div class=\"frmenu\">' + (conf ? '<span>' + (conf === 'remove' ? 'Remove ' : 'Block ')")
    s = rep(s, """'<button class="frb ghost" data-act="askremove" data-id="' + f.id + '" type="button">Remove friend</button><button class="frb ghost" data-act="askblock" data-id="' + f.id + '" type="button">Block</button>') + '</div>') + '</li>';""",
            """'<button class="frb ghost" data-act="askremove" data-id="' + f.id + '" type="button">Remove friend</button><button class="frb ghost" data-act="askreport" data-id="' + f.id + '" type="button">Report</button><button class="frb ghost" data-act="askblock" data-id="' + f.id + '" type="button">Block</button>') + '</div>') + '</li>';""")
    # a request: a ... button with Report and Block
    a = s.index("b.incoming.map(r => '<li class=\"frrow\">'"); e = s.index("').join('') + '</ul></section>';", a)
    s = s[:a] + "b.incoming.map(frReqRow)" + s[e + len("')"):]
    # the players met online, above the blocked list
    s = rep(s, "    if (b.blocked.length) h += '<details class=\"frblk\"", "    h += frRecentHtml(b);\n    if (b.blocked.length) h += '<details class=\"frblk\"")
    s = rep(s, "h += '<p class=\"frfine\">Friends see your name, your look and your rank, and when you’re online.</p>';",
            "h += '<p class=\"frfine\">Friends see your name, your look and your rank, and when you’re online. There’s no chat in Roll Model. To report or block a player, tap ••• by their name.</p>';")
    # the actions
    s = rep(s, "  if (a === 'askremove' || a === 'askblock') { FR.confirm = a.slice(3); return frRender(); }",
            "  if (a === 'askremove' || a === 'askblock' || a === 'askreport') { FR.confirm = a.slice(3); return frRender(); }\n  if (a === 'report') return frReport(b);")
    s = rep(s, "  try { const r = await sbRpc(call[0], call[1]); if (a === 'acc' && r && r.ok) {",
            "  try { const r = await sbRpc(call[0], call[1]); if (a === 'block') store.recent = (store.recent || []).filter(x => x.id !== id), save(); if (a === 'acc' && r && r.ok) {")
    # every online match notes the real players in it
    s = rep(s, "  NM.unsub = netWire(net);\n", "  NM.unsub = netWire(net); try { frSawOnline(m); } catch (e) {}\n")
    # the recent players belong to the phone, not the account's saved progress
    s = rep(s, "'lastErr', 'netTok', 'csHi', 'st'], CS_BOOK", "'lastErr', 'netTok', 'csHi', 'st', 'recent'], CS_BOOK")
    i = s.index("function frRow(f) {"); s = s[:i] + JS.lstrip('\n') + s[i:]
    i = s.index(".frempty{"); s = s[:i] + CSS + s[i:]
    return s
