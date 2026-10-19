#!/usr/bin/env python3
"""Build Roll Model's website (site/) from the game, then check it.

  python3 tools/site_build.py             the Privacy Policy, Terms of Service and Credits pages from the game's own words (the DOCS
                                          in game/index.html), so the website and the game never disagree; the header and footer on
                                          every page; the values in site/js/config.js written into the pages (for anyone without
                                          JavaScript, and for share previews); the fonts and the emails' pictures copied in; the checks
  python3 tools/site_build.py --images    also remakes the pictures that come from the game (needs Pillow): the logo, the canvases,
                                          the stroke icons, Ol' Bloop, the icons (from the app icon) and the share picture
  python3 tools/site_build.py --dist DIR  and then copies what gets uploaded (all of site/ except dev/ and README.md) to DIR

Run it again whenever the game's terms or privacy policy change. The checks fail the build on: an em dash, anything inline
the Content-Security-Policy would block (scripts, styles, event handlers), a link or picture that points at nothing, a picture
without alt text or a size, an account page without noindex, or a _headers file whose policy isn't the one the site is built for.
The screenshots in site/img/shots were taken from the game with Playwright and are not remade here."""
import base64, html, io, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE, GAME = os.path.join(ROOT, 'site'), os.path.join(ROOT, 'game')
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self' "
       "https://nbemerxgukwwtrfgirfl.supabase.co; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
PAGES = ['index.html', 'privacy.html', 'terms.html', 'support.html', 'forgot.html', 'reset.html', 'confirm.html', '404.html']
NOINDEX = ['forgot.html', 'reset.html', 'confirm.html', '404.html']
DOC_PAGES = {'priv': 'privacy.html', 'tos': 'terms.html'}
FONTS = ['bowlby-one-latin-400-normal.woff2'] + ['figtree-latin-%d-normal.woff2' % w for w in (400, 600, 700, 800, 900)]
# the game's own art the site is dressed in (game/art/, copied to site/img/art/): the wall's chevrons and axolotls, the ink band, the
# card, the graph paper, the masking tape, the PLAY stroke, the splat, the picture frame, the gallery wall, the season's art
ART = ['lk_wall.webp', 'sg_ink.webp', 'sg_card.webp', 'm_paperbg.webp', 'm_tape1.webp', 'm_tape2.webp', 'm_tape3.webp', 'm_stroke.webp', 'm_splat.webp',
       'm_frame.webp', 'm_wall.webp', 'm_dot.webp']
problems, notes = [], []

def read(p): return open(p, encoding='utf8').read()
def write(p, s):
    if os.path.exists(p) and read(p) == s: return False
    open(p, 'w', encoding='utf8').write(s); return True

# ---------------------------------------------------------------- the game's words
def js_string(s, i):
    """The JavaScript string literal starting at s[i] (single or double quotes): its value, and the index just after it."""
    q = s[i]; assert q in '\'"', s[i:i + 40]; i += 1; out = []
    while True:
        c = s[i]
        if c == '\\':
            n = s[i + 1]
            if n == 'u' and s[i + 2] == '{': j = s.index('}', i); out.append(chr(int(s[i + 3:j], 16))); i = j + 1
            elif n == 'u': out.append(chr(int(s[i + 2:i + 6], 16))); i += 6
            elif n == 'x': out.append(chr(int(s[i + 2:i + 4], 16))); i += 4
            elif n == '\n': i += 2
            else: out.append({'n': '\n', 't': '\t', 'r': '\r', '0': '\0', 'b': '\b', 'f': '\f', 'v': '\v'}.get(n, n)); i += 2
        elif c == q: return ''.join(out), i + 1
        elif c == '\n': raise ValueError('unterminated string')
        else: out.append(c); i += 1

