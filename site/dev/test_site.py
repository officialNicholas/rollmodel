#!/usr/bin/env python3
"""The website's checks, in Chromium (Playwright) against site/dev/serve.py, so the Content-Security-Policy and the other headers in
site/_headers apply exactly as the host will send them.

  python3 site/dev/test_site.py [--shots DIR]

- Every page at 390x844 and 1440x900, in light and dark: no console errors or warnings, no page errors, no CSP violations, no failed
  requests, every picture loaded, nothing wider than the screen, no layout shift, one h1 and no skipped heading levels, alt text on
  every picture, a label on every field, a visible focus ring, the fonts loaded, and every link on the site going somewhere.
- The headers, the host's addresses (/privacy for privacy.html, a 404 for anything else), and the App Store button both ways.
- The account pages against every answer the game's database can give (forgot, reset and confirm), and against HTTP errors and a
  dropped connection. The calls to Supabase are answered by this script (route **/*supabase.co/**); anything else that isn't the
  local server is blocked, so nothing ever reaches the real project or anywhere else. The token and the password must never show up
  in the console, in storage or in the address bar.
A full-page screenshot of every page and of every state the account pages can be in goes to --shots (default: a temp folder)."""
import json, os, re, sys, tempfile, threading, time, traceback
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import serve
SITE = os.path.dirname(HERE)
CONF = dict(re.findall(r"^\s*([A-Z_]+):\s*'([^']*)'", open(os.path.join(SITE, 'js', 'config.js'), encoding='utf8').read(), re.M))
SUPA, KEY = CONF['SUPABASE_URL'], CONF['SUPABASE_KEY']
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self' "
       "https://nbemerxgukwwtrfgirfl.supabase.co; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
PAGES = ['index.html', 'privacy.html', 'terms.html', 'credits.html', 'support.html', 'forgot.html', 'reset.html', 'confirm.html', '404.html']
SIZES = [(390, 844), (1440, 900)]
OOPS = 'Something went wrong. Try again in a minute.'
SENT = 'If that account has a confirmed email, we’ve sent a link to it. Check your inbox (and spam).'
TOKEN = 'k3Rb9xQ2mVt7wLp4zN8sHc1dYf6gJa0u-Qe5_Tn2WvXo'  # (like the server's: 32 random bytes in base64url)
PASSWORD = 'paint4ever'

args = sys.argv[1:]
SHOTS = args[args.index('--shots') + 1] if '--shots' in args else tempfile.mkdtemp(prefix='rm_site_shots_')
os.makedirs(SHOTS, exist_ok=True)
results = []

def ck(name, ok, info=''):
    results.append((name, bool(ok), str(info)[:400]))
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok or not info else '  ' + str(info)[:400]), flush=True)

# ---------------------------------------------------------------- Supabase, answered here
class Supa:
    """Stands in for the game's Supabase project: answers rpc calls from a queue, records them, refuses anything else."""
    def __init__(self): self.queue, self.calls, self.stray = {}, [], []
    def answer(self, name, *answers): self.queue.setdefault(name, []).extend(answers)
    def handle(self, route, request):
        if request.method == 'OPTIONS':  # (a CORS preflight, should one come through)
            return route.fulfill(status=204, headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'apikey, content-type', 'Access-Control-Allow-Methods': 'POST'})
        m = re.match(r'^%s/rest/v1/rpc/(\w+)$' % re.escape(SUPA), request.url)
        if not m or request.method != 'POST': self.stray.append(request.method + ' ' + request.url); return route.abort()
        name = m.group(1)
        try: body = json.loads(request.post_data or 'null')
        except Exception: body = request.post_data
        self.calls.append({'name': name, 'headers': {k.lower(): v for k, v in request.headers.items()}, 'body': body})
        q = self.queue.get(name) or []
        if not q: self.stray.append('unexpected call ' + name); return route.abort()
        a = q.pop(0)
        if a == 'drop': return route.abort('failed')
        status, payload = a if isinstance(a, tuple) else (200, a)
        route.fulfill(status=status, headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}, body=json.dumps(payload))

class Watch:
    """What a page did that it shouldn't: console errors and warnings, page errors, CSP violations, failed requests, requests off
    the site, and every console line (to look for secrets in)."""
    def __init__(self, page, base, expect_failed=()):
        self.page, self.base, self.bad, self.console, self.offsite = page, base, [], [], []
        self.expect_failed = tuple(expect_failed)  # (addresses this test makes fail on purpose: the browser logs those itself)
        page.on('console', self.on_console)
        page.on('pageerror', lambda e: self.bad.append('pageerror: ' + str(e)[:300]))
        page.on('requestfailed', lambda r: None if r.url.startswith(SUPA) else self.bad.append('requestfailed: %s %s' % (r.url, r.failure)))
    def on_console(self, m):
        self.console.append(m.text)
        if m.type not in ('error', 'warning'): return
        where = (m.location or {}).get('url', '')
        if m.text.startswith('Failed to load resource') and self.expect_failed and where.startswith(self.expect_failed): return
        self.bad.append('console %s: %s %s' % (m.type, m.text[:300], where))
    def csp(self):
        try: return self.page.evaluate('() => window.__csp || []')
        except Exception: return []

