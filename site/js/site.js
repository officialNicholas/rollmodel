// Every page: the footer's year, the support address and the App Store button, from js/config.js.
(() => {
  'use strict';
  const C = window.RM_CONFIG || {};
  for (const el of document.querySelectorAll('[data-year]')) el.textContent = String(new Date().getFullYear());
  if (C.SUPPORT_EMAIL) for (const el of document.querySelectorAll('[data-config="email"]')) { if (el.tagName === 'A') el.href = 'mailto:' + C.SUPPORT_EMAIL; el.textContent = C.SUPPORT_EMAIL; }
  // "Coming soon to the App Store" until the config has the game's link; then a real link to it
  const url = String(C.APP_STORE_URL || '');
  if (!/^https:\/\/apps\.apple\.com\/[^\s"<>]+$/.test(url)) return;
  for (const el of document.querySelectorAll('[data-config="appstore"]')) {
    if (el.tagName === 'A') { el.href = url; continue; }
    const a = document.createElement('a');
    a.className = el.className.replace(/\bis-soon\b/, '').trim(); a.href = url; a.dataset.config = 'appstore';
    const small = el.querySelector('.store-small'), big = el.querySelector('.store-big');
    if (small) small.textContent = 'Download on the';
    if (big) big.textContent = 'App Store';
    while (el.firstChild) a.appendChild(el.firstChild);
    el.replaceWith(a);
  }
})();