def game_docs(src):
    """The DOCS object in the game: {key: (title, html)}."""
    k = src.index('const DOCS = {'); end = src.index('\n};', k); block = src[k:end]
    docs = {}
    for m in re.finditer(r'\n\s*(\w+): \[', block):
        i = m.end(); title, i = js_string(block, i)
        i = block.index(',', i) + 1
        while block[i] in ' \t\n': i += 1
        body, i = js_string(block, i)
        docs[m.group(1)] = (title, body)
    for key in DOC_PAGES: assert key in docs, 'the game has no %r doc any more' % key
    return docs

def doc_html(key, title, body):
    """A doc page's words: the game's own, with its sections as h2 (the page's title is the h1), and a few notes for the website
    around them, set apart so they're never read as part of the policy."""
    body = re.sub(r'<(/?)h3>', r'<\1h2>', body)
    extra = ''
    if key == 'priv':
        # in the game a button follows "You can turn them off here."; on the website, say where it is
        m = re.search(r'(<p id="statsP">.*?</p>)', body)
        if m: body = body.replace(m.group(1), m.group(1) + '<p class="note"><b>Where’s the switch?</b>In the game: <span class="path">Settings › Privacy Policy</span>, then Turn off play stats.</p>')
        else: notes.append('privacy: the game\'s play stats paragraph (id="statsP") has gone, so the note on where its switch is was left out')
        extra = ('<section class="aside" aria-labelledby="site-note"><h2 id="site-note">This website</h2>'
                 '<p>This website has no cookies, ads, analytics or trackers, and loads nothing from anyone else. The forgot password, reset '
                 'password and confirm email pages send what you type straight to our sign-in provider, Supabase, and keep nothing in your browser.</p></section>')
    if key == 'cred':
        extra = ('<section class="aside" aria-labelledby="site-note"><h2 id="site-note">This website</h2>'
                 '<p>Set in Bowlby One and Figtree, under the SIL Open Font License (<a href="fonts/BowlbyOne-OFL.txt">Bowlby One</a>, '
                 '<a href="fonts/Figtree-OFL.txt">Figtree</a>). The screenshots are from the game.</p></section>')
    head = ('<header class="doc-head"><div class="ban kc-aqua"><p class="kick">Roll Model</p><h1>%s</h1><i class="flag" aria-hidden="true"></i></div><p>The same words as in the game, under Settings › %s.</p></header>'
            % (html.escape(title), html.escape(title)))
    return '\n      ' + head + '\n      <div class="prose">' + body + '</div>' + ('\n      ' + extra if extra else '') + '\n      '

# ---------------------------------------------------------------- blocks shared between pages
def get_block(s, name):
    m = re.search(r'<!-- %s -->\n(.*?)<!-- /%s -->' % (re.escape(name), re.escape(name)), s, re.S)
    return m.group(1) if m else None

def put_block(s, name, inner):
    pat = re.compile(r'(<!-- %s -->\n)(.*?)(<!-- /%s -->)' % (re.escape(name), re.escape(name)), re.S)
    assert pat.search(s), 'no <!-- %s --> block' % name
    return pat.sub(lambda m: m.group(1) + inner + m.group(3), s)

def put_all_blocks(s, name, inner):
    pat = re.compile(r'(<!-- %s -->\n)(.*?)(\s*<!-- /%s -->)' % (re.escape(name), re.escape(name)), re.S)
    return pat.sub(lambda m: m.group(1) + inner + m.group(3), s)

def rootify(s):
    """For 404.html, which is served at any depth: links and pictures from the site's root."""
    def fix(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r'^(/|#|[a-z]+:)', url): return m.group(0)
        return '%s="/%s"' % (attr, '' if url in ('./', '.') else url)
    return re.sub(r'\b(href|src)="([^"]*)"', fix, s)