INIT = """
window.__csp = [];
document.addEventListener('securitypolicyviolation', e => window.__csp.push(e.violatedDirective + ' ' + e.blockedURI));
window.__cls = 0;
try { new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({ type: 'layout-shift', buffered: true }); } catch (e) {}
"""

def context(browser, base, supa, w=390, h=844, scheme='light', config=None):
    ctx = browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, color_scheme=scheme, reduced_motion='reduce',
                              is_mobile=w < 600, has_touch=w < 600)
    offsite = []
    def gate(route, request):
        if request.url.startswith(base): return route.continue_()
        offsite.append(request.url); route.abort()
    ctx.route('**/*', gate)                                   # anything that isn't the local server: blocked
    ctx.route('**/*supabase.co/**', supa.handle)               # Supabase: answered here, never reached
    if config is not None:
        src = open(os.path.join(SITE, 'js', 'config.js'), encoding='utf8').read()
        for k, v in config.items(): src = re.sub(r"(%s:\s*)'[^']*'" % k, lambda m: m.group(1) + "'%s'" % v, src)
        ctx.route(base + 'js/config.js', lambda route: route.fulfill(status=200, headers={'Content-Type': 'text/javascript; charset=utf-8'}, body=src))
    ctx.add_init_script(INIT)
    ctx.offsite = offsite
    return ctx

def until(page, js, t=10.0):
    end = time.time() + t
    while time.time() < end:
        try:
            if page.evaluate(js): return True
        except Exception: pass
        time.sleep(0.08)
    return False

def text(page, sel):
    return page.evaluate("s => { const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g, ' ').trim() : null; }", sel)

def visible(page, sel):
    return page.evaluate("s => { const e = document.querySelector(s); return !!e && !e.closest('[hidden]') && e.getClientRects().length > 0; }", sel)

def press(page, supa, button, region, t=10.0):
    """Clicks a button that calls Supabase, and waits for the call and for the message it brings (the region is emptied first)."""
    n0 = len(supa.calls); page.click(button)
    end = time.time() + t
    while time.time() < end and len(supa.calls) == n0 and not supa.stray: time.sleep(0.05)
    until(page, "() => !!document.querySelector('%s .msg') || (!!document.getElementById('resetDone') && !document.getElementById('resetDone').hidden)" % region, t)
    time.sleep(0.05)
    return supa.calls[n0:]

def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, name + '.png'), full_page=True)

