import asyncio, json, threading, http.server, functools, socketserver
from playwright.async_api import async_playwright
ROOT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/ios/build/RollModel/RollModel/Game'
SWIFT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/ios/src/HapticsBridge.swift'
src = open(SWIFT).read(); js = src.split('static let script = """')[1].split('"""')[0]
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=ROOT)); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required']) # the app's web view lets sound start without a tap
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        # what WKWebView provides: a message handler, then the bridge script at document start
        await ctx.add_init_script("window.__hap = []; window.__dev = []; window.webkit = { messageHandlers: { haptic: { postMessage: function (m) { window.__hap.push(m); } }, device: { postMessage: function (m) { window.__dev.push(m); } } } };")
        # DeviceBridge.startScript(): an iPhone 15 Pro, cool, not in Low Power Mode
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script(js)
        pg = await ctx.new_page(); errs=[]; reqs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text[:200]))
        pg.on('request', lambda r: reqs.append(r.url)); warns=[]; pg.on('console', lambda m: m.type=='warning' and warns.append(m.text[:200])); resp={}; pg.on('response', lambda r: resp.__setitem__(r.url.split('/')[-1], r.status))
        pg.set_default_timeout(180000); await pg.goto(f'http://127.0.0.1:{port}/index.html', timeout=240000); await pg.wait_for_function("!document.getElementById('menu').hidden && document.getElementById('boot').className.indexOf('gone') >= 0", polling=250, timeout=240000); await pg.wait_for_timeout(3000)
        st = await pg.evaluate("[document.compatMode, document.getElementById('boot').className, !document.getElementById('menu').hidden, document.fonts.check('30px \"Bowlby One\"'), document.fonts.check('800 16px Figtree'), typeof THREE, getComputedStyle(document.querySelector('.logo .tcard')).backgroundImage.slice(0, 22), document.querySelectorAll('#worlds .wcard, .gcard, [data-s]').length]")
        await pg.screenshot(path='ui/ios_bundle_menu.png')
        # the game's own buzz goes through navigator.vibrate: start a match (name card first) and check pulses reach the bridge
        await pg.tap('#homePlay', no_wait_after=True); await pg.wait_for_timeout(1500); await pg.tap('#startBtn', no_wait_after=True); await pg.wait_for_timeout(1500); await pg.tap('#nameOk', no_wait_after=True); await pg.wait_for_timeout(6000)
        hap = await pg.evaluate("(() => { const before = window.__hap.length; const r = navigator.vibrate([12, 40, 30]); navigator.vibrate(25); return { before, ret: r, msgs: window.__hap.slice(-2), own: Navigator.prototype.vibrate.toString().includes('postMessage') }; })()")
        ext = [u for u in reqs if not u.startswith(f'http://127.0.0.1:{port}/') and not u.startswith('data:')]
        gfx = await pg.evaluate("({ native: window.__NATIVE && window.__NATIVE.tier, awake: window.__dev.slice(-1)[0] })")
        print(json.dumps({'state': st, 'haptics': hap, 'device': gfx, 'external': ext[:5], 'requests': len(reqs), 'slime.pack': resp.get('slime.pack'), 'slimeWarn': [w for w in warns if 'slime' in w][:2], 'music': sorted(k for k in resp if k.endswith('.mp3'))}), errs[:4])
        await pg.screenshot(path='ui/ios_bundle_play.png'); await b.close()
asyncio.run(main()); srv.shutdown()
