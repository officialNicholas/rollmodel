// Support: find a player (adm_find), look at them (adm_player), and help: reset their password, sign them out
// everywhere, or delete their account. Every answer the server can give is a plain sentence (api.js WHY).

import { h, card, table, empty, button, field, dialog, actionsRow, errorLine, toast, copyButton, chip, facts, icon, grid } from '../ui.js';
import { num, dateTime, ago, friendCode, UUID, plural } from '../format.js';
import { rpc, whyText } from '../api.js';
import { stepName } from '../catalog.js';
import { generatePassword, passwordProblem, LENGTH } from '../password.js';
import { actionText, detailText } from './audit.js';

export default {
  id: 'support', title: 'Support', icon: 'support', range: false,
  sub: 'Find a player and help them: a reset link, a new password, signing them out, or deleting their account.',
  async load(ctx) {
    const id = ctx.route.arg;
    if (id) {
      if (!UUID.test(id)) return { bad: true };
      const [player, email] = await Promise.all([rpc('adm_player', { p_id: id }), emailOf(id)]);
      return { id, player, email };
    }
    const q = (ctx.route.q.get('q') || '').trim();
    if (isEmail(q)) {
      try { return { q, email: true, results: await rpc('adm_find_email', { p_q: q }) }; } catch (e) { if (notSetUp(e)) return { q, email: true, off: true, results: [] }; throw e; }
    }
    if (q.length >= 2 && q.length <= 40) return { q, results: await rpc('adm_find', { p_q: q }) };
    return { q };
  },
  view: (d, ctx) => (d.id || d.bad ? playerView(d, ctx) : searchView(d, ctx)),
};

const STATUS = { lobby: 'Online, in the menus', match: 'Online, in a match', offline: 'Offline' };
const isEmail = (q) => q.includes('@');
const EMAIL_MAX = 254;
// The account emails arrived after the rest (supabase/migrations/20261019000000_email.sql): until that's run, PostgREST
// doesn't know the functions (404, PGRST202) and the page works without them.
const notSetUp = (e) => e && e.kind === 'server' && (e.status === 404 || e.code === 'PGRST202');
// a player's email: { email, verified, verified_at, updated_at }, null for none, or { off: true } before the email SQL is run
async function emailOf(id) {
  try { return await rpc('adm_player_email', { p_id: id }); } catch (e) { if (notSetUp(e)) return { off: true }; throw e; }
}
const displayName = (p) => p.name || 'No username';
const possessive = (p) => (p.name ? p.name + "'s" : "this player's");

// ---------------------------------------------------------------- search

let lastSearch = ''; // so a player's page can go back to the results

