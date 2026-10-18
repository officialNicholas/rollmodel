// reset.html: the password-reset email links here as reset.html#t=TOKEN. The token is read from the fragment (it never reaches a
// server log) and wiped from the address bar at once. A new password twice, with the game's rules (8 to 72 characters, a letter
// and a number), then rm_reset_password. The token and the password stay in this page's memory only: never the console, never storage.
(() => {
  'use strict';
  const token = RM.takeToken();
  const form = document.getElementById('resetForm'), pw = document.getElementById('pw'), pw2 = document.getElementById('pw2'),
    show = document.getElementById('pwShow'), btn = document.getElementById('resetGo'), box = document.getElementById('resetMsg'),
    err = document.getElementById('pwErr'), done = document.getElementById('resetDone');
  const bytes = v => new TextEncoder().encode(v).length; // (the server's rules: 8 characters or more, at most 72 bytes, a letter A to Z and a digit)
  const rules = { len: v => Array.from(v).length >= 8 && bytes(v) <= 72, letter: v => /[A-Za-z]/.test(v), digit: v => /[0-9]/.test(v), same: (v, w) => v.length > 0 && v === w };
  const FORGOT = { href: 'forgot.html', text: 'Ask for a new link' };
  const WHY = {
    expired: ['This link has expired. Ask for a new one.', FORGOT],
    used: ['This link was already used.', FORGOT],
    bad: ['This link isn’t valid.', FORGOT]
  };
  let busy = false;

  function dead(why, focus) { // the link can't be used: no form, just why, and where to get a new one
    form.hidden = true; const w = WHY[why] || WHY.bad; RM.say(box, 'bad', w[0], w[1], focus);
  }
  if (!token) { document.documentElement.classList.replace('has-token', 'no-token'); return; } // (the page shows its no-link message)

  // the hints under the fields, ticked off as you type
  function check() {
    const v = pw.value, w = pw2.value; let all = true;
    for (const [k, f] of Object.entries(rules)) {
      const li = document.querySelector('[data-rule="' + k + '"]'), ok = f(v, w); if (!ok) all = false;
      li.classList.toggle('met', ok); li.querySelector('.vh').textContent = ok ? 'Done: ' : 'Still needed: ';
    }
    return all;
  }
  for (const el of [pw, pw2]) el.addEventListener('input', () => { check(); err.hidden = true; el.removeAttribute('aria-invalid'); });
  check();

  // show or hide both passwords
  show.addEventListener('click', () => {
    const on = show.getAttribute('aria-pressed') !== 'true';
    show.setAttribute('aria-pressed', String(on)); show.textContent = on ? 'Hide' : 'Show';
    pw.type = pw2.type = on ? 'text' : 'password';
  });

  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (busy) return;
    if (!check()) {
      const v = pw.value, firstOk = rules.len(v) && rules.letter(v) && rules.digit(v), bad = firstOk ? pw2 : pw;
      err.textContent = !rules.len(v) ? (bytes(v) > 72 ? 'That’s too long: 72 characters at most.' : 'Your password needs 8 characters or more.')
        : !rules.letter(v) ? 'Add at least one letter, A to Z.' : !rules.digit(v) ? 'Add at least one number.' : 'The two passwords don’t match yet.';
      err.hidden = false; bad.setAttribute('aria-invalid', 'true'); bad.focus(); return;
    }
    busy = true; btn.setAttribute('aria-disabled', 'true'); const label = btn.textContent; btn.textContent = 'Saving…'; RM.hush(box);
    let ans = null; try { ans = await RM.call('rm_reset_password', { p_token: token, p_password: pw.value }); } catch (x) { ans = null; }
    busy = false; btn.removeAttribute('aria-disabled'); btn.textContent = label;
    if (ans && ans.ok === true && typeof ans.username === 'string' && ans.username) {
      pw.value = pw2.value = ''; form.hidden = true;
      done.hidden = false; done.querySelector('[data-name]').textContent = ans.username; done.tabIndex = -1; done.focus();
      return;
    }
    const why = ans && ans.ok === false ? ans.why : null;
    if (why === 'weak') { RM.say(box, 'bad', 'That password is too easy to guess. Pick a harder one.'); pw.setAttribute('aria-invalid', 'true'); pw.focus(); return; }
    if (why === 'expired' || why === 'used' || why === 'bad') { pw.value = pw2.value = ''; dead(why, true); return; }
    RM.say(box, 'bad', RM.OOPS); // (an HTTP error, no network, or an answer we don't know: the form stays, to try again)
  });
})();
