"""v355: the account's email, and Forgot password.

- New account asks for an email (required: it's the only way back in after a forgotten password; EMAIL_REQ turns that off). Once the
  account is made it's saved (rm_email_set, supabase/migrations/20261019000000_email.sql) and the server sends the welcome email:
  "Welcome to Roll Model", the username, and a button that confirms the email. If that email is taken or wrong, the account is still
  made and the form says so; fixing it and pressing the button again just saves the email.
- Log in has "Forgot password?": a username or an email, and if that account has a confirmed email, a link to choose a new password
  goes to it (rm_reset_request; the link opens the website's reset page). It always says the same, so it never tells whether an
  account exists.
- The menu's Account has Email for a signed-in player: add one, see whether it's confirmed, send the welcome email again, or change
  it. Until an email is added (or confirmed), the menu says so.
- Until the v355 SQL is run, everything works as before: the account is made without an email, and these say they're coming soon.
- The Privacy Policy says what the email is for (account emails only: the welcome, password resets, and a note when the password
  changes), that it's private, and that Resend sends them. New accounts agree to that version of the terms."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = r"""// ---------- (v355) the account's email: asked for when the account is made (the server sends the welcome email, with the username
// and a button that confirms the email: supabase/migrations/20261019000000_email.sql), added, sent again or changed from the menu's
// Account, and "Forgot password?" on Log in (a reset link to a confirmed email; it opens the website, where the new password is
// chosen). Private: other players never see it, and sign-in stays by username ----------
const EMAIL_REQ = true; // (new accounts give one: it's the only way back in after a forgotten password)
const emOk = s => s.length >= 6 && s.length <= 254 && /^[^@\s<>",;]+@[^@\s<>",;]+\.[A-Za-z]{2,}$/.test(s); // (as the server checks it)
const EM = { st: null, at: 0, note: '' }; // st: { email, verified, mail } from rm_email_get ({ off: true } before the v355 SQL), null when not asked yet
const emWhy = w => w === 'taken' ? 'That email is used by another account.' : w === 'bad' ? 'Check your email address.' : w === 'slow_down' ? 'That’s a lot of changes. Try again in an hour.'
  : w === 'verified' ? 'Your email is already confirmed.' : 'Something went wrong. Try again.';
