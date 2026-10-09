p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:80]); s=s.replace(a,b)
# results sheet docks to the right on wide screens, so the whole stage shows beside it
rep("@media (min-width:700px){.sheet{bottom:20px;border-bottom:3px solid var(--line);border-radius:28px;box-shadow:0 6px 0 var(--line),0 24px 48px rgba(6,2,16,.55)}}",
    "@media (min-width:700px){.sheet{bottom:20px;border-bottom:3px solid var(--line);border-radius:28px;box-shadow:0 6px 0 var(--line),0 24px 48px rgba(6,2,16,.55)}}\n@media (min-width:860px) and (min-aspect-ratio:1/1){.sheet{left:auto;right:clamp(24px,4vw,56px);top:50%;bottom:auto;transform:translateY(-50%);width:min(440px,38vw);max-height:calc(100% - 48px);animation-name:sheetside}}\n@keyframes sheetside{from{transform:translate(48px,-50%);opacity:0}}")
# tap prompt on the victory screen: a readable pill, gently pulsing
rep(".vtap{align-self:center;margin:14px 0 0;font:800 15px/1 var(--font-ui);color:var(--white);opacity:0;text-shadow:0 2px 0 var(--outline);animation:vtap 1.6s 1.9s ease-in-out infinite}\n@keyframes vtap{0%,100%{opacity:.35}50%{opacity:1}}",
    ".vtap{align-self:center;margin:14px 0 0;padding:8px 14px;border-radius:99px;background:rgba(18,10,36,.55);font:800 15px/1 var(--font-ui);color:var(--white);opacity:0;animation:vtap 1.6s 1.9s ease-in-out infinite}\n@keyframes vtap{0%,100%{opacity:.62}50%{opacity:1}}")
rep("outroOffY = 0, outroFrac = 1, outK = 0,", "outroOffY = 0, outroOffX = 0, outroSide = false, outroFrac = 1, outK = 0,")
rep("function measureOutro() { outroOffY = Math.max(0, (viewH - end.offsetTop) / 2); outroFrac = clamp(end.offsetTop / Math.max(1, viewH), 0.3, 1); }",
    "function measureOutro() {\n  // the stage is framed in the space the results leave: above them on a phone, beside them on a wide screen\n  outroSide = sideMQ.matches && end.offsetLeft > viewW * 0.35;\n  if (outroSide) { outroOffX = (viewW - end.offsetLeft) / 2; outroOffY = 0; outroFrac = clamp(end.offsetLeft / Math.max(1, viewW), 0.3, 1); }\n  else { outroOffX = 0; outroOffY = Math.max(0, (viewH - end.offsetTop) / 2); outroFrac = clamp(end.offsetTop / Math.max(1, viewH), 0.3, 1); }\n}")
rep("const sc = ARENA / 26.4 * Math.max(clamp(0.5 / (Math.tan(camera.fov * Math.PI / 360) * camera.aspect), 1, 1.7), clamp(0.62 / outroFrac, 1, 1.8)), fx",
    "const tf = Math.tan(camera.fov * Math.PI / 360), sc = ARENA / 26.4 * (outroSide ? clamp(0.62 / (tf * camera.aspect * outroFrac), 1, 1.8) * 1.04 : Math.max(clamp(0.5 / (tf * camera.aspect), 1, 1.7), clamp(0.62 / outroFrac, 1, 1.8))), fx")
rep("camera.setViewOffset(vw, vh, heroOff.x * heroK, heroOff.y * heroK + outroOffY * outK, vw, vh);",
    "camera.setViewOffset(vw, vh, heroOff.x * heroK + outroOffX * outK, heroOff.y * heroK + outroOffY * outK, vw, vh);")
open(p,'w').write(s); print('ok')
