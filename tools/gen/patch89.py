p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:80]); s=s.replace(a,b)
rep("""  .menu{flex-direction:row;align-items:center;justify-content:center;gap:clamp(16px,5vw,56px);padding:max(10px,env(safe-area-inset-top)) max(16px,env(safe-area-inset-right)) max(10px,env(safe-area-inset-bottom)) max(16px,env(safe-area-inset-left))}
  .logo{align-items:center;text-align:center}
  .logo .l1{font-size:min(44px,9.5vh)}
  .logo .l2{font-size:min(96px,19vh);margin-left:0}
  .dock{width:min(380px,50vw);gap:9px;padding:12px 14px}""",
"""  .menu{flex-direction:row;align-items:center;justify-content:center;gap:clamp(12px,3vw,48px);padding:max(10px,env(safe-area-inset-top)) max(60px,calc(env(safe-area-inset-right) + 48px)) max(10px,env(safe-area-inset-bottom)) max(12px,env(safe-area-inset-left))}
  .logo{align-items:center;text-align:center}
  .logo .l1{font-size:min(44px,9.5vh,5.2vw)}
  .logo .l2{font-size:min(96px,19vh,8.5vw);margin-left:0}
  .dock{width:min(360px,44vw);gap:9px;padding:12px 14px}""")
rep("@media (max-height:520px) and (min-aspect-ratio:1/1){.sheet{left:auto;right:max(12px,env(safe-area-inset-right));",
    "@media (max-height:520px) and (min-aspect-ratio:1/1){.sheet{left:auto;right:max(60px,calc(env(safe-area-inset-right) + 48px));")
rep(".sheet .rtitle{font-size:30px}.sheet .btn.play{min-height:50px}}",
    ".sheet .rtitle{font-size:30px}.sheet .btn.play{min-height:50px}.sheet .ptitle{font-size:12px}.sheet .pchip{padding:7px 10px 7px 8px}.sheet .pchip b{font-size:28px}.sheet .stat{padding:6px 4px}.sheet .stat b{font-size:18px}.sheet .stat>span{margin-top:3px;font-size:11px}.sheet .row .btn{min-height:44px}}")
open(p,'w').write(s); print('ok')