def config():
    src = read(os.path.join(SITE, 'js', 'config.js'))
    c = dict(re.findall(r"^\s*([A-Z_]+):\s*'([^']*)'", src, re.M))
    for k in ('SUPABASE_URL', 'SUPABASE_KEY', 'SUPPORT_EMAIL', 'APP_STORE_URL', 'SITE_URL'): assert k in c, 'js/config.js has no ' + k
    assert re.match(r'^https://[a-z0-9]+\.supabase\.co$', c['SUPABASE_URL']), c['SUPABASE_URL']
    assert re.match(r'^[^\s@<>"]+@[^\s@<>"]+\.[a-z]{2,}$', c['SUPPORT_EMAIL']), c['SUPPORT_EMAIL']
    assert c['APP_STORE_URL'] == '' or re.match(r'^https://apps\.apple\.com/[^\s"<>]+$', c['APP_STORE_URL']), 'APP_STORE_URL: an https://apps.apple.com/ link, or empty'
    assert c['SITE_URL'] == '' or re.match(r'^https://[a-z0-9.-]+$', c['SITE_URL']), 'SITE_URL: https://the.domain with no slash at the end, or empty'
    return c

def store_button(url):
    """The App Store button, the lobby's PLAY: a stroke of red paint (css .splash). A link once there is one, else "Coming soon"."""
    ico = '<svg class="store-ico" aria-hidden="true" focusable="false"><use href="#phone-ico"/></svg>'
    if url:
        return '<a class="splash store" data-config="appstore" href="%s">%s<span class="store-txt"><span class="store-small">Download on the</span><span class="store-big">App Store</span></span></a>' % (html.escape(url), ico)
    return '<span class="splash store is-soon" data-config="appstore">%s<span class="store-txt"><span class="store-small">Coming soon to the</span><span class="store-big">App Store</span></span></span>' % ico

def share_tags(page, s, site_url):
    title = html.unescape(re.search(r'<title>(.*?)</title>', s).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)">', s).group(1))
    e = lambda v: html.escape(v, quote=True)
    img = (site_url + '/img/og.jpg') if site_url else 'img/og.jpg'
    t = ['<meta property="og:type" content="website">', '<meta property="og:site_name" content="Roll Model">',
         '<meta property="og:title" content="%s">' % e(title), '<meta property="og:description" content="%s">' % e(desc),
         '<meta property="og:image" content="%s">' % e(img), '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
         '<meta property="og:image:alt" content="The Roll Model logo, with Dusk the axolotl in the game on a phone.">',
         '<meta name="twitter:card" content="summary_large_image">']
    if site_url:
        url = site_url + '/' + ('' if page == 'index.html' else page[:-5])
        t += ['<meta property="og:url" content="%s">' % e(url), '<link rel="canonical" href="%s">' % e(url)]
    return ''.join(x + '\n' for x in t)

def build_pages():
    c = config()
    src = read(os.path.join(GAME, 'index.html'))
    docs = game_docs(src)
    index = read(os.path.join(SITE, 'index.html'))
    footer = get_block(index, 'footer'); assert footer, 'index.html has no footer block'
    header = get_block(read(os.path.join(SITE, 'support.html')), 'header'); assert header, 'support.html has no header block'
    changed = []
    for page in PAGES:
        p = os.path.join(SITE, page); s = read(p)
        m = re.search(r'<!-- doc:(\w+) -->\n?(.*?)<!-- /doc -->', s, re.S)
        if m:
            key = m.group(1); title, body = docs[key]
            s = s[:m.start()] + '<!-- doc:%s -->' % key + doc_html(key, title, body) + '<!-- /doc -->' + s[m.end():]
        if page != 'index.html':
            if page != 'support.html':
                h = header.replace(' aria-current="page"', '')
                h = re.sub(r'(<a [^>]*href="%s")' % re.escape(page), r'\1 aria-current="page"', h)
                s = put_block(s, 'header', h)
            s = put_block(s, 'footer', footer)
        if '<!-- share -->' in s: s = put_block(s, 'share', share_tags(page, s, c['SITE_URL']))
        s = put_all_blocks(s, 'appstore', '        ' + store_button(c['APP_STORE_URL']))
        mail = c['SUPPORT_EMAIL']
        s = re.sub(r'(<a [^>]*data-config="email"[^>]*href=")mailto:[^"]*("[^>]*>)[^<]*(</a>)', lambda m: m.group(1) + 'mailto:' + mail + m.group(2) + mail + m.group(3), s)
        s = re.sub(r'(<span data-config="email">)[^<]*(</span>)', lambda m: m.group(1) + mail + m.group(2), s)
        if page == '404.html': s = rootify(s)
        if write(p, s): changed.append(page)
    # the fonts (the game's own, from the iOS app) and their licenses, and the pictures the emails show (site/email/)
    for f in FONTS: copy(os.path.join(ROOT, 'ios', 'shared', 'fonts', f), os.path.join(SITE, 'fonts', f), changed)
    for f in ('BowlbyOne-OFL.txt', 'Figtree-OFL.txt'): copy(os.path.join(ROOT, 'ios', 'shared', 'licenses', f), os.path.join(SITE, 'fonts', f), changed)
    for f in ('logo.png', 'icon.png'): copy(os.path.join(ROOT, 'email', 'assets', f), os.path.join(SITE, 'email', f), changed)
    for f in ART: copy(os.path.join(GAME, 'art', f), os.path.join(SITE, 'img', 'art', f), changed)
    return changed

