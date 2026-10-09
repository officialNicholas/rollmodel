import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# cards never grow wider than the screen (a text field's natural width was pushing the name card off the edge)
rep(".modal{position:absolute;inset:0;z-index:12;display:grid;place-items:center;", ".modal{position:absolute;inset:0;z-index:12;display:grid;grid-template-columns:minmax(0,1fr);place-items:center;")
rep(".namefield input{flex:1;min-width:0;", ".namefield input{flex:1;min-width:0;width:100%;")
rep('<input id="nameInput" type="text" maxlength="12"', '<input id="nameInput" type="text" size="8" maxlength="12"')

# ---------- a loading screen until the first frame is drawn ----------
rep('  <section class="victory" id="victory" hidden aria-live="polite">', '''  <div class="boot" id="boot" role="status"><span class="bootdrop" aria-hidden="true"></span><p class="bootmsg" id="bootMsg">Loading</p></div>

  <section class="victory" id="victory" hidden aria-live="polite">''')
rep("/* the victory screen:", """/* loading */
.boot{position:absolute;inset:0;z-index:40;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;background:radial-gradient(ellipse 70% 55% at 50% 45%,var(--plum-2),var(--sky) 75%);transition:opacity .45s ease,visibility .45s}
.boot.gone{opacity:0;visibility:hidden}
.bootdrop{width:46px;height:46px;background:var(--ink);border:4px solid var(--line);border-radius:50% 50% 50% 0;transform:rotate(-45deg);box-shadow:inset 7px -7px 0 rgba(255,255,255,.22),0 6px 0 var(--line);animation:bootbob .9s ease-in-out infinite}
@keyframes bootbob{50%{transform:rotate(-45deg) translate(6px,-6px) scale(1.06)}}
.bootmsg{margin:0;font:800 16px/1.4 var(--font-ui);color:var(--muted);text-align:center;max-width:28ch}
/* the victory screen:""")
rep("  .vplace,.vtag,.vname i,.vsub,.vcard,.victory.out{animation:none}", "  .vplace,.vtag,.vname i,.vsub,.vcard,.victory.out,.bootdrop{animation:none}")
rep("if (!window.THREE) { const n = $('menuNote'); n.hidden = false; n.textContent = 'The 3D engine could not load. Check your connection and reload.'; return; }",
    "if (!window.THREE) { const n = $('bootMsg'); if (n) n.textContent = \"The game couldn't load. Check your connection and reload.\"; return; }")
rep("function frame(t) {\n", "let booted = false;\nfunction frame(t) {\n  if (!booted) { booted = true; requestAnimationFrame(() => $('boot').classList.add('gone')); }\n")
open(F, 'w').write(s)
print('ok')
