// Signing out after 15 minutes without input, with a warning a minute before that the person can dismiss
// by moving the pointer or typing.

const EVENTS = ['pointermove', 'pointerdown', 'keydown', 'wheel', 'touchstart', 'scroll'];

export function watchIdle({ idleMs, warnMs, onWarn, onBack, onIdle }) {
  let last = Date.now();
  let warned = false;
  let stopped = false;

  const bump = () => {
    last = Date.now();
    if (warned) { warned = false; onBack(); }
  };
  const tick = () => {
    if (stopped) return;
    const idle = Date.now() - last;
    if (idle >= idleMs) { stop(); onIdle(); }
    else if (!warned && idle >= idleMs - warnMs) { warned = true; onWarn(idleMs - idle); }
  };
  const stop = () => {
    stopped = true;
    clearInterval(timer);
    EVENTS.forEach((e) => window.removeEventListener(e, bump, true));
    document.removeEventListener('visibilitychange', tick);
  };

  EVENTS.forEach((e) => window.addEventListener(e, bump, { capture: true, passive: true }));
  document.addEventListener('visibilitychange', tick);
  const timer = setInterval(tick, Math.min(1000, Math.max(200, warnMs / 4)));
  return { stop, bump };
}
