"""v398: a shorter "New canvas" (the user: "Work further on that initial 'new canvas' long load time. Bake some of that into the
actual game file or something").

Measured (v397, the first New canvas after a launch): laying out and building the canvas took under a second; nearly all the rest
was making the match's shaders, about 115 of them (83 for the match itself, 31 for the victory pose drawn straight to the screen,
the edge), which a phone has to make itself: a compiled shader can't be stored in the game file. A second canvas made only one
more, because they're shared between canvases. So:

- The shaders are made in the background while you're in the lobby, or on the pages that cover it (Choose Event, the canvases),
  a few at a time, in the gaps when you aren't touching anything: in the lobby after a second and a half of quiet, under a covering
  page after a moment. A piece is followed at once by a normal frame, as v367's menu warm-up does. Whatever is done by the time you
  press Play is done; the New canvas carries on from there. In the lobby the pieces are small (about 40 of them) so none of them
  holds a frame for long.
- On an iPhone (and Safari), the browser says it can make shaders in the background (KHR_parallel_shader_compile) but its WebKit
  still makes each one on the spot when it's linked (WebKit bug 251514). The New canvas asked for every one of them at once that
  way, a long freeze before the bar could move. Now it makes them in its pieces there, the bar filling as it goes.
- The first lesson's ground (its Blank Canvas surfaces: colour, relief and shine, painted the first time a theme is used) is painted
  in the background in the lobby while the lesson is due, so the lesson's New canvas doesn't paint it.
- The canvas's layout: the distance fields the placing of basins, pick-ups and starts leans on (a third of the layout time) no longer
  make garbage on every step (two typed arrays for the queue instead of arrays of pairs). The same queue, the same order, the same
  numbers: a canvas from a seed is exactly what it was, so online matches with older games still agree on it."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

BG = r"""
// ---------- (v398) the match's shaders made ahead, in the background, while you're in the lobby or on a page that covers it. A few
// at a time in the quiet moments (no touch for a while), each piece followed at once by a normal frame; what's left when Play is
// pressed is all the New canvas has to make. And the first lesson's ground painted ahead while the lesson is due ----------
const LWB = { busy: false, quiet: 0, tex: false };
for (const t of ['pointerdown', 'pointermove', 'keydown', 'wheel']) addEventListener(t, () => { LWB.quiet = performance.now(); }, { capture: true, passive: true });
const lwbCover = () => menuPage === 'events' || menuPage === 'worlds'; // (pages that hide the lobby: nothing drawn shows)
const lwbOK = () => bootWarm && !LW.done && state === 'menu' && !document.hidden && !vic && !irisBusy && !prepOn && !building && !warming && !NM && !lookOpen && !shopOpen && !lkOn() && (lobbyOn() || lwbCover());
async function lwbTick() {
  if (LWB.busy || !lwbOK()) return;
  const quiet = performance.now() - LWB.quiet; if (quiet < (lwbCover() ? 350 : 1500)) return;
  LWB.busy = true;
  try {
    // the lesson's Blank Canvas ground, painted before the lesson asks for it
    if (!LWB.tex && typeof tutMatchDue === 'function' && tutMatchDue() && THEME_BY.blank) { LWB.tex = true; themeMats(THEME_BY.blank); await twoFrames(); return; }
    if (!LW.parts) { LW.i = 0; LW.parts = warmPieces(scene, lwbCover() ? 16 : 40); }
    if (LW.i < LW.parts.length) { warmRender(LW.parts[LW.i], 2); LW.i++; try { renderFrame(); } catch (e) {} await gpuIdle(2500); }
    else if (quiet > 2500 || lwbCover()) { warmRender(floatSet()); await gpuIdle(2500); LW.done = true; } // (the whole pass: the victory pose, the edge; then it's all done)
  } catch (e) { console.error(e); }
  finally { LWB.busy = false; }
}
setInterval(lwbTick, 300);
"""

def apply(s):
    # an iPhone links each shader on the spot: no asking for them all at once
    s = rep(s, "  if (typeof renderer.compileAsync !== 'function' || !renderer.extensions.has('KHR_parallel_shader_compile')) return; // (v269: without it, compileAsync made every one at once: the warm-up's pieces make them instead)",
               "  if (typeof renderer.compileAsync !== 'function' || !renderer.extensions.has('KHR_parallel_shader_compile')) return; // (v269: without it, compileAsync made every one at once: the warm-up's pieces make them instead)\n"
               "  if (WK_LINK) return; // (v398: WebKit says it has it, but still makes each one when it's linked: all at once froze the screen)")
    s = rep(s, "async function warmCompile() {",
               "// (v398) WebKit (every iPhone browser, Safari): KHR_parallel_shader_compile is offered, but a shader is still made when it's linked\n"
               "const WK_LINK = (() => { const u = navigator.userAgent || ''; return /iPhone|iPad|iPod/.test(u) || (/Macintosh/.test(u) && navigator.maxTouchPoints > 1) || (/AppleWebKit/.test(u) && !/(Chrome|Chromium|Edg|OPR|Android)/.test(u)); })();\n"
               "async function warmCompile() {")
    # the background warm-up, after the step it carries on
    a = s.index("async function bgWarm() {"); b = s.index("\n}\n", a) + 3
    s = s[:b] + BG.lstrip("\n") + s[b:]
    # the distance fields: the same heap, without a pair made for every step
    s = rep(s, """function navField(srcs) {
  const N = NN, d = new Float32Array(N).fill(Infinity), hi = [], hd = [];
  const push = (i, v) => { let k = hi.length; hi.push(i); hd.push(v); while (k > 0) { const p = (k - 1) >> 1; if (hd[p] <= hd[k]) break; [hi[p], hi[k]] = [hi[k], hi[p]]; [hd[p], hd[k]] = [hd[k], hd[p]]; k = p; } };
  const pop = () => { const i = hi[0], v = hd[0], li = hi.pop(), lv = hd.pop(); if (hi.length) { hi[0] = li; hd[0] = lv; let k = 0; for (;;) { const l = 2 * k + 1, r = l + 1; let m = k; if (l < hi.length && hd[l] < hd[m]) m = l; if (r < hi.length && hd[r] < hd[m]) m = r; if (m === k) break; [hi[m], hi[k]] = [hi[k], hi[m]]; [hd[m], hd[k]] = [hd[k], hd[m]]; k = m; } } return [i, v]; };
  for (const [i, v] of srcs) if (v < d[i]) { d[i] = v; push(i, v); }
  while (hi.length) { const [i, v] = pop(); if (v > d[i]) continue; const nb = NAV.nodes[i].nb; for (let e = 0; e < nb.length; e += 2) { const j = nb[e], nv = v + nb[e + 1]; if (nv < d[j]) { d[j] = nv; push(j, nv); } } }
  return d;
}""", """// (v398: the same binary heap, step for step, in two typed arrays kept between calls: no pair made for every push and pop, which was a
// third of a canvas's layout time. Same order, same numbers: a seed lays out exactly the canvas it did)
let NF_HI = new Int32Array(1024), NF_HD = new Float64Array(1024);
function navField(srcs) {
  const N = NN, d = new Float32Array(N).fill(Infinity); let hi = NF_HI, hd = NF_HD, n = 0;
  const push = (i, v) => { if (n === hi.length) { const a = new Int32Array(n * 2), b = new Float64Array(n * 2); a.set(hi); b.set(hd); NF_HI = hi = a; NF_HD = hd = b; }
    let k = n++; hi[k] = i; hd[k] = v; while (k > 0) { const p = (k - 1) >> 1; if (hd[p] <= hd[k]) break; const ti = hi[p]; hi[p] = hi[k]; hi[k] = ti; const tv = hd[p]; hd[p] = hd[k]; hd[k] = tv; k = p; } };
  for (const [i, v] of srcs) if (v < d[i]) { d[i] = v; push(i, v); }
  while (n) {
    const i = hi[0], v = hd[0]; n--;
    if (n) { hi[0] = hi[n]; hd[0] = hd[n]; let k = 0; for (;;) { const l = 2 * k + 1, r = l + 1; let m = k; if (l < n && hd[l] < hd[m]) m = l; if (r < n && hd[r] < hd[m]) m = r; if (m === k) break; const ti = hi[m]; hi[m] = hi[k]; hi[k] = ti; const tv = hd[m]; hd[m] = hd[k]; hd[k] = tv; k = m; } }
    if (v > d[i]) continue; const nb = NAV.nodes[i].nb; for (let e = 0; e < nb.length; e += 2) { const j = nb[e], nv = v + nb[e + 1]; if (nv < d[j]) { d[j] = nv; push(j, nv); } }
  }
  return d;
}""")
    return s