# ---------------------------------------------------------------- every page, both sizes, both schemes
def check_pages(browser, base, supa):
    linked = set()
    for page_name in PAGES:
        for w, h in SIZES:
            for scheme in ('light', 'dark'):
                tag = '%s %dx%d %s' % (page_name, w, h, scheme)
                ctx = context(browser, base, supa, w, h, scheme); page = ctx.new_page()
                url = base + ('no/such/page' if page_name == '404.html' else page_name)
                W = Watch(page, base, [url] if page_name == '404.html' else [])  # (the 404 page's own address answers 404, as it should)
                resp = page.goto(url, wait_until='load')
                ck(tag + ': status', resp.status == (404 if page_name == '404.html' else 200), resp.status)
                page.evaluate('() => document.fonts.ready.then(() => 1)')
                fonts = page.evaluate("() => [document.fonts.check('400 20px \"Bowlby One\"'), document.fonts.check('400 16px Figtree'), document.fonts.check('800 16px Figtree')]")
                ck(tag + ': the fonts loaded (Bowlby One, Figtree)', all(fonts), fonts)
                cls0 = page.evaluate('() => window.__cls')
                # down the page and back, so the lazy pictures load
                page.evaluate("() => new Promise(r => { let y = 0; const t = setInterval(() => { window.scrollTo(0, y += 500); if (y > document.documentElement.scrollHeight) { clearInterval(t); window.scrollTo(0, 0); r(); } }, 60); })")
                ok = until(page, "() => [...document.images].every(i => i.complete && i.naturalWidth > 0)", 15)
                broken = page.evaluate("() => [...document.images].filter(i => !(i.complete && i.naturalWidth > 0)).map(i => i.currentSrc || i.src)")
                ck(tag + ': every picture loaded', ok and not broken, broken)
                time.sleep(0.3)
                cls = page.evaluate('() => window.__cls')
                ck(tag + ': no layout shift (CLS %.4f on load, %.4f after scrolling)' % (cls0, cls), cls < 0.01, cls)
                m = page.evaluate("""() => {
                  const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(h => !h.closest('[hidden]')).map(h => +h.tagName[1]);
                  let skip = null; hs.reduce((p, l) => { if (l > p + 1 && skip === null) skip = p + '>' + l; return l; }, 0);
                  return { sw: document.documentElement.scrollWidth, iw: innerWidth, h1: hs.filter(l => l === 1).length, skip,
                    noalt: [...document.images].filter(i => !i.hasAttribute('alt')).map(i => i.src),
                    nolabel: [...document.querySelectorAll('input,select,textarea')].filter(i => i.type !== 'hidden' && !(i.labels && i.labels.length) && !i.getAttribute('aria-label')).map(i => i.id),
                    lang: document.documentElement.lang, title: document.title,
                    robots: (document.querySelector('meta[name=robots]') || {}).content || '',
                    links: [...document.querySelectorAll('a[href]')].filter(a => !a.getAttribute('href').startsWith('#')).map(a => a.href),
                    dupes: [...document.querySelectorAll('[id]')].map(e => e.id).filter((id, i, all) => all.indexOf(id) !== i),
                    storage: localStorage.length + sessionStorage.length, cookies: document.cookie };
                }""")
                ck(tag + ': nothing wider than the screen', m['sw'] <= m['iw'], (m['sw'], m['iw']))
                ck(tag + ': one h1, no skipped heading levels', m['h1'] == 1 and m['skip'] is None, (m['h1'], m['skip']))
                ck(tag + ': alt text on every picture, a label on every field', not m['noalt'] and not m['nolabel'], (m['noalt'], m['nolabel']))
                ck(tag + ': lang, title, no id used twice', m['lang'] == 'en' and 'Roll Model' in m['title'] and not m['dupes'], (m['title'], m['dupes']))
                ck(tag + ': noindex where it should be', ('noindex' in m['robots']) == (page_name in ('forgot.html', 'reset.html', 'confirm.html', '404.html')), m['robots'])
                ck(tag + ': no cookies, nothing stored', m['storage'] == 0 and not m['cookies'] and not ctx.cookies(), (m['storage'], m['cookies']))
                linked.update(l for l in m['links'] if l.startswith(base))
                # the keyboard: the first Tab shows the skip link, the next has a visible focus ring
                page.keyboard.press('Tab')
                skip = page.evaluate("() => { const a = document.activeElement, r = a.getBoundingClientRect(); return [a.className, r.top >= 0 && r.bottom <= innerHeight, getComputedStyle(a).outlineStyle]; }")
                page.keyboard.press('Tab')
                ring = page.evaluate("() => { const a = document.activeElement, s = getComputedStyle(a); return [a.tagName, s.outlineStyle, parseFloat(s.outlineWidth)]; }")
                ck(tag + ': skip link first, then a visible focus ring', skip[0] == 'skip' and skip[1] and ring[1] != 'none' and ring[2] >= 2, (skip, ring))
                page.keyboard.press('Shift+Tab'); page.keyboard.press('Shift+Tab'); page.evaluate('() => document.activeElement && document.activeElement.blur()')
                if page_name not in ('reset.html', 'confirm.html'):  # (those two answer a link; their states are shot below)
                    shot(page, '%s-%d-%s' % (page_name.replace('.html', ''), w, scheme))
                csp = W.csp()
                ck(tag + ': no console errors or warnings, no CSP violations, nothing off the site', not W.bad and not csp and not ctx.offsite, (W.bad, csp, ctx.offsite))
                ctx.close()
    # in between the two sizes too: nothing wider than the screen
    for w in (320, 768, 1024, 1180):
        ctx = context(browser, base, supa, w, 900); page = ctx.new_page(); wide = []
        for page_name in PAGES:
            page.goto(base + page_name, wait_until='load')
            sw = page.evaluate('() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]')
            if sw[0] > sw[1]: wide.append((page_name, sw))
        ck('at %dpx wide, no page is wider than the screen' % w, not wide, wide)
        ctx.close()
    # every link on the site goes somewhere
    ctx = context(browser, base, supa); req = ctx.request; dead = []
    for l in sorted(linked):
        u, _, frag = l.partition('#')
        r = req.get(u)
        if r.status != 200: dead.append((l, r.status)); continue
        if frag and r.headers.get('content-type', '').startswith('text/html') and ('id="%s"' % frag) not in r.text(): dead.append((l, 'no #' + frag))
    ck('every link on the site goes somewhere (%d links)' % len(linked), not dead, dead)
    ctx.close()

