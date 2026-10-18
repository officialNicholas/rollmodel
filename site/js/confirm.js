// confirm.html: the welcome email's button links here as confirm.html#t=TOKEN. On load the token is read from the fragment, wiped
// from the address bar, and sent to rm_email_verify; the page then says the email's confirmed, or why not.
(() => {
  'use strict';
  const token = RM.takeToken();
  const box = document.getElementById('confirmMsg'), wait = document.getElementById('confirmWait'), again = document.getElementById('confirmAgain');
  const RESEND = 'Ask the game to send a new one: in the menu, tap Email, then Send it again.';
  const WHY = {
    expired: ['This link has expired. ' + RESEND],
    used: ['This link was already used. If you opened it before, your email is already confirmed.'],
    bad: ['This link isn’t valid. ' + RESEND]
  };
  const stop = () => { wait.hidden = true; };
  async function go() {
    again.hidden = true; wait.hidden = false; RM.hush(box);
    let ans = null; try { ans = await RM.call('rm_email_verify', { p_token: token }); } catch (e) { ans = null; }
    stop();
    if (ans && ans.ok === true && typeof ans.username === 'string' && ans.username) return RM.say(box, 'ok', ['Email confirmed, ', { b: ans.username }, '! You can close this page.']);
    const why = ans && ans.ok === false ? ans.why : null;
    if (WHY[why]) return RM.say(box, 'bad', WHY[why][0]);
    RM.say(box, 'bad', RM.OOPS); again.hidden = false; // (an HTTP error or no network: the token's still here, so it can try again)
  }
  again.addEventListener('click', go);
  if (!token) { document.documentElement.classList.replace('has-token', 'no-token'); return; } // (the page shows its no-link message)
  go();
})();