function searchView(d, ctx) {
  lastSearch = d.results ? d.q : '';
  const input = h('input', { type: 'search', name: 'q', value: d.q || '', autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off', maxlength: String(EMAIL_MAX) });
  const err = errorLine();
  const form = h('form', { class: 'search', role: 'search', novalidate: true, onsubmit: (e) => {
    e.preventDefault();
    const q = input.value.trim();
    if (q.length < 2) return err.show('Type at least 2 characters.');
    if (isEmail(q) ? q.length > EMAIL_MAX : q.length > 40) return err.show('That\'s too long: ' + (isEmail(q) ? EMAIL_MAX : 40) + ' characters at most.');
    ctx.go('#support?q=' + encodeURIComponent(q));
  } },
  h('div', { class: 'search-row' }, field('Find a player', input),
    button('Search', { kind: 'primary', type: 'submit', ico: 'support' })),
  h('p', { class: 'hint', id: 'q-hint' }, 'The start of their username, their friend code (like ABCD 2345), their whole email address, or their user id.'),
  err.el);
  input.setAttribute('aria-describedby', 'q-hint');

  let results = null;
  if (d.results) {
    const list = Array.isArray(d.results) ? d.results : [];
    results = card('Results', { sub: list.length ? plural(list.length, 'player') + ' for "' + d.q + '"' + (list.length >= 25 ? ': the best 25' : '') : null },
      list.length ? table([
        { key: 'name', label: 'Username', cell: (r) => (UUID.test(r.id || '')
          ? h('a', { href: '#support/' + r.id, class: r.name ? '' : 'muted' }, displayName(r))
          : displayName(r)) },
        { key: 'code', label: 'Friend code', cell: (r) => h('span', { class: 'mono' }, friendCode(r.code)) },
        { key: 'rank', label: 'Rank', num: true, cell: (r) => (r.rank == null ? 'n/a' : num(r.rank)) },
        { key: 'account', label: 'Account', cell: (r) => (r.account ? 'Account' : chip('No account', 'muted')) },
        { key: 'created', label: 'Joined', cell: (r) => h('span', { title: dateTime(r.created_at) }, ago(r.created_at)) },
        { key: 'seen', label: 'Last seen', cell: (r) => h('span', { title: dateTime(r.last_seen) }, ago(r.last_seen)) },
      ], list, { caption: 'Players found' })
        : d.off ? empty("Email search isn't set up yet", 'Run the email migration first (admin/README.md, Email).', 'support')
        : empty('No players match "' + d.q + '"', d.email ? 'Emails have to match exactly (any capitals).' : 'Usernames match from the start. Friend codes and user ids have to be exact.', 'support'));
  } else if (d.q) {
    results = card(null, null, empty('Type at least 2 characters', 'Then search again.', 'support'));
  }

  setTimeout(() => { if (!d.q) input.focus(); }, 0);
  return [card(null, { cls: 'search-card' }, form), results];
}

// ---------------------------------------------------------------- one player

function playerView(d, ctx) {
  const back = h('a', { class: 'back', href: lastSearch ? '#support?q=' + encodeURIComponent(lastSearch) : '#support' }, icon('back'), lastSearch ? 'Back to results' : 'Back to search');
  if (d.bad) return [back, card(null, null, empty("That isn't a player id", 'Search for the player instead.', 'support'))];
  const p = d.player;
  if (!p) return [back, card(null, null, empty('No such player', 'They may have deleted their account, or the id is wrong.', 'support'))];

  const online = p.status === 'lobby' || p.status === 'match';
  const noAccount = !p.account || p.anonymous;
  const locked = p.admin === true;
  const reason = locked ? "This is an admin account: it can't be changed from the dashboard."
    : noAccount ? 'No password to reset: this player plays without an account.'
    : d.email && !d.email.off && !(d.email.verified === true) ? (d.email.email ? "Their email isn't confirmed yet, so a reset link can't go to it. Reset their password instead." : 'No email on this account, so a reset link has nowhere to go. Reset their password instead.')
    : null;

  const em = d.email && !d.email.off ? d.email : null;
  const canLink = !locked && !noAccount && !!em && em.verified === true;
  const actions = h('div', { class: 'player-actions' },
    d.email && d.email.off ? null : button('Send reset link', { kind: 'secondary', ico: 'mail', disabled: !canLink, onclick: () => linkDialog(p, em, ctx) }),
    button('Reset password', { kind: 'secondary', ico: 'key', disabled: locked || noAccount, onclick: () => resetDialog(p, ctx) }),
    button('Sign out everywhere', { kind: 'secondary', ico: 'out', disabled: locked, onclick: () => signoutDialog(p, ctx) }),
    button('Delete account', { kind: 'danger-outline', ico: 'trash', disabled: locked, onclick: () => deleteDialog(p, ctx) }));

  const header = card(null, { cls: 'player-head' },
    h('div', { class: 'player-id' },
      h('div', { class: 'avatar', 'aria-hidden': 'true' }, (p.name || '?').slice(0, 1).toUpperCase()),
      h('div', null,
        h('h2', { class: 'player-name' + (p.name ? '' : ' muted') }, displayName(p)),
        h('div', { class: 'player-chips' },
          chip(STATUS[p.status] || 'Offline', online ? 'live' : 'muted'),
          chip(noAccount ? 'No account' : 'Account'),
          locked ? chip('Admin', 'alert') : null,
          p.code ? h('span', { class: 'mono player-code', title: 'Friend code' }, friendCode(p.code)) : null))),
    actions,
    reason ? h('p', { class: 'hint' }, reason) : null);

  const det = p.details;
  const account = card('Account details', { sub: 'What the player typed when making their account' },
    det ? [
      h('p', { class: 'check' }, icon('info'), "Before resetting a password, ask the player for these to check it's really them."),
      facts([
        ...emailRow(d.email),
        ['First name', det.first_name || 'n/a'],
        ['Last name', det.last_name || 'n/a'],
        ['Birth year', det.birth_year == null ? 'n/a' : String(det.birth_year)],
        ['Terms agreed', (det.terms ? 'Version ' + det.terms : 'n/a') + (det.agreed_at ? ', ' + dateTime(det.agreed_at) : '')],
      ]),
    ] : empty('No account details', noAccount ? 'This player plays without an account, so there are none.' : 'They didn\'t leave any.'));

  const profile = card('Profile', null, facts([
    ['Rank', p.rank == null ? 'n/a' : num(p.rank)],
    ['Joined', dateTime(p.created_at)],
    ['Last signed in', p.last_sign_in_at ? dateTime(p.last_sign_in_at) : 'Never'],
    ['Last seen', p.last_seen ? ago(p.last_seen) + ' (' + dateTime(p.last_seen) + ')' : 'Never'],
    ['Friends', num(p.friends)],
    ['Blocked by', plural(p.blocked_by_them || 0, 'player')],
    ['User id', h('span', { class: 'mono wrap' }, p.id)],
  ]));

  const sv = p.save;
  const save = card('Saved progress', { sub: 'The copy kept with their account' },
    sv ? facts([
      ['Rank', num(sv.rank)],
      ['XP', num(sv.xp)],
      ['Dabs', num(sv.drops)],
      ['Items owned', num(sv.items)],
      ['Saved', sv.at ? dateTime(sv.at) + ' (' + ago(sv.at) + ')' : 'n/a'],
    ]) : empty('No saved copy', 'Progress is only kept for players with an account.'));

  const installs = card('Installs', { sub: 'Each copy of the game they played on' },
    table([
      { key: 'platform', label: 'Platform', cell: (i) => (i.platform === 'ios' ? 'iPhone app' : i.platform === 'web' ? 'Web' : String(i.platform || 'n/a')) },
      { key: 'app', label: 'App', cell: (i) => (i.app_ver ? String(i.app_ver) : 'n/a') },
      { key: 'game', label: 'Game', num: true, cell: (i) => (i.game_ver == null ? 'n/a' : 'v' + i.game_ver) },
      { key: 'first', label: 'First seen', cell: (i) => h('span', { title: dateTime(i.first_at) }, ago(i.first_at)) },
      { key: 'last', label: 'Last seen', cell: (i) => h('span', { title: dateTime(i.last_at) }, ago(i.last_at)) },
      { key: 'sessions', label: 'Sessions', num: true, cell: (i) => num(i.sessions) },
      { key: 'matches', label: 'Matches', num: true, cell: (i) => num(i.matches) },
      { key: 'tut', label: 'Tutorial', cell: (i) => (i.tut ? stepName(i.tut) : 'Not started') },
    ], p.installs || [], { caption: 'Installs', empty: 'No installs linked to this player.' }));

  const trail = card('Audit trail', { sub: 'Changes made to this player from the dashboard' },
    (p.audit || []).length ? table([
      { key: 'at', label: 'When', cell: (r) => h('span', { title: dateTime(r.at) }, ago(r.at)) },
      { key: 'admin', label: 'Who', cell: (r) => r.admin || 'n/a' },
      { key: 'action', label: 'What', cell: (r) => actionText(r.action) },
      { key: 'detail', label: 'Details', cls: 'wrapcell', cell: (r) => detailText({ ...r, target: r.target || p.id }) },
    ], p.audit, { caption: 'Audit trail' }) : empty('Nothing yet', 'Password resets, sign-outs and other changes to this player show up here.', 'audit'));

  return [back, header, grid('two', account, profile), save, installs, trail];
}

// the Email row of Account details: nothing before the email SQL is run
function emailRow(e) {
  if (e && e.off) return [];
  if (!e || !e.email) return [['Email', h('span', { class: 'muted' }, 'None')]];
  return [['Email', h('span', { class: 'email-cell' }, h('span', { class: 'wrap' }, e.email), ' ',
    e.verified ? chip('Confirmed', 'live') : chip('Not confirmed', 'muted'))]];
}

// ---------------------------------------------------------------- the actions

// Run an action and turn every answer into a sentence. Returns the result, or null when it showed an error.
async function act(name, args, err, btn) {
  err.clear();
  btn.disabled = true;
  try {
    const res = await rpc(name, args);
    if (res && res.ok === true) return res;
    err.show(whyText(res && res.why));
  } catch (e) {
    if (e.kind === 'denied' || e.kind === 'auth') return null;
    err.show(e.kind === 'net' ? "Can't reach the server. Nothing changed; try again." : e.message);
  }
  btn.disabled = false;
  return null;
}

function resetDialog(p, ctx) {
  let mode = 'make';
  let typed = '';
  let changed = false;
  const who = p.name || 'this player';

  const choose = (api) => {
    const err = errorLine();
    const input = h('input', { type: 'text', autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off', value: typed, class: 'mono' });
    const problem = h('p', { class: 'hint', id: 'pw-problem', 'aria-live': 'polite' });
    const typedBox = h('div', { class: 'form', hidden: mode !== 'type' }, field('Password to set', input), problem);
    const check = () => { typed = input.value; problem.textContent = typed ? passwordProblem(typed) || 'Looks good.' : '8 to 72 characters, with a letter and a digit.'; };
    input.addEventListener('input', () => { err.clear(); check(); });
    check();
    const radio = (value, label, sub) => h('label', { class: 'radio' },
      h('input', { type: 'radio', name: 'pwmode', value, checked: mode === value, onchange: () => { mode = value; typedBox.hidden = mode !== 'type'; if (mode === 'type') input.focus(); err.clear(); } }),
      h('span', null, h('b', null, label), h('small', null, sub)));
    return h('form', { class: 'form', novalidate: true, onsubmit: (e) => {
      e.preventDefault();
      if (mode === 'type') { const bad = passwordProblem(typed); if (bad) { err.show(bad); input.focus(); return; } }
      api.step(confirm);
    } },
    h('p', { class: 'check' }, icon('info'), "Check it's really them first: ask for their first and last name and birth year (under Account details)."),
    h('fieldset', { class: 'radios' }, h('legend', null, 'New password'),
      radio('make', 'Make a strong one for me', LENGTH + ' letters and digits, with no look-alikes like 0 and O'),
      radio('type', 'Type one', 'For example one the player asked for')),
    typedBox,
    err.el,
    actionsRow(button('Cancel', { kind: 'ghost', onclick: () => api.close() }), button('Next', { kind: 'primary', type: 'submit' })));
  };

  const confirm = (api) => {
    const err = errorLine();
    const go = button('Set password', { kind: 'primary', ico: 'key', onclick: async () => {
      const pw = mode === 'make' ? generatePassword() : typed;
      const res = await act('adm_set_password', { p_id: p.id, p_password: pw }, err, go);
      if (!res) return;
      changed = true;
      typed = '';
      api.step(() => done(api, pw));
    } });
    return [
      h('p', null, 'Set a new password for ', h('b', null, who), '?'),
      h('p', { class: 'hint' }, 'They\'ll be signed out everywhere, and log in again with their username and the new password.'),
      err.el,
      actionsRow(button('Back', { kind: 'ghost', onclick: () => api.step(choose) }), go),
    ];
  };

  const done = (api, pw) => {
    const out = h('input', { type: 'text', readOnly: true, value: pw, class: 'mono password-out', 'aria-label': 'The new password', spellcheck: 'false' });
    out.addEventListener('focus', () => out.select());
    return [
      h('p', { class: 'ok-line' }, icon('check'), h('span', null, h('b', null, who), ' is signed out everywhere.')),
      h('div', { class: 'secret-row' }, out, copyButton(() => pw)),
      h('p', null, 'Give them this password. They log in with their username', p.name ? [', ', h('b', null, p.name), ','] : '', ' and this password. ',
        h('b', null, "It's shown only this once.")),
      h('p', { class: 'hint' }, 'A device that\'s already signed in keeps working for up to an hour, then has to log in again.'),
      actionsRow(button('Done', { kind: 'primary', onclick: () => api.close() })),
    ];
  };

  dialog('Reset ' + possessive(p) + ' password', choose, { onClose: () => { if (changed) ctx.reload(); } });
}

// Email the player a link to choose a new password themselves (adm_email_reset): better than making one up for them.
function linkDialog(p, em, ctx) {
  let changed = false;
  const who = p.name || 'this player';
  const confirm = (api) => {
    const err = errorLine();
    const go = button('Send link', { kind: 'primary', ico: 'mail', onclick: async () => {
      const res = await act('adm_email_reset', { p_id: p.id }, err, go);
      if (!res) return;
      changed = true;
      api.step(() => [
        res.sent === false
          ? h('p', { class: 'danger-line' }, icon('alert'), h('span', null, "Nothing was sent: the game's email isn't switched on (admin/README.md, Email). Reset their password instead."))
          : h('p', { class: 'ok-line' }, icon('check'), h('span', null, 'Sent to ', h('b', null, em.email), '.')),
        res.sent === false ? null : h('p', { class: 'hint' }, 'The link works once, for 30 minutes. Their password stays the same until they use it.'),
        actionsRow(button('Done', { kind: 'primary', onclick: () => api.close() })),
      ]);
    } });
    return [
      h('p', null, 'Email ', h('b', null, who), ' a link to choose a new password?'),
      h('p', null, 'It goes to ', h('b', { class: 'wrap' }, em.email), ', their confirmed email.'),
      h('p', { class: 'hint' }, 'The link works once, for 30 minutes. Their password stays the same until they use it, and nothing is shown to you.'),
      err.el,
      actionsRow(button('Cancel', { kind: 'ghost', onclick: () => api.close() }), go),
    ];
  };
  dialog('Send ' + who + ' a reset link', confirm, { onClose: () => { if (changed) ctx.reload(); } });
}

function signoutDialog(p, ctx) {
  let changed = false;
  const who = p.name || 'this player';
  const confirm = (api) => {
    const err = errorLine();
    const go = button('Sign out everywhere', { kind: 'primary', ico: 'out', onclick: async () => {
      const res = await act('adm_signout', { p_id: p.id }, err, go);
      if (!res) return;
      changed = true;
      const n = Number(res.sessions) || 0;
      api.step(() => [
        h('p', { class: 'ok-line' }, icon('check'), h('span', null, n ? 'Ended ' + plural(n, 'session') + '.' : 'Done. There were no sessions to end.')),
        h('p', { class: 'hint' }, 'A device that\'s already signed in keeps working for up to an hour, then has to log in again.'),
        actionsRow(button('Done', { kind: 'primary', onclick: () => api.close() })),
      ]);
    } });
    return [
      h('p', null, 'Sign ', h('b', null, who), ' out on every device?'),
      h('p', { class: 'hint' }, 'Their password stays the same. They can log in again whenever they like.'),
      err.el,
      actionsRow(button('Cancel', { kind: 'ghost', onclick: () => api.close() }), go),
    ];
  };
  dialog('Sign ' + who + ' out everywhere', confirm, { onClose: () => { if (changed) ctx.reload(); } });
}

function deleteDialog(p, ctx) {
  const target = p.name || p.id;
  const step = (api) => {
    const err = errorLine();
    const input = h('input', { type: 'text', autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off' });
    const go = button('Delete account', { kind: 'danger', ico: 'trash', disabled: true, onclick: async () => {
      const res = await act('adm_delete_player', { p_id: p.id, p_confirm: input.value.trim() }, err, go);
      if (!res) return;
      api.close();
      toast('Deleted ' + (p.name ? p.name + "'s" : 'the') + ' account and everything of theirs.');
      lastSearch = '';
      ctx.go('#support');
    } });
    input.addEventListener('input', () => { err.clear(); go.disabled = input.value.trim().toLowerCase() !== String(target).toLowerCase(); });
    return [
      h('p', { class: 'danger-line' }, icon('alert'), h('b', null, "This can't be undone.")),
      h('p', null, 'It deletes everything of theirs, like Delete account in the game: their username, profile, friends, saved progress and account details. Their install analytics stay, but are no longer linked to them.'),
      field(p.name ? 'Type their username, ' + p.name + ', to confirm' : 'They have no username: type their user id to confirm', input, p.name ? 'Any capitals.' : p.id),
      err.el,
      actionsRow(button('Cancel', { kind: 'ghost', onclick: () => api.close() }), go),
    ];
  };
  dialog('Delete ' + possessive(p) + ' account', step, { danger: true });
}