def copy(a, b, changed):
    os.makedirs(os.path.dirname(b), exist_ok=True)
    if os.path.exists(b) and open(a, 'rb').read() == open(b, 'rb').read(): return
    shutil.copyfile(a, b); changed.append(os.path.relpath(b, SITE))

# ---------------------------------------------------------------- pictures from the game (--images)
def build_images():
    from PIL import Image
    src = read(os.path.join(GAME, 'index.html')); img = os.path.join(SITE, 'img'); made = []
    def save(im, name, **kw):
        p = os.path.join(img, name); os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p, **kw); made.append('img/' + name)
    def raw(name, b): p = os.path.join(img, name); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'wb').write(b); made.append('img/' + name)
    # the logo: the game's title card (--tcard), as it is, and half size
    b = base64.b64decode(re.search(r'--tcard:url\("data:image/webp;base64,([A-Za-z0-9+/=]+)"\)', src).group(1)); raw('logo-1100.webp', b)
    logo = Image.open(io.BytesIO(b)).convert('RGBA'); assert logo.size == (1100, 771), logo.size
    save(logo.resize((560, 393), Image.LANCZOS), 'logo-560.webp', quality=88, method=6)
    save(logo.resize((800, 561), Image.LANCZOS), 'logo-800.webp', quality=86, method=6)
    # the canvases: the pictures on the game's canvas picker
    for kind, key, b64 in re.findall(r'<button class="(world|stg)" type="button" data-s="(\w+)">(?:<span class="s?fr(?:ame)?">)<img class="art" src="data:image/webp;base64,([A-Za-z0-9+/=]+)"', src):
        if key in ('island', 'blank', 'sewer', 'raft', 'crypt', 'cathedral', 'manor'): raw('canvas/%s.webp' % key, base64.b64decode(b64))
    # the strokes: the game's painted icons
    for key in ('rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets', 'roller', 'turret', 'trap', 'whirl', 'boom'):
        m = re.search(r"(?:\b%s: |ST_IMG\.%s = )'data:image/webp;base64,([A-Za-z0-9+/=]+)'" % (key, key), src)
        save(Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGBA').resize((160, 160), Image.LANCZOS), 'strokes/%s.webp' % key, quality=86, method=6)
    # Ol' Bloop
    # (the website's own drawing of him, cut out: tools/assets/ol_bloop.webp)
    bl = Image.open(os.path.join(ROOT, 'tools', 'assets', 'ol_bloop.webp')).convert('RGBA')
    save(bl.resize((440, round(bl.height * 440 / bl.width)), Image.LANCZOS), 'bloop.webp', quality=86, method=6)
    # the icons, from the app's icon: the tab's icon, the home screen's, and the one in the header and footer
    icon = Image.open(os.path.join(ROOT, 'ios', 'RollModel', 'RollModel', 'Assets.xcassets', 'AppIcon.appiconset', 'AppIcon-1024.png')).convert('RGB')
    icon.resize((180, 180), Image.LANCZOS).save(os.path.join(SITE, 'apple-touch-icon.png'), optimize=True); made.append('apple-touch-icon.png')
    icon.save(os.path.join(SITE, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)]); made.append('favicon.ico')
    save(icon.resize((192, 192), Image.LANCZOS), 'icon-192.png', optimize=True)
    save(icon.resize((96, 96), Image.LANCZOS), 'icon-96.webp', quality=88, method=6)
    # the share picture (1200 x 630): the logo and a line on the left, the game on two phones on the right, on paper with a splat
    save(share_picture(logo), 'og.jpg', quality=86, optimize=True, progressive=True)
    return made

