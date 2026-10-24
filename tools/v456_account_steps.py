"""v456: the account sheet in steps, so it's never a wall of boxes.

- The user: "This is too much, so let's break this into steps. First we get "new account" and login. Then if new account, we get
  username, password, birth year. Then first name and email and I agree to terms".
- Opened from anything that hasn't already picked (Play online, parties, friends), the sheet first shows just the two big choices,
  New account and Log in. A button that already said which (Settings' Log in, the friends page's own buttons) still goes straight there.
- New account, step 1: Username, Password, Birth year, then Next (on once those three are good). Under 13 stops here, kindly, as before.
- Step 2: First name, Email, I agree to the Terms and Privacy Policy, then Make my account. Back returns to step 1 with everything kept
  (it's the same form, only half of it shown), and step 1's Back returns to the choice. A username, password or birth year the server
  turns down sends you back to step 1 with its message. Log in gets a Back to the choice too (not on the start-up "Already playing?" sheet).
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """
/* (v456) the account sheet in steps: the choice, then username/password/year, then name/email/terms */
#acModal:not(.pick) .actabs{display:none}
#acModal.pick .actabs{grid-template-columns:minmax(0,1fr);gap:14px;margin:8px 0 4px -10px}
#acModal.pick .actabs button{min-height:64px;font-size:22px;filter:none;scale:1}
#acModal.pick .acbody{min-height:0}
#acModal .acpk{margin:6px 0 0;text-align:center}
#acNew:not(.st2) .ac2,#acNew.st2 .ac1{display:none!important}
#acNew .acback{justify-self:center}
"""

def apply(s):
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    s = rep(s, "const AC = { open: false, tab: 'new',", "const AC = { open: false, tab: 'new', step: 1,")
    # the new-account form: step 1 (username, password, year) and step 2 (first name, email, terms) as halves of one form
    s = rep(s, "'<form class=\"acform\" id=\"acNew\" novalidate autocomplete=\"on\">'",
               "'<form class=\"acform' + (AC.step === 2 ? ' st2' : '') + '\" id=\"acNew\" novalidate autocomplete=\"on\">'")
    a_user = "'<div class=\"acf\"><label for=\"acUser\">Username</label>"
    a_email = "    + '<div class=\"acf\"><label for=\"acEmail\">Email</label>"
    a_first = "    + '<div class=\"acf\">' + tx('acFirst', 'first', 'First name', 'given-name', 'words') + '<p class=\"unst\" id=\"acNameSt\" aria-live=\"polite\"></p></div>'\n"
    a_year = "    + '<fieldset class=\"acf\"><legend>Birth year</legend>"
    a_pass = "    + '<div class=\"acf\"><label for=\"acPass\">Password</label>' + acPw('acPass', 'pass', 'new-password') + '<p class=\"unst\" id=\"acPassSt\" aria-live=\"polite\"></p></div>'\n"
    s = rep(s, a_first, ""); s = rep(s, a_pass, "")
    s = rep(s, a_user, "'<div class=\"acf ac1\"><label for=\"acUser\">Username</label>")
    s = rep(s, a_year, a_pass.replace('class=\\"acf\\"', 'class=\\"acf ac1\\"').replace('"acf"', '"acf ac1"') + "    + '<fieldset class=\"acf ac1\"><legend>Birth year</legend>")
    s = rep(s, a_email, a_first.replace('"acf"', '"acf ac2"') + "    + '<div class=\"acf ac2\"><label for=\"acEmail\">Email</label>")
    s = rep(s, "'<div class=\"acagree acw\"><input type=\"checkbox\" id=\"acAgree\"", "'<div class=\"acagree acw ac2\"><input type=\"checkbox\" id=\"acAgree\"")
    s = rep(s, "id=\"acGo\" type=\"submit\" disabled>Make my account</button>'",
               "id=\"acGo\" type=\"submit\" disabled>' + (AC.step === 2 ? 'Make my account' : 'Next') + '</button>'")
    s = rep(s, "'<p class=\"frfine acw\">Friends see your username, paint colour and rank. Your email, name and birth year stay private.</p></form>';",
               "'<p class=\"frfine acw ac2\">Friends see your username, paint colour and rank. Your email, name and birth year stay private.</p>'\n"
               "    + '<button class=\"aclink acw acback\" data-ac=\"nback\" type=\"button\">Back</button></form>';")
    # Log in: a Back to the choice (not on the start-up sheet, which has no choice)
    s = rep(s, "+ csInNote() + '</form>';", "+ csInNote() + (baSheet() ? '' : '<button class=\"aclink acw acback\" data-ac=\"pick\" type=\"button\">Back</button>') + '</form>';")
    # the choice
    s = rep(s, "function acRender() {",
            "const acPickHtml = () => '<p class=\"frfine acpk\">One account for friends and online play. Your progress is saved with it.</p>';\n"
            "const acStepOk = w => !(w.user || w.bday || w.pass); // (step 1's three)\n"
            "function acStep(n, keep) { AC.step = n; const f = $('acNew'), g = $('acGo'); if (!f) return; f.classList.toggle('st2', n === 2); if (!keep) { AC.err = ''; const x = $('acErr'); if (x) x.textContent = ''; }\n"
            "  if (g) { delete g.dataset.t; g.textContent = n === 2 ? 'Make my account' : 'Next'; } $('acBody').scrollTop = 0; acValid();\n"
            "  setTimeout(() => { const i = !touchy() && $(n === 2 ? 'acFirst' : 'acUser'); if (i) i.focus({ preventScroll: true }); }, 40); }\n"
            "function acNext() { const f = acForm(); if (!acStepOk(f.why)) { AU.nope(); return acValid(); }\n"
            "  if (f.young) { store.acYoung = Date.now(); save(); adHello(false); AU.nope(); return acRender(); } acStep(2); } // (under 13: the kind word, before anything else is asked)\n"
            "function acRender() {")
    s = rep(s, "$('acModal').classList.toggle('nu', nu && !young);", "$('acModal').classList.toggle('nu', nu && !young); $('acModal').classList.toggle('pick', t === 'pick');")
    s = rep(s, "$('acTitle').textContent = nu ? 'Make an account' :", "$('acTitle').textContent = t === 'pick' ? 'Your account' : nu ? 'Make an account' :")
    s = rep(s, "body.innerHTML = young ? AC_YOUNG : nu ? acNewHtml() :", "body.innerHTML = t === 'pick' ? acPickHtml() : young ? AC_YOUNG : nu ? acNewHtml() :")
    s = rep(s, "const g = $('acGo'); if (g && !AC.busy) g.disabled = !f.ok || NET_WALLED;",
               "const g = $('acGo'); if (g && !AC.busy) g.disabled = !(AC.step === 2 ? f.ok : acStepOk(w)) || NET_WALLED;")
    # a step-1 answer the server turns down: back to step 1, with its message
    s = rep(s, "  const x = $('acErr'); if (x) x.textContent = AC.err; AU.nope(); acBusy(null); if (x) kick(x, 'unshake');",
               "  if (AC.tab === 'new' && AC.step === 2 && ((e && e.at === 'user') || w === 'birthday' || (e && e.code === 'weak_password'))) acStep(1, true); // (v456)\n"
               "  const x = $('acErr'); if (x) x.textContent = AC.err; AU.nope(); acBusy(null); if (x) kick(x, 'unshake');")
    s = rep(s, "if (e.target.id === 'acNew') acCreate();", "if (e.target.id === 'acNew') { if (AC.step === 2) acCreate(); else acNext(); }")
    s = rep(s, "  if (b.dataset.ac === 'resend') return acEmailResend();",
               "  if (b.dataset.ac === 'nback') { if (AC.step === 2) return acStep(1); AC.tab = 'pick'; AC.err = ''; return acRender(); } // (v456)\n"
               "  if (b.dataset.ac === 'pick') { AC.tab = 'pick'; AC.err = ''; return acRender(); }\n"
               "  if (b.dataset.ac === 'resend') return acEmailResend();")
    s = rep(s, "if (f.id !== 'acNew' || acForm().ok) return; e.preventDefault(); const els = [...f.querySelectorAll('input:not([type=checkbox]),select')],",
               "if (f.id !== 'acNew' || (AC.step === 2 ? acForm().ok : acStepOk(acForm().why))) return; e.preventDefault(); const els = [...f.querySelectorAll('input:not([type=checkbox]),select')].filter(x => x.offsetParent),")
    s = rep(s, "AU.init(); AU.ui(); AC.tab = b.dataset.tab; AC.err = ''; acRender(); });", "AU.init(); AU.ui(); AC.tab = b.dataset.tab; AC.step = 1; AC.err = ''; acRender(); });")
    s = rep(s, "AC.tab = tab === 'in' ? 'in' : 'new'; AC.err = '';", "AC.tab = tab === 'in' || tab === 'new' ? tab : 'pick'; AC.step = 1; AC.err = '';")
    s = rep(s, "AC.busy = false; AC.tab = 'new'; AC.f.user = me.name;", "AC.busy = false; AC.tab = 'new'; AC.step = 1; AC.f.user = me.name;")
    return s
