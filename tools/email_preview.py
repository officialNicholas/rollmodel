"""email_preview.py [out dir]: pictures of the account emails (email/*.html) as an inbox would show them: a wide window and a phone,
light and dark, with sample values filled in. Pictures come from email/assets (as the website's /email/ folder will serve them)."""
import asyncio, os, sys, html
from playwright.async_api import async_playwright
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); EM = os.path.join(ROOT, 'email')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(EM, 'preview')
SAMPLE = {'username': 'Dusk_Painter', 'site': 'https://playrollmodel.com', 'support': 'support@playrollmodel.com', 'year': '2026',
          'link': 'https://playrollmodel.com/reset#t=3f9a1c07b2d84e6f9a0c1d2e3f4a5b6c', 'when': 'October 18, 2026 at 9:41 AM UTC'}
def fill(s): 
    for k, v in SAMPLE.items(): s = s.replace('{{' + k + '}}', html.escape(v))
    return s
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        for k in ['welcome', 'reset', 'changed']:
            for tag, w, scheme in [('wide', 680, 'light'), ('phone', 390, 'light'), ('phone_dark', 390, 'dark'), ('phone_font', 390, 'light')]:
                ctx = await b.new_context(viewport={'width': w, 'height': 900}, device_scale_factor=2, color_scheme=scheme)
                if tag != 'phone_font': await ctx.route('https://fonts.googleapis.com/**', lambda r: r.abort())  # (most inboxes don't load web fonts: show the fallback; phone_font is Apple Mail, which does)
                await ctx.route('**/email/*.png', lambda r: r.fulfill(path=os.path.join(EM, 'assets', r.request.url.rsplit('/', 1)[1])))
                pg = await ctx.new_page(); await pg.set_content(fill(open(os.path.join(EM, k + '.html')).read()), wait_until='load')
                await pg.screenshot(path=os.path.join(OUT, '%s_%s.png' % (k, tag)), full_page=True); await ctx.close()
        await b.close()
    print('previews in', OUT)
asyncio.run(main())
