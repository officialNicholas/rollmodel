# Roll Model website

The game's public website: what the game is, the Privacy Policy, Terms of Service and Support pages Apple asks for, and
the pages the account emails link to. Plain HTML, CSS and a little JavaScript: no trackers, no cookies, no third-party
scripts or fonts, and a strict Content Security Policy (`_headers`).

| Page | What it's for |
|---|---|
| `index.html` | The game: how it plays, the modes, the Paint Shop and Strokes, the canvases, screenshots |
| `privacy.html`, `terms.html`, `credits.html` | The game's own text, word for word (made by `tools/site_build.py`) |
| `support.html` | How to reach us, and short answers |
| `forgot.html` | Forgot password: a username or email in, a reset link out (if the account has a confirmed email) |
| `reset.html` | Where a reset email's button goes: choose a new password |
| `confirm.html` | Where a welcome email's button goes: confirm the email |
| `404.html` | Not found |

The three account pages call the game's Supabase project directly (`rm_reset_request`, `rm_reset_password`,
`rm_email_verify` in `supabase/migrations/20261019000000_email.sql`). The links carry their one-time code after a `#`,
so it never reaches a server log, and the page clears it from the address bar once read.

## Building and trying it
- `python3 tools/site_build.py` rewrites privacy, terms and credits from the game (`DOCS` in `game/index.html`), writes
  `js/config.js`'s values into the pages, and checks every page (no em dashes, nothing inline the CSP would block, no
  broken links, alt text and image sizes, noindex on the account pages). Run it whenever the game's text changes.
  `--images` remakes the pictures taken from the game; `--dist DIR` makes the folder to upload (everything but `dev/`).
- `python3 site/dev/serve.py` serves it at http://127.0.0.1:8798 with the real headers.
- `python3 site/dev/test_site.py` runs the browser tests: every page at phone and desktop size in light and dark, and
  every answer the account pages can get (the Supabase calls are answered by the test, never sent).

`js/config.js` holds the few absolute values: the Supabase address and publishable key (public by design, they ship in
the game), `SUPPORT_EMAIL`, `APP_STORE_URL` (empty until the game is live: the button then says "Coming soon") and
`SITE_URL` (the domain, for share previews). Change them there, then run the build.

## Going live (about an hour, once)

Everything here is free except the domain (about $10 a year). The steps use `playrollmodel.com`: put your own domain
wherever it appears, here and in `js/config.js`.

### 1. The domain
Buy it at Cloudflare (Dashboard > Domain Registration > Register Domains). It sells at cost, and the domain's DNS is
then already in Cloudflare, where every step below happens.

### 2. The website
1. In `site/js/config.js`, set `SITE_URL` to `https://playrollmodel.com` (and `SUPPORT_EMAIL` if it differs), then make
   the upload folder: `python3 tools/site_build.py --dist /tmp/rollmodel-site`.
2. Cloudflare > Workers & Pages > Create > Pages > Upload assets. Name it `rollmodel-site` and drop that folder in. Each
   time the site changes, build and upload again.
3. The project's Custom domains tab: add `playrollmodel.com`, then `www.playrollmodel.com`.
4. Check https://playrollmodel.com/privacy and /support load. In App Store Connect, use them as the Privacy Policy URL
   and the Support URL, and https://playrollmodel.com as the Marketing URL.

### 3. support@ (free)
Cloudflare > Email > Email Routing > Enable. Add `support@playrollmodel.com` (and `dmarc@playrollmodel.com`, for the
reports in step 4) forwarding to your own inbox. Cloudflare adds the records it needs on its own.

### 4. Sending email that lands in the inbox (Resend, free up to 3,000 a month)
Account emails go out from a subdomain, `mail.playrollmodel.com`, so anything that happens to its reputation never
touches the main domain.
1. Sign up at resend.com. Domains > Add Domain: `mail.playrollmodel.com`, region closest to your Supabase project.
2. Resend lists DNS records (SPF and the bounce MX on `send.mail`, and a DKIM key on `resend._domainkey.mail`). In
   Cloudflare > DNS > Records, add each one exactly as shown, with the proxy **off** (grey cloud). (If Resend offers
   to add them to Cloudflare for you, that works too.)
3. Add DMARC, one TXT record on the main domain:
   - Name: `_dmarc`
   - Content: `v=DMARC1; p=none; rua=mailto:dmarc@playrollmodel.com`

   After two to four weeks of reports showing only your own mail, change `p=none` to `p=quarantine`.
4. Back in Resend, press Verify. It usually takes a few minutes.
5. API Keys > Create API Key: permission **Sending access**, domain `mail.playrollmodel.com`. Copy it once, straight into
   the Supabase SQL editor (and nowhere else: not a chat, not a file, not the repository):
   ```sql
   select vault.create_secret('re_paste_it_here', 'resend_api_key');
   ```
6. Finish in `admin/README.md`, Email: turn on pg_net, set the site and addresses, and make an account to try it.

What keeps these emails out of spam, and is already built in:
- They're signed (DKIM) and allowed (SPF) for the exact domain they come from, with DMARC on top.
- They're only ever account emails a player asked for. No newsletters from this domain, ever.
- Each one has a plain-text version, a real reply-to address (support@), the same sender name every time, links only
  to your own domain (no link shorteners), and a small logo image.
- Volume starts tiny and grows with the game, which is how a new domain earns its reputation.

### 5. The dashboard
See `admin/README.md`, Hosting: a second Pages project at `admin.playrollmodel.com`, behind Cloudflare Access.

### If you use a different domain
Change `SUPPORT_EMAIL` in `js/config.js`, the addresses in the SQL in `admin/README.md`, and rebuild. The game itself
doesn't need the domain: the emails' links come from the database settings.