# ---------------------------------------------------------------- the headers and the host's addresses
def check_host(browser, base, supa):
    ctx = context(browser, base, supa); req = ctx.request
    r = req.get(base)
    hd = {k.lower(): v for k, v in r.headers.items()}
    ck('headers: the Content-Security-Policy is the one asked for', hd.get('content-security-policy') == CSP, hd.get('content-security-policy'))
    ck('headers: nosniff, no-referrer, no framing, HSTS, Permissions-Policy', hd.get('x-content-type-options') == 'nosniff' and hd.get('referrer-policy') == 'no-referrer'
       and hd.get('x-frame-options') == 'DENY' and hd.get('strict-transport-security', '').startswith('max-age=') and 'camera=()' in hd.get('permissions-policy', ''), hd)
    for path, want in (('privacy', 'Privacy Policy'), ('terms', 'Terms of Service'), ('support', 'Support'), ('credits', 'Credits'), ('reset', 'Choose a new password'), ('email/logo.png', None), ('email/icon.png', None)):
        r = req.get(base + path)
        ck('the host: /%s answers' % path, r.status == 200 and (want is None or ('<h1' in r.text() and want in r.text())), r.status)
    r = req.get(base + 'nope/deeper/still')
    ck('the host: anything else is a 404 with the 404 page', r.status == 404 and 'This page rolled away' in r.text(), r.status)
    r = req.get(base + 'dev/serve.py')
    ck('the host: dev/ is not served', r.status == 404, r.status)
    ctx.close()
    # the 404 page's links and styles work however deep the address
    ctx = context(browser, base, supa); page = ctx.new_page(); W = Watch(page, base, [base + 'a/b/c/d'])
    page.goto(base + 'a/b/c/d', wait_until='load')
    bg = page.evaluate("() => getComputedStyle(document.body).backgroundColor")
    hrefs = page.evaluate("() => [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))")
    ck('404 deep down: styled, and its links start at the root', bg == 'rgb(244, 238, 227)' and all(h.startswith(('/', '#', 'mailto:')) for h in hrefs), (bg, hrefs))
    ck('404 deep down: no errors', not W.bad and not W.csp(), W.bad)
    ctx.close()

def check_store(browser, base, supa):
    for url, want in (('', 'soon'), ('https://apps.apple.com/app/roll-model/id1234567890', 'link')):
        ctx = context(browser, base, supa, config={'APP_STORE_URL': url}); page = ctx.new_page(); W = Watch(page, base)
        page.goto(base, wait_until='load'); time.sleep(0.2)
        els = page.evaluate("() => [...document.querySelectorAll('[data-config=appstore]')].map(e => [e.tagName, e.getAttribute('href'), e.innerText.replace(/\\s+/g, ' ').trim()])")
        if want == 'soon': ok = len(els) == 2 and all(e[0] == 'SPAN' and e[1] is None and e[2].lower() == 'coming soon to the app store' for e in els)
        else: ok = len(els) == 2 and all(e[0] == 'A' and e[1] == url and e[2].lower() == 'download on the app store' for e in els)
        ck('App Store button with APP_STORE_URL %r: %s' % (url, 'Coming soon' if want == 'soon' else 'a link to it'), ok and not W.bad, (els, W.bad))
        if want == 'link': shot(page, 'index-390-light-appstore-live')
        ctx.close()

# ---------------------------------------------------------------- the account pages, against every answer
def account_page(browser, base, supa, path, scheme='light', w=390, h=844, clock=False):
    ctx = context(browser, base, supa, w, h, scheme); page = ctx.new_page()
    if clock: page.clock.install()
    W = Watch(page, base, [SUPA + '/rest/v1/rpc/'])  # (the calls these tests fail on purpose: HTTP errors, a dropped connection)
    page.goto(base + path, wait_until='load')
    return ctx, page, W

def no_secrets(tag, page, W, secrets):
    store = page.evaluate("() => JSON.stringify([Object.entries(localStorage), Object.entries(sessionStorage), document.cookie, location.href, history.state])")
    leaks = [s for s in secrets if any(s in c for c in W.console) or s in store]
    ck(tag + ': the token and password never in the console, storage or address bar', not leaks, leaks)

