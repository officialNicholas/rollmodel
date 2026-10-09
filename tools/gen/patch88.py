p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:80]); s=s.replace(a,b)
# 1. landscape phones: menu as a row, compact dock (placed after the desktop block so it wins)
rep("""  .dock{width:420px}
}
""", """  .dock{width:420px}
}
@media (max-height:520px) and (min-aspect-ratio:1/1){
  /* landscape phones: the logo beside the controls, all of it on one screen */
  .menu{flex-direction:row;align-items:center;justify-content:center;gap:clamp(16px,5vw,56px);padding:max(10px,env(safe-area-inset-top)) max(16px,env(safe-area-inset-right)) max(10px,env(safe-area-inset-bottom)) max(16px,env(safe-area-inset-left))}
  .logo{align-items:center;text-align:center}
  .logo .l1{font-size:min(44px,9.5vh)}
  .logo .l2{font-size:min(96px,19vh);margin-left:0}
  .dock{width:min(380px,50vw);gap:9px;padding:12px 14px}
  .nametag{margin-top:-30px;min-height:38px}
  .sw{height:40px}
  .seg button{min-height:34px}
  .btn.play{min-height:50px;font-size:26px}
  .chipbtn{min-height:34px}
}
""")
# 2. victory screen on landscape phones
rep("""@media (min-width:700px) and (min-aspect-ratio:1/1){
  .victory{padding:max(28px,env(safe-area-inset-top)) clamp(28px,5vw,64px) 28px}
  .vfoot{max-width:56%}
  .vtap{align-self:flex-start}
}""", """@media (min-width:700px) and (min-aspect-ratio:1/1),(max-height:520px) and (min-aspect-ratio:1/1){
  .victory{padding:max(28px,env(safe-area-inset-top)) clamp(28px,5vw,64px) 28px}
  .vfoot{max-width:56%}
  .vtap{align-self:flex-start}
}
@media (max-height:520px) and (min-aspect-ratio:1/1){
  .victory{padding:max(12px,env(safe-area-inset-top)) max(24px,env(safe-area-inset-right)) max(10px,env(safe-area-inset-bottom)) max(24px,env(safe-area-inset-left))}
  .vplace{font-size:min(132px,23vh)}
  .vplace.word{font-size:min(84px,15vh)}
  .vtag{font-size:15px;padding:6px 12px}
  .vsub{margin-top:8px;font-size:16px;padding:6px 12px}
  .vcards{margin-top:8px;gap:8px}
  .vcard{padding:3px 12px 3px 6px}
  .vtap{margin-top:8px}
}""")
# 3. results sheet on landscape phones: docked right, full height
rep("@keyframes sheetside{from{transform:translate(48px,-50%);opacity:0}}",
    "@keyframes sheetside{from{transform:translate(48px,-50%);opacity:0}}\n@media (max-height:520px) and (min-aspect-ratio:1/1){.sheet{left:auto;right:max(12px,env(safe-area-inset-right));top:max(10px,env(safe-area-inset-top));bottom:max(10px,env(safe-area-inset-bottom));transform:none;width:min(400px,50vw);max-height:none;gap:10px;padding:14px 14px 12px;border-bottom:3px solid var(--line);border-radius:24px;animation-name:sheetside2}.sheet .rtitle{font-size:30px}.sheet .btn.play{min-height:50px}}\n@keyframes sheetside2{from{transform:translateX(48px);opacity:0}}")
# JS: what counts as landscape for the victory shot, and when the results dock to the side
rep("land = viewW / viewH > 1.05 && viewW >= 700;", "land = vicLand();")
rep("land = W / Hh > 1.05 && W >= 700;", "land = vicLand();")
rep("const lines = []; for (const w of words)", "const lines = []; for (const w of words)")
rep("el.style.fontSize = clamp(Math.floor(100 * maxW / widest), 40, land ? 150 : 132) + 'px';",
    "el.style.fontSize = clamp(Math.floor(Math.min(100 * maxW / widest, viewH * 0.36 / (lines.length * 0.88))), 40, land ? 150 : 132) + 'px'; // fits across, and leaves room above and below on a short screen")
rep("function vicName(name) {", "const vicLand = () => viewW / viewH > 1.05 && (viewW >= 700 || viewH < 520);\nfunction vicName(name) {")
rep("sideMQ = window.matchMedia ? matchMedia('(min-width:860px) and (min-aspect-ratio:1/1)') : { matches: false };",
    "sideMQ = window.matchMedia ? matchMedia('(min-width:860px) and (min-aspect-ratio:1/1)') : { matches: false }, endSideMQ = window.matchMedia ? matchMedia('(min-width:860px) and (min-aspect-ratio:1/1),(max-height:520px) and (min-aspect-ratio:1/1)') : { matches: false };")
rep("outroSide = sideMQ.matches && end.offsetLeft > viewW * 0.35;", "outroSide = endSideMQ.matches && end.offsetLeft > viewW * 0.35;")
open(p,'w').write(s); print('ok')