async function emLoad(force) {
  if (!acctReady()) { EM.st = null; return null; }
  if (EM.st && !force && Date.now() - EM.at < 60000) return EM.st;
  try { const r = await sbRpc('rm_email_get', {}); EM.st = r && typeof r === 'object' ? r : null; }
  catch (e) { if (!csMissing(e)) throw e; EM.st = { off: true }; }
  EM.at = Date.now(); return EM.st;
}
function acShake(msg) { AC.err = msg; const x = $('acErr'); if (x) { x.textContent = msg; kick(x, 'unshake'); } AU.nope(); }
function acForgotHtml() {
  if (AC.sentTo) return '<div class="frmsg acmsg">' + FR_FACES + '<b>Check your email</b><p>If <b>' + frEsc(AC.sentTo) + '</b> has a confirmed email, a link to choose a new password is on its way. It works for 30 minutes. Not there? Check your spam folder.</p><div class="acbtns"><button class="frb go" data-ac="back" type="button">Back to Log in</button></div></div>';
  return '<form class="acform acin" id="acForgot" novalidate autocomplete="on">'
    + '<p class="frfine acw acflead">Type your username, or the email on your account. If it has a confirmed email, we’ll send it a link to choose a new password.</p>'
    + '<div class="acf acw"><label for="acWho">Username or email</label><input id="acWho" data-k="who" type="text" maxlength="254" autocomplete="username" autocapitalize="off" autocorrect="off" spellcheck="false" value="' + frEsc(AC.f.who || '') + '"></div>'
    + '<p class="acerr acw" id="acErr" role="alert">' + frEsc(AC.err || (NET_WALLED ? NET_APP : '')) + '</p>'
    + '<button class="frb go acgo acw" id="acGo" type="submit">Send me a link</button>'
    + '<button class="aclink acw acback" data-ac="back" type="button">Back to Log in</button></form>';
}
async function acForgot() {
  if (AC.busy) return; const w = ($('acWho') ? $('acWho').value : '').trim();
  if (w.length < 3) return acShake('Type your username or email.');
  if (AC.forgotAt && Date.now() - AC.forgotAt < 30000) return acShake('We just sent one. Give it a minute.');
  AC.busy = true; AC.err = ''; acBusy('Sending…');
  try { await sbFetch('/rest/v1/rpc/rm_reset_request', { p_who: w }); AC.forgotAt = Date.now(); AC.busy = false; AC.sentTo = w; AU.power(); acRender(); }
  catch (e) { AC.busy = false; acBusy(null); acShake(csMissing(e) ? 'Password resets are coming soon.' : acErrText(e)); }
}
function acEmailHtml() {
  const s = EM.st;
  if (!s) return '<div class="frmsg acmsg"><p>' + frEsc(AC.err || 'Getting your email…') + '</p>' + (AC.err ? '<div class="acbtns"><button class="frb" data-ac="close" type="button">Close</button></div>' : '') + '</div>';
  if (s.off) return '<div class="frmsg acmsg">' + FR_FACES + '<b>Coming soon</b><p>Emails for accounts are on their way.</p><div class="acbtns"><button class="frb" data-ac="close" type="button">OK</button></div></div>';
  const top = !s.email ? 'Add your email, so you can get back in if you ever forget your password. Other players never see it.'
    : !s.verified ? 'We sent a link to <b>' + frEsc(s.email) + '</b>. Tap it to confirm your email' + (s.mail ? ', so you can reset your password if you ever forget it.' : '.')
    : '<b>' + frEsc(s.email) + '</b> is confirmed. If you ever forget your password, Log in has a link to reset it.';
  return '<form class="acform acin" id="acEm" novalidate autocomplete="on">'
    + '<p class="frfine acw acflead">' + top + (EM.note ? ' <b>' + frEsc(EM.note) + '</b>' : '') + '</p>'
    + (s.email && !s.verified && s.mail ? '<button class="frb ghost acw acresend" data-ac="resend" type="button">Send it again</button>' : '')
    + '<div class="acf acw"><label for="acEmail2">' + (s.email ? 'Change your email' : 'Email') + '</label><input id="acEmail2" data-k="email2" type="email" inputmode="email" maxlength="254" autocomplete="email" autocapitalize="off" autocorrect="off" spellcheck="false" value="' + frEsc(AC.f.email2 || '') + '"></div>'
    + '<p class="acerr acw" id="acErr" role="alert">' + frEsc(AC.err || (NET_WALLED ? NET_APP : '')) + '</p>'
    + '<button class="frb go acgo acw" id="acGo" type="submit">' + (s.email ? 'Save new email' : 'Save email') + '</button>'
    + (s.mail ? '' : '<p class="frfine acw">Account emails are switching on soon. Your email is kept for when they do.</p>') + '</form>';
}
async function acEmailSave() {
  if (AC.busy) return; const em = ($('acEmail2') ? $('acEmail2').value : '').trim();
  if (!emOk(em)) return acShake('Check your email address.');
  AC.busy = true; AC.err = ''; EM.note = ''; acBusy('Saving…');
  try {
    const r = await sbRpc('rm_email_set', { p_email: em }); AC.busy = false;
    if (!r || r.ok === false) { acBusy(null); return acShake(emWhy(r && r.why)); }
    AC.f.email2 = ''; EM.note = r.verified ? 'Already confirmed.' : r.sent ? 'Check your inbox.' : ''; await emLoad(true).catch(() => {}); AU.power(); acRender(); acSetPaint();
  } catch (e) { AC.busy = false; acBusy(null); acShake(acErrText(e)); }
}
async function acEmailResend() {
  if (AC.busy) return; AC.busy = true; EM.note = '';
  try { const r = await sbRpc('rm_email_resend', {}); EM.note = r && r.ok ? (r.sent ? 'Sent again: check your inbox.' : '') : emWhy(r && r.why); }
  catch (e) { EM.note = acErrText(e); }
  AC.busy = false; if (AC.open && AC.tab === 'email') acRender();
}
function acEmailOpen() {
  if (!acctReady()) return acctOpen(null, 'in');
  AC.next = null; AC.tab = 'email'; AC.err = ''; AC.busy = false; AC.f.email2 = ''; EM.note = '';
  if (!AC.open) AC.ret = document.activeElement; AC.open = true; $('acModal').hidden = false; acRender();
  emLoad(true).then(() => { if (AC.open && AC.tab === 'email') acRender(); }).catch(e => { AC.err = acErrText(e); if (AC.open && AC.tab === 'email') acRender(); });
}
"""

CSS = """/* (v355) the account sheet's own pages (Forgot password, Your email): no tabs; their links and lead line */
#acModal.side .actabs{display:none}
.acform .acforgot{justify-self:start;margin:-4px 0 2px}
.acform .acback{justify-self:center;margin-top:2px}
.acform .acflead{margin:0;text-align:left}
.acform .acresend{justify-self:start}
/* (v355) the email fields look like the other fields (the browser's own email field is dark in a dark colour scheme) */
.acform input[type=email]{display:block;width:100%;min-width:0;height:44px;box-sizing:border-box;margin:0;padding:0 11px;border:2px solid var(--black);border-radius:6px;background-color:#fff;color:var(--black);font:600 16px/1 var(--font-ui);-webkit-appearance:none;appearance:none}
/* the lead line of Forgot password and Your email stays on top, sideways too */
.acform>.acflead{order:-1}
@media (min-aspect-ratio:1/1) and (max-height:600px){.acform input[type=email]{height:40px;min-height:40px}}
/* the sheet keeps to the screen (its body scrolls if it must), and sideways New account takes three columns so it fits */
#acModal{grid-template-rows:minmax(0,1fr)}
@media (min-aspect-ratio:1/1) and (max-height:600px){#acModal.nu .accard{width:min(100%,780px)}#acNew{grid-template-columns:repeat(3,minmax(0,1fr))}#acNew>.frfine{order:0;grid-column:span 2;align-self:center}}
"""

def apply(s):
    # ---- the code, before the account sheet's own
    s = rep(s, "// ---- the account sheet: New account (from the player you are) and Log in\n", JS + "// ---- the account sheet: New account (from the player you are) and Log in\n")
    s = rep(s, "</style>\n\n<div id=\"stage\">", CSS + "</style>\n\n<div id=\"stage\">")
    # ---- New account: an email field, checked as the server checks it
    s = rep(s, """<p class="unst" id="acUserSt" aria-live="polite"></p></div>'
    + '<div class="acf"><div class="acpair">""",
               """<p class="unst" id="acUserSt" aria-live="polite"></p></div>'
    + '<div class="acf"><label for="acEmail">Email</label><input id="acEmail" data-k="email" type="email" inputmode="email" maxlength="254" autocomplete="email" autocapitalize="off" autocorrect="off" spellcheck="false" aria-describedby="acEmailSt" value="' + frEsc(f.email || '') + '"><p class="unst" id="acEmailSt" aria-live="polite"></p></div>'
    + '<div class="acf"><div class="acpair">""")
    s = rep(s, "Friends see your username, paint colour and rank. Your name and birth year stay private.",
               "Friends see your username, paint colour and rank. Your email, name and birth year stay private.")
    s = rep(s, "const user = unNorm(v('acUser')), first = clean(v('acFirst')),", "const user = unNorm(v('acUser')), email = v('acEmail').trim(), first = clean(v('acFirst')),")
    s = rep(s, "  const why = { user: !!unWhy(user) || !!($('acUser') && $('acUser').dataset.un === 'bad'), first:",
               "  const why = { user: !!unWhy(user) || !!($('acUser') && $('acUser').dataset.un === 'bad'), email: EMAIL_REQ ? !emOk(email) : !!email && !emOk(email), first:")
    s = rep(s, "  return { ok: !Object.values(why).some(Boolean), why, user, first, last,", "  return { ok: !Object.values(why).some(Boolean), why, user, email, first, last,")
    s = rep(s, "  set('acPassSt', w.pass ? '' : 'ok',",
               "  { const eb = !!AC.f.email && w.email; set('acEmailSt', eb ? 'bad' : '', eb ? 'Check your email address' : ''); $('acEmail').setAttribute('aria-invalid', String(eb)); }\n  set('acPassSt', w.pass ? '' : 'ok',")
    # once the account's made: its email saved, and the welcome email on its way
    s = rep(s, """    acDone('<span>Welcome, <b>' + frEsc(hdOf(me.name)) + '</b>! Your account is ready.</span>'); csSync(); // (v312: this phone's progress, its first copy)""",
               """    let sent = false; // (v355) its email: if that one's taken or wrong, the account's made and the form says so (the button again just saves the email)
    if (f.email) { try { const r2 = await sbRpc('rm_email_set', { p_email: f.email }); EM.st = null;
        if (r2 && r2.ok === false) throw acStop(r2.why === 'taken' ? 'email_taken' : r2.why === 'bad' ? 'email_bad' : 'email', 'email'); sent = !!(r2 && r2.sent); }
      catch (e) { if (!csMissing(e)) throw e; } } // (the v355 SQL not run yet: the account works, and its email comes later)
    acDone('<span>Welcome, <b>' + frEsc(hdOf(me.name)) + '</b>! ' + (sent ? 'Check your email to confirm it.' : 'Your account is ready.') + '</span>'); csSync(); // (v312: this phone's progress, its first copy)""")
    s = rep(s, "    : w === 'first' ? 'Check your first name: letters only.'",
               "    : w === 'email_taken' ? 'Your account is made, but that email is used by another account. Type another one and press the button again.'\n"
               "    : w === 'email_bad' ? 'Your account is made, but check that email and press the button again.' : w === 'email' ? 'Your account is made, but its email couldn’t be saved. Press the button again.'\n"
               "    : w === 'first' ? 'Check your first name: letters only.'")
    # ---- Log in: Forgot password?
    s = rep(s, "    + '<div class=\"acf acw\"><label for=\"acInPass\">Password</label>' + acPw('acInPass', 'inPass', 'current-password') + '</div>'",
               "    + '<div class=\"acf acw\"><label for=\"acInPass\">Password</label>' + acPw('acInPass', 'inPass', 'current-password') + '</div>'\n"
               "    + '<button class=\"aclink acw acforgot\" data-ac=\"forgot\" type=\"button\">Forgot password?</button>'")
    # ---- the sheet's pages: New account, Log in, and (v355) Forgot password and Your email (no tabs on those)
    s = rep(s, """function acRender() {
  const body = $('acBody'); if (!body) return; const nu = AC.tab === 'new', young = nu && acYoung();
  for (const b of $('acModal').querySelectorAll('.actabs button')) b.setAttribute('aria-selected', String(b.dataset.tab === AC.tab));
  $('acTitle').textContent = nu ? 'Make an account' : 'Welcome back';
  body.innerHTML = young ? AC_YOUNG : nu ? acNewHtml() : acInHtml(); body.scrollTop = 0;""",
               """function acRender() {
  const body = $('acBody'); if (!body) return; const t = AC.tab, nu = t === 'new', young = nu && acYoung();
  $('acModal').classList.toggle('side', t === 'forgot' || t === 'email'); $('acModal').classList.toggle('nu', nu && !young); // (v355)
  for (const b of $('acModal').querySelectorAll('.actabs button')) b.setAttribute('aria-selected', String(b.dataset.tab === t));
  $('acTitle').textContent = nu ? 'Make an account' : t === 'forgot' ? 'Forgot your password?' : t === 'email' ? 'Your email' : 'Welcome back';
  body.innerHTML = young ? AC_YOUNG : nu ? acNewHtml() : t === 'forgot' ? acForgotHtml() : t === 'email' ? acEmailHtml() : acInHtml(); body.scrollTop = 0;""")
    s = rep(s, "if (e.target.id === 'acNew') acCreate(); else if (e.target.id === 'acIn') acLogin(); });",
               "if (e.target.id === 'acNew') acCreate(); else if (e.target.id === 'acIn') acLogin(); else if (e.target.id === 'acForgot') acForgot(); else if (e.target.id === 'acEm') acEmailSave(); });")
    s = rep(s, "  if (b.dataset.ac === 'close') return acClose();\n",
               "  if (b.dataset.ac === 'close') return acClose();\n"
               "  if (b.dataset.ac === 'forgot') { AC.tab = 'forgot'; AC.err = ''; AC.sentTo = ''; if (!AC.f.who) AC.f.who = AC.f.inUser || ''; return acRender(); } // (v355)\n"
               "  if (b.dataset.ac === 'back') { AC.tab = 'in'; AC.err = ''; AC.sentTo = ''; return acRender(); }\n"
               "  if (b.dataset.ac === 'resend') return acEmailResend();\n")
    # ---- the menu's Account: Email (and a word while there's no email, or it isn't confirmed)
    s = rep(s, "  else if (acctReady()) { t = (AC.note ? frEsc(AC.note) + ' ' : '') + 'Signed in as <b>' + frEsc(hdOf(nm)) + '</b>'; h = b('out', 'Log out'); }",
               "  else if (acctReady()) { const es = EM.st; t = (AC.note ? frEsc(AC.note) + ' ' : '') + 'Signed in as <b>' + frEsc(hdOf(nm)) + '</b>'\n"
               "      + (es && !es.off && !es.email ? '. Add your email, so you can always get back in.' : es && !es.off && es.email && !es.verified && es.mail ? '. Confirm your email: the link’s in your inbox.' : '');\n"
               "    h = b('email', 'Email') + b('out', 'Log out'); if (!es) emLoad().then(r => { if (r && !$('sideMenu').hidden) acSetPaint(); }).catch(() => {}); } // (v355)")
    s = rep(s, "  if (a === 'new' || a === 'in') { closeSide(); return acctOpen(null, a); }",
               "  if (a === 'new' || a === 'in') { closeSide(); return acctOpen(null, a); }\n  if (a === 'email') { closeSide(); return acEmailOpen(); } // (v355)")
    # ---- the Privacy Policy: the email
    s = rep(s, "If you make an account, we keep your username, your first and last name, your birth year, and when you agreed to these terms. Your name and birth year are private: other players never see them.",
               "If you make an account, we keep your username, your email, your first and last name, your birth year, and when you agreed to these terms. Your email, name and birth year are private: other players never see them.")
    s = rep(s, "We ask for your birth year because online play is for players 13 and older.</p>",
               "We ask for your birth year because online play is for players 13 and older.</p><p>We use your email only for your account: a welcome email that confirms it, a link to reset your password when you ask for one, and a note if your password changes. No newsletters, and we never share it.</p>")
    s = rep(s, "<h3>Who has it</h3><p>We don’t sell your information. Supabase stores it for us, and online matches run on our game server.</p>",
               "<h3>Who has it</h3><p>We don’t sell your information. Supabase stores it for us, Resend sends our account emails, and online matches run on our game server.</p>")
    s = rep(s, "const ACC_TERMS = 'tos-2026-10-15';", "const ACC_TERMS = 'tos-2026-10-18';")
    # ---- an error under the form scrolls into view with the button below it (the sheet's body scrolls on small screens)
    s = rep(s, "  const x = $('acErr'); if (x) x.textContent = AC.err; AU.nope(); acBusy(null); if (x) kick(x, 'unshake');\n}",
               "  const x = $('acErr'); if (x) x.textContent = AC.err; AU.nope(); acBusy(null); if (x) kick(x, 'unshake');\n"
               "  const b = $('acBody'), g = $('acGo'); if (b && g) { const d = g.getBoundingClientRect().bottom - b.getBoundingClientRect().bottom; if (d > 0) b.scrollTop += d + 8; } // (v355)\n}")
    return s