def splat_shape(seed, cx, cy, r, lobes, n=360):
    """A paint splat: a wobbly round body with arms that end in round drops, and a few drops flung clear. Its outline (a list of
    points) and its drops (circles: x, y, radius)."""
    import math, random
    rnd = random.Random(seed); arms = []
    for k in range(lobes):
        a = 2 * math.pi * k / lobes + rnd.uniform(-.22, .22)
        arms.append((a, r * rnd.uniform(.28, .62), rnd.uniform(.09, .15)))
    body = []
    for i in range(n):
        t = 2 * math.pi * i / n
        rr = r * (1 + .035 * math.sin(3 * t + seed) + .025 * math.sin(7 * t + 2 * seed))
        for a, ln, w in arms:
            dt = math.atan2(math.sin(t - a), math.cos(t - a)); rr += ln * math.exp(-(dt / w) ** 2)
        body.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    drops = []
    for a, ln, w in arms:  # each arm ends in a drop a little wider than the arm
        dr = r + ln * .92; drops.append((cx + dr * math.cos(a), cy + dr * math.sin(a), max(4.0, w * r * .62)))
    for k in range(lobes):  # and a few flung clear
        a = rnd.uniform(0, 2 * math.pi); dist = r * rnd.uniform(1.62, 1.9)
        drops.append((cx + dist * math.cos(a), cy + dist * math.sin(a), r * rnd.uniform(.035, .075)))
    return body, drops

def share_picture(logo):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630; S = 2  # drawn at twice the size, then scaled down (smooth edges)
    im = Image.new('RGB', (W * S, H * S), '#F4EEE3'); d = ImageDraw.Draw(im)
    body, drops = splat_shape(7, 905 * S, 318 * S, 205 * S, 9)
    d.polygon(body, fill='#E3122F')
    for x, y, s in drops: d.ellipse((x - s, y - s, x + s, y + s), fill='#E3122F')
    def phone(shot, w):
        sc = Image.open(os.path.join(SITE, 'img', 'shots', shot)).convert('RGB'); h = round(w * sc.height / sc.width)
        sc = sc.resize((w, h), Image.LANCZOS); pad = round(w * .035)
        fr = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); fd = ImageDraw.Draw(fr)
        fd.rounded_rectangle((0, 0, fr.width - 1, fr.height - 1), radius=round(w * .17), fill='#0E0B14')
        mask = Image.new('L', (w, h), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=round(w * .14), fill=255)
        fr.paste(sc, (pad, pad), mask)
        isl = (round(fr.width * .35), round(w * .06), round(fr.width * .65), round(w * .06 + w * .085)); fd.rounded_rectangle(isl, radius=99, fill='#0E0B14')
        return fr
    def place(fr, angle, x, y):
        r = fr.rotate(angle, resample=Image.BICUBIC, expand=True)
        sh = Image.new('RGBA', r.size, (0, 0, 0, 0)); sh.paste((23, 19, 32, 255), (0, 0), r.split()[3])
        im.paste(sh, (x, y + 14 * S), sh); im.paste(r, (x, y), r)
    place(phone('victory-720.webp', 220 * S), 8, 735 * S, 40 * S)
    place(phone('lobby-720.webp', 236 * S), -5, 905 * S, 70 * S)
    lw = 560 * S; lg = logo.resize((lw, round(lw * logo.height / logo.width)), Image.LANCZOS)
    im.paste(lg, (52 * S, 38 * S), lg)
    font = ImageFont.truetype(os.path.join(SITE, 'fonts', 'bowlby-one-latin-400-normal.woff2'), 44 * S)
    ui = ImageFont.truetype(os.path.join(SITE, 'fonts', 'figtree-latin-800-normal.woff2'), 25 * S)
    d = ImageDraw.Draw(im)
    d.text((84 * S, 436 * S), 'Roll it. Splat it.', font=font, fill='#171320')
    d.text((84 * S, 490 * S), 'Own the canvas!', font=font, fill='#E3122F')
    tag = 'COMING SOON FOR IPHONE'; tw = d.textlength(tag, font=ui); x0, y0 = 98 * S, 568 * S
    d.rounded_rectangle((x0 - 14 * S, y0 - 9 * S, x0 + tw + 14 * S, y0 + 35 * S), radius=10 * S, fill='#171320')
    d.text((x0, y0), tag, font=ui, fill='#CBE45A')
    return im.resize((W, H), Image.LANCZOS)

