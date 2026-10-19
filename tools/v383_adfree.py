"""v383: Get dabs' ad-free line becomes a gold foil plate: simply "Go ad-free" with any purchase.

- In place of the dark strip ("Any pack turns the ads off for good, and crafting is instant"): a gold foil plate in an ink outline, set a
  touch askew like a sticker on the paper, a light sweeping across it now and then, two sparkles, and a red stamp with a struck-out "AD"
  that hangs over its left edge. It reads "Any purchase" over "Go ad-free".
- Once a pack is bought: the stamp turns green with a tick, and it reads "Thanks for your support" over "Ad-free"."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

# the stamp: a scalloped seal, "AD" struck through (free players) or a tick (buyers)
SEAL = ('<svg class="dsseal" viewBox="-50 -50 100 100" aria-hidden="true"><path class="dssb" d="' + ' '.join(
    ('M' if i == 0 else 'L') + '%.1f %.1f' % (r * __import__('math').cos(i * 3.14159265 / 16), r * __import__('math').sin(i * 3.14159265 / 16))
    for i, r in ((i, 46 if i % 2 == 0 else 40) for i in range(32))) + 'Z" stroke="#171320" stroke-width="4" stroke-linejoin="round"/>'
    '<circle r="31" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2" stroke-dasharray="3 4"/>'
    '<g class="dsad"><text y="2" text-anchor="middle" dominant-baseline="central" font-family="Bowlby One, Arial Black, sans-serif" font-size="27" fill="#fff" stroke="#171320" stroke-width="5" paint-order="stroke">AD</text>'
    '<path d="M-25 21L25 -21" stroke="#171320" stroke-width="7.5" stroke-linecap="round"/><path d="M-25 21L25 -21" stroke="#FFE48A" stroke-width="3" stroke-linecap="round"/></g>'
    '<path class="dstick" d="M-17 1L-5 13L19 -13" fill="none" stroke="#171320" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>'
    '<path class="dstick" d="M-17 1L-5 13L19 -13" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def apply(s):
    s = rep(s, '      <p class="dsnoads" id="dsNoAds"></p>\n',
               '      <div class="dsnoads" id="dsNoAds">' + SEAL + '<div class="dsnat"><small id="dsNoAdsK">Any purchase</small><b id="dsNoAdsH">Go ad-free</b></div><i class="dsspark" aria-hidden="true"></i><i class="dsspark b" aria-hidden="true"></i></div>\n')
    s = rep(s, '.dsnoads{margin:0;padding:7px 10px;border-radius:10px;background:#171320;color:#F4EEE3;font:800 12.5px/1.3 var(--font-head);text-align:center}\n'
               '.dsnoads b{color:#7BE36A}\n',
               '/* (v383) Go ad-free: a gold foil plate, a little askew, with a stamp over its left edge */\n'
               '.dsnoads{position:relative;display:flex;align-items:center;min-height:58px;margin:6px 4px 2px 22px;padding:6px 16px 6px 52px;border:3px solid #171320;border-radius:14px;background:linear-gradient(115deg,#FFE48A 0,#F6C649 28%,#E9A82C 55%,#FFD86A 78%,#F3B73C 100%);box-shadow:inset 0 2px 0 rgba(255,255,255,.65),inset 0 -3px 0 rgba(150,90,10,.35),0 4px 0 #171320;rotate:-1.2deg;overflow:visible}\n'
               '.dsnoads::before{content:"";position:absolute;inset:0;border-radius:11px;background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.75) 47%,rgba(255,255,255,0) 58%) no-repeat;background-size:250% 100%;background-position:150% 0;animation:dsfoil 3.8s ease-in-out infinite;pointer-events:none}\n'
               '@keyframes dsfoil{0%,55%{background-position:150% 0}100%{background-position:-60% 0}}\n'
               '.dsseal{position:absolute;left:-26px;top:50%;width:70px;height:70px;translate:0 -50%;rotate:-12deg;filter:drop-shadow(0 3px 0 rgba(23,19,32,.9))}\n'
               '.dsseal .dssb{fill:#E5413A}.dsseal .dstick{display:none}\n'
               '.dsnoads.paid .dsseal .dssb{fill:#3FB54A}.dsnoads.paid .dsseal .dstick{display:inline}.dsnoads.paid .dsad{display:none}\n'
               '.dsnat{position:relative;display:grid;gap:1px;min-width:0}\n'
               '.dsnat small{font:900 11px/1 var(--font-head);letter-spacing:.14em;text-transform:uppercase;color:#7A4A06}\n'
               '.dsnat b{font:400 26px/1.02 var(--font-display);color:#fff;letter-spacing:.01em;text-shadow:0 3px 0 #171320,2px 0 0 #171320,-2px 0 0 #171320,0 -2px 0 #171320,2px 2px 0 #171320,-2px 2px 0 #171320,2px -2px 0 #171320,-2px -2px 0 #171320}\n'
               '.dsspark{position:absolute;right:16px;top:9px;width:14px;height:14px;background:#fff;clip-path:polygon(50% 0,62% 38%,100% 50%,62% 62%,50% 100%,38% 62%,0 50%,38% 38%);animation:dsspark 2.4s ease-in-out infinite;pointer-events:none}\n'
               '.dsspark.b{right:40px;top:auto;bottom:9px;width:9px;height:9px;animation-delay:-1.2s}\n'
               '@keyframes dsspark{0%,100%{scale:.3;opacity:0}50%{scale:1;opacity:1;rotate:45deg}}\n'
               '@media (prefers-reduced-motion:reduce){.dsnoads::before,.dsspark{animation:none}.dsspark{opacity:.8}}\n')
    s = rep(s, ".dsnoads{padding:5px 8px}", ".dsnoads{min-height:46px;padding-block:3px}.dsseal{width:56px;height:56px;left:-22px}.dsnat b{font-size:21px}")
    s = rep(s, "  $('dsNoAds').innerHTML = store.paid ? '<b>Ad-free.</b> Thanks for backing Roll Model!' : 'Any pack turns the ads off for good, <b>and crafting is instant</b>';",
               "  $('dsNoAds').classList.toggle('paid', !!store.paid); $('dsNoAdsK').textContent = store.paid ? 'Thanks for your support' : 'Any purchase'; $('dsNoAdsH').textContent = store.paid ? 'Ad-free' : 'Go ad-free'; // (v383)")
    return s
