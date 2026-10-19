"""email_build.py: Roll Model's account emails (welcome, password reset, password changed), built from one layout into email/.

Each email is an HTML file and a plain-text twin. The server fills in the {{...}} values (HTML-escaped) before sending:
  {{username}}  the player's username             {{link}}     the button's link (confirm email / choose a new password)
  {{site}}      the website, e.g. https://playrollmodel.com (its /email/ folder holds the pictures)
  {{support}}   the support address                {{when}}     when the password was changed (password changed only)
  {{year}}      this year

Built for inboxes, not browsers: tables for layout, every style inline (a short <style> only adds dark mode and phone sizes for the
apps that read it), images with their size and alt text, and a plain-text version, which helps them stay out of spam.
Run: python3 tools/email_build.py"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), 'email')

INK, PAPER, CARD, LINE, RED, RED_LO, LIME, MUTED = '#171320', '#F4EEE3', '#FFFCF6', '#E6DCCB', '#E3122F', '#99091F', '#CBE45A', '#6E6577'
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
DISPLAY = "'Bowlby One','Arial Black','Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif" # (Bowlby One where the inbox loads web fonts, Apple Mail mostly; a heavy system font elsewhere)

def layout(title, preheader, body):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Bowlby+One&amp;display=swap" rel="stylesheet">
<style>
  body{{margin:0;padding:0;-webkit-text-size-adjust:100%;text-size-adjust:100%}}
  a{{text-decoration:none}}
  @media (max-width:620px){{
    .wrap{{padding:12px 10px 28px!important}}
    .card{{border-radius:22px!important}}
    .pad{{padding-left:22px!important;padding-right:22px!important}}
    .h1{{font-size:28px!important;line-height:32px!important}}
    .name{{font-size:26px!important}}
  }}
  @media (prefers-color-scheme:dark){{
    .bg{{background:#110E18!important}}
    .card{{background:#1E1928!important;border-color:#342C42!important}}
    .ink{{color:#F4EEE3!important}}
    .soft{{color:#B9AFC6!important}}
    .namebox{{background:#2A2336!important;border-color:#CBE45A!important}}
    .namebox .name{{color:#CBE45A!important}}
    .rule{{border-color:#342C42!important}}
    .warn{{background:#2A2336!important;border-color:#4A3F5C!important}}
  }}
</style>
</head>
<body class="bg" style="margin:0;padding:0;background:{PAPER}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;mso-hide:all">{preheader}&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
<table role="presentation" class="bg" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{PAPER}">
<tr><td class="wrap" align="center" style="padding:28px 16px 40px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:560px">
    <tr><td align="center" style="padding:0 0 6px">
      <a href="{{{{site}}}}" style="text-decoration:none"><img src="{{{{site}}}}/email/logo.png" width="230" height="161" alt="Roll Model" style="display:block;width:230px;max-width:62%;height:auto;border:0"></a>
    </td></tr>
    <tr><td>
      <table role="presentation" class="card" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{CARD};border:1px solid {LINE};border-radius:28px;border-collapse:separate">
        <tr><td class="pad" style="padding:34px 40px 36px">
{body}
        </td></tr>
      </table>
    </td></tr>
    <tr><td class="pad" style="padding:22px 30px 0;font-family:{SANS};font-size:12px;line-height:18px;color:{MUTED};text-align:center">
      <p class="soft" style="margin:0 0 8px;color:{MUTED}">{{{{why}}}}</p>
      <p class="soft" style="margin:0 0 8px;color:{MUTED}">Questions? Write to <a href="mailto:{{{{support}}}}" style="color:{MUTED};text-decoration:underline">{{{{support}}}}</a></p>
      <p class="soft" style="margin:0;color:{MUTED}"><a href="{{{{site}}}}/privacy" style="color:{MUTED};text-decoration:underline">Privacy Policy</a> &nbsp;&middot;&nbsp; <a href="{{{{site}}}}/terms" style="color:{MUTED};text-decoration:underline">Terms of Service</a> &nbsp;&middot;&nbsp; <a href="{{{{site}}}}/support" style="color:{MUTED};text-decoration:underline">Support</a></p>
      <p class="soft" style="margin:10px 0 0;color:{MUTED}">Roll Model &middot; A Marcelin Game &middot; &copy; {{{{year}}}}</p>
    </td></tr>
  </table>
</td></tr>
</table>
</body>
</html>
"""

def h1(t): return f'          <h1 class="h1 ink" style="margin:0 0 14px;font-family:{DISPLAY};font-weight:900;font-synthesis:none;font-size:32px;line-height:36px;color:{INK};text-align:center;letter-spacing:.2px">{t}</h1>\n'
def p(t, center=True, small=False):
    size, lh, col, cls = ('13px', '20px', MUTED, 'soft') if small else ('16px', '25px', INK, 'ink')
    return f'          <p class="{cls}" style="margin:0 0 16px;font-family:{SANS};font-size:{size};line-height:{lh};color:{col};text-align:{"center" if center else "left"}">{t}</p>\n'