# ---------------------------------------------------------------- the checks
class Doc:
    def __init__(self, page):
        self.page, self.path = page, os.path.join(SITE, page); self.s = read(self.path)
        self.ids = set(re.findall(r'\bid="([^"]+)"', self.s))

def resolve(page, url):
    """The file a link on page points at (and its #fragment), or None for anything that isn't the site's."""
    if re.match(r'^[a-z][a-z0-9+.-]*:', url, re.I) or url.startswith('//'): return None
    url, _, frag = url.partition('#'); url = url.split('?')[0]
    if url == '': return page, frag
    base = '' if url.startswith('/') else os.path.dirname(page)
    p = os.path.normpath(os.path.join(base, url.lstrip('/'))).replace(os.sep, '/')
    if p in ('.', ''): p = 'index.html'
    if url.endswith('/') and p != 'index.html': p += '/index.html'
    if not os.path.splitext(p)[1] and os.path.exists(os.path.join(SITE, p + '.html')): p += '.html'  # (the host's pretty addresses)
    return p, frag

def check():
    docs = {p: Doc(p) for p in PAGES}
    used = set(); site_url = config()['SITE_URL']
    for p, d in docs.items():
        s = d.s
        if '<html lang="en">' not in s: problems.append('%s: no <html lang="en">' % p)
        if len(re.findall(r'<h1[\s>]', s)) != 1: problems.append('%s: needs exactly one h1' % p)
        for tag in ('<title>', '<meta name="description"', '<meta name="viewport"', '<meta charset="utf-8">'):
            if tag not in s: problems.append('%s: no %s' % (p, tag))
        if (p in NOINDEX) != ('<meta name="robots" content="noindex">' in s): problems.append('%s: noindex should be %s' % (p, p in NOINDEX))
        # what the Content-Security-Policy would block: inline scripts and styles, event handlers, javascript: links
        for m in re.finditer(r'<script\b([^>]*)>(.*?)</script>', s, re.S):
            if 'src=' not in m.group(1) or m.group(2).strip(): problems.append('%s: an inline script' % p)
        if re.search(r'<style[\s>]', s): problems.append('%s: a <style> element' % p)
        if re.search(r'\sstyle\s*=', s): problems.append('%s: a style attribute' % p)
        if re.search(r'\son[a-z]+\s*=', s, re.I): problems.append('%s: an inline event handler' % p)
        if 'javascript:' in s.lower(): problems.append('%s: a javascript: link' % p)
        for m in re.finditer(r'<img\b([^>]*)>', s):
            a = m.group(1)
            for need in ('alt=', 'width=', 'height='):
                if need not in a: problems.append('%s: a picture without %s %s' % (p, need[:-1], a[:90]))
        # every link and picture points at something
        urls = re.findall(r'\b(?:href|src)="([^"]*)"', s)
        for ss in re.findall(r'\bsrcset="([^"]*)"', s): urls += [x.strip().split(' ')[0] for x in ss.split(',')]
        for u in urls:
            if u.startswith('http') and not u.startswith('https://apps.apple.com/') and not (site_url and u.startswith(site_url)):
                problems.append('%s: points off the site: %s' % (p, u))
            r = resolve(p, u)
            if not r: continue
            f, frag = r; used.add(f)
            if not os.path.isfile(os.path.join(SITE, f)): problems.append('%s: %s points at nothing' % (p, u)); continue
            if frag and f.endswith('.html') and frag not in (docs[f].ids if f in docs else Doc(f).ids): problems.append('%s: %s has no #%s' % (p, f, frag))
    css = read(os.path.join(SITE, 'css', 'site.css'))
    for u in re.findall(r'url\(([^)]+)\)', css):
        u = u.strip('"\''); f = os.path.normpath(os.path.join('css', u)).replace(os.sep, '/'); used.add(f)
        if not os.path.isfile(os.path.join(SITE, f)): problems.append('site.css: %s points at nothing' % u)
    # the words: no em dashes (or en dashes) anywhere on the site
    for dirpath, dirs, files in os.walk(SITE):
        if os.path.relpath(dirpath, SITE).split(os.sep)[0] in ('fonts', 'dev'): continue
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.txt', '.svg')) or f == '_headers':
                t = read(os.path.join(dirpath, f))
                for bad in (chr(0x2014), chr(0x2013), '&mdash;', '&ndash;', '&#8212;', '&#8211;', '&#x2014;', '&#x2013;'):
                    if bad in t: problems.append('%s: an em or en dash (%r)' % (os.path.relpath(os.path.join(dirpath, f), SITE), bad))
    # the headers: the policy the site is built for, and the rest of the security headers
    h = read(os.path.join(SITE, '_headers'))
    if 'Content-Security-Policy: ' + CSP + '\n' not in h: problems.append('_headers: the Content-Security-Policy isn\'t the expected one')
    for need in ('X-Content-Type-Options: nosniff', 'Referrer-Policy: no-referrer', 'X-Frame-Options: DENY', 'Strict-Transport-Security: max-age=', 'Permissions-Policy: '):
        if need not in h: problems.append('_headers: no ' + need)
    # pictures nothing uses (a note, not a failure)
    for dirpath, dirs, files in os.walk(os.path.join(SITE, 'img')):
        for f in files:
            rel = os.path.relpath(os.path.join(dirpath, f), SITE).replace(os.sep, '/')
            if rel not in used and rel != 'img/og.jpg': notes.append('not used: ' + rel)