def check_forgot(browser, base, supa):
    for scheme in ('light', 'dark'):
        ctx, page, W = account_page(browser, base, supa, 'forgot.html', scheme, clock=True)
        n0 = len(supa.calls)
        page.click('#forgotGo')
        ck('forgot (%s): empty, says what to type, calls nothing' % scheme, visible(page, '#whoHint') and 'username or the email' in text(page, '#whoHint') and len(supa.calls) == n0, text(page, '#whoHint'))
        page.fill('#who', 'a!'); page.click('#forgotGo')
        ck('forgot: not a username, says so, calls nothing', 'isn’t a username' in (text(page, '#whoHint') or '') and len(supa.calls) == n0, text(page, '#whoHint'))
        page.fill('#who', 'not@an'); page.click('#forgotGo')
        ck('forgot: not an email, says so', 'email doesn’t look right' in (text(page, '#whoHint') or '') and len(supa.calls) == n0, text(page, '#whoHint'))
        page.fill('#who', '  Dusk  ')
        ck('forgot: typing clears the hint', not visible(page, '#whoHint'))
        supa.answer('rm_reset_request', {'ok': True})
        page.click('#forgotGo'); until(page, "() => !!document.querySelector('#forgotMsg .msg')")
        c = supa.calls[-1] if len(supa.calls) > n0 else {}
        ck('forgot: calls rm_reset_request once, with p_who', len(supa.calls) == n0 + 1 and c.get('body') == {'p_who': 'Dusk'}, c)
        ck('forgot: the call carries the publishable key and JSON', c.get('headers', {}).get('apikey') == KEY and c.get('headers', {}).get('content-type', '').startswith('application/json') and 'authorization' not in c.get('headers', {}), c.get('headers'))
        ck('forgot: says the link is on its way (whether or not the account exists)', text(page, '#forgotMsg') == SENT, text(page, '#forgotMsg'))
        b = page.evaluate("() => [document.getElementById('forgotGo').getAttribute('aria-disabled'), document.getElementById('forgotGo').textContent]")
        ck('forgot: the button waits 30 s', b[0] == 'true' and re.match(r'Try again in (30|29) s', b[1]), b)
        if scheme == 'light': shot(page, 'forgot-390-light-sent')
        else: shot(page, 'forgot-390-dark-sent')
        page.click('#forgotGo', force=True); time.sleep(0.3)
        ck('forgot: a second try inside 30 s calls nothing', len(supa.calls) == n0 + 1, len(supa.calls) - n0)
        page.clock.run_for(15000)
        ck('forgot: 15 s later, 15 s to go', re.match(r'Try again in 1[3-6] s', page.evaluate("() => document.getElementById('forgotGo').textContent")) is not None, page.evaluate("() => document.getElementById('forgotGo').textContent"))
        page.clock.run_for(16000)
        b = page.evaluate("() => [document.getElementById('forgotGo').getAttribute('aria-disabled'), document.getElementById('forgotGo').textContent]")
        ck('forgot: after 30 s it can be pressed again', b[0] is None and b[1] == 'Send me a link', b)
        # an email this time, and the server failing
        page.fill('#who', 'dusk@example.com'); supa.answer('rm_reset_request', (500, {'code': 'XX000', 'message': 'boom'}))
        calls = press(page, supa, '#forgotGo', '#forgotMsg')
        ck('forgot: an email goes as p_who too', len(calls) == 1 and calls[0]['body'] == {'p_who': 'dusk@example.com'}, calls)
        ck('forgot: an HTTP 500 says try again in a minute', text(page, '#forgotMsg') == OOPS, text(page, '#forgotMsg'))
        if scheme == 'light': shot(page, 'forgot-390-light-error')
        for answer, what in (('drop', 'no network'), ((429, {'code': '429', 'message': 'slow down'}), 'an HTTP 4xx'), ({'ok': False}, 'an answer it doesn\'t know')):
            page.clock.run_for(31000); supa.answer('rm_reset_request', answer)
            calls = press(page, supa, '#forgotGo', '#forgotMsg')
            ck('forgot: %s says try again in a minute' % what, len(calls) == 1 and text(page, '#forgotMsg') == OOPS, (len(calls), text(page, '#forgotMsg')))
        ck('forgot (%s): no console errors, CSP violations, stray calls' % scheme, not W.bad and not W.csp() and not supa.stray and not ctx.offsite, (W.bad, W.csp(), supa.stray, ctx.offsite))
        ctx.close()

def reset_flow(browser, base, supa, answer, scheme='light', w=390, h=844, name=None, pw=PASSWORD):
    """Opens a reset link, types a good password twice, sends it; the server answers with `answer`."""
    ctx, page, W = account_page(browser, base, supa, 'reset.html#t=' + TOKEN, scheme, w, h)
    page.fill('#pw', pw); page.fill('#pw2', pw)
    supa.answer('rm_reset_password', answer); n0 = len(supa.calls)
    page.click('#resetGo')
    until(page, "() => !!document.querySelector('#resetMsg .msg') || !document.getElementById('resetDone').hidden")
    time.sleep(0.15)
    if name: shot(page, name)
    return ctx, page, W, supa.calls[n0:]

