import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# restart a CSS animation without forcing a layout: take the class off now, put it back next frame
rep("function banner(big, small, long) {", """const reAdd = new Map(); let reAddQ = false;
function restartCls(el, cls) { el.classList.remove(cls); let l = reAdd.get(el); if (!l) reAdd.set(el, l = []); if (!l.includes(cls)) l.push(cls); if (!reAddQ) { reAddQ = true; requestAnimationFrame(() => { reAddQ = false; for (const [e, cs] of reAdd) for (const c of cs) e.classList.add(c); reAdd.clear(); }); } }
function banner(big, small, long) {""")
rep("bannerEl.classList.remove('on'); bannerEl.classList.toggle('long', !!long); void bannerEl.offsetWidth; bannerEl.classList.add('on')", "bannerEl.classList.toggle('long', !!long); restartCls(bannerEl, 'on')")
rep("const f = $('flash'); f.classList.remove('on'); void f.offsetWidth; f.classList.add('on'); }", "restartCls($('flash'), 'on'); }")
rep("const p = $('pop'); p.textContent = t; p.classList.remove('on'); void p.offsetWidth; p.classList.add('on'); }", "const p = $('pop'); p.textContent = t; restartCls(p, 'on'); }")
rep("function kick(el, cls) { el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls); }", "function kick(el, cls) { restartCls(el, cls); }")
rep("b.classList.remove('ready'); if (ready) { void b.offsetWidth; b.classList.add('ready'); }", "if (ready) restartCls(b, 'ready'); else b.classList.remove('ready');")
open(F, 'w').write(s)
print('ok')
