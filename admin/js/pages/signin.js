// Signing in: email and password, then the authenticator app (set it up the first time, a code after that),
// then adm_whoami. Nothing of the dashboard shows until it says admin: true.

import { h, mount, brand, button, field, errorLine, copyButton, icon, loading } from '../ui.js';
import * as auth from '../auth.js';
import { rpc } from '../api.js';

export const NOT_ADMIN = "This account isn't an admin.";
export const STALE = 'Your sign-in is over 12 hours old. Sign in again.';

// The page frame shared by every step.
function frame(root, title, lede, message, ...body) {
  const h1 = h('h1', { class: 'signin-title', tabindex: '-1' }, title);
  mount(root, h('main', { class: 'signin', id: 'main' },
    h('div', { class: 'signin-card' },
      brand('Admin'),
      h1,
      lede ? h('p', { class: 'signin-lede' }, lede) : null,
      message ? h('div', { class: 'banner ' + (message.tone || 'info'), role: 'alert' }, icon(message.tone === 'error' ? 'alert' : 'info'), h('span', null, message.text)) : null,
      body),
    h('p', { class: 'signin-foot' }, 'Sessions end after 12 hours, or after 15 minutes without input.')));
  return h1;
}

// Step 1: email and password.
export function showSignIn(root, opts) {
  const message = opts.message ? { text: opts.message, tone: opts.tone || 'error' } : null;
  const email = h('input', { type: 'email', name: 'email', autocomplete: 'username', required: true, spellcheck: 'false', autocapitalize: 'off' });
  const password = h('input', { type: 'password', name: 'password', autocomplete: 'current-password', required: true });
  const err = errorLine();
  const submit = button('Sign in', { kind: 'primary wide', type: 'submit' });
  const form = h('form', { class: 'form', novalidate: true, onsubmit: async (e) => {
    e.preventDefault();
    err.clear();
    if (!email.value.trim() || !password.value) return err.show('Enter your email and password.');
    submit.disabled = true;
    try {
      await auth.signIn(email.value.trim(), password.value);
      password.value = '';
      await decide(root, opts);
    } catch (e2) {
      submit.disabled = false;
      err.show(e2.message || 'Sign-in failed. Try again.');
      password.select();
    }
  } }, field('Email', email), field('Password', password), err.el, submit);
  frame(root, 'Sign in', "Roll Model's admin dashboard. You'll need your password and your authenticator app.", message, form);
  email.focus();
}

// adm_whoami decides what's next.
export async function decide(root, opts, tries = 0) {
  frame(root, 'Signing in', null, null, loading('Checking your account'));
  let who;
  try {
    who = await rpc('adm_whoami');
  } catch (e) {
    return retryStep(root, opts, e.message || "Couldn't check your account.", () => decide(root, opts));
  }
  if (who && who.admin === true) return opts.onAdmin(who);
  const why = who && who.why;
  if (why === 'needs_code' && tries < 1 && auth.aal() !== 'aal2') return factorStep(root, opts);
  await auth.signOut();
  if (why === 'stale') return showSignIn(root, { ...opts, message: STALE });
  if (why === 'needs_code') return showSignIn(root, { ...opts, message: "The authenticator code didn't stick. Sign in again." });
  return showSignIn(root, { ...opts, message: NOT_ADMIN });
}

function retryStep(root, opts, text, again) {
  frame(root, "Couldn't sign in", null, { text, tone: 'error' },
    h('div', { class: 'row' }, button('Try again', { kind: 'primary', ico: 'reload', onclick: again }), cancelButton(root, opts)));
}

function cancelButton(root, opts) {
  return button('Use a different account', { kind: 'ghost', onclick: async () => { await auth.signOut(); showSignIn(root, { ...opts, message: null }); } });
}

// Step 2: does the account have an authenticator yet?
async function factorStep(root, opts) {
  frame(root, 'Signing in', null, null, loading('Checking your authenticator'));
  let list;
  try {
    list = await auth.factors();
  } catch (e) {
    return retryStep(root, opts, e.message, () => factorStep(root, opts));
  }
  const ok = list.find((f) => f.status === 'verified');
  return ok ? codeStep(root, opts, ok.id) : enrolStep(root, opts);
}

// A 6-digit code field and what to do with it.
function codeForm(root, opts, factorId, label) {
  const code = h('input', { type: 'text', name: 'code', inputmode: 'numeric', autocomplete: 'one-time-code', maxlength: '7', pattern: '[0-9 ]*', required: true, spellcheck: 'false', class: 'code-input' });
  const err = errorLine();
  const submit = button('Verify', { kind: 'primary wide', type: 'submit' });
  return h('form', { class: 'form', novalidate: true, onsubmit: async (e) => {
    e.preventDefault();
    err.clear();
    const digits = code.value.replace(/\s+/g, '');
    if (!/^\d{6}$/.test(digits)) return err.show('Enter the 6 digits your app shows.');
    submit.disabled = true;
    try {
      await auth.verify(factorId, digits);
      await decide(root, opts, 1);
    } catch (e2) {
      submit.disabled = false;
      if (e2.code === 'mfa_factor_not_found' || e2.code === 'session_not_found' || e2.status === 401) {
        await auth.signOut();
        return showSignIn(root, { ...opts, message: e2.message });
      }
      err.show(e2.message || "That code didn't work. Try again.");
      code.select();
    }
  } }, field(label, code, 'It changes every 30 seconds.'), err.el, submit, cancelButton(root, opts));
}

// Step 3a: no verified authenticator yet: set one up.
async function enrolStep(root, opts) {
  frame(root, 'Signing in', null, null, loading('Setting up your authenticator'));
  let f;
  try {
    f = await auth.enroll();
  } catch (e) {
    return retryStep(root, opts, e.message, () => enrolStep(root, opts));
  }
  const secret = h('code', { class: 'secret' }, f.secret.replace(/(.{4})(?=.)/g, '$1 '));
  const h1 = frame(root, 'Set up your authenticator', 'This account needs a second step: a code from an authenticator app (like 1Password, Google Authenticator or Authy).', null,
    h('ol', { class: 'steps' },
      h('li', null, h('p', null, 'Scan this QR code with the app.'),
        f.qr ? h('img', { class: 'qr', src: f.qr, alt: 'QR code to add Roll Model admin to your authenticator app', width: '184', height: '184' }) : h('p', { class: 'hint' }, "The QR code didn't come through: use the key below.")),
      h('li', null, h('p', null, "Or, if you can't scan, add this key by hand:"),
        h('div', { class: 'secret-row' }, secret, copyButton(() => f.secret, 'Copy key'))),
      h('li', null, codeForm(root, opts, f.id, 'Then enter the 6-digit code it shows'))));
  h1.focus();
}

// Step 3b: an authenticator is set up: ask for a code.
function codeStep(root, opts, factorId) {
  const h1 = frame(root, 'Enter your code', 'Open your authenticator app and enter the code for Roll Model admin.', null,
    codeForm(root, opts, factorId, '6-digit code'));
  h1.focus();
  const input = root.querySelector('.code-input');
  if (input) input.focus();
}