def check_reset(browser, base, supa):
    # no token at all
    ctx, page, W = account_page(browser, base, supa, 'reset.html')
    ck('reset, no token: no form, "This link isn’t valid." and a way to a new one', not visible(page, '#resetForm') and visible(page, '#resetNoLink') and text(page, '#resetNoLink').startswith('This link isn’t valid.')
       and page.evaluate("() => document.querySelector('#resetNoLink a').getAttribute('href')") == 'forgot.html', text(page, '#resetNoLink'))
    ctx.close()
    ctx, page, W = account_page(browser, base, supa, 'reset.html#t=short')
    ck('reset, a token too short to be one: the same', not visible(page, '#resetForm') and visible(page, '#resetNoLink') and '#' not in page.url, page.url)
    shot(page, 'reset-390-light-nolink'); ctx.close()
    # the link: the token is taken from the address and wiped from it
    ctx, page, W = account_page(browser, base, supa, 'reset.html#t=' + TOKEN)
    ck('reset: with a token, the form and no "not valid" message', visible(page, '#resetForm') and not visible(page, '#resetNoLink'))
    ck('reset: the token is wiped from the address bar', '#' not in page.url and TOKEN not in page.url and page.evaluate('() => location.hash') == '', page.url)
    shot(page, 'reset-390-light-empty')
    rules = lambda: page.evaluate("() => Object.fromEntries([...document.querySelectorAll('[data-rule]')].map(li => [li.dataset.rule, li.classList.contains('met')]))")
    page.fill('#pw', 'abc')
    ck('reset hints: "abc" has a letter only', rules() == {'len': False, 'letter': True, 'digit': False, 'same': False}, rules())
    page.fill('#pw', '12345678')
    ck('reset hints: "12345678" is long enough with a number, no letter', rules() == {'len': True, 'letter': False, 'digit': True, 'same': False}, rules())
    page.fill('#pw', PASSWORD); page.fill('#pw2', PASSWORD[:-1])
    ck('reset hints: a good password, the second not the same yet', rules() == {'len': True, 'letter': True, 'digit': True, 'same': False}, rules())
    shot(page, 'reset-390-light-typing')
    n0 = len(supa.calls); page.click('#resetGo')
    ck('reset: different passwords say so, call nothing', visible(page, '#pwErr') and 'don’t match' in text(page, '#pwErr') and len(supa.calls) == n0, text(page, '#pwErr'))
    page.fill('#pw', 'short1'); page.fill('#pw2', 'short1'); page.click('#resetGo')
    ck('reset: too short says so, calls nothing', 'needs 8 characters' in (text(page, '#pwErr') or '') and len(supa.calls) == n0, text(page, '#pwErr'))
    page.fill('#pw', 'nodigitshere'); page.fill('#pw2', 'nodigitshere'); page.click('#resetGo')
    ck('reset: no number says so', 'one number' in (text(page, '#pwErr') or ''), text(page, '#pwErr'))
    page.fill('#pw', '1234567890'); page.fill('#pw2', '1234567890'); page.click('#resetGo')
    ck('reset: no letter says so', 'one letter' in (text(page, '#pwErr') or ''), text(page, '#pwErr'))
    page.fill('#pw', 'пароль1234'); page.fill('#pw2', 'пароль1234')
    ck('reset hints: as the server counts, only A to Z are letters', rules() == {'len': True, 'letter': False, 'digit': True, 'same': True}, rules())
    page.fill('#pw', 'paint1' + 'é' * 34); page.fill('#pw2', 'paint1' + 'é' * 34)
    ck('reset hints: 72 bytes at most, as the server counts (40 characters, 74 bytes)', not rules()['len'], rules())
    ck('reset: 72 characters at most', page.evaluate("() => [document.getElementById('pw').maxLength, document.getElementById('pw2').maxLength]") == [72, 72])
    page.fill('#pw', 'a' * 71 + '1'); page.fill('#pw2', 'a' * 71 + '1')
    ck('reset hints: 72 characters is fine', rules() == {'len': True, 'letter': True, 'digit': True, 'same': True}, rules())
    page.click('#pwShow')
    t = page.evaluate("() => [document.getElementById('pw').type, document.getElementById('pw2').type, document.getElementById('pwShow').getAttribute('aria-pressed'), document.getElementById('pwShow').textContent]")
    ck('reset: Show shows both passwords', t == ['text', 'text', 'true', 'Hide'], t)
    page.click('#pwShow')
    t = page.evaluate("() => [document.getElementById('pw').type, document.getElementById('pw2').type, document.getElementById('pwShow').getAttribute('aria-pressed'), document.getElementById('pwShow').textContent]")
    ck('reset: Hide hides them again', t == ['password', 'password', 'false', 'Show'], t)
    no_secrets('reset (typing)', page, W, [TOKEN, PASSWORD])
    ck('reset (typing): no console errors or CSP violations', not W.bad and not W.csp(), (W.bad, W.csp()))
    ctx.close()
    # every answer
    for scheme in ('light', 'dark'):
        ctx, page, W, calls = reset_flow(browser, base, supa, {'ok': True, 'username': 'Dusk'}, scheme, name='reset-390-%s-done' % scheme)
        c = calls[0] if calls else {}
        ck('reset (%s): calls rm_reset_password with the token and the password' % scheme, len(calls) == 1 and c['body'] == {'p_token': TOKEN, 'p_password': PASSWORD}
           and c['headers'].get('apikey') == KEY and c['headers'].get('content-type', '').startswith('application/json'), c)
        ck('reset (%s): ok says the password changed, with the username' % scheme, not visible(page, '#resetForm') and text(page, '#resetDone') == 'Password changed. Open Roll Model and log in as Dusk with your new password.', text(page, '#resetDone'))
        ck('reset: the fields are emptied', page.evaluate("() => document.getElementById('pw').value + document.getElementById('pw2').value") == '')
        no_secrets('reset (done)', page, W, [TOKEN, PASSWORD])
        ck('reset (%s, done): no console errors or CSP violations' % scheme, not W.bad and not W.csp(), (W.bad, W.csp()))
        ctx.close()
    for why, want, link, form in (('expired', 'This link has expired. Ask for a new one.', True, False), ('used', 'This link was already used.', True, False),
                                  ('bad', 'This link isn’t valid.', True, False), ('weak', 'That password is too easy to guess. Pick a harder one.', False, True)):
        for scheme in (('light', 'dark') if why in ('expired', 'weak') else ('light',)):
            ctx, page, W, calls = reset_flow(browser, base, supa, {'ok': False, 'why': why}, scheme, name='reset-390-%s-%s' % (scheme, why))
            msg = text(page, '#resetMsg'); href = page.evaluate("() => { const a = document.querySelector('#resetMsg a'); return a && a.getAttribute('href'); }")
            ck('reset (%s): "%s" says "%s"' % (scheme, why, want), msg is not None and msg.startswith(want) and (href == 'forgot.html') == link and visible(page, '#resetForm') == form, (msg, href))
            ck('reset (%s, %s): no console errors or CSP violations' % (scheme, why), not W.bad and not W.csp(), (W.bad, W.csp()))
            no_secrets('reset (%s)' % why, page, W, [TOKEN, PASSWORD])
            ctx.close()
    # the server failing, then the same link working on a second try
    ctx, page, W, calls = reset_flow(browser, base, supa, (500, {'code': 'XX000', 'message': 'boom'}), name='reset-390-light-error')
    ck('reset: an HTTP 500 says try again in a minute, and keeps the form', text(page, '#resetMsg') == OOPS and visible(page, '#resetForm'), text(page, '#resetMsg'))
    for answer, what in (('drop', 'no network'), ((400, {'code': 'P0001', 'message': 'nope'}), 'an HTTP 4xx'), ({'ok': False, 'why': 'mystery'}, 'an answer it doesn\'t know')):
        supa.answer('rm_reset_password', answer); calls = press(page, supa, '#resetGo', '#resetMsg')
        ck('reset: %s says try again in a minute, and keeps the form' % what, len(calls) == 1 and text(page, '#resetMsg') == OOPS and visible(page, '#resetForm'), (len(calls), text(page, '#resetMsg')))
    supa.answer('rm_reset_password', {'ok': True, 'username': '<img src=x onerror=alert(1)>'}); press(page, supa, '#resetGo', '#resetMsg')
    ck('reset: tried again, the same link still works (the token was kept in memory)', supa.calls[-1]['body'] == {'p_token': TOKEN, 'p_password': PASSWORD} and not page.evaluate("() => document.getElementById('resetDone').hidden"), supa.calls[-1]['body'])
    ck('reset: a username is shown as text, never as HTML', page.evaluate("() => document.querySelector('#resetDone b').textContent") == '<img src=x onerror=alert(1)>' and page.evaluate("() => document.querySelectorAll('#resetDone img').length") == 1)
    no_secrets('reset (retry)', page, W, [TOKEN, PASSWORD])
    ck('reset (errors): no console errors or CSP violations, no stray calls', not W.bad and not W.csp() and not supa.stray and not ctx.offsite, (W.bad, W.csp(), supa.stray))
    ctx.close()
    # the host's own address for the page (the emails link to /reset#t=...): the same page, the same token handling
    ctx, page, W = account_page(browser, base, supa, 'reset#t=' + TOKEN)
    ok = until(page, "() => [...document.images].every(i => i.complete && i.naturalWidth > 0) && document.fonts.status === 'loaded'")
    page.fill('#pw', PASSWORD); page.fill('#pw2', PASSWORD); supa.answer('rm_reset_password', {'ok': True, 'username': 'Dusk'})
    calls = press(page, supa, '#resetGo', '#resetMsg')
    ck('reset at /reset#t=...: loads in full, wipes the token, and works', ok and page.url == base + 'reset' and len(calls) == 1 and calls[0]['body']['p_token'] == TOKEN
       and not page.evaluate("() => document.getElementById('resetDone').hidden") and not W.bad and not W.csp(), (page.url, W.bad))
    ctx.close()
    # at desktop size too
    ctx, page, W, calls = reset_flow(browser, base, supa, {'ok': True, 'username': 'Dusk'}, 'dark', 1440, 900, name='reset-1440-dark-done'); ctx.close()
    ctx, page, W, calls = reset_flow(browser, base, supa, {'ok': False, 'why': 'expired'}, 'light', 1440, 900, name='reset-1440-light-expired'); ctx.close()