def dist(out):
    out = os.path.abspath(out)
    if out == SITE or out.startswith(SITE + os.sep) or SITE.startswith(out + os.sep): sys.exit('--dist: pick a folder outside site/')
    if os.path.exists(out):  # (only ever replaces an empty folder, or an earlier copy of the site)
        if not os.path.isdir(out) or (os.listdir(out) and not all(os.path.exists(os.path.join(out, f)) for f in ('_headers', 'index.html', 'privacy.html'))):
            sys.exit('--dist: %s is already there and isn\'t an earlier copy of the site; pick a new or empty folder' % out)
        shutil.rmtree(out)
    shutil.copytree(SITE, out, ignore=lambda d, names: [n for n in names if (d == SITE and n in ('dev', 'README.md')) or n in ('.DS_Store', '__pycache__')])
    return out

if __name__ == '__main__':
    args = sys.argv[1:]
    if '--images' in args: print('pictures:', ', '.join(build_images()))
    changed = build_pages(); print('pages:', ', '.join(changed) if changed else 'no changes')
    check()
    for n in notes: print('note:', n)
    if problems:
        for pr in problems: print('PROBLEM:', pr)
        sys.exit('%d problem(s)' % len(problems))
    if '--dist' in args: print('copied to', dist(args[args.index('--dist') + 1]))
    print('ok')
