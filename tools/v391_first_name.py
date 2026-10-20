"""v391: making an account asks for a first name only (the user: no last name at sign-up or account creation).

- The account form's name row is one field, First name, across the form's width (it was First name and Last name side by side).
- Nothing about a last name is checked or sent; the account keeps none, and the privacy policy says so. (The database takes an account without one from v391's
  supabase/migrations/20261020010000_first_name.sql, which has to be run before this version of the game is out.)"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the form: First name alone
    s = rep(s, "'<div class=\"acf\"><div class=\"acpair\">' + tx('acFirst', 'first', 'First name', 'given-name', 'words') + tx('acLast', 'last', 'Last name', 'family-name', 'words') + '</div><p class=\"unst\" id=\"acNameSt\" aria-live=\"polite\"></p></div>'",
               "'<div class=\"acf\">' + tx('acFirst', 'first', 'First name', 'given-name', 'words') + '<p class=\"unst\" id=\"acNameSt\" aria-live=\"polite\"></p></div>'")
    # its checks: no last name to read, check or mark
    s = rep(s, "first = clean(v('acFirst')), last = clean(v('acLast')), y = +v('acY')", "first = clean(v('acFirst')), last = '', y = +v('acY')")
    s = rep(s, "first: !nameOk(first), last: !nameOk(last),", "first: !nameOk(first), last: false,")
    s = rep(s, "const nb = !!(AC.f.first && w.first) || !!(AC.f.last && w.last), all = !!AC.f.y;", "const nb = !!(AC.f.first && w.first), all = !!AC.f.y;")
    s = rep(s, " $('acLast').setAttribute('aria-invalid', String(!!(AC.f.last && w.last)));", "")
    # the privacy policy says so
    s = rep(s, "priv: ['Privacy Policy', '<p>Updated October 18, 2026.</p>", "priv: ['Privacy Policy', '<p>Updated October 20, 2026.</p>")
    s = rep(s, "we keep your username, your email, your first and last name, your birth year,", "we keep your username, your email, your first name, your birth year,")
    s = rep(s, "An account (username and password, first and last name, birthday,", "An account (username and password, first name, birthday,")
    return s