def button(label, href='{{link}}'):
    return f"""          <table role="presentation" align="center" cellpadding="0" cellspacing="0" border="0" style="margin:8px auto 22px">
            <tr><td align="center" bgcolor="{RED}" style="border-radius:999px;background:{RED};border-bottom:4px solid {RED_LO}">
              <a href="{href}" style="display:inline-block;padding:16px 34px;font-family:{SANS};font-size:17px;line-height:20px;font-weight:800;color:#FFFFFF;text-decoration:none;border-radius:999px">{label}</a>
            </td></tr>
          </table>
"""
def namebox():
    return f"""          <table role="presentation" class="namebox" align="center" cellpadding="0" cellspacing="0" border="0" style="margin:6px auto 22px;background:{LIME};border:2px solid {INK};border-radius:18px;border-collapse:separate">
            <tr><td align="center" style="padding:12px 30px 14px">
              <p class="soft" style="margin:0 0 2px;font-family:{SANS};font-size:11px;line-height:14px;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;color:{INK};opacity:.7">Your username</p>
              <p class="name" style="margin:0;font-family:{DISPLAY};font-weight:900;font-synthesis:none;font-size:30px;line-height:36px;color:{INK};word-break:break-all">{{{{username}}}}</p>
            </td></tr>
          </table>
"""
def fallback(t='Button not working? Copy this link into your browser:'):
    return (p(t, small=True).replace('margin:0 0 16px', 'margin:0 0 4px')
            + f'          <p style="margin:0 0 4px;font-family:{SANS};font-size:12px;line-height:18px;text-align:center;word-break:break-all"><a href="{{{{link}}}}" style="color:{RED};text-decoration:underline">{{{{link}}}}</a></p>\n')
def rule(): return f'          <hr class="rule" style="border:0;border-top:1px solid {LINE};margin:22px 0 20px">\n'
def sign(): return p('See you on the canvas!<br><b>Ol&#8217; Bloop</b>, your coach')

EMAILS = {
  'welcome': dict(
    subject='Welcome to Roll Model, {{username}}!',
    preheader='Your username is {{username}}. Confirm your email so you can always get back in.',
    why='You got this email because a Roll Model account was made with this address. If that wasn&#8217;t you, ignore it.',
    body=h1('Welcome to Roll&nbsp;Model!')
      + p('Your account is ready. This is the name the canvas will know you by:')
      + namebox()
      + p('Log in with it and your password on any phone, and your progress comes with you.')
      + p('One last thing: confirm your email, so we can get you back in if you ever forget your password.')
      + button('Confirm my email')
      + p('The button works for 24 hours.', small=True)
      + rule() + sign(),
    text="""Welcome to Roll Model!

Your account is ready. Your username is:

    {{username}}

Log in with it and your password on any phone, and your progress comes with you.

One last thing: confirm your email, so we can get you back in if you ever forget your password:
{{link}}
(The link works for 24 hours.)

See you on the canvas!
Ol' Bloop, your coach

--
You got this email because a Roll Model account was made with this address. If that wasn't you, ignore it.
Questions? Write to {{support}}
Privacy Policy: {{site}}/privacy  Terms: {{site}}/terms  Support: {{site}}/support
Roll Model, A Marcelin Game
"""),
  'reset': dict(
    subject='Reset your Roll Model password',
    preheader='Choose a new password for {{username}}. The link works for 30 minutes.',
    why='You got this email because someone asked to reset the password of the Roll Model account with this address.',
    body=h1('Forgot your password?')
      + p('No problem, <b>{{username}}</b>. Tap the button and choose a new one.')
      + button('Choose a new password')
      + p('The button works once, for 30 minutes.', small=True)
      + rule()
      + p('Didn&#8217;t ask for this? Ignore this email. Your password stays the same and your account is safe.', small=True)
      + fallback(),
    text="""Forgot your password?

No problem, {{username}}. Open this link and choose a new one:
{{link}}

The link works once, for 30 minutes.

Didn't ask for this? Ignore this email. Your password stays the same and your account is safe.

--
You got this email because someone asked to reset the password of the Roll Model account with this address.
Questions? Write to {{support}}
Privacy Policy: {{site}}/privacy  Terms: {{site}}/terms  Support: {{site}}/support
Roll Model, A Marcelin Game
"""),
  'changed': dict(
    subject='Your Roll Model password was changed',
    preheader='If this was you, you&#8217;re all set.',
    why='You got this email because the password of the Roll Model account with this address was changed.',
    body=h1('Your password was changed')
      + p('<b>{{username}}</b>, the password for your Roll Model account was changed on {{when}}. You&#8217;ve been signed out on your other devices.')
      + p('If this was you, you&#8217;re all set.')
      + f"""          <table role="presentation" class="warn" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 18px;background:{PAPER};border:1px solid {LINE};border-radius:16px;border-collapse:separate">
            <tr><td style="padding:16px 18px 2px">
""" + p('<b>Wasn&#8217;t you?</b> Choose a new password right away, then write to us at {{support}}.').replace('          <p', '              <p')
      + button('Reset my password').replace('          ', '              ')
      + """            </td></tr>
          </table>
""",
    text="""Your password was changed

{{username}}, the password for your Roll Model account was changed on {{when}}. You've been signed out on your other devices.

If this was you, you're all set.

Wasn't you? Choose a new password right away:
{{link}}
then write to us at {{support}}.

--
You got this email because the password of the Roll Model account with this address was changed.
Questions? Write to {{support}}
Privacy Policy: {{site}}/privacy  Terms: {{site}}/terms  Support: {{site}}/support
Roll Model, A Marcelin Game
"""),
}

def build():
    os.makedirs(OUT, exist_ok=True)
    for k, e in EMAILS.items():
        html = layout(e['subject'], e['preheader'], e['body']).replace('{{why}}', e['why'])
        assert '—' not in html and '—' not in e['text']
        open(os.path.join(OUT, k + '.html'), 'w').write(html)
        open(os.path.join(OUT, k + '.txt'), 'w').write(e['text'])
        open(os.path.join(OUT, k + '.subject.txt'), 'w').write(e['subject'] + '\n')
        print(k, len(html), sorted(set(re.findall(r'\{\{(\w+)\}\}', html + e['text']))))

if __name__ == '__main__':
    build()
