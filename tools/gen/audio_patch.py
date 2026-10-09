# The drum kit and the reverbs are synthesized sample by sample (12 jobs, up to ~60 ms each). They used to start on the first tap,
# which is often Play, so the opening seconds of a match hitched. Now they're made while the menu is up, before any tap (an AudioBuffer
# doesn't need the audio context), and the queue never runs a job during active play.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

rep("  let MB = {}, SM = {}, SC = [], ECHO = [], echoBpm = 116;",
    """  let MB = {}, SM = {}, SC = [], ECHO = [], echoBpm = 116;
  // sounds can be synthesized before there's an audio context (at a standard rate; playback resamples if the phone differs)
  const PRE_SR = 48000, PRE_IR = {}; let kitGo = false;
  const SR = () => ctx ? ctx.sampleRate : PRE_SR, newBuf = (ch, n, sr) => ctx ? ctx.createBuffer(ch, n, sr) : new AudioBuffer({ numberOfChannels: ch, length: n, sampleRate: sr });""")
rep("    const sr = ctx.sampleRate, n = Math.floor(sr * sec), b = ctx.createBuffer(2, n, sr);\n    for (let c = 0; c < 2; c++) {\n      const d = b.getChannelData(c); let lp = 0;",
    "    const sr = SR(), n = Math.floor(sr * sec), b = newBuf(2, n, sr);\n    for (let c = 0; c < 2; c++) {\n      const d = b.getChannelData(c); let lp = 0;")
rep("    const sr = ctx.sampleRate, n = Math.floor(sr * sec), b = ctx.createBuffer(2, n, sr), pre = Math.floor(sr * 0.018);",
    "    const sr = SR(), n = Math.floor(sr * sec), b = newBuf(2, n, sr), pre = Math.floor(sr * 0.018);")
rep("    const sr = ctx.sampleRate, NT = new Float32Array(1 << 16);", "    const sr = SR(), NT = new Float32Array(1 << 16);")
rep("    const mk = (sec, ch) => ctx.createBuffer(ch || 1, Math.max(2, Math.floor(sr * sec)), sr);", "    const mk = (sec, ch) => newBuf(ch || 1, Math.max(2, Math.floor(sr * sec)), sr);")
rep("    let i = 0; const next = () => { if (ctx && i < jobs.length) { try { jobs[i++](); } finally { setTimeout(next, 0); } } }; next();",
    "    // one job between frames, and none while a match is being played (it waits for the end screen or a pause)\n    let i = 0; const next = () => { if (i < jobs.length) { if (state === 'play') { setTimeout(next, 300); return; } try { jobs[i++](); } finally { setTimeout(next, 0); } } }; next();")
rep("const conv = ctx.createConvolver(), irs = [() => { conv.buffer = plate(2.2); }];", "const conv = ctx.createConvolver(), irs = [() => { conv.buffer = PRE_IR.plate || (PRE_IR.plate = plate(2.2)); }];")
rep("irs.unshift(() => { cv.buffer = hall(2.6); });", "irs.unshift(() => { cv.buffer = PRE_IR.hall || (PRE_IR.hall = hall(2.6)); });")
rep("    SM = {}; renderKit(!live, irs);\n  }",
    """    if (!live) { SM = {}; renderKit(true, irs); }
    else if (!kitGo) { kitGo = true; SM = {}; renderKit(false, irs); }
    // made ahead (or still being made): the reverbs take their impulses as soon as they're ready
    else { const wait = () => { if (PRE_IR.plate && PRE_IR.hall) irs.forEach(f => f()); else setTimeout(wait, 250); }; wait(); }
  }""")
rep("  const api = {\n    init() {",
    """  const api = {
    // synthesize the kit and the reverbs now, while the menu is up, so the first tap (often Play) doesn't pay for it
    pre() {
      if (kitGo || ctx || typeof AudioBuffer !== 'function') return; try { new AudioBuffer({ numberOfChannels: 1, length: 2, sampleRate: PRE_SR }); } catch (e) { return; }
      kitGo = true; SM = {}; renderKit(false, [() => { PRE_IR.hall = PRE_IR.hall || hall(2.6); }, () => { PRE_IR.plate = PRE_IR.plate || plate(2.2); }]);
    },
    init() {""")
rep("showMenu();\nwarmRender();\nrequestAnimationFrame(frame);", "showMenu();\nwarmRender();\nsetTimeout(() => AU.pre(), 1200);\nrequestAnimationFrame(frame);")
open(p, 'w').write(s)
print('ok')
