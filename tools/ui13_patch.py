#!/usr/bin/env python3
"""Plates: the match banner and the tips arrive on a dark billboard with an ink emblem block, not on paper. On top of ui12_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui12_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CSS = '''
/* ===== plates: what matters mid-match comes in on a dark billboard, an ink block with an emblem on its left, a cream rim ===== */
.banner{left:0;right:0;top:24%;z-index:8;align-items:center;opacity:1;animation:none;text-align:left}
.banner.on,.banner.on.long{animation:none}
.banner .plate{position:relative;display:grid;grid-template-columns:auto minmax(0,1fr);align-items:stretch;min-height:84px;width:max-content;max-width:min(92vw,520px);background:#1E1828;border-radius:8px;box-shadow:0 0 0 3px #F4EEE3,7px 9px 0 rgba(0,0,0,.45),0 26px 40px rgba(0,0,0,.35);transform:rotate(-2deg) skewX(-5deg);overflow:hidden;opacity:0}
.banner .plate::before{content:"";position:absolute;inset:0;background:rgba(255,255,255,.06);-webkit-mask:url(art/m_splat2.webp) 6px 8px/54px 54px repeat,url(art/m_drip.webp) 34px -6px/36px 48px repeat;mask:url(art/m_splat2.webp) 6px 8px/54px 54px repeat,url(art/m_drip.webp) 34px -6px/36px 48px repeat;animation:platepat 6s linear infinite;pointer-events:none}
@keyframes platepat{to{-webkit-mask-position:60px 8px,88px -6px;mask-position:60px 8px,88px -6px}}
.banner .pem{position:relative;width:84px;display:grid;place-items:center;background:var(--ink);box-shadow:3px 0 0 rgba(0,0,0,.25)}
.banner .pem i{width:54px;height:54px;background:#FFF4E6;-webkit-mask:url(art/m_splat2.webp) center/contain no-repeat;mask:url(art/m_splat2.webp) center/contain no-repeat;transform:skewX(5deg) rotate(-10deg);filter:drop-shadow(2px 2px 0 rgba(0,0,0,.3))}
.banner .pem[data-k="drip"] i{-webkit-mask-image:url(art/m_drip.webp);mask-image:url(art/m_drip.webp);width:40px;height:56px}
.banner .pem[data-k="stroke"] i{-webkit-mask-image:url(art/m_stroke2.webp);mask-image:url(art/m_stroke2.webp);width:70px;height:40px}
.banner .pem[data-k="heat"]{background:#FF7A1E}
.banner .pem[data-k="rain"]{background:#2E9BFF}
.banner .ptxt{display:grid;align-content:center;gap:3px;padding:12px 22px 13px 18px;transform:skewX(5deg)}
#bannerBig{font:900 clamp(26px,7.5vw,40px)/.95 var(--font-head);font-style:italic;text-transform:uppercase;color:#fff;transform:none;text-shadow:.04em .04em 0 var(--black),.08em .08em 0 var(--ink);text-wrap:balance}
#bannerSmall{background:none;color:#F4EEE3;border:0;border-radius:0;padding:2px 0 0;font:800 12px/1.25 var(--font-ui);letter-spacing:.1em;text-transform:uppercase;opacity:.85;max-width:34ch}
.banner.on .plate{animation:platein 2.1s cubic-bezier(.2,1,.3,1) forwards}
.banner.on.long .plate{animation-duration:3.4s}
@keyframes platein{0%{opacity:0;transform:translateX(70%) rotate(-2deg) skewX(-5deg)}11%{opacity:1;transform:translateX(-3%) rotate(-2deg) skewX(-5deg)}17%{transform:translateX(0) rotate(-2deg) skewX(-5deg)}85%{opacity:1;transform:translateX(0) rotate(-2deg) skewX(-5deg)}100%{opacity:0;transform:translateX(-55%) rotate(-2deg) skewX(-5deg)}}
.hint{top:104px;z-index:8;justify-content:center}
.hint span{position:relative;max-width:min(92vw,440px);box-sizing:border-box;background:#1E1828;color:#F4EEE3;border:0;border-radius:6px;padding:10px 16px 11px 64px;box-shadow:0 0 0 2.5px #F4EEE3,5px 6px 0 rgba(0,0,0,.45);font:700 14px/1.35 var(--font-ui);text-align:left;transform:rotate(-1.5deg) translateY(-8px);overflow:hidden}
.hint span::before{content:"Tip";position:absolute;left:0;top:0;bottom:0;width:50px;display:grid;place-items:center;background:var(--ink);color:#fff;font:900 14px/1 var(--font-head);font-style:italic;text-transform:uppercase;letter-spacing:.06em;box-shadow:2px 0 0 rgba(0,0,0,.25)}
.hint.on span{transform:rotate(-1.5deg)}
@media (min-aspect-ratio:1/1){.banner{top:20%}.hint{top:70px}}
@media (prefers-reduced-motion:reduce){.banner .plate::before{animation:none}.banner.on .plate{animation:fadein .2s both;opacity:1}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]
rep('<div class="banner" id="banner" aria-live="polite"><p id="bannerBig"></p><p id="bannerSmall"></p></div>',
    '<div class="banner" id="banner" aria-live="polite"><div class="plate"><span class="pem" id="bannerEm" aria-hidden="true"><i></i></span><div class="ptxt"><p id="bannerBig"></p><p id="bannerSmall"></p></div></div></div>')
rep("function banner(big, small, long) { $('bannerBig').textContent = big; $('bannerSmall').textContent = small || ''; bannerEl.classList.toggle('long', !!long); restartCls(bannerEl, 'on'); }",
    "function banner(big, small, long) { $('bannerBig').textContent = big; $('bannerSmall').textContent = small || ''; bannerEl.classList.toggle('long', !!long); const em = $('bannerEm'); em.dataset.k = /rain/i.test(big) ? 'rain' : /heat/i.test(big) ? 'heat' : /paint it/i.test(big) ? 'stroke' : /giant|overtime|new item/i.test(big) ? 'splat' : 'drip'; restartCls(bannerEl, 'on'); }")
rep('<p class="ver">Version 82</p>', '<p class="ver">Version 83</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
