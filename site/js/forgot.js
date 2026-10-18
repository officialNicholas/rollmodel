// forgot.html: one field, a username or an email; the game's database sends a reset link if the account has a confirmed email.
// The answer is always the same, so the page never says whether an account exists. One try every 30 seconds.
(() => {
  'use strict';
  const form = document.getElementById('forgotForm'), who = document.getElementById('who'), btn = document.getElementById('forgotGo'),
    hint = document.getElementById('whoHint'), box = document.getElementById('forgotMsg');
  const SENT = 'If that account has a confirmed email, we’ve sent a link to it. Check your inbox (and spam).';
  const WAIT = 30, LABEL = btn.textContent;
  let busy = false, until = 0, timer = 0;

  // a username (3 to 16 letters, numbers or underscores, with a letter; spaces count as underscores, as in the game) or an email
  function read() {
    const v = who.value.trim();
    if (!v) return { why: 'Type your username or the email on your account.' };
    if (v.includes('@')) return v.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? { v } : { why: 'That email doesn’t look right. Check it and try again.' };
    const n = v.replace(/\s+/g, '_');
    return /^[A-Za-z0-9_]{3,16}$/.test(n) && /[A-Za-z]/.test(n) ? { v: n } : { why: 'That isn’t a username: they’re 3 to 16 letters, numbers or underscores.' };
  }
  function wrong(text) {
    hint.textContent = text; hint.hidden = false; who.setAttribute('aria-invalid', 'true'); who.focus();
  }
  who.addEventListener('input', () => { if (!hint.hidden) { hint.hidden = true; who.removeAttribute('aria-invalid'); } });

  function tick() {
    const left = Math.ceil((until - Date.now()) / 1000);
    if (left > 0) { btn.textContent = 'Try again in ' + left + ' s'; return; }
    clearInterval(timer); timer = 0; btn.textContent = LABEL; btn.removeAttribute('aria-disabled');
  }
  function cool() { until = Date.now() + WAIT * 1000; btn.setAttribute('aria-disabled', 'true'); clearInterval(timer); timer = setInterval(tick, 1000); tick(); }

  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (busy || Date.now() < until) return;
    const r = read(); if (r.why) return wrong(r.why);
    busy = true; btn.setAttribute('aria-disabled', 'true'); btn.textContent = 'Sending…'; RM.hush(box);
    let ans = null; try { ans = await RM.call('rm_reset_request', { p_who: r.v }); } catch (err) { ans = null; }
    busy = false;
    if (ans && ans.ok === true) RM.say(box, 'ok', SENT); else RM.say(box, 'bad', RM.OOPS);
    cool();
  });
})();
