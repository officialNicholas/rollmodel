import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# the victory poses update before the blobs are drawn
rep("  if (vic) vicFrame(rdt);\n  // camera\n  if (state === 'menu') {", "  // camera\n  if (state === 'menu') {")
rep("""function visuals(dt, rdt) {
  const ke = 1 - Math.exp(-dt * 10),""", """function visuals(dt, rdt) {
  if (vic) vicFrame(rdt);
  const ke = 1 - Math.exp(-dt * 10),""")

# ---------- the canvas after the victory screen: the camera circles high over it, framed above the results ----------
rep("let keyL = false, keyR = false, kbCharge = false, deathReason = null, outro = false, outroAge = 0, celebrating = false, endInfo = null;",
    "let keyL = false, keyR = false, kbCharge = false, deathReason = null, outro = false, outroAge = 0, outroT = 0, outroOffY = 0, outK = 0, celebrating = false, endInfo = null;")
rep("    if (state === 'dead' && outro) { const fx = Math.sin(camYaw), fz = Math.cos(camYaw), cx = P.x * 0.3, cz = P.z * 0.3; dPos.set(cx - fx * 28, 40, cz - fz * 28); dLook.set(cx + fx * 4, -14, cz + fz * 4); }",
    "    if (state === 'dead' && outro) { outroT += rdt; camYaw += rdt * 0.07; const sc = ARENA / 26.4, fx = Math.sin(camYaw), fz = Math.cos(camYaw); dPos.set(-fx * 31 * sc, 37 * sc, -fz * 31 * sc); dLook.set(fx * 3 * sc, -12 * sc, fz * 3 * sc); }")
rep("""  if (heroK > 0.003) { const vw = viewW, vh = viewH; camera.setViewOffset(vw, vh, heroOff.x * heroK, heroOff.y * heroK, vw, vh); }""",
    """  outK += ((state === 'dead' && outro && !end.hidden ? 1 : 0) - outK) * (1 - Math.exp(-rdt * 2.5));
  if (heroK > 0.003 || outK > 0.003) { const vw = viewW, vh = viewH; camera.setViewOffset(vw, vh, heroOff.x * heroK, heroOff.y * heroK + outroOffY * outK, vw, vh); }""")

# ---------- a compact results sheet: the stage is the painting now ----------
rep("""    <h2 class="rtitle" id="endTitle">You win!</h2>
    <div class="endgrid">
      <figure class="frame" id="frame">
        <div class="wood"><img id="paintImg" alt="Top view of the canvas you painted this match"></div>
        <figcaption class="placard"><b id="pTitle">Nocturne in Crimson No. 1</b><span id="pMeta">Blood on canvas</span></figcaption>
      </figure>
      <div class="scores">""", """    <h2 class="rtitle" id="endTitle">You win!</h2>
    <p class="ptitle"><b id="pTitle">Nocturne in Crimson No. 1</b><span id="pMeta">Blood on canvas</span></p>
    <div class="endgrid">
      <div class="scores">""")
rep("""        <span class="pill" id="endPill" hidden>New best</span>
      </div>
    </div>""", """      </div>
    </div>""")
rep(".endgrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px;align-items:center}",
    """.endgrid{display:block}
.ptitle{margin:-6px 0 0;display:flex;flex-wrap:wrap;justify-content:center;gap:2px 8px;text-align:center;font-size:13px;line-height:1.3}
.ptitle b{font-weight:800;color:var(--bone);font-style:italic}
.ptitle span{font-weight:700;color:var(--muted)}""")
rep(".scores{display:grid;gap:12px;align-content:center}", ".scores{display:grid;grid-template-columns:repeat(auto-fit,minmax(0,1fr));gap:10px}")
rep(".scores:has(#chipCpu2:not([hidden])) .pchip{padding-top:7px;padding-bottom:7px}\n.scores:has(#chipCpu2:not([hidden])) .pchip b{font-size:clamp(24px,7vw,30px)}",
    ".scores:has(#chipCpu2:not([hidden])) .pchip{grid-template-columns:10px 1fr;gap:9px;padding:9px 9px 9px 8px}\n.scores:has(#chipCpu2:not([hidden])) .pchip b{font-size:clamp(24px,7vw,30px)}")
rep(".pchip span{display:block;margin-top:5px;font:700 13px/1.1 var(--font-ui);color:var(--muted)}", ".pchip span{display:block;margin-top:5px;font:700 13px/1.1 var(--font-ui);color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n.pchip>div{min-width:0}")
# fill the sheet without the old painting snapshot, with names, and frame the stage above it
rep("""  $('endPill').hidden = !endInfo.newBest;
  $('frame').hidden = !img; if (img) $('paintImg').src = img;
""", "  paintName();\n")
rep("""  end.dataset.next = '';
  end.hidden = false;
  setTimeout(() => $('endBtn').focus({ preventScroll: true }), 30);
}""", """  end.dataset.next = '';
  end.hidden = false; measureOutro();
  setTimeout(() => $('endBtn').focus({ preventScroll: true }), 30);
}
function measureOutro() { outroOffY = Math.max(0, (viewH - end.offsetTop) / 2); }
window.addEventListener('resize', () => { if (!end.hidden) measureOutro(); });""")
# the snapshot isn't needed any more (the stage itself is shown), which also saves a stall at the buzzer
rep("endImg = null; try { endImg = snapshotPainting(); } catch (e) { endImg = null; } startVictory();", "startVictory();")
rep("abortVictory(); runId++;", "abortVictory(); outK = 0; runId++;")
open(F, 'w').write(s)
print('ok')
