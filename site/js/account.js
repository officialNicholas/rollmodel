// What the account pages (forgot, reset, confirm) share: the call to the game's database, the link's token, and the messages.
// Nothing here writes to the console or to storage: a token or a password only ever lives in these pages' memory.
(() => {
  'use strict';
  const C = window.RM_CONFIG || {};
  const OOPS = 'Something went wrong. Try again in a minute.';

  // POST {SUPABASE_URL}/rest/v1/rpc/<name> with the publishable key. Resolves to the answer's JSON; rejects on an HTTP error
  // (4xx or 5xx, with {code, message}), a network failure, no answer within 15 s, or an answer that isn't a JSON object.
  async function call(name, args) {
    const ctl = new AbortController(), timer = setTimeout(() => ctl.abort(), 15000);
    try {
      const r = await fetch(C.SUPABASE_URL + '/rest/v1/rpc/' + name, {
        method: 'POST', headers: { apikey: C.SUPABASE_KEY, 'Content-Type': 'application/json' }, body: JSON.stringify(args),
        signal: ctl.signal, credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer'
      });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const j = await r.json();
      if (!j || typeof j !== 'object') throw new Error('not an object');
      return j;
    } finally { clearTimeout(timer); }
  }

  // The link's token, from the address's fragment (#t=TOKEN), which never reaches a server. It's read once and the fragment
  // is wiped from the address bar (and so from the history) straight away.
  function takeToken() {
    const m = /(?:^|&)t=([^&]*)/.exec(location.hash.slice(1));
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
    if (!m) return '';
    let t = ''; try { t = decodeURIComponent(m[1]); } catch (e) { return ''; }
    t = t.trim();
    return /^[A-Za-z0-9_-]{20,100}$/.test(t) ? t : ''; // (the server's own rule for a link's token)
  }

  // A message, put in a live region (a box that's always on the page, so a screen reader reads out what lands in it): its words
  // (a string, or a list of strings and {b: 'bold words'}), an optional link after them, and how it looks (ok, bad). With focus,
  // the keyboard moves to it too (for when the thing that had focus has just gone).
  function say(region, kind, words, link, focus) {
    const m = document.createElement('div'); m.className = 'msg msg-' + kind;
    const p = document.createElement('p');
    for (const w of [].concat(words)) {
      if (typeof w === 'string') p.appendChild(document.createTextNode(w));
      else { const b = document.createElement('b'); b.textContent = w.b; p.appendChild(b); }
    }
    m.appendChild(p);
    if (link) { const a = document.createElement('a'); a.href = link.href; a.textContent = link.text; a.className = 'msg-link'; m.appendChild(a); }
    region.replaceChildren(m);
    if (focus) { m.tabIndex = -1; m.focus(); }
  }
  const hush = region => region.replaceChildren();

  window.RM = Object.freeze({ call, takeToken, say, hush, OOPS });
})();