def check_confirm(browser, base, supa):
    n0 = len(supa.calls); ctx, page, W = account_page(browser, base, supa, 'confirm.html'); time.sleep(0.3)
    ck('confirm, no token: "This link isn’t valid.", calls nothing', visible(page, '#confirmNoLink') and text(page, '#confirmNoLink').startswith('This link isn’t valid.') and not visible(page, '#confirmWait') and len(supa.calls) == n0, text(page, '#confirmNoLink'))
    shot(page, 'confirm-390-light-nolink'); ctx.close()
    RESEND = 'Ask the game to send a new one: in the menu, tap Email, then Send it again.'
    cases = [({'ok': True, 'username': 'Dusk'}, 'Email confirmed, Dusk! You can close this page.', 'done'),
             ({'ok': False, 'why': 'expired'}, 'This link has expired. ' + RESEND, 'expired'),
             ({'ok': False, 'why': 'used'}, 'This link was already used. If you opened it before, your email is already confirmed.', 'used'),
             ({'ok': False, 'why': 'bad'}, 'This link isn’t valid. ' + RESEND, 'bad'),
             ((500, {'code': 'XX000', 'message': 'boom'}), OOPS, 'error'),
             ('drop', OOPS, 'offline'),
             ((404, {'code': 'PGRST202', 'message': 'no such function'}), OOPS, 'error404')]
    for answer, want, name in cases:
        for scheme in (('light', 'dark') if name in ('done', 'expired', 'error') else ('light',)):
            supa.answer('rm_email_verify', answer); n0 = len(supa.calls)
            ctx, page, W = account_page(browser, base, supa, 'confirm.html#t=' + TOKEN, scheme)
            until(page, "() => !!document.querySelector('#confirmMsg .msg')")
            calls = supa.calls[n0:]
            got = page.evaluate("() => { const e = document.querySelector('#confirmMsg'); return e && e.textContent.trim(); }")
            ck('confirm (%s, %s): calls rm_email_verify once with the token' % (scheme, name), len(calls) == 1 and calls[0]['body'] == {'p_token': TOKEN} and calls[0]['headers'].get('apikey') == KEY, calls)
            ck('confirm (%s, %s): says "%s"' % (scheme, name, want), got == want, got)
            ck('confirm (%s): the token is wiped from the address bar' % name, '#' not in page.url and TOKEN not in page.url, page.url)
            again = visible(page, '#confirmAgain')
            ck('confirm (%s): Try again only when it might help' % name, again == (want == OOPS), again)
            shot(page, 'confirm-390-%s-%s' % (scheme, name))
            if name == 'error':
                supa.answer('rm_email_verify', {'ok': True, 'username': 'Dusk'}); page.click('#confirmAgain'); until(page, "() => (document.querySelector('#confirmMsg .msg-ok') || {}).textContent")
                ck('confirm: Try again works with the same token', supa.calls[-1]['body'] == {'p_token': TOKEN} and text(page, '#confirmMsg') == 'Email confirmed, Dusk! You can close this page.', text(page, '#confirmMsg'))
            no_secrets('confirm (%s)' % name, page, W, [TOKEN])
            ck('confirm (%s, %s): no console errors or CSP violations' % (scheme, name), not W.bad and not W.csp(), (W.bad, W.csp()))
            ctx.close()
    supa.answer('rm_email_verify', {'ok': True, 'username': 'Dusk'})
    ctx, page, W = account_page(browser, base, supa, 'confirm.html#t=' + TOKEN, 'light', 1440, 900); until(page, "() => !!document.querySelector('#confirmMsg .msg')")
    shot(page, 'confirm-1440-light-done'); ctx.close()
    # the address in the welcome email: /confirm#t=...
    supa.answer('rm_email_verify', {'ok': True, 'username': 'Dusk'}); n0 = len(supa.calls)
    ctx, page, W = account_page(browser, base, supa, 'confirm#t=' + TOKEN); until(page, "() => !!document.querySelector('#confirmMsg .msg')")
    ck('confirm at /confirm#t=...: confirms, and wipes the token', text(page, '#confirmMsg') == 'Email confirmed, Dusk! You can close this page.' and page.url == base + 'confirm'
       and len(supa.calls) == n0 + 1 and not W.bad and not W.csp(), (page.url, text(page, '#confirmMsg'), W.bad))
    ctx.close()

def main():
    httpd = serve.serve(0, quiet=True); port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = 'http://127.0.0.1:%d/' % port
    supa = Supa()
    with sync_playwright() as p:
        exe = os.environ.get('RM_CHROMIUM')
        browser = p.chromium.launch(**({'executable_path': exe} if exe else {}))
        for fn in (check_host, check_store, check_pages, check_forgot, check_reset, check_confirm):
            try: fn(browser, base, supa)
            except Exception as e: ck('%s ran to the end' % fn.__name__, False, traceback.format_exc()[-600:])
        ck('Supabase: nothing reached it (every call answered here), and no call nobody expected', not supa.stray, supa.stray)
        browser.close()
    httpd.shutdown()
    bad = [r for r in results if not r[1]]
    print('\n%d checks, %d failed. Screenshots: %s' % (len(results), len(bad), SHOTS))
    for r in bad: print('FAILED:', r[0], r[2])
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
