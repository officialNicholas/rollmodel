# Roll Model account emails

The emails the game's backend sends, in the game's look. `tools/email_build.py` builds them from one layout. Edit them there and
run it again; `tools/email_preview.py` draws what they look like in an inbox.

| Email | When | Subject |
|---|---|---|
| `welcome` | A player adds their email to their account. Shows their username, and a button that confirms the email (24 hours) | Welcome to Roll Model, {{username}}! |
| `reset` | "Forgot password?" in the game, or on the website. A button to choose a new password (once, 30 minutes) | Reset your Roll Model password |
| `changed` | The password changed (by the player, or by support). A button to reset it, in case it wasn't them | Your Roll Model password was changed |

Each has an HTML version, a plain-text version (`.txt`) and its subject (`.subject.txt`). The server fills in `{{username}}`,
`{{link}}`, `{{site}}`, `{{support}}`, `{{year}}` and `{{when}}`, HTML-escaped. The pictures (`assets/logo.png`, `assets/icon.png`)
are served by the website from `/email/`.

What keeps them out of spam is partly here and partly in the domain's settings (see `site/README.md` once the site is set up):
- they're built from tables with every style inline, so they look right everywhere;
- each one has a plain-text twin;
- there's one clear button, links only to our own domain, and no link shorteners;
- they're light on pictures, the logo is small, and every picture has alt text;
- the footer has a real reply address and says why the email was sent.
